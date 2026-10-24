"""Reveal a real FaithfulFaces / VACE comparison from Figure 13.

The divider reveals published static frames from the same reference identity,
prompt, and displayed frame column. A shared gentle camera push continues after
the reveal; it is editorial motion, not synthesized facial or body animation.
"""
import argparse
import hashlib
import json
from pathlib import Path
from tempfile import gettempdir
import urllib.request

from PIL import Image, ImageDraw

from motion_common import cover, ease, font, render


MANIFEST = Path(__file__).with_name("faithful_motion_sources.json")


def ensure_sources(source_dir, spec):
    """Fetch the recorded paper and extract its original embedded images."""
    source_dir.mkdir(parents=True, exist_ok=True)
    paper = source_dir / spec["paper"]["file"]
    if not paper.exists():
        temporary = paper.with_suffix(".download")
        request = urllib.request.Request(spec["paper"]["url"], headers={"User-Agent": "Mozilla/5.0"})
        try:
            with urllib.request.urlopen(request, timeout=90) as response:
                temporary.write_bytes(response.read())
            temporary.replace(paper)
        finally:
            temporary.unlink(missing_ok=True)
    if hashlib.sha256(paper.read_bytes()).hexdigest() != spec["paper"]["sha256"]:
        raise ValueError(f"Published paper changed: {paper}")
    import fitz
    with fitz.open(paper) as document:
        for asset in spec["assets"]:
            target = source_dir / asset["file"]
            if not target.exists():
                fitz.Pixmap(document, asset["pdf_xref"]).save(target)
            if hashlib.sha256(target.read_bytes()).hexdigest() != asset["sha256"]:
                raise ValueError(f"Extracted source mismatch: {target}")


def build(source_dir, spec):
    size = tuple(spec["size"])
    baseline = Image.open(source_dir / spec["baseline"]).convert("RGB")
    result = Image.open(source_dir / spec["result"]).convert("RGB")
    width, height = size

    def camera(image, t):
        # Constant logarithmic zoom speed keeps moving during the entire result
        # hold. Floating source bounds avoid integer crop/resize stepping.
        u = min(1, max(0, t / spec["duration_seconds"]))
        zoom = spec["camera_motion"]["end_scale"] ** u
        fit_scale = max(width / image.width, height / image.height)
        crop_width = width / fit_scale / zoom
        crop_height = height / fit_scale / zoom
        left = (image.width - crop_width) / 2
        top = (image.height - crop_height) / 2
        return image.resize(size, Image.Resampling.LANCZOS,
                            box=(left, top, left + crop_width, top + crop_height))

    def label(draw, words, xy, anchor="ls", alpha=255):
        draw.text(xy, words, font=font(29, "medium"), anchor=anchor,
                  fill=(255, 255, 255, alpha), stroke_width=1,
                  stroke_fill=(15, 27, 25, round(alpha * .6)))

    def frame(t):
        progress = ease((t - spec["sweep_start_seconds"]) /
                        (spec["sweep_end_seconds"] - spec["sweep_start_seconds"]))
        x = round(width * progress)
        image = camera(baseline, t)
        if x:
            result_frame = camera(result, t)
            image.paste(result_frame.crop((0, 0, x, height)), (0, 0))
        layer = Image.new("RGBA", size)
        draw = ImageDraw.Draw(layer)
        if 0 < x < width:
            draw.line((x, 0, x, height), fill=(15, 36, 30, 90), width=5)
            draw.line((x, 0, x, height), fill=(224, 252, 240, 245), width=2)
        # Transparent in-image method labels keep the comparison truthful;
        # there is no header, caption bar, score, or fabricated baseline.
        if x > 210:
            label(draw, "FaithfulFaces", (24, height - 23), alpha=round(255 * min(1, (x - 210) / 70)))
        if x < width - 110:
            label(draw, "VACE", (width - 24, height - 23), "rs",
                  round(255 * min(1, (width - 110 - x) / 70)))
        return Image.alpha_composite(image.convert("RGBA"), layer).convert("RGB")

    poster = cover(Image.open(source_dir / spec["poster_asset"]), size)
    return frame, poster


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, default=Path(gettempdir()) / "homepage-faithful-motion")
    parser.add_argument("--contact-dir", type=Path)
    parser.add_argument("--fetch-only", action="store_true")
    args = parser.parse_args()
    spec = json.loads(MANIFEST.read_text())
    ensure_sources(args.source_dir, spec)
    if args.fetch_only:
        return
    contact = args.contact_dir or args.source_dir
    frame, poster_image = build(args.source_dir, spec)
    _, poster = render("faithfulfaces", frame, spec["duration_seconds"],
                       poster_t=spec["duration_seconds"] - .2, crf=21,
                       size=tuple(spec["size"]),
                       contact_path=contact / "faithfulfaces-200px.jpg")
    poster_image.save(poster, quality=95, optimize=True)


if __name__ == "__main__":
    main()
