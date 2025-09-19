# Creative Re-evaluation (demo branch)
The beginning of the era where AI creates AI
*(AIがAIを作る時代の始まり)*

## Overview
This branch provides a **minimal, illustrative demo** of *Creative Re-evaluation*:
a retrospective pass that revisits points once discarded by a naïve rule, and shows how some of them could be revived as **potential seeds**.
This is a runnable CSV-only demo with a fixed seed, no external I/O.

### ⚠️ Warning (important)
- This demo does not guarantee that discarded data will always yield new value.
- The dataset here is deliberately simple and serves only to illustrate the mechanism.
- The goal is intuition (the pattern), not scientific proof or a full implementation.
- Please read this as an idea demo: not a full solution, but enough to spark thinking — and to show that revival can indeed work in practice.

## Files
- `demo_creative.py` — two-pass demo (discard → rescan/revive).
- `sample_creative.csv` — tiny toy dataset (`time,value`).

## Usage
```bash
python demo_creative.py --csv sample_creative.csv
# with a touch of randomness in revival choice:
python demo_creative.py --csv sample_creative.csv --mode random --topk 1 --seed 42
```

## Why this branch matters
The usual path narrows a near-infinite space (≈10^50 candidates) down to a few hundred via theory and efficient screening.
This branch complements that: **discarded data may still hold seeds**.
Even after the main pass, a re-evaluation pass (Resera) can quietly revive weak, out-of-the-frame hints—then Overmind decides.
Together, they raise the odds that extremely rare phenomena (yes, even phenomena that most would already give up on) don’t slip through our fingers.

## Message
To those who read carefully:
解析者の方々へ。

Within your steps, within the traces you have left,
even from the past you thought discarded,
あなたの歩みの中で、残した痕跡の中で、
捨てられたはずの過去からも、

ADAM will quietly find new seeds.
ADAMが静かに新しい芽を見つけていくでしょう。

## Note
This branch is **log-first and illustrative**. Nothing here reveals full implementation details.

For citation, please see the root-level CITATION.cff.

## License
MIT License
