#!/usr/bin/env python3
"""Export complete published figures. No cropping, rearrangement or overlays."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path
import fitz
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SOURCES = {
    'hy-nomas': 'hy-nomas-figure1.png',
    'faithfulfaces': 'faithfulfaces.svg',
    'reward-lightning': 'reward-lightning.jpg',
    'ipa': 'ipa.png',
    'v-pae': 'v-pae.jpg',
    'resadapter': 'resadapter.png',
    'hunyuan-game': 'hunyuan-game.png',
    'hunyuanvideo': 'hunyuanvideo-overall.png',
    'beyond-reward': 'beyond-reward.png',
    'personavlog': 'personavlog.jpg',
}

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--papers', nargs='+', choices=SOURCES, default=list(SOURCES))
    args = parser.parse_args()
    manifest_path = ROOT / 'scripts/full_paper_cover_sources.json'
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {
        'policy': 'Complete original published figures only. Every original panel and label is retained. Only proportional scaling and transparency compositing on white are permitted.',
        'builder': 'python3 scripts/build_full_paper_covers.py',
        'covers': {},
    }
    for slug in args.papers:
        src = ROOT / 'images/paper-methods' / SOURCES[slug]
        out = ROOT / 'images/paper-previews' / (slug + '-full-paper-cover.png')
        if src.suffix == '.svg':
            with fitz.open(src) as doc:
                page = doc[0]
                scale = 1200 / page.rect.width
                page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False).save(out)
            operation = 'Render entire original vector figure on white at 1200px width.'
        else:
            w,h = Image.open(src).size
            nw = min(w, 1200)
            nh = round(h * nw / w)
            graph = f'[1:v][0:v]overlay=shortest=1,scale={nw}:{nh}:flags=lanczos,format=rgb24[out]'
            subprocess.run(['ffmpeg','-v','error','-y','-i',str(src),'-f','lavfi','-i',f'color=white:s={w}x{h},format=rgba',
                            '-filter_complex',graph,'-map','[out]','-frames:v','1',str(out)],check=True)
            operation = 'Whole image; proportional scaling only, with original transparency composited onto white.'
        size = Image.open(out).size
        manifest['covers'][slug] = {**manifest['covers'].get(slug, {}), 'source':str(src.relative_to(ROOT)), 'source_sha256':digest(src),
                                   'file':str(out.relative_to(ROOT)), 'dimensions':list(size),
                                   'sha256':digest(out), 'operation':operation, 'crop':None}
    manifest_path.write_text(json.dumps(manifest,indent=2)+'\n')
    print('Exported complete figures:', ', '.join(args.papers))

if __name__ == '__main__':
    main()
