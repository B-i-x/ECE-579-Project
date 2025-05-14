#!/usr/bin/env python3
import re
import sys
import csv
import argparse
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def parse_delivery_times(logfile_path):
    """
    Scan the logfile for lines like:
      2025-05-13 14:40:43 Robot 0 delivered order ...
    and return a sorted list of datetime objects.
    """
    pattern = re.compile(
        r"^(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*delivered order"
    )
    times = []
    with open(logfile_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            m = pattern.match(line)
            if m:
                ts = datetime.strptime(m.group("ts"), "%Y-%m-%d %H:%M:%S")
                times.append(ts)
    return sorted(times)


def build_throughput_timeseries(delivery_times, bin_width_seconds=1):
    """
    Given a sorted list of datetimes, build two parallel lists:
      xs : the start‐time of each bin
      ys : the count of deliveries that fell into [xs[i], xs[i] + bin_width)
    Bins cover from the first delivery to the last (inclusive).
    """
    if not delivery_times:
        return [], []

    start = delivery_times[0].replace(microsecond=0)
    end   = delivery_times[-1].replace(microsecond=0)

    bin_delta = timedelta(seconds=bin_width_seconds)
    xs = []
    ys = []

    idx = 0
    n   = len(delivery_times)
    t   = start
    while t <= end:
        bin_end = t + bin_delta
        count = 0
        # count how many deliveries fall into [t, bin_end)
        while idx < n and delivery_times[idx] < bin_end:
            count += 1
            idx += 1
        xs.append(t)
        ys.append(count)
        t += bin_delta

    return xs, ys


def plot_throughput(xs, ys, logfile_path, bin_width_seconds=1):
    """
    Render and show a line chart of xs vs ys (throughput per bin).
    """
    plt.figure(figsize=(10, 5))
    plt.plot(xs, ys, marker='o', linestyle='-')
    plt.title(f"Order Throughput (bin = {bin_width_seconds}s)")
    plt.xlabel("Time")
    plt.ylabel(f"Orders per {bin_width_seconds}s")
    plt.grid(True, axis='y')

    # format the x-axis ticks
    ax = plt.gca()
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())

    plt.tight_layout()
    out_png = logfile_path + f"_throughput_{bin_width_seconds}s_line.png"
    plt.savefig(out_png)
    print(f"Saved throughput plot to {out_png}")
    plt.show()


def main():
    parser = argparse.ArgumentParser(
        description="Plot order throughput from a log file."
    )
    parser.add_argument("logfile", help="path to the timestamped .log file")
    parser.add_argument(
        "--bin", "-b",
        type=int,
        default=5,
        help="bin width in seconds (default: 5s)"
    )
    args = parser.parse_args()

    deliveries = parse_delivery_times(args.logfile)
    if not deliveries:
        print("No delivery events found in", args.logfile)
        sys.exit(1)

    # overall stats
    first_ts = deliveries[0]
    last_ts  = deliveries[-1]
    total_time_sec = (last_ts - first_ts).total_seconds()
    total_orders   = len(deliveries)
    if total_time_sec > 0:
        ops_per_sec = total_orders / total_time_sec
        ops_per_min = ops_per_sec * 60
    else:
        ops_per_sec = float("inf")
        ops_per_min = float("inf")

    print("===== Overall throughput =====")
    print(f"Start time : {first_ts}")
    print(f"End time   : {last_ts}")
    print(f"Duration   : {total_time_sec:.2f} seconds")
    print(f"Total delivered orders: {total_orders}")
    print(f"Throughput: {ops_per_sec:.2f} orders/sec  "
          f"({ops_per_min:.1f} orders/min)")
    print("===============================")

    # build the time‐binned throughput
    xs, ys = build_throughput_timeseries(deliveries, bin_width_seconds=args.bin)

    # write CSV alongside the PNG
    csv_path = args.logfile + f"_throughput_{args.bin}s.csv"
    with open(csv_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["timestamp", f"orders_per_{args.bin}s"])
        for t, count in zip(xs, ys):
            writer.writerow([t.strftime("%Y-%m-%d %H:%M:%S"), count])
    print(f"Wrote throughput data to {csv_path}")

    # plot
    plot_throughput(xs, ys, args.logfile, bin_width_seconds=args.bin)


if __name__ == "__main__":
    main()
