#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Creative re-evaluation demo (generalized terminology)
# - pass1: discard with a very simple threshold rule (reason is logged)
# - pass2: rescan and revive points that satisfy recovery conditions
#
# Caution
# fixed seed; offline CSV-only demo; no external calls
#
# ⚠️ 注意
# これは「仕組みのデモ」です。恣意的なサンプルを使っており、
# 失敗データから必ず芽が得られることを保証しません。

import csv
import argparse
import random
from typing import List, Tuple, Dict

def load_csv(path: str) -> List[Tuple[float, float]]:
    """Load CSV as [(time, value)], skip comment lines beginning with '#'."""
    xs = []
    with open(path, "r", encoding="utf-8") as f:
        r = csv.reader(f)
        for row in r:
            if not row or row[0].startswith("#"):
                continue
            try:
                t = float(row[0]); v = float(row[1])
                xs.append((t, v))
            except:
                # ignore non-numeric rows
                pass
    xs.sort(key=lambda x: x[0])
    return xs

def initial_pass(series: List[Tuple[float,float]], drop_eps: float = 1.5) -> Dict[str, List[Dict]]:
    """
    pass1:
      - discard by a very simple local rule (fall from previous / deviation from short MA)
      - record the reason so we can inspect later
    """
    out_keep, out_drop = [], []
    for i, (t, v) in enumerate(series):
        if i == 0:
            out_keep.append({"t": t, "v": v, "why": "first"})
            continue
        prev_v = series[i-1][1]
        window = series[max(0, i-2):i+1]
        ma = sum(p[1] for p in window) / len(window)
        fall = prev_v - v
        dev  = ma - v
        if fall >= drop_eps or dev >= drop_eps:
            out_drop.append({"t": t, "v": v, "reason": f"drop: prev-v={fall:.2f}, ma-v={dev:.2f}"})
        else:
            out_keep.append({"t": t, "v": v, "why": "norm"})
    return {"keep": out_keep, "drop": out_drop}

def rescan_and_revive(series: List[Tuple[float,float]],
                      dropped: List[Dict],
                      look_ahead: int = 2,
                      recover_eps: float = 2.0,
                      mode: str = "deterministic",
                      topk: int = 1,
                      seed: int = 42) -> List[Dict]:
    """
    pass2:
      - rescan: for each discarded point, look ahead for a limited number of steps
      - revive: if recovery >= recover_eps within the look-ahead window, mark as a seed
      - mode:
          'deterministic' -> revive all candidates that satisfy the condition
          'random'        -> pick at most topk randomly from the candidate set
    """
    random.seed(seed)
    revived_all = []
    idx_by_t = {t: i for i, (t, _) in enumerate(series)}
    for d in dropped:
        t0, v0 = d["t"], d["v"]
        i0 = idx_by_t.get(t0)
        if i0 is None:
            continue
        window = series[i0+1 : min(len(series), i0+1+look_ahead)]
        cands = []
        for tj, vj in window:
            up = vj - v0
            if up >= recover_eps:
                cands.append({
                    "t": t0, "v": v0, "seed": True,
                    "evidence": f"recovered +{up:.2f} within {look_ahead} step(s) (to t={tj})",
                    "origin_reason": d["reason"]
                })
        if not cands:
            continue
        if mode == "random":
            random.shuffle(cands)
            revived_all.extend(cands[:max(1, topk)])
        else:
            revived_all.extend(cands)
    return revived_all

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="sample_creative.csv")
    ap.add_argument("--drop-eps", type=float, default=1.5,
                    help="pass1: drop threshold (local fall / short MA deviation)")
    ap.add_argument("--look-ahead", type=int, default=2,
                    help="pass2: number of steps to look ahead")
    ap.add_argument("--recover-eps", type=float, default=2.0,
                    help="pass2: recovery threshold within look-ahead")
    ap.add_argument("--mode", choices=["deterministic","random"], default="deterministic",
                    help="revival selection mode (deterministic / random)")
    ap.add_argument("--topk", type=int, default=1,
                    help="when mode=random, maximum number of revivals")
    ap.add_argument("--seed", type=int, default=42,
                    help="random seed (used when mode=random)")
    args = ap.parse_args()

    series = load_csv(args.csv)
    if not series:
        print("[ERR] empty series"); return

    print("[Initial pass] start")
    r1 = initial_pass(series, drop_eps=args.drop_eps)
    if r1["drop"]:
        print("  discarded:")
        for d in r1["drop"]:
            print(f"    t={d['t']:.0f} v={d['v']:.2f} :: {d['reason']}")
    else:
        print("  discarded: (none)")

    print("\n[Rescan / Revive] start")
    revived = rescan_and_revive(series, r1["drop"],
                                look_ahead=args.look_ahead,
                                recover_eps=args.recover_eps,
                                mode=args.mode, topk=args.topk, seed=args.seed)
    if revived:
        for r in revived:
            print(f"  revived: t={r['t']:.0f} v={r['v']:.2f} :: {r['evidence']} | origin={r['origin_reason']}")
    else:
        print("  revived: (none)")

    print("\n[Note]")
    print("  This is a mechanism demo using a deliberately contrived sample.")
    print("  It does not guarantee that discarded data will always yield new seeds.")

if __name__ == "__main__":
    main()