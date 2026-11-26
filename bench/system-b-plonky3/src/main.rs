//! Step 0.3 smoke benchmark for system B: Plonky3 univariate STARK over KoalaBear, FRI, Keccak only.
//!
//! Proves `N` Keccak-f[1600] permutations with `p3-keccak-air`, commits with a salted (hiding)
//! Keccak Merkle tree, draws challenges from a Keccak-256 transcript, and opens through
//! `HidingFriPcs` (zero-knowledge configuration). No algebraic hash appears anywhere.
//!
//! Usage: yugen-bench-b-plonky3 <config> <num_permutations> [repeats] [queries]
//!   config = bench100   quartic extension, 256-bit digests, rate 1/2, 100 queries, 16-bit query grind
//!                       (Plonky3's own benchmark FRI parameters, with ZK on)
//!          | q100       octic extension, 384-bit digests, rate 1/16, arity 8, 110 queries by default
//!                       (chosen before soundness/ existed: it gives 61.7 QROM bits there; 199 queries
//!                       meet 100 under confirmed bounds, 94 under DKT26; pass the count as 4th arg)

use std::time::Instant;

use p3_challenger::{HashChallenger, SerializingChallenger32};
use p3_commit::ExtensionMmcs;
use p3_dft::Radix2DitParallel;
use p3_field::extension::BinomialExtensionField;
use p3_fri::{FriParameters, HidingFriPcs};
use p3_keccak::{Keccak256Hash, KeccakF, VECTOR_LEN};
use p3_keccak_air::{KeccakAir, generate_trace_rows};
use p3_koala_bear::KoalaBear;
use p3_merkle_tree::MerkleTreeHidingMmcs;
use p3_symmetric::{CompressionFunctionFromHasher, PaddingFreeSponge, SerializingHasher};
use p3_uni_stark::{StarkConfig, prove, verify};
use rand::rngs::StdRng;
use rand::{RngExt, SeedableRng};

type Val = KoalaBear;
/// Salt per Merkle leaf, in KoalaBear elements: 9 x 31 bits = 279 bits (plan §4: at least 32 bytes).
const SALT_ELEMS: usize = 9;

/// FRI shape for one run.
struct Shape {
    log_blowup: usize,
    num_queries: usize,
    max_log_arity: usize,
    query_pow: usize,
    commit_pow: usize,
    batch_pow: usize,
    /// Random codewords mixed into the batch (HidingFriPcs); at least the extension degree.
    random_codewords: usize,
}

macro_rules! run_config {
    ($name:ident, $deg:literal, $digest_lanes:literal) => {
        fn $name(num_perms: usize, shape: &Shape, repeats: usize) {
            type Challenge = BinomialExtensionField<Val, $deg>;
            type U64Hash = PaddingFreeSponge<KeccakF, 25, 17, $digest_lanes>;
            type FieldHash = SerializingHasher<U64Hash>;
            type Compress = CompressionFunctionFromHasher<U64Hash, 2, $digest_lanes>;
            type ValMmcs = MerkleTreeHidingMmcs<
                [Val; VECTOR_LEN],
                [u64; VECTOR_LEN],
                FieldHash,
                Compress,
                StdRng,
                2,
                $digest_lanes,
                SALT_ELEMS,
            >;
            type ChallengeMmcs = ExtensionMmcs<Val, Challenge, ValMmcs>;
            type Dft = Radix2DitParallel<Val>;
            type Challenger = SerializingChallenger32<Val, HashChallenger<u8, Keccak256Hash, 32>>;
            type Pcs = HidingFriPcs<Val, Dft, ValMmcs, ChallengeMmcs, StdRng>;
            type Config = StarkConfig<Pcs, Challenge, Challenger>;

            let mut sizes = Vec::new();
            let mut prove_s = Vec::new();
            let mut verify_ms = Vec::new();
            for rep in 0..repeats {
                let u64_hash = U64Hash::new(KeccakF {});
                // Benchmark seeding only; production seeds from the operating system.
                let val_mmcs = ValMmcs::new(
                    FieldHash::new(u64_hash),
                    Compress::new(u64_hash),
                    0,
                    StdRng::seed_from_u64(1000 + rep as u64),
                );
                let challenge_mmcs = ChallengeMmcs::new(val_mmcs.clone());
                let fri = FriParameters {
                    log_blowup: shape.log_blowup,
                    log_final_poly_len: 0,
                    max_log_arity: shape.max_log_arity,
                    num_queries: shape.num_queries,
                    batch_proof_of_work_bits: shape.batch_pow,
                    commit_proof_of_work_bits: shape.commit_pow,
                    query_proof_of_work_bits: shape.query_pow,
                    mmcs: challenge_mmcs,
                };
                let pcs = Pcs::new(
                    Dft::default(),
                    val_mmcs,
                    fri,
                    shape.random_codewords,
                    StdRng::seed_from_u64(2000 + rep as u64),
                );
                let config = Config::new(pcs, Challenger::from_hasher(vec![], Keccak256Hash {}));

                let mut rng = StdRng::seed_from_u64(7);
                let inputs: Vec<[u64; 25]> = (0..num_perms).map(|_| rng.random()).collect();
                let air = KeccakAir {};

                let t0 = Instant::now();
                let trace = generate_trace_rows::<Val>(inputs, shape.log_blowup);
                let proof = prove(&config, &air, trace, &[]).expect("prove");
                let t_prove = t0.elapsed().as_secs_f64();

                let bytes = postcard::to_allocvec(&proof).expect("serialize");
                let t1 = Instant::now();
                verify(&config, &air, &proof, &[]).expect("verify");
                let t_verify = t1.elapsed().as_secs_f64() * 1000.0;

                sizes.push(bytes.len());
                prove_s.push(t_prove);
                verify_ms.push(t_verify);
            }
            report(stringify!($name), num_perms, shape, &sizes, &prove_s, &verify_ms);
        }
    };
}

run_config!(run_d4_digest256, 4, 4);
run_config!(run_d8_digest384, 8, 6);

fn report(name: &str, n: usize, s: &Shape, sizes: &[usize], prove_s: &[f64], verify_ms: &[f64]) {
    let mean = |v: &[f64]| v.iter().sum::<f64>() / v.len() as f64;
    let minf = |v: &[f64]| v.iter().cloned().fold(f64::INFINITY, f64::min);
    println!("system B (Plonky3 0.9.0-rc.2, KoalaBear, FRI, Keccak, HidingFriPcs) config={name}");
    println!(
        "  keccak-f permutations      : {n} (24 rows each; log_blowup {}, queries {}, arity 2^{}, pow query/commit/batch {}/{}/{}, random codewords {})",
        s.log_blowup, s.num_queries, s.max_log_arity, s.query_pow, s.commit_pow, s.batch_pow, s.random_codewords
    );
    println!("  proof size (postcard)      : {} bytes ({:.1} KiB)", sizes[0], sizes[0] as f64 / 1024.0);
    println!(
        "  prove (trace gen + prove)  : mean {:.3} s, min {:.3} s over {} runs",
        mean(prove_s),
        minf(prove_s),
        prove_s.len()
    );
    println!("  verify                     : mean {:.2} ms, min {:.2} ms", mean(verify_ms), minf(verify_ms));
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let config = args.get(1).map(String::as_str).unwrap_or("bench100");
    let n: usize = args.get(2).and_then(|s| s.parse().ok()).unwrap_or(128);
    let repeats: usize = args.get(3).and_then(|s| s.parse().ok()).unwrap_or(3);
    match config {
        "bench100" => run_d4_digest256(
            n,
            &Shape {
                log_blowup: 1,
                num_queries: 100,
                max_log_arity: 1,
                query_pow: 16,
                commit_pow: 0,
                batch_pow: 0,
                random_codewords: 4,
            },
            repeats,
        ),
        "q100" => {
            let q: usize = args.get(4).and_then(|s| s.parse().ok()).unwrap_or(110);
            run_d8_digest384(
                n,
                &Shape {
                    log_blowup: 4,
                    num_queries: q,
                    max_log_arity: 3,
                    query_pow: 24,
                    commit_pow: 16,
                    batch_pow: 16,
                    random_codewords: 8,
                },
                repeats,
            )
        }
        other => panic!("unknown config {other}"),
    }
}
