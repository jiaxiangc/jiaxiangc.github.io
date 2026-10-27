"""Build the Reward Lightning cherry-street comparison from official footage.

The SVG composes authentic frame pixels with small native comparison labels.
FFmpeg preserves both original videos at 1x and reveals the matched result.
No source retouching, grading, synthetic degradation, interpolation or holds.
"""
from pathlib import Path
from urllib.request import urlopen
import argparse
import base64
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
FONT = "/System/Library/Fonts/Supplemental/Arial.ttf"
SOURCES = {
    "baseline": {
        "url": "https://reward-lightning.github.io/assets/videos/s2-vs-baseline/row4-baseline-4nfes.mp4",
        "sha256": "8dd10b3ab98be03227da4dc3c3ea16649cd7705666dcf8143edd2d5624d43a96",
    },
    "our": {
        "url": "https://reward-lightning.github.io/assets/videos/s2-vs-baseline/row4-our-4nfes.mp4",
        "sha256": "12fed40b05d399610346b01e3ad39b8728a557c27cece1180a085ec891560869",
    },
}


def ffmpeg(*args):
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *map(str, args)], check=True)


def build(source):
    source.mkdir(parents=True, exist_ok=True)
    for name, spec in SOURCES.items():
        path = source / f"row4-{name}.mp4"
        if not path.exists():
            path.write_bytes(urlopen(spec["url"], timeout=90).read())
        if hashlib.sha256(path.read_bytes()).hexdigest() != spec["sha256"]:
            raise ValueError(f"Official source has changed: {path}")
        ffmpeg("-ss", 2, "-i", path, "-frames:v", 1, "-vf", "scale=768:432", "-q:v", 2,
               source / f"row4-{name}-2s.jpg")
    images = {name: base64.b64encode((source / f"row4-{name}-2s.jpg").read_bytes()).decode()
              for name in SOURCES}
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="400" height="225" viewBox="0 0 400 225" role="img" aria-labelledby="title desc">
  <title id="title">Reward Lightning: preference distillation at 4 NFE</title>
  <desc id="desc">Matched official cherry-blossom street results at the same four function evaluations: Wan 2.2 on the left and the preference-distilled Reward Lightning result on the right. Source time is 2 seconds for both. The source baseline is naturally softer; no degradation was added.</desc>
  <defs><clipPath id="baseline"><rect width="136" height="225"/></clipPath></defs>
  <image width="400" height="225" href="data:image/jpeg;base64,{images['our']}"/>
  <image width="400" height="225" clip-path="url(#baseline)" href="data:image/jpeg;base64,{images['baseline']}"/>
  <path d="M136 0v225" fill="none" stroke="white" stroke-width="1.5"/>
  <circle cx="136" cy="112.5" r="9" fill="#172320" fill-opacity=".45" stroke="white" stroke-width="1.2"/>
  <path d="m132 109-3 3.5 3 3.5m8-7 3 3.5-3 3.5" fill="none" stroke="white" stroke-width="1.4"/>
  <text x="346" y="36" text-anchor="middle" font-family="Arial,Helvetica,sans-serif" font-size="24" font-weight="600" fill="#26332d" stroke="white" stroke-width="2.2" stroke-opacity=".88" paint-order="stroke" stroke-linejoin="round">4 NFE</text>
  <g font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="600" fill="#19231e" stroke="white" stroke-width="2.2" stroke-opacity=".88" paint-order="stroke" stroke-linejoin="round">
    <text x="12" y="212">Wan 2.2</text>
    <text x="388" y="212" text-anchor="end">Preference distilled</text>
  </g>
</svg>'''
    image_dir = ROOT / "images/paper-previews"
    (image_dir / "reward-lightning-cover.svg").write_text(svg)
    # Pure official result remains available as the video poster fallback.
    (image_dir / "reward-lightning-poster.jpg").write_bytes((source / "row4-our-2s.jpg").read_bytes())
    seam = ".34*W*(1-min(T/2.6,1))"
    mix = f"if(lt(T,2.6)*lt(abs(X-({seam})),1),255,if(lt(X,{seam}),A,B))"
    filters = (
        "[0:v]trim=duration=5,setpts=PTS-STARTPTS,scale=768:432,fps=24,format=gbrp[a];"
        "[1:v]trim=duration=5,setpts=PTS-STARTPTS,scale=768:432,fps=24,format=gbrp[b];"
        f"[a][b]blend=all_expr='{mix}',format=yuv420p,"
        f"drawtext=fontfile='{FONT}':text='4 NFE':fontcolor=0x26332d:bordercolor=white@0.88:borderw=3:fontsize=46:x=664-tw/2:y=30,"
        f"drawtext=fontfile='{FONT}':text='Wan 2.2':fontcolor=0x19231e:bordercolor=white@0.88:borderw=3:fontsize=34:x=23:y=h-45:alpha='if(lt(t,0.75),1,max(0,1-(t-0.75)/0.35))',"
        f"drawtext=fontfile='{FONT}':text='Preference distilled':fontcolor=0x19231e:bordercolor=white@0.88:borderw=3:fontsize=34:x=w-tw-23:y=h-45[out]"
    )
    ffmpeg("-i", source / "row4-baseline.mp4", "-i", source / "row4-our.mp4", "-filter_complex", filters,
           "-map", "[out]", "-an", "-t", 5, "-c:v", "libx264", "-preset", "slow", "-crf", 22,
           "-pix_fmt", "yuv420p", "-movflags", "+faststart", ROOT / "videos/reward-lightning-preview.mp4")
    audit = {
        "project": "https://reward-lightning.github.io/#sec-baseline",
        "section": "Comparison with Baseline / Visualization Comparison with Wan2.2-I2V",
        "row": 4,
        "columns": ["Wan2.2-4NFEs", "Ours-4NFEs"],
        "prompt": "Forward street movement during 'Sakura Fubuki'; petals swirl toward camera in hazy morning sunlight.",
        "sources": SOURCES,
        "poster": {"source_time": 2.0, "size": [400, 225], "baseline_region": [0, 0, 136, 225]},
        "video": {"duration": 5.0, "size": [768, 432], "fps": 24, "source_times": [0, 5], "speed": 1,
                  "reveal": "Baseline starts at left 34% and shrinks to zero by 2.6 seconds; both originals advance together throughout."},
        "labels": "4 NFE is shared by both methods. Preference distilled identifies the actual method result; it is not a score or an invented preference label.",
        "pixel_policy": "Official outputs only. Scale and frame sampling; no retouching, color grading, blur, interpolated motion, holds or repeated scene loops."
    }
    (source / "source-audit.json").write_text(json.dumps(audit, indent=2))
    print(json.dumps(audit, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, required=True)
    build(parser.parse_args().source_dir)
