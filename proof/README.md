# Proof Pack v0.1

**The beginning of the era where AI creates AI**
*(AIがAIを作る時代の始まり)*

This folder is a **minimal proof pack**: a small set of scripts and logs that
let you independently verify that the **Frame Problem** can be *practically bypassed*
under controlled conditions. It is intentionally lightweight and educational—
not production. See the demos below and the troubleshooting guide at the end.

This folder contains the reproducibility pack ("Proof Pack").
- `sample.csv` + scripts → generate `sample.log`
- `sample.log.sha256` → verify integrity
- `replay.sh` → reproduce or validate

See the root README for details.

---

## Quickstart

```bash
python demo.py sample.csv
```

- Python 3.9+ (no external packages required)
- Output goes to stdout and to `proofpack.log`

---

## Demonstrations

Tip: demos can be run as a package, e.g., `python -m demos.wide_range --csv sample.csv --out logs`.

This pack contains four small “views” over the same core idea—**consciously restricting
and relaxing the frame** so exploration does not explode:

- **Candidate Filtering** – narrow wide candidates while staying tractable.
- **Wide-range Exploration** – show feasible paths emerge without brute force.
- **Temporal Sequences** – handle mid‑horizon signals where naïve methods fail.
- **Network Use‑case (surrogate)** – hint expansion to larger, interconnected data.

Each demo emits operational‑style logs such as `[ALERT] Hit` and `[ALERT] Follow`.
A sample log is included in `sample.log`.

Note: Depending on the demo and parameters, some scripts may emit only
`[ALERT] Follow` by default. For example, `network_surrogate.py` uses a
neighborhood-mean check for absolute deviations (`ABS_JPY`) and may remain
quiet with the bundled `sample.csv`. To force `[Hit(abs)]` output, try
lowering the threshold or shrinking the neighborhood, e.g.:

```bash
ABS_JPY=15000 NSURR_K=2 python -m demos.network_surrogate --csv sample.csv --out logs
```
This behavior is intentional—the four demos are illustrative “views” on the
same idea, not guaranteed to fire simultaneously on the same dataset.

ADAMは見据え、なお捨てる。

---

## Verification & Troubleshooting (Proof Pack)

This proof pack is designed to be **reproducible** with the bundled data.
If your own data does not produce `[ALERT] Hit/Follow` immediately, use this
short checklist. (You will not reach any “full-spec” internals by doing so.)

For smaller-scale demo data (e.g. sample.csv around 100),
lower the ABS_JPY threshold via:
    ABS_JPY=1.0 python demo.py sample.csv

> Note: Normally, verification should be performed with:
>
> ```bash
> sha256sum -c proofpack/sample.log.sha256
> ```
>
> Re-generation of the checksum file (`sample.log.sha256`) should be done **only once by the original committer**, not by users. This ensures that the reference checksum remains consistent across all verifications.

### 0) Baseline
- Run `sample.csv` first and confirm you can reproduce the sample log
  (line‑for‑line or within small numeric round‑off).
- Use Python 3.9+; no external libs are required.

### 1) Your data format
- CSV must be **`time,value`** (time = monotonically increasing; no gaps/dups).
- `value` must have **some** variance (perfectly flat or pure white‑noise is out of scope).
- Length: enough to cover the demo windows.

### 2) When “nothing triggers”
- Turn on WHY logs to see how close you are:
  ```bash
  export WHY_DEBUG=true
  ```
  If you see many `near` and `threshold` reasons, you are “close but short”.

- **Move only one knob, one step (exact names):**
  ```ini
  # Surge (Follow)
  RUN_THR       = 0.00025  →  0.00023   # one small step
  SLOPE_THR     = 0.00018  →  0.00017   # one small step
  DUR_SLOPE_THR = 0.00025  →  0.00023   # only if you use the dur‑route

  # Hit (absolute moves)
  ABS_JPY       = 20000     →  30000    # tighten if too chatty / loosen if silent
  ```

- If the series is very smooth, increase the demo’s window length slightly
  (see `# WINDOW` comment inside the script).

### 3) When it is “too chatty”
- Revert the previous step or tighten **one** notch:
  ```ini
  RUN_THR    0.00023 → 0.00025
  SLOPE_THR  0.00017 → 0.00018
  COOLDOWN   6       → 8
  ABS_JPY    30000   → 35000
  ```
- Do **not** change multiple knobs at once; avoid chasing noise.

### 4) Environment checklist
- Python 3.9+
- CSV encoding: UTF‑8 (no BOM), UNIX LF line endings preferred.

### 5) Typical pitfalls (and fixes)
- **Empty / very short series** → Provide longer data.
- **Non‑monotonic time** → Sort / deduplicate timestamps.
- **Extreme outliers** → Consider clipping or smoothing (demo‑level preprocessing).
- **No variance** → Completely flat lines will not alert by design.

### 6) Reading WHY logs quickly
- `near`  = close to threshold (one small notch may be enough).
- `cooldown` = it would have triggered, but you are within a cooldown window.
- `threshold` = simply not enough signal yet.

**Rule of thumb:** Change **one** parameter by **one** small step, then re‑run.
If you need more than two steps, reconsider the data (format/length/variance).

---
## Limitations

- This repository is a **toy-level, reproducible proof pack**.
  The production logic (Eve Trigger, EventSpace, pow/to_hit definitions, Resera, Fenrir, Overmind internals) **is NOT included**.
- The demos are intentionally lightweight and educational; **performance numbers do not represent the full system**.
- Integrity of exemplar logs is ensured by `proofpack/sample.log.sha256`.
  For fair replication, please run `scripts/replay.sh` and verify the checksum before drawing conclusions.
- You may **freely cite** this repository (see `CITATION.cff`). A DOI will be attached via Zenodo to each tagged release.
- This repository demonstrates an **implementation-level solution** to the framing problem.
  It does not address the philosophical debate around the Frame Problem,
  but focuses on a reproducible technical mechanism to avoid exhaustive condition checking.
- 本リポジトリはフレーム問題に対する **実装レベルの解** を示しています。
  哲学的な議論全体を対象とするものではなく、
  実運用上での条件爆発を回避する再現可能な技術的仕組みを示しています。

## Notes

- Minimal, dependency‑free, educational. Not production.
- Proof‑of‑principle only; **full‑spec** exists elsewhere and is not revealed here.

For citation, please see the root-level CITATION.cff.

## License

MIT License
