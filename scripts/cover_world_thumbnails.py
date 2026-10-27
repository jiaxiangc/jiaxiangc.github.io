"""Scientific publication thumbnails composed from unchanged official assets.

The SVGs embed originals and use viewBox clipping, never retouching pixels.
Run with --source-dir containing the recorded official files. HTML/CSS or SVG
rendering may rasterize these compositions for the site's JPEG/video fallbacks.
"""
from pathlib import Path
import argparse
import base64
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'images/paper-previews'


def data_uri(path):
    mime = 'image/png' if path.suffix == '.png' else 'image/jpeg'
    return 'data:' + mime + ';base64,' + base64.b64encode(path.read_bytes()).decode()


def image(uri, crop, box, source_size, clip=None):
    x, y, w, h = box
    attr = f' clip-path="url(#{clip})"' if clip else ''
    native = (f'<use href="{uri}"/>' if uri.startswith('#') else
              f'<image width="{source_size[0]}" height="{source_size[1]}" href="{uri}"/>')
    return (f'<g{attr}><svg x="{x}" y="{y}" width="{w}" height="{h}" '
            f'viewBox="{" ".join(map(str,crop))}" preserveAspectRatio="none" overflow="hidden">'
            f'{native}</svg></g>')


def text(x, y, label, size=28, color='#26343a', anchor='middle'):
    return f'<text x="{x}" y="{y}" font-family="Arial, sans-serif" font-size="{size}" fill="{color}" text-anchor="{anchor}">{label}</text>'


def svg(content, background, defs=''):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="720" height="432" viewBox="0 0 720 432">'
            f'<defs>{defs}</defs><rect width="720" height="432" fill="{background}"/>{content}</svg>')


def build(source):
    OUT.mkdir(exist_ok=True)
    originals = {
        'resadapter-resolution-source.png': source / 'res-dreamlike1.png',
        'hunyuan-game-structure-source.png': source / 'game-character-2-o.png',
        'hunyuan-game-texture-source.png': source / 'game-character-2-g.png',
    }
    robot_path = source / 'hy-nomas-robot-source.jpg'
    robot = data_uri(robot_path)
    body = image(robot, (310, 120, 1300, 690), (0, 0, 720, 382), (1920, 1080))
    body += '<path d="M24 407h26m-6-6 6 6-6 6" stroke="#218a97" stroke-width="3" fill="none"/>'
    body += text(65, 417, 'Text control', 29, anchor='start')
    body += text(339, 417, '→', 29)
    body += text(699, 417, 'Robotics adaptation', 29, anchor='end')
    (OUT / 'hy-nomas-cover.svg').write_text(svg(body, '#ffffff'))

    game_in = data_uri(originals['hunyuan-game-structure-source.png'])
    game_out = data_uri(originals['hunyuan-game-texture-source.png'])
    body = image('#game-structure', (0, 0, 2351, 2351), (0, 20, 360, 360), (2351, 2351))
    body += image('#game-structure', (0, 0, 2351, 2351), (360, 20, 360, 360), (2351, 2351))
    body += image(game_out, (0, 0, 1024, 1024), (360, 20, 360, 360), (1024, 1024), 'game-reveal')
    body += '<path d="M338 207h38m-9-9 9 9-9 9" fill="none" stroke="#aabcc0" stroke-width="3"/>'
    body += text(180, 410, 'Reference + structure', 27, '#e9eef0')
    body += text(540, 410, 'Generated texture', 27, '#e9eef0')
    defs = f'<image id="game-structure" width="2351" height="2351" href="{game_in}"/>'
    defs += '<clipPath id="game-reveal"><rect id="game-wipe" x="360" y="20" width="360" height="360"/></clipPath>'
    (OUT / 'hunyuan-game-cover.svg').write_text(svg(body, '#000000', defs))

    fox = data_uri(originals['resadapter-resolution-source.png'])
    samples = [
        ((72, 0, 560, 560), (632, 0, 564, 560), (12, 39, 330, 330), '1024 × 1024'),
        ((72, 571, 182, 235), (254, 571, 184, 235), (364, 131, 184, 238), '336 × 432'),
        ((72, 819, 134, 176), (208, 819, 140, 176), (570, 197, 131, 172), '224 × 288'),
    ]
    body, defs = '', f'<image id="res-original" width="1196" height="1000" href="{fox}"/>'
    for i, (result_crop, baseline_crop, box, label) in enumerate(samples):
        x, y, w, h = box
        defs += f'<clipPath id="res-reveal-{i}"><rect id="res-wipe-{i}" x="{x}" y="{y}" width="{w}" height="{h}"/></clipPath>'
        body += image('#res-original', baseline_crop, box, (1196, 1000))
        body += image('#res-original', result_crop, box, (1196, 1000), f'res-reveal-{i}')
        body += text(x + w/2, 410, label, 26)
    (OUT / 'resadapter-cover.svg').write_text(svg(body, '#ffffff', defs))

    sources = {
        'hy-nomas': {
            'source_page': 'https://hy.tencent.com/model/open-source-model/detail?id=hy-nomas',
            'source_url': 'https://hy-model-ap-prod-1258344703.cos.ap-guangzhou.myqcloud.com/llm-blog/default/323a6063/2026102317595821_6c5ce50cf275899541755de746f010a0.mov',
            'frame_seconds': 7.5,
            'source_crop_xywh': [310, 120, 1300, 690],
            'video': 'Existing approved three-shot montage is unchanged.',
            'description': 'Original robot/cup result with a small white annotation band explaining text control and robotics adaptation.',
        },
        'hunyuan-game': {
            'source_page': 'https://cdn-portal.hunyuan.tencent.com/game/index.html',
            'source_urls': ['https://cdn-portal.hunyuan.tencent.com/game/assets/images/game_character/p2_o.png', 'https://cdn-portal.hunyuan.tencent.com/game/assets/images/game_character/p2_g.png'],
            'description': 'Official Game Character Generation input (appearance reference plus white structure model) and corresponding textured result. Full originals are retained.',
            'video': 'Seven-second editorial reveal of the published static pair; no generated motion or synthesized intermediate poses.',
        },
        'resadapter': {
            'source_page': 'https://res-adapter.github.io/',
            'source_url': 'https://res-adapter.github.io/assets/dreamlike1.png',
            'description': 'Published Dreamlike fox results at 1024×1024, 336×432, and 224×288. Exact original figure crops are recorded in samples; no resizing claim is inferred from layout.',
            'samples': [{'result_xywh': list(s[0]), 'baseline_xywh': list(s[1]), 'layout_xywh': list(s[2]), 'native_resolution': s[3]} for s in samples],
            'video': 'Seven-second synchronized baseline-to-ResAdapter reveal of these same published static results; no generated subject motion.',
        },
        'original_sha256': {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in [*originals.values(), robot_path]},
    }
    (ROOT / 'scripts/cover_world_sources.json').write_text(json.dumps(sources, indent=2, ensure_ascii=False) + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir', type=Path, required=True)
    build(parser.parse_args().source_dir)
