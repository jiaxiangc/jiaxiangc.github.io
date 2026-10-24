"""Video sampling and encoding for full-bleed paper covers.

Requires Pillow, NumPy, OpenCV and FFmpeg. All composites use published assets;
animation is editorial motion, never synthesized model output.
"""
from functools import lru_cache
from pathlib import Path
import subprocess

import cv2
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
W, H, FPS = 720, 432, 24
INK = "#17242d"
FONT = "/System/Library/Fonts/Avenir Next.ttc"


@lru_cache(maxsize=128)
def font(size, weight="regular"):
    index = {"regular": 7, "medium": 5, "demi": 2, "bold": 0}.get(weight, 7)
    try:
        return ImageFont.truetype(FONT, int(size), index=index)
    except OSError:
        return ImageFont.truetype("DejaVuSans-Bold.ttf" if weight == "bold" else "DejaVuSans.ttf", int(size))


def text(im, value, xy, size=28, color=INK, weight="regular", anchor="lt", max_width=None, stroke=0):
    draw = ImageDraw.Draw(im)
    size = int(size)
    while max_width and draw.textlength(value, font=font(size, weight)) > max_width and size > 18:
        size -= 1
    draw.text(xy, value, font=font(size, weight), fill=color, anchor=anchor,
              stroke_width=stroke, stroke_fill=color)
    return im


def ease(x):
    x = min(1, max(0, x))
    return x * x * (3 - 2 * x)


def lerp(a, b, x):
    return a + (b - a) * x


def cover(image, size, focus=(0.5, 0.5), zoom=1):
    image = image.convert("RGB")
    w, h = map(int, size)
    scale = max(w / image.width, h / image.height) * max(1, zoom)
    nw, nh = max(w, round(image.width * scale)), max(h, round(image.height * scale))
    resized = image.resize((nw, nh), Image.Resampling.LANCZOS)
    left = round((nw - w) * min(1, max(0, focus[0])))
    top = round((nh - h) * min(1, max(0, focus[1])))
    return resized.crop((left, top, left + w, top + h))


def crossfade(a, b, amount):
    return Image.blend(a.convert("RGB"), b.convert("RGB"), min(1, max(0, amount)))


class Clip:
    """Sample a real clip at its original source time; no motion interpolation."""
    def __init__(self, path):
        self.path = Path(path)
        self.cap = cv2.VideoCapture(str(self.path))
        if not self.cap.isOpened():
            raise OSError(f"Cannot open video {path}")
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.duration = self.count / self.fps
        self.previous_index = -1
        self.previous_frame = None

    def frame(self, seconds):
        index = min(self.count - 1, max(0, int(seconds * self.fps)))
        if index == self.previous_index and self.previous_frame is not None:
            return self.previous_frame.copy()
        if index != self.previous_index + 1:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, index)
        ok, raw = self.cap.read()
        if not ok:
            raise OSError(f"Cannot decode frame {index} of {self.path}")
        image = Image.fromarray(cv2.cvtColor(raw, cv2.COLOR_BGR2RGB))
        self.previous_index, self.previous_frame = index, image
        return image.copy()

    def close(self):
        self.cap.release()


def render(slug, frame_fn, duration, poster_t=1.5, crf=23, contact_path=None, size=(W, H)):
    """Encode an editorial preview at its chosen landscape or portrait size."""
    width, height = size
    target = ROOT / "videos" / f"{slug}-preview.mp4"
    temporary = target.with_name(f".{target.stem}.render.mp4")
    poster = ROOT / "images/paper-previews" / f"{slug}-poster.jpg"
    target.parent.mkdir(parents=True, exist_ok=True)
    poster.parent.mkdir(parents=True, exist_ok=True)
    command = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo",
               "-pix_fmt", "rgb24", "-s", f"{width}x{height}", "-r", str(FPS), "-i", "-", "-an",
               "-c:v", "libx264", "-preset", "slow", "-crf", str(crf), "-threads", "2",
               "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(temporary)]
    process = subprocess.Popen(command, stdin=subprocess.PIPE)
    try:
        for n in range(round(duration * FPS)):
            frame = frame_fn(n / FPS).convert("RGB")
            if frame.size != size:
                raise ValueError(f"Incorrect frame size: {frame.size}")
            process.stdin.write(frame.tobytes())
        process.stdin.close()
        if process.wait():
            raise RuntimeError(f"FFmpeg failed for {slug}")
        temporary.replace(target)
    except BaseException:
        process.kill()
        process.wait()
        temporary.unlink(missing_ok=True)
        raise
    frame_fn(poster_t).convert("RGB").save(poster, quality=94, optimize=True)
    if contact_path:
        contact_path = Path(contact_path)
        contact_path.parent.mkdir(parents=True, exist_ok=True)
        cell_height = round(200 * height / width)
        sheet = Image.new("RGB", (800, (cell_height + 28) * 2), "white")
        for i in range(8):
            frame = frame_fn((i + 0.4) / 8 * duration).convert("RGB")
            # First row is actual homepage display size, second row too.
            frame.thumbnail((200, cell_height), Image.Resampling.LANCZOS)
            sheet.paste(frame, ((i % 4) * 200, (i // 4) * (cell_height + 28)))
            text(sheet, f"{(i + 0.4) / 8 * duration:.1f}s", ((i % 4) * 200 + 8, (i // 4) * (cell_height + 28) + cell_height + 4), size=18)
        sheet.save(contact_path, quality=94)
    print(f"{slug}: {duration:.2f}s, {target.stat().st_size / 1024:.0f} KiB", flush=True)
    return target, poster
