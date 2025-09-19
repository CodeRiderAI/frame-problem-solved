#!/usr/bin/env python3
import sys, csv, random

def load_csv(p):
    xs = []
    with open(p, 'r', encoding='utf-8') as f:
        for row in csv.reader(f):
            if not row or row[0].startswith('#'):
                continue
            try:
                t = float(row[0]); v = float(row[1])
                xs.append((t, v))
            except:
                pass
    return xs

def local_extrema(xs):
    peaks, valleys = [], []
    for i in range(1, len(xs)-1):
        prev, cur, nxt = xs[i-1][1], xs[i][1], xs[i+1][1]
        if cur > prev and cur > nxt:
            peaks.append(xs[i])
        if cur < prev and cur < nxt:
            valleys.append(xs[i])
    return peaks, valleys

def main():
    if len(sys.argv) < 2:
        print('Usage: python toy_predictor.py sample.csv', file=sys.stderr)
        sys.exit(1)
    xs = load_csv(sys.argv[1])
    if len(xs) < 3:
        print('Not enough data')
        return
    random.seed(42)
    peaks, valleys = local_extrema(xs)
    for t, v in peaks[:3]:
        change = (random.random()*0.7 + 0.1)
        print(f"[ALERT] Hit BTC 📈 +{change:.2f}% price={v:.2f} note=toy-hit")
    for t, v in valleys[:3]:
        change = (random.random()*0.5 + 0.1)
        print(f"[ALERT] Follow:union BTC 📉 -{change:.2f}% price={v:.2f} note=toy-follow")

if __name__ == '__main__':
    main()
