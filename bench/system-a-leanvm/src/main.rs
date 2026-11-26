//! Step 0.3 smoke benchmark for system A: leanVM (binary field GF(2^128), WHIR, Keccak only).
//!
//! Proves a chain of `N` Keccak-256 two-to-one compressions (`h_{i+1} = keccak(h_i || h_i)`,
//! one Keccak-f[1600] permutation each), the shape of a Merkle path, with the final digest bound
//! as the public input. Proves on leanVM's stable prover and verifies with its verifier crate.
//!
//! Usage: yugen-bench-a-leanvm <num_compressions> [repeats] [log_inv_rate] [threads] [log_extra_cycles]
//!
//! `log_extra_cycles` (design basis, optional) adds a runtime loop of 2^k field squarings before the
//! hash chain, so that the committed trace reaches leaf size (the Yugen leaf is estimated at about
//! 2^19 cycles in docs/framework-selection.md section 6). The loop's result is not published.

use std::time::Instant;

use isa::Prover;
use stable_lean_vm_core::StableProver;
use zkdsl_compiler::{compile, parse};

fn chain_source(n: usize, log_extra: usize) -> String {
    let mut s = String::from("def main():\n");
    if log_extra > 0 {
        s += &format!(
            "    sq = HeapBuf({})\n    sq[1] = GEN\n    for i in mul_range(1, GEN ** {}):\n        sq[i * GEN] = sq[i] * sq[i]\n",
            (1usize << log_extra) + 2,
            1usize << log_extra
        );
    }
    s += "    h0 = StackBuf(2)\n    h0[0] = 5\n    h0[1] = 7\n";
    for i in 0..n {
        s += &format!("    h{} = StackBuf(2)\n    keccak(h{i}, h{i}, h{})\n", i + 1, i + 1);
    }
    s += &format!("    p = 1\n    p[1] = h{n}[0]\n    p[GEN] = h{n}[1]\n    return\n");
    s
}

fn chained_digest(n: usize) -> [u8; 32] {
    let mut h = [0u8; 32];
    (h[0], h[16]) = (5, 7);
    for _ in 0..n {
        h = keccak256::hash_pair(&h, &h);
    }
    h
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let n: usize = args.get(1).and_then(|s| s.parse().ok()).unwrap_or(128);
    let repeats: usize = args.get(2).and_then(|s| s.parse().ok()).unwrap_or(3);
    let log_inv_rate: usize = args.get(3).and_then(|s| s.parse().ok()).unwrap_or(1);
    let threads: usize = args.get(4).and_then(|s| s.parse().ok()).unwrap_or(0);
    let log_extra: usize = args.get(5).and_then(|s| s.parse().ok()).unwrap_or(0);
    StableProver::set_num_threads(threads);
    StableProver::init();

    let program = isa::Program::from(compile(&parse(&chain_source(n, log_extra)).expect("parse")));
    let digest = chained_digest(n);
    let (lo, hi) = verifier::Digest(digest).halves();
    let pi = [lo, hi];

    let mut prove_s = Vec::new();
    let mut verify_ms = Vec::new();
    let mut size = 0;
    let mut cycles = 0;
    for _ in 0..repeats {
        let t0 = Instant::now();
        let (proof, stats) = StableProver::prove(&program, &[], pi, log_inv_rate).expect("prove");
        prove_s.push(t0.elapsed().as_secs_f64());
        let t1 = Instant::now();
        verifier::verify_execution(program.bytecode(), &digest, &proof).expect("verify");
        verify_ms.push(t1.elapsed().as_secs_f64() * 1000.0);
        size = proof.to_bytes().len();
        cycles = stats.cycles;
    }
    let mean = |v: &[f64]| v.iter().sum::<f64>() / v.len() as f64;
    let minf = |v: &[f64]| v.iter().cloned().fold(f64::INFINITY, f64::min);
    println!("system A (leanVM @ 84780fb4, stable prover, GF(2^128), WHIR, Keccak)");
    println!(
        "  keccak compressions        : {n} (VM cycles {cycles}, log_inv_rate {log_inv_rate}, threads {})",
        if threads == 0 { "default".to_string() } else { threads.to_string() }
    );
    println!("  proof size                 : {size} bytes ({:.1} KiB)", size as f64 / 1024.0);
    println!(
        "  prove                      : mean {:.3} s, min {:.3} s over {} runs",
        mean(&prove_s),
        minf(&prove_s),
        prove_s.len()
    );
    println!("  verify                     : mean {:.2} ms, min {:.2} ms", mean(&verify_ms), minf(&verify_ms));
}
