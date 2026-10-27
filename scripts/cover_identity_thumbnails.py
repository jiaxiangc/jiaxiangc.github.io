"""Lay out unchanged official images as compact research thumbnails.

Only SVG image placement, cropping and small semantic labels are authored here.
No research image pixels, results, faces or motion are synthesized or retouched.
Source provenance is in cover_identity_sources.json.
"""
from pathlib import Path
import argparse
import base64
import hashlib
import json
import mimetypes
import subprocess

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "images/paper-previews"
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--source-dir", type=Path, required=True,
                    help="Directory with the official images and faithfulfaces-fig1_fig12.mp4 recorded in cover_identity_sources.json")
SOURCE = parser.parse_args().source_dir
SOURCE_VIDEO = SOURCE / "faithfulfaces-fig1_fig12.mp4"
if not SOURCE_VIDEO.is_file():
    parser.error(f"Missing official boxing source: {SOURCE_VIDEO}")
manifest = json.loads(Path(__file__).with_name("cover_identity_sources.json").read_text())
expected_hash = manifest["covers"]["faithfulfaces"]["source_video_sha256"]
if hashlib.sha256(SOURCE_VIDEO.read_bytes()).hexdigest() != expected_hash:
    parser.error(f"Official boxing source does not match its recorded SHA-256: {SOURCE_VIDEO}")


def image(name, x, y, width, height, *, fit="xMidYMid slice", viewbox=None):
    path = SOURCE / name
    data = base64.b64encode(path.read_bytes()).decode()
    href = f"data:{mimetypes.guess_type(name)[0]};base64,{data}"
    if viewbox:
        bx, by, bw, bh, iw, ih = viewbox
        return (f'<svg x="{x}" y="{y}" width="{width}" height="{height}" '
                f'viewBox="{bx} {by} {bw} {bh}" preserveAspectRatio="{fit}">'
                f'<image href="{href}" width="{iw}" height="{ih}"/></svg>')
    return (f'<image href="{href}" x="{x}" y="{y}" width="{width}" '
            f'height="{height}" preserveAspectRatio="{fit}"/>')


def label(text, x, y, anchor="middle", size=28):
    return (f'<text x="{x}" y="{y}" fill="#30343b" font-family="Arial, sans-serif" '
            f'font-size="{size}" text-anchor="{anchor}">{text}</text>')


def write(slug, content):
    (DEST / f"{slug}-research-cover.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="720" height="432" '
        'viewBox="0 0 720 432"><rect width="720" height="432" fill="white"/>'
        + content + '</svg>\n')


write("faithfulfaces",
      image("faithfulfaces-reference.png", 0, 70, 224, 224, fit="xMidYMid meet")
      + label("Reference", 112, 337)
      + '<path d="M87 368H135M123 357L135 368L123 379" fill="none" stroke="#6f747c" stroke-width="3"/>'
      + image("faithfulfaces-guard.jpg", 232, 0, 488, 214)
      + image("faithfulfaces-turn.jpg", 232, 218, 488, 214))

write("ipa",
      label("VACE", 178, 33, size=30)
      + label("IPA", 542, 33, size=30)
      + image("ipa-xref893.png", 0, 46, 356, 386, viewbox=(0, 38, 240, 260, 240, 416))
      + image("ipa-xref873.png", 364, 46, 356, 386, viewbox=(0, 38, 240, 260, 240, 416)))

write("personavlog",
      label("Reference", 87, 32, size=26)
      + label("Generated story", 451, 32, size=28)
      + image("personavlog-reference.jpg", 0, 46, 174, 386)
      + image("personavlog-garden.jpg", 182, 46, 174, 386)
      + image("personavlog-sketch.jpg", 364, 46, 174, 386)
      + image("personavlog-walk.jpg", 546, 46, 174, 386))

subprocess.run([
    "ffmpeg", "-loglevel", "error", "-y", "-i", str(SOURCE_VIDEO),
    "-t", "5.0625", "-vf",
    "scale=720:432:force_original_aspect_ratio=increase,crop=720:432,setsar=1,fps=24",
    "-an", "-c:v", "libx264", "-preset", "slow", "-crf", "21",
    "-pix_fmt", "yuv420p", "-movflags", "+faststart",
    str(ROOT / "videos/faithfulfaces-preview.mp4"),
], check=True)

print("Wrote three 720×432 SVG covers and the continuous official FaithfulFaces boxing preview.")
