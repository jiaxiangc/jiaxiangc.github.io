"""Hy-Nomas: an in-scene method trace and selected interactive world demos.

The diagram is an editorial simplification of official Figures 5 and 9.
All world pixels are original model footage at its original speed. Captions
paraphrase verified inputs or identify the official adaptation demo.
"""
import argparse
import hashlib
import html
import json
from pathlib import Path
import re
import tempfile
import urllib.parse
import urllib.request

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from motion_common import Clip, W, H, FPS, cover, ease, font, render

MANIFEST = Path(__file__).with_name('world_motion_sources.json')
PURPLE = (219, 185, 255)
TEAL = (133, 243, 223)
BLUE = (156, 208, 255)
WHITE = (249, 252, 255)


def resolve_source_url(asset, page_cache):
    """Resolve public model-page media in memory; never persist signed URLs."""
    source_page = asset.get('source_page')
    if not source_page:
        return asset['url']
    if source_page not in page_cache:
        model_id = urllib.parse.parse_qs(urllib.parse.urlsplit(source_page).query).get('id', [''])[0]
        if not model_id:
            raise ValueError('Official source page is missing its model identifier')
        request = urllib.request.Request(
            'https://api.hunyuan.tencent.com/api/new-portal/opensource/query',
            data=json.dumps({'openSourceId': model_id}).encode(),
            headers={'Content-Type': 'application/json', 'Accept-Language': 'zh',
                     'User-Agent': 'Mozilla/5.0', 'Origin': 'https://hy.tencent.com',
                     'Referer': 'https://hy.tencent.com/'}, method='POST')
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.load(response)
        if payload.get('code') != 0 or not payload.get('data', {}).get('content'):
            raise ValueError('Official model page returned no public media content')
        # Responses contain expiring download credentials. Keep them only here,
        # not in a source manifest, cache file, exception message, or log.
        page_cache[source_page] = html.unescape(payload['data']['content'])
    expected = urllib.parse.urlsplit(asset['url'])
    for match in re.finditer(r'''https?://[^\s<>"']+''', page_cache[source_page]):
        candidate = match.group(0).rstrip(')')
        parsed = urllib.parse.urlsplit(candidate)
        if (parsed.scheme, parsed.netloc, parsed.path) == (expected.scheme, expected.netloc, expected.path):
            return candidate
    raise ValueError('Requested media file is absent from the official model page')


def ensure_source(asset, source_dir, page_cache):
    """Use a verified local source or download an official asset atomically."""
    path = source_dir / asset['filename']
    if not path.exists():
        temporary = path.with_suffix('.download')
        try:
            url = resolve_source_url(asset, page_cache)
            request = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0',
                'Referer': asset.get('source_page', 'https://hy-nomas.hy.tencent.com/')})
            digest = hashlib.sha256()
            # Signed COS media permits GET; HEAD can return 403 even when valid.
            with urllib.request.urlopen(request, timeout=90) as response, temporary.open('wb') as target:
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    target.write(chunk)
                    digest.update(chunk)
            if digest.hexdigest() != asset['sha256']:
                raise ValueError('Downloaded media did not match the recorded source')
            temporary.replace(path)
        except Exception:
            source_page = asset.get('source_page', 'https://hy-nomas.hy.tencent.com/')
            # Suppress chained network exceptions: they can contain signed URLs.
            raise RuntimeError(
                f"Could not download or verify {asset['filename']}. "
                f"Open the official page {source_page}, download the matching original media, "
                f"and save it as {path}; then rerun with --source-dir {source_dir}. "
                "Keep download signatures out of the repository; cached files are SHA-256 checked."
            ) from None
        finally:
            temporary.unlink(missing_ok=True)
    if hashlib.sha256(path.read_bytes()).hexdigest() != asset['sha256']:
        raise ValueError(f'Source changed or is incomplete: {path}')
    return path


def fade(t, start, end, ramp=.35):
    return ease((t-start)/ramp) * ease((end-t)/ramp)


def bezier(points, n=100):
    p = np.asarray(points, dtype=float)
    return [tuple((1-u)**3*p[0]+3*(1-u)**2*u*p[1]+3*(1-u)*u*u*p[2]+u**3*p[3]) for u in np.linspace(0,1,n)]


def stroke(draw, points, color, alpha, width=2, progress=1):
    visible = points[:max(2, round(len(points)*min(1,max(0,progress))))]
    draw.line(visible, fill=(*color, round(255*alpha)), width=width, joint='curve')


def label(layer, value, xy, size=34, color=WHITE, alpha=1, anchor='mm'):
    # Soft glyph-only shadow: no boxed background and no hard subtitle outline.
    shadow=Image.new('RGBA',(W,H))
    d=ImageDraw.Draw(shadow)
    d.text((xy[0],xy[1]+1),value,font=font(size,'demi'),fill=(0,15,22,round(245*alpha)),anchor=anchor,stroke_width=2,stroke_fill=(0,15,22,round(140*alpha)))
    layer.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(2)))
    ImageDraw.Draw(layer).text(xy,value,font=font(size,'demi'),fill=(*color,round(255*alpha)),anchor=anchor)


def method_trace(image, t):
    alpha=fade(t,.12,1.9,.24)
    if alpha <= 0: return image
    # An unboxed input/output trace sits inside the scene. Its feedback arc
    # expresses the official history loop without miniaturizing a whole figure.
    layer=Image.new('RGBA',(W,H));d=ImageDraw.Draw(layer)
    paths=[
        (bezier([(121,317),(192,317),(228,351),(294,351)]),PURPLE),
        (bezier([(171,393),(206,393),(244,361),(294,361)]),TEAL),
        (bezier([(326,355),(393,355),(433,355),(485,355)]),WHITE),
        (bezier([(565,334),(604,257),(319,254),(312,335)]),BLUE),
    ]
    for i,(points,color) in enumerate(paths):
        progress=ease((t-.12-i*.07)/.55)
        stroke(d,points,color,alpha*.85,3,progress)
        if progress>.98:
            at=(t*.75+i*.2)%1
            q=points[int(at*(len(points)-1))]
            d.ellipse((q[0]-4,q[1]-4,q[0]+4,q[1]+4),fill=(*color,round(255*alpha)))
    d.ellipse((294,337,326,373),outline=(*WHITE,round(235*alpha)),width=2)
    label(layer,'text',(71,316),40,PURPLE,alpha)
    label(layer,'camera',(91,391),40,TEAL,alpha)
    label(layer,'world',(555,355),42,WHITE,alpha)
    return Image.alpha_composite(image.convert('RGBA'),layer).convert('RGB')


def cue(image, t, start, end, words, color, kind):
    alpha=fade(t,start,end,.32)
    if alpha<=0:return image
    layer=Image.new('RGBA',(W,H)); d=ImageDraw.Draw(layer)
    # Small input glyph, then the prompt itself. Both sit directly in the scene.
    y=382
    if kind=='camera':
        points=[(36,y+11),(36,y-10),(16,y-10)]
        stroke(d,points,color,alpha,3)
        d.line([(16,y-2),(16,y-10),(24,y-10)],fill=(*color,round(255*alpha)),width=3)
    else:
        d.line([(19,y-14),(19,y+14)],fill=(*color,round(255*alpha)),width=3)
        d.ellipse((28,y-3,33,y+2),fill=(*color,round(255*alpha)))
    label(layer,words,(52,y),38,WHITE,alpha,anchor='lm')
    return Image.alpha_composite(image.convert('RGBA'),layer).convert('RGB')


def build(source_dir, contact_dir, contact_only=False):
    info=json.loads(MANIFEST.read_text())
    source_dir.mkdir(parents=True,exist_ok=True);contact_dir.mkdir(parents=True,exist_ok=True)
    clips={}
    timeline=[]
    elapsed=0
    for shot in info['shots']:
        # Cuts land on output frame boundaries; original source speed is kept.
        count=round((shot['source_end']-shot['source_start'])*FPS)
        timeline.append((elapsed/FPS,(elapsed+count)/FPS,shot))
        elapsed+=count
    duration=elapsed/FPS
    if abs(duration-info['format']['duration'])>1/FPS:
        raise ValueError('Manifest duration does not match the edit')
    def clean(asset_id, source_t, crop=None):
        source=clips[asset_id].frame(source_t)
        if crop:source=source.crop(tuple(crop))
        return cover(source,(W,H),focus=(.5,.5))
    def frame(t):
        start,end,shot=next((s for s in timeline if s[0]<=t<s[1]),timeline[-1])
        local=max(0,min(t-start,end-start-1/FPS))
        out=clean(shot['asset'],shot['source_start']+local,shot.get('crop'))
        out=method_trace(out,t)
        for item in shot.get('cues',[]):
            color=TEAL if item['kind']=='camera' else PURPLE
            out=cue(out,local,*item['interval'],item['text'],color,item['kind'])
        return out
    try:
        page_cache = {}
        for asset in info['assets']:
            path=ensure_source(asset,source_dir,page_cache)
            clips[asset['id']]=Clip(path)
        for start,end,shot in timeline:
            if shot['source_start']<0 or shot['source_end']>clips[shot['asset']].duration+1/FPS:
                raise ValueError(f'Shot outside source: {shot["asset"]}')
        times=info['review_times']
        rows=(len(times)+3)//4
        sheet=Image.new('RGB',(1440,248*rows),(245,245,245))
        for i,t in enumerate(times):
            f=frame(t)
            f.save(contact_dir/f'hy-montage-frame-{t:.2f}.jpg',quality=95)
            small=f.resize((360,216),Image.Resampling.LANCZOS)
            sheet.paste(small,((i%4)*360,(i//4)*248))
            ImageDraw.Draw(sheet).text(((i%4)*360+10,(i//4)*248+222),f'{t:.2f}s',fill='black',font=font(18))
        sheet.save(contact_dir/'hy-montage-storyboard.jpg',quality=95)
        if not contact_only:
            render('hy-nomas',frame,duration,poster_t=0,crf=21,
                   contact_path=contact_dir/'hy-montage-200px.jpg')
            poster=info['poster']
            clean(poster['asset'],poster['source_time'],poster.get('crop')).save(
                Path(__file__).resolve().parents[1]/'images/paper-previews/hy-nomas-poster.jpg',quality=95,optimize=True)
    finally:
        for clip in clips.values():clip.close()


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir',type=Path,default=Path(tempfile.gettempdir())/'paper-motion-sources/world')
    parser.add_argument('--contact-dir',type=Path,default=Path(tempfile.gettempdir())/'paper-motion-contacts')
    parser.add_argument('--contact-only',action='store_true')
    args=parser.parse_args();build(args.source_dir,args.contact_dir,args.contact_only)
