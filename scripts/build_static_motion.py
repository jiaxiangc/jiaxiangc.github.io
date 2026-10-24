"""Short visual explanations composed only from authentic paper images.

Full-bleed comparison wipes reveal published baselines and method results.
Camera moves and comparison wipes are editorial; no model samples are
retouched and no intermediate body poses are synthesized.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import urllib.request
from PIL import Image, ImageDraw, ImageFilter
from motion_common import ease, lerp, render, font


def ensure_sources(source_dir, slugs):
    manifest = json.loads(Path(__file__).with_name('static_motion_sources.json').read_text())
    source_dir.mkdir(parents=True, exist_ok=True)
    for slug in slugs:
        for source in manifest[slug]['sources']:
            path = source_dir / source['file']
            if not path.exists():
                request = urllib.request.Request(source['url'], headers={'User-Agent': 'Mozilla/5.0 paper-preview-builder'})
                with urllib.request.urlopen(request, timeout=60) as response:
                    data = response.read()
                if hashlib.sha256(data).hexdigest() != source['sha256']:
                    raise ValueError(f"Official source changed: {source['url']}")
                temporary = path.with_suffix(path.suffix + '.download')
                temporary.write_bytes(data)
                temporary.replace(path)
                print(f"Downloaded {source['file']}", flush=True)
            if hashlib.sha256(path.read_bytes()).hexdigest() != source['sha256']:
                raise ValueError(f'Source hash mismatch: {path}')
            if source.get('size'):
                with Image.open(path) as image:
                    if list(image.size) != source['size']:
                        raise ValueError(f'Source dimensions changed: {path}')


def rgb(path):
    source = Image.open(path).convert('RGBA')
    background = Image.new('RGBA', source.size, 'white')
    background.alpha_composite(source)
    return background.convert('RGB')


def crop(image, box):
    x, y, w, h = box
    return image.crop((x, y, x + w, y + h))


def pdf_image(path, xref):
    # Extract the native embedded photo rather than enlarging the HTML composite.
    import fitz
    with fitz.open(path) as document:
        data = document.extract_image(xref)['image']
    return Image.open(io.BytesIO(data)).convert('RGB')


def camera(image, a, b, progress, size):
    """An editorial camera move wholly inside a published image."""
    x, y, width = [lerp(v0, v1, ease(progress)) for v0, v1 in zip(a, b)]
    height = width * size[1] / size[0]
    if x < -.01 or y < -.01 or x + width > image.width + .01 or y + height > image.height + .01:
        raise ValueError(f'Camera outside source: {(x, y, width, height)} / {image.size}')
    return image.transform(size, Image.Transform.EXTENT, (x, y, x + width, y + height), Image.Resampling.BICUBIC)


def fade(t, start, end, ramp=.25):
    return ease((t-start)/ramp)*ease((end-t)/ramp)


def label(layer, words, xy, alpha=1, color=(248, 252, 255), size=36, anchor='lm'):
    # Glyph-only shadow, never a title bar or caption panel.
    shadow = Image.new('RGBA', layer.size)
    ImageDraw.Draw(shadow).text((xy[0], xy[1]+1), words, font=font(size, 'demi'),
                               anchor=anchor, fill=(5, 18, 25, round(230*alpha)),
                               stroke_width=2, stroke_fill=(5, 18, 25, round(170*alpha)))
    layer.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(2)))
    ImageDraw.Draw(layer).text(xy, words, font=font(size, 'demi'), anchor=anchor,
                              fill=(*color, round(255*alpha)))


def comparison_reveal(before, after, result_name, baseline_name='baseline'):
    """A single, steady horizontal reveal of a factual published comparison.

    A matched 2.5% editorial push applies to both still images. The hard
    boundary marks the qualitative comparison; the gentle camera movement
    continues after the reveal. Original poster pixels stay unchanged.
    """
    size, duration = (720, 432), 7.0
    if before.size != size or after.size != size:
        raise ValueError('Comparison sources must share the final canvas')
    def clean(t):
        # Keep the approved poster exactly as it was: no editorial zoom.
        return after.copy()
    def push(image,t):
        # A shared affine crop, never pose interpolation or generated motion.
        # Linear progress also retains movement after the wipe has ended.
        zoom=1+.025*min(1,max(0,t/duration))
        width,height=size[0]/zoom,size[1]/zoom
        x,y=(size[0]-width)/2,(size[1]-height)/2
        return image.transform(size,Image.Transform.EXTENT,
                               (x,y,x+width,y+height),Image.Resampling.BICUBIC)
    def frame(t):
        amount=min(1,max(0,(t-.55)/3.7))
        boundary=round(size[0]*amount)
        out=push(before,t)
        result=push(after,t)
        if boundary>0:
            out.paste(result.crop((0,0,boundary,size[1])),(0,0))
        layer=Image.new('RGBA',size)
        if 0<boundary<size[0]:
            glow=Image.new('RGBA',size)
            ImageDraw.Draw(glow).line([(boundary,0),(boundary,size[1])],
                                     fill=(198,236,240,125),width=5)
            layer.alpha_composite(glow.filter(ImageFilter.GaussianBlur(3)))
            ImageDraw.Draw(layer).line([(boundary,0),(boundary,size[1])],
                                      fill=(235,250,250,235),width=2)
        label(layer,baseline_name,(size[0]-24,399),fade(t,.15,3.3),size=30,anchor='rm')
        label(layer,result_name,(24,399),fade(t,1.5,5.3),size=30)
        return Image.alpha_composite(out.convert('RGBA'),layer).convert('RGB')
    return {'frame':frame,'clean':clean,'duration':duration,'poster_t':5.8,'size':size}


def resadapter_builder(src):
    # Official DreamshaperXL extrapolation gallery: the same castle-knight
    # example, ResAdapter on the left and baseline on the right. The original
    # duplicated subject is the reported baseline failure, never a fake edit.
    sheet=rgb(src/'res-dreamshaperxl-extrapolation.png')
    after=crop(sheet,(116,1022,1020,612)).resize((720,432),Image.Resampling.LANCZOS)
    before=crop(sheet,(1138,1022,1020,612)).resize((720,432),Image.Resampling.LANCZOS)
    return comparison_reveal(before,after,'ResAdapter')


def ipa_builder(src):
    # Figure 8 / page 18, right example, first two time columns. Extracting the
    # native images omits the PDF's separate red annotation rectangles without
    # retouching any model output. VACE and Ours use the exact same columns.
    def pair(xrefs):
        canvas=Image.new('RGB',(720,432))
        for i,xref in enumerate(xrefs):
            native=pdf_image(src/'ipa-paper.pdf',xref)
            # Adjacent full-bleed portraits preserve face, fingertips and arms.
            panel=crop(native,(0,40,240,288)).resize((360,432),Image.Resampling.LANCZOS)
            canvas.paste(panel,(i*360,0))
        return canvas
    return comparison_reveal(pair([892,893]),pair([870,873]),'IPA','VACE')


def beyond_builder(src):
    size, duration = (720,432), 7.0
    car_sheet=rgb(src/'beyond-vc_ab1.png')
    tie_sheet=rgb(src/'beyond-wan_ab1.png')
    pairs=[
        (crop(car_sheet,(79,54,293,179)),crop(car_sheet,(79,650,293,179)),'baseline'),
        (crop(tie_sheet,(2433,386,270,152)),crop(tie_sheet,(2433,550,270,152)),'DPO'),
    ]
    def shot(image,local):
        if image.width==293:
            return camera(image,(0,1,293),(8,2,278),local/3.5,size)
        return camera(image,(6,0,253),(11,3,243),local/3.5,size)
    def clean(t):
        idx=0 if t<3.5 else 1; local=t%3.5
        return shot(pairs[idx][1],local)
    def frame(t):
        idx=0 if t<3.5 else 1; local=t%3.5
        baseline,result,name=pairs[idx]
        before,after=shot(baseline,local),shot(result,local)
        # Full-bleed comparative reveal: source columns and rows are documented.
        # The hard seam means this cannot be mistaken for synthesized motion.
        amount=ease((local-.5)/1.25)
        boundary=round(size[0]*(1-amount))
        out=after.copy()
        if boundary>0:out.paste(before.crop((0,0,boundary,size[1])),(0,0))
        layer=Image.new('RGBA',size);d=ImageDraw.Draw(layer)
        if 0<amount<1:
            d.line([(boundary,0),(boundary,size[1])],fill=(196,231,238,220),width=2)
            d.ellipse((boundary-5,207,boundary+5,217),fill=(222,247,249,245))
        label(layer,name,(30,389),fade(local,.1,1.1),size=34)
        label(layer,'PG-DPO',(size[0]-30,389),fade(local,1.3,3.15),size=36,anchor='rm')
        return Image.alpha_composite(out.convert('RGBA'),layer).convert('RGB')
    return {'frame':frame,'clean':clean,'duration':duration,'poster_t':1.8,'size':size}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-dir', type=Path, required=True)
    parser.add_argument('--scratch-dir', type=Path, required=True)
    parser.add_argument('--paper', choices=['all', 'resadapter', 'ipa', 'beyond-reward'], default='all')
    parser.add_argument('--fetch-only', action='store_true')
    parser.add_argument('--contact-only', action='store_true')
    args = parser.parse_args()
    args.scratch_dir.mkdir(parents=True, exist_ok=True)
    builders = {'resadapter': resadapter_builder, 'ipa': ipa_builder, 'beyond-reward': beyond_builder}
    selected = list(builders) if args.paper == 'all' else [args.paper]
    ensure_sources(args.source_dir, selected)
    if args.fetch_only:
        return
    sheets=[]
    for slug in selected:
        info=builders[slug](args.source_dir)
        fn,duration,poster_t,size=[info[k] for k in ('frame','duration','poster_t','size')]
        cell_height=round(200*size[1]/size[0])
        sheet=Image.new('RGB',(1000,cell_height+30),'white')
        for col,fraction in enumerate([.1,.25,.4,.65,.85]):
            t=duration*fraction; image=fn(t)
            small=image.resize((200,cell_height),Image.Resampling.LANCZOS)
            small.save(args.scratch_dir/f'{slug}-{col}-200px.jpg',quality=95)
            sheet.paste(small,(col*200,0))
            ImageDraw.Draw(sheet).text((col*200+8,cell_height+5),f'{t:.1f}s',fill='black',font=font(18))
            image.save(args.scratch_dir/f'{slug}-{col}-full.jpg',quality=95)
        sheet.save(args.scratch_dir/f'{slug}-storyboard.jpg',quality=95)
        sheets.append(sheet)
        if not args.contact_only:
            _,poster=render(slug,fn,duration,poster_t=poster_t,crf=21,size=size,
                            contact_path=args.scratch_dir/f'{slug}-contact-200px.jpg')
            # The homepage owns cover typography; preserve a pure source still.
            info['clean'](poster_t).save(poster,quality=95,optimize=True)
    combined=Image.new('RGB',(1000,sum(s.height for s in sheets)),'white')
    y=0
    for sheet in sheets:
        combined.paste(sheet,(0,y)); y+=sheet.height
    combined.save(args.scratch_dir/'static-compact-storyboard.jpg',quality=95)



if __name__ == '__main__':
    main()
