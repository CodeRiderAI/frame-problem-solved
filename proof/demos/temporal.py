from .loader import load_csv
import os, argparse

def temporal_demo(inp, outdir):
    xs = load_csv(inp)
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "temporal.log")

    # ノブ（demo.py と名称合わせ）
    DUR_SLOPE_THR = float(os.getenv("DUR_SLOPE_THR", "0.00025"))
    DUR_MIN_SAMPLES = int(os.getenv("DUR_MIN_SAMPLES", "3"))
    COOLDOWN_WIN = int(float(os.getenv("COOLDOWN", "6")))

    alerts = []
    cool = 0

    def pct(a, b):
        try: return (b - a) / max(1e-12, a)
        except: return 0.0

    # 連続上昇/下降の「塊」を拾う
    i = 1
    while i < len(xs):
        if cool > 0:
            cool -= 1
            i += 1
            continue

        start = i-1
        sign = 1 if xs[i][1] >= xs[i-1][1] else -1
        j = i
        while j < len(xs):
            s = pct(xs[j-1][1], xs[j][1])
            if (s >= 0) != (sign >= 0):
                break
            j += 1
        length = j - start  # 連続サンプル数
        if length >= DUR_MIN_SAMPLES:
            # 平均勾配で判定
            s_total = pct(xs[start][1], xs[j-1][1])
            s_avg = s_total / max(1, length-1)
            if abs(s_avg) >= DUR_SLOPE_THR:
                arrow = "📈" if s_avg > 0 else "📉"
                line = f"[ALERT] [Follow] BTC {arrow} {s_avg:+.4%} price={xs[j-1][1]:.2f} note=dur_len={length} slope_avg={s_avg:+.6f}"
                print(line)
                alerts.append(line)
                cool = COOLDOWN_WIN
                i = j
                continue
        i = max(i+1, j)

    with open(path, "w", encoding="utf-8") as f:
        for ln in alerts: f.write(ln + "\n")

    print(f"[CFG] DUR_SLOPE_THR={DUR_SLOPE_THR:.6f} DUR_MIN_SAMPLES={DUR_MIN_SAMPLES} COOLDOWN={COOLDOWN_WIN}")
    return {"name": "temporal", "kept": len(alerts), "log": path}

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="sample.csv")
    ap.add_argument("--out", default="logs")
    args = ap.parse_args()
    res = temporal_demo(args.csv, args.out)
    print(f"[CFG] alerts={res['kept']} log={res['log']}")