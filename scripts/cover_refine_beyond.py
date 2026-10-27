"""Compose a PG-DPO cover and editorial reveal from published Figure 3 frames.

Uses unchanged image pixels: the animation is a shared 2% camera push and a
comparison wipe, not reconstructed video or generated intermediate frames.
"""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
URL = 'https://arxiv.org/html/2511.19049v1/fig/comparison_vc2.png'
SHA = '9ae7745bbfa3370bbe3eea2b7a7738f2cb633e296b54ffc3d7e0dfc70ab90fa5'


def ffmpeg(*args):
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', *map(str, args)], check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir', type=Path, required=True)
    a = parser.parse_args()
    a.source_dir.mkdir(parents=True, exist_ok=True)
    source = a.source_dir / 'comparison_vc2.png'
    if not source.exists():
        source.write_bytes(urlopen(URL, timeout=90).read())
    if hashlib.sha256(source.read_bytes()).hexdigest() != SHA:
        raise ValueError('Published source differs from the recorded Figure 3.')
    crops = {'videodpo': [3786, 634, 410, 252], 'pgdpo': [3786, 914, 410, 252]}
    frames = {}
    for method, (x, y, w, h) in crops.items():
        frames[method] = a.source_dir / (method + '-coast.jpg')
        ffmpeg('-i', source, '-vf', f'crop={w}:{h}:{x}:{y},format=rgb24', '-frames:v', 1, '-q:v', 2, frames[method])
    data = {k: base64.b64encode(v.read_bytes()).decode() for k, v in frames.items()}
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="720" height="432" viewBox="0 0 720 432" role="img" aria-labelledby="title desc">
<title id="title">Preference alignment in a coastal portrait</title>
<desc id="desc">Published VideoDPO and PG-DPO frames from the same seaside example in Figure 3. A thin comparison boundary separates the original results.</desc>
<defs><clipPath id="left"><rect width="230" height="432"/></clipPath></defs>
<image width="720" height="432" preserveAspectRatio="xMidYMid slice" href="data:image/jpeg;base64,{data['pgdpo']}"/>
<image width="720" height="432" preserveAspectRatio="xMidYMid slice" clip-path="url(#left)" href="data:image/jpeg;base64,{data['videodpo']}"/>
<path d="M230 0V432" stroke="white" stroke-opacity=".8" stroke-width="2"/>
<g font-family="Arial,Helvetica,sans-serif" font-size="29" fill="white" stroke="#15232b" stroke-opacity=".65" stroke-width="2" paint-order="stroke fill">
<text x="18" y="408">VideoDPO</text><text x="700" y="408" text-anchor="end" font-weight="700">PG-DPO</text>
</g></svg>'''
    dest = ROOT / 'images/paper-previews'
    (dest / 'beyond-reward-coast-cover.svg').write_text(svg)
    ffmpeg('-i', frames['pgdpo'], '-vf', 'scale=720:442,crop=720:432', '-frames:v', 1, '-q:v', 2, dest / 'beyond-reward-poster.jpg')
    zoom = "scale=1200:-1,crop=1200:720,zoompan=z='1+0.02*on/167':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s=720x432:fps=24,format=yuv420p"
    progress = 'clip((T-0.55)/3.2,0,1)'
    reveal = f"if(lt(abs(X-W*(1-{progress})),1.2),235,if(gte(X,W*(1-{progress})),B,A))"
    vf = (f'[0:v]{zoom}[a];[1:v]{zoom}[b];'
          f"[a][b]blend=all_expr='{reveal}',"
          "drawtext=text='VideoDPO':fontcolor=white:fontsize=25:borderw=1.5:bordercolor=black@0.6:x=18:y=h-40:enable='lt(t,3.7)',"
          "drawtext=text='PG-DPO':fontcolor=white:fontsize=28:borderw=1.5:bordercolor=black@0.6:x=w-tw-18:y=h-42[out]")
    ffmpeg('-loop', 1, '-i', frames['videodpo'], '-loop', 1, '-i', frames['pgdpo'],
           '-filter_complex', vf, '-map', '[out]', '-t', 7, '-an', '-c:v', 'libx264',
           '-preset', 'slow', '-crf', 21, '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
           ROOT / 'videos/beyond-reward-preview.mp4')
    manifest = {'paper': 'https://arxiv.org/abs/2511.19049', 'figure': 3,
                'source_url': URL, 'source_sha256': SHA, 'source_size': [4214, 1172],
                'crop_xywh': crops, 'example': 'Woman standing by the sea, final displayed frame',
                'rows': {'videodpo': 'VideoDPO, third row', 'pgdpo': 'Ours, fourth row'},
                'cover': 'Full coastal scene: VideoDPO left 32%, PG-DPO right 68%; transparent labels and one comparison seam.',
                'animation': 'Seven-second editorial comparison wipe and identical 2% push on two published still frames. No synthesized subject motion or quality modification.'}
    (ROOT / 'scripts/cover_refine_beyond_sources.json').write_text(json.dumps(manifest, indent=2) + '\n')


if __name__ == '__main__':
    main()
