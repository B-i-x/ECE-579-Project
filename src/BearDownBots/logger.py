import os
import sys
import datetime

from BearDownBots.config import Config

def setup_logging():
    """
    Set up logging so that stdout/stderr go to both a timestamped file
    in build/ and still appear on the console, with each line prefixed
    by its current timestamp (YYYY-MM-DD HH:MM:SS).
    """
    # determine project root & build/ directory
    assets_dir  = Config.get_asset_dir()
    project_dir = os.path.dirname(assets_dir)
    build_dir   = os.path.join(project_dir, "build")
    os.makedirs(build_dir, exist_ok=True)

    # logfile named by current timestamp
    ts      = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    logfile = os.path.join(build_dir, f"{ts}.log")
    f       = open(logfile, "a")

    orig_stdout = sys.stdout
    orig_stderr = sys.stderr

    class TimestampedTee:
        def __init__(self, *streams):
            self.streams       = streams
            self._at_line_start = True

        def write(self, msg):
            # split into chunks that keep newline at end
            for chunk in msg.splitlines(keepends=True):
                if self._at_line_start and chunk:
                    # emit timestamp once per new line
                    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    for s in self.streams:
                        s.write(f"{now} ")
                for s in self.streams:
                    s.write(chunk)
                # if chunk ends with "\n", next write is new line
                self._at_line_start = chunk.endswith("\n")

        def flush(self):
            for s in self.streams:
                try:
                    s.flush()
                except:
                    pass

    # replace stdout & stderr
    sys.stdout = TimestampedTee(orig_stdout, f)
    sys.stderr = TimestampedTee(orig_stderr, f)

    print(f"[{ts}] Starting BearDownBotsApp — logging to {logfile}")
