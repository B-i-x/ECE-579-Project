#!/usr/bin/env python3
import os
import argparse
import csv
from datetime import datetime
import matplotlib.pyplot as plt

def read_csv(path):
    """
    Read a two-column CSV with header "timestamp,orders_per_*s",
    parse timestamps and counts, and return (list_of_datetimes, list_of_ints).
    """
    times = []
    counts = []
    with open(path, newline='') as f:
        reader = csv.reader(f)
        header = next(reader, None)
        for row in reader:
            if len(row) < 2:
                continue
            ts_str, cnt_str = row[0].strip(), row[1].strip()
            try:
                dt = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
                cnt = int(cnt_str)
            except ValueError:
                continue
            times.append(dt)
            counts.append(cnt)
    return times, counts

def gather_csvs(inputs):
    """
    Given a list of input paths, expand directories into all .csv files,
    and return the flattened list of csv file paths.
    """
    all_csvs = []
    for p in inputs:
        if os.path.isdir(p):
            for fn in os.listdir(p):
                if fn.lower().endswith('.csv'):
                    all_csvs.append(os.path.join(p, fn))
        elif os.path.isfile(p) and p.lower().endswith('.csv'):
            all_csvs.append(p)
        else:
            print(f"Warning: skipping non-CSV path {p}")
    return sorted(all_csvs)

def main():
    p = argparse.ArgumentParser(
        description="Compare throughput CSVs by plotting orders/bin vs time elapsed."
    )
    p.add_argument(
        "inputs", nargs="+",
        help="One or more CSV files or directories containing CSVs"
    )
    p.add_argument(
        "--save", "-s",
        help="Optional path to save the combined plot (e.g. out.png)"
    )
    args = p.parse_args()

    csvfiles = gather_csvs(args.inputs)
    if not csvfiles:
        print("No CSV files found in your inputs:", args.inputs)
        return

    plt.figure(figsize=(10,6))
    for csvfile in csvfiles:
        times, counts = read_csv(csvfile)
        if not times:
            print(f"Warning: no data in {csvfile}")
            continue

        # compute elapsed seconds from first timestamp
        start = times[0]
        elapsed = [(t - start).total_seconds() for t in times]

        # label by filename only
        label = os.path.basename(csvfile)
        plt.plot(elapsed, counts, linestyle='-', label=label)

    plt.xlabel("Time elapsed (s)")
    plt.ylabel("Orders per bin")
    plt.title("Throughput comparison")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    if args.save:
        plt.savefig(args.save)
        print(f"Saved combined plot to {args.save}")
    else:
        plt.show()

if __name__ == "__main__":
    main()
