from .loader import load_csv
import os, argparse, math

def wide_range_demo(inp, outdir):
    xs = load_csv(inp)  # [(t,v), ...]
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "wide_range.log")

    # 環境変数ノブ（demo.pyと同名で合わせる）
    RUN_THR      = float(os.getenv("RUN_THR",      "0.00025"))
    SLOPE_THR    = float(os.getenv("SLOPE_THR",    "0.00018"))
    COOLDOWN_WIN = int(float(os.getenv("COOLDOWN", "6")))

    W = int(os.getenv("RUN_WIN", "5"))  # 簡易の走行量ウィンドウ
    alerts = []
    cool = 0

    def pct(a, b):
        try:
            return (b - a) / max(1e-12, a)
        except Exception:
            return 0.0

    for i in range(1, len(xs)):
        if cool > 0:
            cool -= 1
            continue

        # slope（一歩の勾配）
        s = pct(xs[i-1][1], xs[i][1])

        # run（直近Wの累積abs・比率）
        j0 = max(0, i - W)
        r = 0.0
        for j in range(j0+1, i+1):
            r += abs(pct(xs[j-1][1], xs[j][1]))

        if s >= SLOPE_THR or r >= RUN_THR:
            line = f"[ALERT] [Follow] BTC 📈 {s:+.4%} price={xs[i][1]:.2f} note=slope={s:+.6f} run={r:+.6f}"
            print(line)
            alerts.append(line)
            cool = COOLDOWN_WIN

    with open(path, "w", encoding="utf-8") as f:
        for ln in alerts: f.write(ln + "\n")

    # 画面に簡易CFGも出す
    print(f"[CFG] RUN_THR={RUN_THR:.6f} SLOPE_THR={SLOPE_THR:.6f} COOLDOWN={COOLDOWN_WIN} RUN_WIN={W}")
    return {"name": "wide_range", "kept": len(alerts), "log": path}

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="sample.csv")
    ap.add_argument("--out", default="logs")
    args = ap.parse_args()
    res = wide_range_demo(args.csv, args.out)
    print(f"[CFG] alerts={res['kept']} log={res['log']}")