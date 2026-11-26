//! Single-thread Keccak-f[1600] throughput: the cost unit of proof-of-work grinding (one
//! permutation per nonce for a transcript state that fits one rate block).
//! Usage: yugen-bench-keccak-rate [log2_permutations]
use std::time::Instant;

fn main() {
    let log_n: u32 = std::env::args().nth(1).and_then(|s| s.parse().ok()).unwrap_or(24);
    let n = 1u64 << log_n;
    let mut state = [0u64; 25];
    let t = Instant::now();
    for i in 0..n {
        state[0] ^= i;
        keccak::f1600(&mut state);
    }
    let s = t.elapsed().as_secs_f64();
    println!("keccak-f[1600] x 2^{log_n}: {s:.3} s, {:.2} M permutations/s, check {:x}", n as f64 / s / 1e6, state[0]);
}
