# yugen-proofs

Part of Yugen, the post-quantum shielded pool for Ycash. | Path | Step | What |
|---|---|---|
| `docs/framework-selection.md` | 0.3 | Choice of proof systems A (leanVM) and B (Plonky3), criteria, measurements, risks, layout for 0.4 |
| `docs/what-is-proven.md` | 0.6 | Every soundness and zero-knowledge claim with its figure and status (proven / conditional / owed), its proof and whether refereed; the open obligations |
| `docs/soundness-method.md` | 0.6 | How soundness is computed, with every formula's source and status |
| `soundness/` | 0.6 | The calculator: `cd soundness && uv run yugen-soundness`; tests: `uv run pytest` |
| `bench/` | 0.3 | Smallest Keccak proofs in each pinned framework; raw results in `bench/results/` |

Builds: `.cargo/config.toml` sets `-j 3` and `target/`; run cargo under `nice -n 10` .

## Provenance and licence

`REFERENCES.md` lists every paper used, the result taken from each and where it is relied on, and
labels each part **Published**, **Adapted** or **Original (the Ycash developers, 2026)**. Some
documents cite working repositories and studies that are not published (`yugen-pir`,
`yugen-review`, `yugen-zk-b`, `yugen-b-eval`, `yugen-plan-draft`, `yugen-bundler`, the bundle-mining
design record and the single-server PIR study); their conclusions are restated where they are used.
Commit hashes quoted in the documents refer to the working history before publication.

Licence: MIT, see `LICENSE`.
