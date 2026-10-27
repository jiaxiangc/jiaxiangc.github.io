"""Build the one-step V-PAE cover from verified official result footage.

The left-hand noise tile and arrow are a schematic of single-step sampling,
not recorded experimental tensors. The forest is an unaltered official result
frame. This builder also restores the continuous original-speed hover clip.
"""
import argparse
import base64
import hashlib
from pathlib import Path
import subprocess
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
URL = "https://v-pae.github.io/assets/videos_pose_compressed/main/scene/%E7%8E%B0%E5%AE%9E%E4%B8%BB%E4%B9%89%E9%A3%8E%E6%A0%BC_1280x720_8.mp4"
SHA256 = "155c402888302a68bbb6997afaad31c162f930a35d2911a82376ed2b6e8b6905"


def ffmpeg(*args):
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                    *map(str, args)], check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, required=True)
    args = parser.parse_args()
    args.source_dir.mkdir(parents=True, exist_ok=True)
    source = args.source_dir / "vp-snow.mp4"
    if not source.exists():
        source.write_bytes(urlopen(URL, timeout=90).read())
    if hashlib.sha256(source.read_bytes()).hexdigest() != SHA256:
        parser.error("The official vp-snow.mp4 does not match the recorded SHA-256.")

    frame = args.source_dir / "forest-result-1.0s.jpg"
    ffmpeg("-ss", 1.0, "-i", source, "-frames:v", 1, "-q:v", 2, frame)
    photo = base64.b64encode(frame.read_bytes()).decode()
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="768" height="432" viewBox="0 0 768 432" role="img" aria-labelledby="title desc">
  <title id="title">V-PAE: one-step video generation</title>
  <desc id="desc">A schematic noise tile passes through one sampling step into an authentic snow-forest result from the official V-PAE 1-NFE gallery. The noise is illustrative; the forest is the original video frame at one second.</desc>
  <defs>
    <filter id="noise" x="0" y="0" width="100%" height="100%">
      <feTurbulence type="fractalNoise" baseFrequency="0.6" numOctaves="1" seed="13"/>
      <feColorMatrix type="saturate" values="0"/>
      <feComponentTransfer>
        <feFuncR type="linear" slope="3" intercept="-1"/>
        <feFuncG type="linear" slope="3" intercept="-1"/>
        <feFuncB type="linear" slope="3" intercept="-1"/>
      </feComponentTransfer>
    </filter>
  </defs>
  <rect width="768" height="432" fill="#f7f7f4"/>
  <image href="data:image/jpeg;base64,{photo}" x="216" y="0" width="552" height="432" preserveAspectRatio="xMidYMid slice"/>
  <g fill="#172e3d" font-family="Arial,Helvetica,sans-serif" text-anchor="middle">
    <text x="108" y="148" font-size="150" font-weight="700">1</text>
    <text x="108" y="193" font-size="43" font-weight="700" letter-spacing="2">STEP</text>
  </g>
  <rect x="26" y="239" width="136" height="112" fill="#999" filter="url(#noise)"/>
  <path d="M150 295H251M229 274L251 295L229 316" fill="none" stroke="#f7f7f4" stroke-width="15" stroke-linecap="square" stroke-linejoin="miter"/>
  <path d="M150 295H251M229 274L251 295L229 316" fill="none" stroke="#172e3d" stroke-width="7" stroke-linecap="square" stroke-linejoin="miter"/>
  <text x="94" y="388" fill="#52616a" font-family="Arial,Helvetica,sans-serif" font-size="30" text-anchor="middle">Noise</text>
</svg>'''
    out = ROOT / "images/paper-previews/v-pae-onestep-cover.svg"
    out.write_text(svg)
    ffmpeg("-i", source, "-t", 5, "-vf", "scale=768:432,fps=24", "-an",
           "-c:v", "libx264", "-preset", "slow", "-crf", 23,
           "-pix_fmt", "yuv420p", "-movflags", "+faststart",
           ROOT / "videos/v-pae-preview.mp4")
    print("Wrote the 768×432 one-step SVG cover and 5-second official forest preview.")


if __name__ == "__main__":
    main()
