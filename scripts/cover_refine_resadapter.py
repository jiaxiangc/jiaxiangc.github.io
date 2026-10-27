"""Build a photographic ResAdapter comparison from official native JPEGs.

SVG viewports crop original images without retouching or synthesized outputs.
PyMuPDF renders the code-native SVG, and ffmpeg encodes its comparison wipe.
Raw originals stay in --source-dir; public assets contain only final results.
"""
import argparse
import base64
import hashlib
import json
import math
from pathlib import Path
import subprocess
import urllib.request

import fitz

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://raw.githubusercontent.com/bytedance/res-adapter/main/assets/misc/controlnet/'
FILES = ['bird_1_Baseline.jpg', 'bird_1_ResAdapter.jpg']
WIDTH, HEIGHT, FPS, DURATION = 720, 432, 24, 7


def compose(sources, amount=1, comparison=False):
    encoded = ['data:image/jpeg;base64,' + base64.b64encode(p.read_bytes()).decode() for p in sources]
    # Same spatial crop for both native 840×1264 results. The top 190px and
    # bottom 66px are outside the viewport; both birds and the baseline's
    # duplicated bird remain visible. The output pixels are never changed.
    scale = 360 / 840
    y = -190 * scale
    def image(which, x):
        return f'<image width="840" height="1264" transform="translate({x} {y}) scale({scale})" href="{encoded[which]}"/>'
    def label(x, y, words, anchor='start', size=30):
        attrs = f'x="{x}" y="{y}" text-anchor="{anchor}" font-family="Helvetica" font-size="{size}"'
        # Explicit shadow and face layers render consistently in SVG engines
        # that do not implement the CSS paint-order property.
        return (f'<text {attrs} fill="#17232a" stroke="#17232a" stroke-width="4" stroke-linejoin="round" opacity=".65">{words}</text>'
                f'<text {attrs} fill="#ffffff">{words}</text>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="720" height="432" viewBox="0 0 720 432">
<defs>
  <clipPath id="left"><rect width="360" height="432"/></clipPath>
  <clipPath id="right"><rect x="360" width="360" height="432"/></clipPath>
  <clipPath id="reveal"><rect x="360" width="{360*amount}" height="432"/></clipPath>
</defs>
<g clip-path="url(#left)">{image(0,0)}</g>
<g clip-path="url(#right)">{image(0,360)}<g clip-path="url(#reveal)">{image(1,360)}</g></g>
<path d="M360 0v432" stroke="#fff" stroke-width="3"/>
{label(22,42,'840 × 1264')}
{label(22,405,'Baseline')}
{label(698,405,'Baseline / ResAdapter' if comparison else 'ResAdapter','end',26 if comparison else 30)}
</svg>'''


def raster(svg, width=WIDTH):
    with fitz.open(stream=svg.encode(), filetype='svg') as doc:
        return doc[0].get_pixmap(matrix=fitz.Matrix(width / WIDTH, width / WIDTH), alpha=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir', type=Path, required=True)
    parser.add_argument('--scratch-dir', type=Path, required=True)
    parser.add_argument('--poster-only', action='store_true')
    args = parser.parse_args()
    args.source_dir.mkdir(parents=True, exist_ok=True)
    args.scratch_dir.mkdir(parents=True, exist_ok=True)
    sources = []
    for name in FILES:
        path = args.source_dir/name
        if not path.exists():
            urllib.request.urlretrieve(BASE+name,path)
        sources.append(path)
    out = ROOT/'images/paper-previews'
    poster = compose(sources)
    (out/'resadapter-cover.svg').write_text(poster)
    raster(poster).save(out/'resadapter-poster.jpg', jpg_quality=94)
    raster(poster, 200).save(args.scratch_dir/'resadapter-proof-200.png')
    raster(poster).save(args.scratch_dir/'resadapter-proof-720.png')

    manifest = {
        'paper': 'ResAdapter: Domain Consistent Resolution Adapter for Diffusion Models',
        'project': 'https://res-adapter.github.io/',
        'source_page': 'https://github.com/bytedance/res-adapter#resadapter-with-controlnet-for-image-to-image',
        'source_description': 'Official README labels the ControlNet comparison 840×1264, top row with ResAdapter, bottom row without. These are native paired sample 1 files.',
        'sources': [{'file':p.name,'url':BASE+p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'size':[840,1264]} for p in sources],
        'crop_xywh': [0,190,840,1008],
        'layout': 'Baseline left; ResAdapter right. Both equal 360×432 viewports; 3px white divider; glyph-only in-image resolution and method labels with thin outline. No cards, chips, or title bars.',
        'poster': 'images/paper-previews/resadapter-cover.svg',
        'poster_fallback': 'images/paper-previews/resadapter-poster.jpg',
        'video': 'videos/resadapter-preview.mp4',
        'video_format': {'size':[720,432],'fps':24,'duration_seconds':7,'audio':False},
        'video_description': 'The left baseline stays fixed. A 7-second editorial comparison wipe reveals the authentic ResAdapter still over its baseline on the right. No subject motion, pose synthesis, or intentionally degraded baseline.',
        'reviewed_alternatives': ['All project gallery images, official repository README native assets, and all 11 paper pages. No official landscape/architecture example found; selected natural photographic wildlife with a clearly visible reported duplication failure.'],
    }
    (ROOT/'scripts/cover_refine_resadapter_sources.json').write_text(json.dumps(manifest, indent=2, ensure_ascii=False)+'\n')
    if args.poster_only:
        return
    frames = args.scratch_dir/'frames'
    frames.mkdir(exist_ok=True)
    for frame in range(FPS*DURATION):
        t = frame/FPS
        # Start and end at the poster's full result; comparison sweeps away
        # and back without an abrupt loop cut. Source samples stay static.
        amount = (1 + math.cos(2*math.pi*t/DURATION))/2
        raster(compose(sources,amount,comparison=True)).save(frames/f'{frame:04}.png')
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-framerate',str(FPS),'-i',str(frames/'%04d.png'),'-c:v','libx264','-preset','slow','-crf','21','-pix_fmt','yuv420p','-movflags','+faststart','-an',str(ROOT/'videos/resadapter-preview.mp4')],check=True)
    print('ResAdapter: photographic baseline/result comparison, 720×432, 7s, 24fps, no audio.')


if __name__ == '__main__':
    main()
