#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, csv, sys, time, math, datetime

# === Knobs (env) ===
RUN_THR       = float(os.getenv("RUN_THR", "0.00025"))   # surge run threshold (ratio)
SLOPE_THR     = float(os.getenv("SLOPE_THR", "0.00018")) # slope threshold (ratio per step)
DUR_SLOPE_THR = float(os.getenv("DUR_SLOPE_THR", "0.00025"))
COOLDOWN      = int(os.getenv("COOLDOWN", "6"))          # steps cooldown between Follow
ABS_JPY       = float(os.getenv("ABS_JPY", "20000"))     # absolute JPY move for Hit(abs)
WHY_DEBUG     = os.getenv("WHY_DEBUG", "false").lower() == "true"

WINDOW_MA     = int(os.getenv("WINDOW_MA", "2"))         # MA window for pct
SLOPE_K       = int(os.getenv("SLOPE_K", "3"))           # WINDOW for slope  (# WINDOW)

LOG_PATH = "proofpack.log"

def log(line: str):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    out = f"{ts} INFO {line}"
    print(out)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(out + "\n")

def load_csv(path):
    xs = []
    with open(path) as f:
        r = csv.reader(f)
        for row in r:
            try:
                t = float(row[0]); v = float(row[1])
            except ValueError:
                # ヘッダーなど数字に変換できない行はスキップ
                continue
            xs.append((t, v))
    return xs

def moving_avg(vals, w):
    if len(vals) < w: return vals[-1]
    return sum(vals[-w:]) / w

def slope(vals, k):
    # simple linear slope over last k points (ratio per step against last value)
    if len(vals) < k: return 0.0
    ys = vals[-k:]
    n = len(ys)
    sx = sum(range(n))
    sxx = sum(i*i for i in range(n))
    sy = sum(ys)
    sxy = sum(i*ys[i] for i in range(n))
    denom = n*sxx - sx*sx
    if denom == 0: return 0.0
    a = (n*sxy - sx*sy)/denom  # slope per step (value units per step)
    last = ys[-1] if ys[-1] != 0 else 1.0
    return a/last  # ratio per step

def pct_vs_ma(v, hist, w):
    ma = moving_avg(hist, w)
    if ma == 0: return 0.0
    return (v - ma)/ma

def why(chan, reason, **kw):
    if not WHY_DEBUG: return
    kv = " ".join(f"{k}={v}" for k,v in kw.items())
    log(f"[WHY] {chan} {reason} {kv}".strip())

def main():
    if len(sys.argv) < 2:
        print("Usage: python demo.py sample.csv")
        sys.exit(1)
    path = sys.argv[1]
    xs = load_csv(path)
    if not xs:
        print("Empty series"); return

    prices = []
    last_follow_step = -999999
    last_hit_price = None

    log(f"[CFG] RUN_THR={RUN_THR:.6f} SLOPE_THR={SLOPE_THR:.6f} DUR_SLOPE_THR={DUR_SLOPE_THR:.6f} COOLDOWN={COOLDOWN} ABS_JPY={ABS_JPY:.0f}")
    for idx,(t,v) in enumerate(xs):
        prices.append(v)

        # --- Hit (abs/pct vs MA) ---
        pct = pct_vs_ma(v, prices, WINDOW_MA)
        hit_abs = False
        if last_hit_price is None:
            last_hit_price = v
        abs_move = abs(v - last_hit_price)
        if abs_move >= ABS_JPY:
            hit_abs = True

        if hit_abs:
            dir_ = "📈" if v >= last_hit_price else "📉"
            log(f"[ALERT] [Hit(abs)] BTC {dir_} {pct*100:+.2f}% price={v:.2f} note=MA-based w={WINDOW_MA} (abs>={ABS_JPY:.0f}JPY)")
            last_hit_price = v
        else:
            why("hit", "threshold", abs=f"{abs_move:.0f}", need=f"{ABS_JPY:.0f}")

        # --- Follow (surge) ---
        # run from recent base = ratio change from the min(max) over last k window depending on direction
        k = SLOPE_K
        sl = slope(prices, k)  # ratio/step
        dir_now = 1 if sl >= SLOPE_THR else (-1 if sl <= -SLOPE_THR else 0)
        # run = cumulative move from base chosen when direction set:
        # simplify: use last k window base
        if len(prices) >= k:
            base = prices[-k]
            run = ((v - base)/base) if dir_now>=0 else ((base - v)/base)
        else:
            run = 0.0

        if dir_now == 0:
            why("surge", "threshold", slope=f"{sl:.6f}", need=f"{SLOPE_THR:.6f}")
        else:
            # cooldown in steps
            if idx - last_follow_step < COOLDOWN:
                why("surge", "cooldown", steps=f"{idx-last_follow_step}", need=f"{COOLDOWN}")
            elif run >= RUN_THR or abs(sl) >= DUR_SLOPE_THR:
                last_follow_step = idx
                up = (dir_now >= 0)
                note = f"slope={sl:+.6f} run={run:+.6f}"
                log(f"[ALERT] [Follow] BTC {'📈' if up else '📉'} {run*100:+.2f}% price={v:.2f} note={note}")
            else:
                why("surge", "near", slope=f"{sl:.6f}", run=f"{run:.6f}")

if __name__ == "__main__":
    main()