"""Rebuild all ten editorial paper previews from their official source assets.

Requires Python 3, Pillow, NumPy, OpenCV, PyMuPDF and FFmpeg. Downloads and review contact
sheets are cached outside the repository by default.
"""
import argparse
from pathlib import Path
import subprocess
import sys
import tempfile

SCRIPTS = Path(__file__).resolve().parent
GROUPS = {
    "world": ["hy-nomas"],
    "faithful": ["faithfulfaces"],
    "static": ["resadapter", "ipa", "beyond-reward"],
    "identity_game": ["personavlog", "hunyuan-game"],
    "generation": ["reward-lightning", "v-pae", "hunyuanvideo"],
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paper", choices=["all"] + [p for papers in GROUPS.values() for p in papers], default="all")
    parser.add_argument("--source-dir", type=Path, default=Path(tempfile.gettempdir()) / "paper-motion-sources")
    parser.add_argument("--contact-dir", type=Path, default=Path(tempfile.gettempdir()) / "paper-motion-contacts")
    args = parser.parse_args()
    for group, papers in GROUPS.items():
        if args.paper != "all" and args.paper not in papers:
            continue
        command = [sys.executable, str(SCRIPTS / f"build_{group}_motion.py"),
                   "--source-dir", str(args.source_dir / group)]
        if group == "static":
            command += ["--scratch-dir", str(args.contact_dir / group)]
            if args.paper != "all":
                command += ["--paper", args.paper]
        elif group == "identity_game":
            command += ["--contact-dir", str(args.contact_dir / group)]
            if args.paper != "all":
                command += ["--only", args.paper]
        else:
            command += ["--contact-dir", str(args.contact_dir / group)]
            if group == "generation" and args.paper != "all":
                command += ["--only", args.paper]
        subprocess.run(command, check=True)


if __name__ == "__main__":
    main()
