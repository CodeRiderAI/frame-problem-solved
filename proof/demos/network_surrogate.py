from .loader import load_csv
import os, argparse, statistics

def network_surrogate_demo(inp, outdir):
    xs = load_csv(inp)
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "network_surrogate.log")

    ABS_JPY  = float(os.getenv("ABS_JPY", "20000"))  # demo.py と同名
    K        = int(os.getenv("NSURR_K", "3"))        # 近傍幅（片側K点）

    alerts = []

    def neigh_mean(idx):
        j0 = max(0, idx-K)
        j1 = min(len(xs), idx+K+1)
        vals = [v for _, v in xs[j0:j1] if v is not None]
        return statistics.mean(vals) if vals else xs[idx][1]

    for i in range(len(xs)):
        v = xs[i][1]
        m = neigh_mean(i)
        diff = v - m
        if abs(diff) >= ABS_JPY:
            arrow = "📈" if diff > 0 else "📉"
            line = f"[ALERT] [Hit(abs)] BTC {arrow} {diff:+.0f}JPY price={v:.2f} note=nsurr_mean={m:.2f} K={K} (abs>={ABS_JPY:.0f}JPY)"
            print(line)
            alerts.append(line)

    with open(path, "w", encoding="utf-8") as f:
        for ln in alerts: f.write(ln + "\n")

    print(f"[CFG] ABS_JPY={ABS_JPY:.0f} NSURR_K={K}")
    return {"name": "network_surrogate", "kept": len(alerts), "log": path}

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="sample.csv")
    ap.add_argument("--out", default="logs")
    args = ap.parse_args()
    res = network_surrogate_demo(args.csv, args.out)
    print(f"[CFG] alerts={res['kept']} log={res['log']}")