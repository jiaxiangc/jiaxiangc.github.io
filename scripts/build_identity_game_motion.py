"""Build short cinematic covers from inspected official footage.

No title bars, cards, borders, reference insets or progress indicators are rendered.
Original model output is edited with clean cuts and documented subject crops.
See identity_game_motion_sources.json for URLs and the selection rationale.
"""
import argparse
import hashlib
import json
from pathlib import Path
from tempfile import gettempdir
import urllib.request

from PIL import Image, ImageDraw

from motion_common import Clip, cover, ease, font, render


DEFAULT_SOURCE_DIR = Path(gettempdir()) / "homepage-identity-game-motion"


def ensure_sources(source_dir, only=None):
    """Fetch missing official assets, so an empty --source-dir is reproducible."""
    manifest_path = Path(__file__).with_name("identity_game_motion_sources.json")
    manifest = json.loads(manifest_path.read_text())
    source_dir.mkdir(parents=True, exist_ok=True)
    selected = []
    for preview in manifest["previews"]:
        slug = Path(preview["output"]).name.removesuffix("-preview.mp4")
        if only and slug != only:
            continue
        for item in [preview] + preview.get("chapters", []):
            for url_key, path_key in [
                ("video_url", "local_video"),
                ("reference_url", "local_reference"),
                ("input_url", "local_input"),
            ]:
                if url_key in item:
                    selected.append((item[path_key], item[url_key]))
    for name, url in dict(selected).items():
        path = source_dir / name
        if not path.exists():
            temporary = source_dir / (name + ".download")
            print(f"Downloading {name}", flush=True)
            request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            try:
                with urllib.request.urlopen(request, timeout=90) as response, temporary.open("wb") as target:
                    while True:
                        chunk = response.read(1024 * 1024)
                        if not chunk:
                            break
                        target.write(chunk)
                temporary.replace(path)
            finally:
                if temporary.exists():
                    temporary.unlink()
        expected = manifest.get("source_sha256", {}).get(name)
        if expected and hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError(f"Official source changed or is incomplete: {path}")


def build_cover(source, slug):
    """Full-frame original footage, subject-aware crops, clean editorial cuts."""
    manifest = json.loads(Path(__file__).with_name("identity_game_motion_sources.json").read_text())
    spec = next(p for p in manifest["previews"] if p["slug"] == slug)
    # Some covers deliberately keep one uninterrupted interval from the official
    # edit. Chapters then change only the crop at a native scene boundary.
    if "continuous_source_interval" in spec:
        start, end = spec["continuous_source_interval"]
        cursor = start
        source_name = spec["chapters"][0]["local_video"]
        for shot in spec["chapters"]:
            if shot["local_video"] != source_name or abs(shot["source_start_seconds"] - cursor) > .0001:
                raise ValueError(f"{slug}: source interval must stay continuous at native speed")
            cursor += shot["duration_seconds"]
        if abs(cursor - end) > .0001:
            raise ValueError(f"{slug}: chapters do not match the documented source interval")
    names = dict.fromkeys(item["local_video"] for item in spec["chapters"])
    clips = {name: Clip(source / name) for name in names}
    boundaries = []
    elapsed = 0.0
    for shot in spec["chapters"]:
        boundaries.append(elapsed)
        elapsed += shot["duration_seconds"]

    size = tuple(spec.get("size", [720, 432]))

    def clean_frame(t):
        index = max(i for i, boundary in enumerate(boundaries) if t >= boundary)
        shot = spec["chapters"][index]
        sample = clips[shot["local_video"]].frame(shot["source_start_seconds"] + t - boundaries[index])
        if "source_crop_xyxy" in shot:
            sample = sample.crop(tuple(shot["source_crop_xyxy"]))
        return cover(sample, size, focus=tuple(shot.get("focus", [0.5, 0.5])))

    def frame(t):
        image = clean_frame(t)
        cue = spec.get("cue")
        if not cue or not cue["start_seconds"] < t < cue["end_seconds"]:
            return image
        alpha = ease((t - cue["start_seconds"]) / .22) * ease((cue["end_seconds"] - t) / .28)
        overlay = Image.new("RGBA", size)
        draw = ImageDraw.Draw(overlay)
        x, y = 24, size[1] - 54
        # A brief annotation stays inside the original footage: no title strip,
        # text card or fabricated model output. The poster uses clean_frame.
        draw.line((x, y - 12, x + 28, y - 12), fill=(139, 224, 235, round(alpha * 230)), width=2)
        draw.text((x, y), cue["text"], font=font(30, "medium"),
                  fill=(255, 255, 255, round(alpha * 245)),
                  stroke_width=1, stroke_fill=(12, 23, 35, round(alpha * 100)))
        return Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")

    return frame, clean_frame, elapsed, spec["poster_output_seconds"], list(clips.values()), size


SLUGS = ("personavlog", "hunyuan-game")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, default=DEFAULT_SOURCE_DIR)
    parser.add_argument("--contact-dir", type=Path,
                        help="Contact sheet directory (default: SOURCE_DIR/cinematic)")
    parser.add_argument("--only", choices=SLUGS)
    parser.add_argument("--fetch-only", action="store_true", help="Download and verify sources without rendering")
    args = parser.parse_args()
    ensure_sources(args.source_dir, args.only)
    if args.fetch_only:
        return
    contact_dir = args.contact_dir or args.source_dir / "cinematic"
    for slug in SLUGS:
        if args.only and args.only != slug:
            continue
        fn, clean_fn, duration, poster_t, clips, size = build_cover(args.source_dir, slug)
        try:
            _, poster = render(slug, fn, duration, poster_t=poster_t, crf=23,
                   contact_path=contact_dir / f"{slug}-200px.jpg", size=size)
            clean_fn(poster_t).save(poster, quality=94, optimize=True)
        finally:
            for clip in clips:
                clip.close()


if __name__ == "__main__":
    main()
