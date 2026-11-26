//! Step 0.3 / design-basis benchmark for system B in Plonky3's native binary configuration.
//!
//! Proves `N` Keccak-f[1600] permutations with `KeccakBinaryAir` (Boolean trace), a Keccak-256
//! Merkle commitment and a Keccak-256 transcript, through `p3-examples`' binary harness at the
//! pinned commit. These proofs are NOT zero-knowledge (Plonky3's binary path is non-hiding at the
//! pin; see docs/framework-selection.md).
//!
//! Usage (positional form, kept from step 0.3):
//!   yugen-bench-b-plonky3-binary <pcs> <log_trace_length> [log_inv_rate] [security_bits]
//! Usage (key=value form, for the proof-size engineering measurements):
//!   yugen-bench-b-plonky3-binary pcs=folding logh=14 rate=2 sec=100 fold=4 arity=4 pow=0 \
//!       scpow=0 leaf=0 regime=ud
//!   pcs    = folding         BaseFold-style folding PCS over GF(2^128) (the harness default)
//!          | whir            additive WHIR over GF(2^128)
//!          | whir-gf192      additive WHIR, GF(2^64) values, GF(2^192) challenges
//!          (whir-ud and whir-ud-gf192 are accepted as aliases with regime=ud)
//!   fold   = variables folded between commitments (the harness's `folding`)
//!   arity  = Merkle arity, 2 or 4
//!   pow    = grinding bits before the PCS query phase (`pcs_pow_bits`)
//!   scpow  = grinding bits per sumcheck round (`sumcheck_pow_bits`)
//!   leaf   = field elements per Merkle leaf, 0 for the harness default (one fold coset)
//!   regime = ud (unique decoding) | jb (proven Johnson radius), WHIR only

use p3_binary_field::{BinaryField128, Gf2, Poly64};
use p3_examples::binary::{
    Backend, BinaryProofOptions, BinaryWhirBudget, BooleanPcsChoice, HashFamily, WhirOptions,
    WhirRegime, prove_boolean_air_cubic, prove_boolean_air_with_backend,
};
use p3_keccak_air::{KECCAK_BINARY_ROWS_PER_PERM, KeccakBinaryAir};
use p3_sumcheck::layout::Table;

fn main() {
    let args: Vec<String> = std::env::args().skip(1).collect();
    let kv = args.iter().any(|a| a.contains('='));
    let get = |key: &str, pos: usize, default: &str| -> String {
        if kv {
            args.iter()
                .find_map(|a| a.strip_prefix(&format!("{key}=")).map(str::to_string))
                .unwrap_or_else(|| default.to_string())
        } else {
            args.get(pos).cloned().unwrap_or_else(|| default.to_string())
        }
    };
    let num = |key: &str, pos: usize, default: usize| -> usize {
        get(key, pos, &default.to_string()).parse().expect("integer argument")
    };
    let mut pcs = get("pcs", 0, "folding");
    let log_height = num("logh", 1, 12);
    let log_inv_rate = num("rate", 2, 1);
    let security_bits = num("sec", 3, 100);
    let mut regime = get("regime", 99, "ud");
    if pcs == "whir-ud" || pcs == "whir-ud-gf192" {
        pcs = pcs.replace("-ud", "");
        regime = "ud".into();
    }
    let folding = num("fold", 99, 4);
    let arity = num("arity", 99, if pcs == "folding" { 4 } else { 2 });
    let pow = num("pow", 99, 0);
    let scpow = num("scpow", 99, 0);
    let leaf = num("leaf", 99, 0);

    let num_hashes = (1usize << log_height) / KECCAK_BINARY_ROWS_PER_PERM;
    let air = KeccakBinaryAir::assuming_boolean_trace();
    let whir_regime = match regime.as_str() {
        "ud" => WhirRegime::UniqueDecoding,
        "jb" => WhirRegime::Johnson,
        other => panic!("unknown regime {other}"),
    };
    let whir = BooleanPcsChoice::Whir(WhirOptions {
        regime: whir_regime,
        term_security_bits: security_bits + 2,
        budget: BinaryWhirBudget {
            max_stir_queries: 4000,
            max_proof_bytes: 256 << 20,
            max_grinding_bits: BinaryWhirBudget::PRODUCTION.max_grinding_bits.max(pow),
        },
    });
    let options = BinaryProofOptions {
        log_inv_rate,
        security_bits,
        pcs_pow_bits: pow,
        sumcheck_pow_bits: scpow,
        merkle_arity: arity,
        folding,
        hash: HashFamily::Keccak256,
        leaf_elements: if leaf == 0 { None } else { Some(leaf) },
        pcs: if pcs == "folding" { BooleanPcsChoice::Folding } else { whir },
        ..BinaryProofOptions::default()
    };
    let words = air.generate_random_trace_packed::<Gf2>(num_hashes);
    let report = match pcs.as_str() {
        "folding" | "whir" => prove_boolean_air_with_backend(
            &air,
            Table::<BinaryField128>::from_packed_bits(words, log_height),
            options,
            Backend::preferred(),
        ),
        "whir-gf192" => prove_boolean_air_cubic(
            &air,
            Table::<Poly64>::from_packed_bits(words, log_height),
            options,
        ),
        other => panic!("unknown pcs {other}"),
    }
    .expect("prove and verify");
    println!(
        "system B, Plonky3 native binary @ fe5e46d7, pcs={pcs} regime={regime} rate=1/{} fold={folding} \
         arity={arity} pow={pow} scpow={scpow} leaf={leaf}, {num_hashes} Keccak-f permutations",
        1usize << log_inv_rate
    );
    println!("{report}");
}
