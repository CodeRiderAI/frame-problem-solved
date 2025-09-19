# demos/candidate_filtering.py 置き換え版
from .loader import load_csv
import os, argparse

def candidate_filtering_demo(inp, outdir):
    xs = load_csv(inp)
    candidates = []
    for i in range(1, len(xs)-1):
        prev, cur, nxt = xs[i-1][1], xs[i][1], xs[i+1][1]
        if cur > prev and cur > nxt:
            candidates.append({'t': xs[i][0], 'v': xs[i][1], 'type': 'peak', 'score': 1.2})
        elif cur < prev and cur < nxt:
            candidates.append({'t': xs[i][0], 'v': xs[i][1], 'type': 'valley', 'score': 1.2})

    topK = 5
    kept = candidates[:topK]

    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, 'candidate_filtering.log')
    with open(path, 'w', encoding='utf-8') as f:
        for c in kept:
            line = f"[ALERT] Hit t={c['t']:.0f} v={c['v']:.2f} type={c['type']} score={c['score']:.2f}"
            print(line)          # ← 画面にも出す
            f.write(line + "\n") # ← ファイルにも残す
    return {'name': 'candidate_filtering', 'candidates': len(candidates), 'kept': len(kept), 'log': path}

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="sample.csv", help="input CSV (time,value)")
    ap.add_argument("--out", default=".", help="output directory")
    args = ap.parse_args()
    res = candidate_filtering_demo(args.csv, args.out)
    print(f"[CFG] candidates={res['candidates']} kept={res['kept']} log={res['log']}")
