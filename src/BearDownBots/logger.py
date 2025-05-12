import os
import sys
import datetime

from BearDownBots.config import Config

def setup_logging():
    """
    Set up logging so that stdout/stderr go to both a timestamped file
    in build/ and still appear on the console.
    """
    # determine project root & build/ directory
    assets_dir = Config.get_asset_dir()
    project_dir = os.path.dirname(assets_dir)
    build_dir = os.path.join(project_dir, "build")
    os.makedirs(build_dir, exist_ok=True)

    # logfile named by current timestamp
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    logfile = os.path.join(build_dir, f"{ts}.log")
    f = open(logfile, "a")

    # remember original streams
    orig_stdout = sys.stdout
    orig_stderr = sys.stderr

    class Tee:
        def __init__(self, *streams):
            self.streams = streams
        def write(self, msg):
            for s in self.streams:
                s.write(msg)
        def flush(self):
            for s in self.streams:
                try:
                    s.flush()
                except:
                    pass

    # replace stdout & stderr with our Tee
    sys.stdout = Tee(orig_stdout, f)
    sys.stderr = Tee(orig_stderr, f)

    print(f"[{ts}] Starting BearDownBotsApp — logging to {logfile}")
