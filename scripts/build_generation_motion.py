"""Build three full-bleed motion covers from official video results.

Usage:
    python3 scripts/build_generation_motion.py --source-dir /outside/repo/generation

Sources and edit decisions are documented in generation_motion_sources.json.
Source downloads and contact sheets stay outside the repository; only the final
MP4 previews and JPEG posters are written to the site's assets directories.
"""
import argparse
import hashlib
import json
from pathlib import Path
import tempfile
from urllib.request import urlopen

from PIL import Image, ImageDraw, ImageFilter

from motion_common import Clip, W, H, cover, crossfade, ease, font, render


MANIFEST = Path(__file__).with_name("generation_motion_sources.json")


def capability_cue(image, t, cue):
    """A brief, transparent in-scene method cue; never a title or caption bar."""
    start, end = cue["output"]
    alpha = ease((t - start) / .25) * ease((end - t) / .25)
    if alpha <= 0:
        return image
    _, height = image.size
    ink = Image.new("RGBA", image.size)
    draw = ImageDraw.Draw(ink)
    y = height - 44
    color = tuple(cue["accent"])
    # One open node and an outgoing trace represent the compact generation path.
    draw.ellipse((28, y - 7, 42, y + 7), outline=(*color, 255), width=2)
    draw.line((43, y, 62, y), fill=(*color, 255), width=2)
    draw.ellipse((59, y - 3, 65, y + 3), fill=(*color, 255))
    draw.text((80, y + 1), cue["text"], font=font(37, "medium"),
              fill=(*cue.get("foreground", [255, 255, 255]), 255), anchor="lm")
    # Shadow follows only the glyphs, keeping the source image unobscured.
    shadow = Image.new("RGBA", image.size, (0, 0, 0, 0))
    shadow.putalpha(ink.getchannel("A").filter(ImageFilter.GaussianBlur(3)))
    shadow.putalpha(shadow.getchannel("A").point(lambda value: round(value * .75 * alpha)))
    ink.putalpha(ink.getchannel("A").point(lambda value: round(value * alpha)))
    return Image.alpha_composite(Image.alpha_composite(image.convert("RGBA"), shadow), ink).convert("RGB")


def download(asset, directory):
    path = directory / asset["file"]
    if not path.exists():
        temporary = path.with_suffix(".download")
        with urlopen(asset["url"], timeout=90) as response, temporary.open("wb") as target:
            while chunk := response.read(1024 * 1024):
                target.write(chunk)
        temporary.replace(path)
    if asset.get("sha256") and hashlib.sha256(path.read_bytes()).hexdigest() != asset["sha256"]:
        raise ValueError(f"Source checksum mismatch: {path}")
    return path


def moving_reveal_frames(preview, clips):
    """Compare two real official videos on a shared, continuously advancing clock."""
    size = tuple(preview["dimensions"])
    width, height = size
    reveal = preview["moving_reveal"]
    start = reveal.get("source_start", 0)
    before_clip, after_clip = clips[reveal["before"]], clips[reveal["after"]]
    for clip in (before_clip, after_clip):
        if start + preview["duration"] > clip.duration + .0001:
            raise ValueError("A moving reveal cannot extend past its real source footage")

    def source_frame(clip, t):
        return cover(clip.frame(start + t), size)

    def method_label(layer, words, xy, alpha, anchor="ls"):
        if alpha <= 0:
            return
        shadow = Image.new("RGBA", size)
        ImageDraw.Draw(shadow).text((xy[0], xy[1] + 1), words, font=font(33, "medium"),
                                   anchor=anchor, fill=(5, 17, 25, round(220 * alpha)),
                                   stroke_width=2, stroke_fill=(5, 17, 25, round(160 * alpha)))
        layer.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(2)))
        ImageDraw.Draw(layer).text(xy, words, font=font(33, "medium"), anchor=anchor,
                                  fill=(249, 253, 255, round(255 * alpha)))

    def frame(t):
        # Both inputs advance at 1x, including while hidden. The wipe never
        # freezes either video and never restarts the revealed result.
        before, after = source_frame(before_clip, t), source_frame(after_clip, t)
        amount = min(1, max(0, (t - reveal["start"]) / (reveal["end"] - reveal["start"])))
        x = round(width * amount)
        image = before
        if x:
            image.paste(after.crop((0, 0, x, height)), (0, 0))
        overlay = Image.new("RGBA", size)
        draw = ImageDraw.Draw(overlay)
        if 0 < x < width:
            draw.line((x, 0, x, height), fill=(15, 36, 39, 100), width=5)
            draw.line((x, 0, x, height), fill=(233, 251, 253, 245), width=2)
        fade_out = ease((reveal.get("label_end", 3.35) - t) / .4)
        for name, space, xy, anchor in (
            (reveal["after_label"], x, (24, height - 22), "ls"),
            (reveal["before_label"], width - x, (width - 24, height - 22), "rs"),
        ):
            label_width = draw.textlength(name, font=font(33, "medium"))
            alpha = ease((space - label_width - 35) / 65) * fade_out
            method_label(overlay, name, xy, alpha, anchor)
        return Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")

    def clean_poster(t):
        return source_frame(after_clip, t)

    return frame, clean_poster


def build(preview, directory, contact_directory, crf):
    clips = {asset["id"]: Clip(download(asset, directory)) for asset in preview["assets"]}
    size = tuple(preview.get("dimensions", (W, H)))

    def shot_frame(shot, t):
        source_time = shot["source"][0] + t - shot["output"][0]
        return cover(clips[shot["asset"]].frame(source_time), size,
                     focus=shot["focus"])

    def footage(t):
        active = [s for s in preview["shots"] if s["output"][0] <= t < s["output"][1]]
        if not active:
            raise ValueError(f"No shot at {t} seconds")
        if len(active) == 1:
            return shot_frame(active[0], t)
        previous, current = active
        overlap = previous["output"][1] - current["output"][0]
        amount = (t - current["output"][0]) / overlap
        return crossfade(shot_frame(previous, t), shot_frame(current, t), amount)

    def frame(t):
        image = footage(t)
        for cue in preview.get("cues", []):
            image = capability_cue(image, t, cue)
        return image

    try:
        frame_fn, poster_fn = (moving_reveal_frames(preview, clips)
                              if preview.get("mode") == "moving_reveal"
                              else (frame, footage))
        _, poster = render(preview["slug"], frame_fn, preview["duration"],
               poster_t=preview["poster_time"], crf=crf,
               contact_path=contact_directory / (preview["slug"] + "-final-200px.jpg"),
               size=size)
        # Website cover typography is a separate HTML layer, so this stays clean.
        poster_fn(preview["poster_time"]).save(poster, quality=94, optimize=True)
    finally:
        for clip in clips.values():
            clip.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path,
                        default=Path(tempfile.gettempdir()) / "paper-motion-generation",
                        help="External directory for original videos and contact sheets")
    parser.add_argument("--contact-dir", type=Path,
                        help="Optional separate directory for 200px contact sheets")
    parser.add_argument("--only", choices=["reward-lightning", "v-pae", "hunyuanvideo"])
    args = parser.parse_args()
    args.source_dir.mkdir(parents=True, exist_ok=True)
    contact_directory = args.contact_dir or args.source_dir
    contact_directory.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(MANIFEST.read_text())
    for preview in manifest["previews"]:
        if not args.only or args.only == preview["slug"]:
            build(preview, args.source_dir, contact_directory, manifest["format"]["crf"])


if __name__ == "__main__":
    main()
