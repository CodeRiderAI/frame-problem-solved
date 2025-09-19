import csv
def load_csv(path):
    xs = []
    with open(path, 'r', encoding='utf-8') as f:
        for row in csv.reader(f):
            if not row or row[0].startswith('#'):
                continue
            try:
                t = float(row[0]); v = float(row[1])
                xs.append((t, v))
            except:
                pass
    return xs
