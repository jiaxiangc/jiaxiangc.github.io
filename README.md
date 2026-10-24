# jiaxiangc.github.io

Personal academic homepage of **Jiaxiang Cheng**, Researcher at Tencent HY.

Live site: <https://jiaxiangc.github.io>

## Structure

A minimal static site based on [Jon Barron's website template](https://github.com/jonbarron/jonbarron_website):

- `index.html` — all page content (bio, news, publications, education, experience)
- `stylesheet.css` — Lato font and styling
- `images/` — avatar, paper thumbnails, logos, and favicons
- `videos/` — compact previews for all ten publications and preprints
- `paper-previews.js` — hover playback, selected covers, and touch/keyboard controls
- `site-visits.js` — production-only page-view counter
- `.nojekyll` — tells GitHub Pages to serve the HTML directly without a Jekyll build

## Local preview

Open `index.html` directly in a browser, or serve the folder:

```sh
python3 -m http.server 8000
# then visit http://localhost:8000
```

## Paper previews

Every publication and preprint starts with a selected static cover. Hovering a
cover loads and plays its silent preview; leaving restores the cover and resets
the video. Touch users can tap, and keyboard users can press Enter or Space on
the cover to toggle playback. Reduced-motion users get explicit play controls
without hover playback. Videos stop offscreen or when the page is hidden.

Previews last 5–8 seconds. Landscape compositions keep the publication list
consistent, with thumbnails displayed at 200px wide. Static covers pair an
authentic image with a small research descriptor inside the image. This web overlay
fades out during playback. There are no separate title bars or caption cards.

Hy-Nomas combines three official demonstrations in 7.875 seconds: a ray passing
over Coral City, a robotics adaptation separating nested cups, and a winged
character flying above a coastal palace. A short transparent method
trace is based on official Figures 5 and 9. An in-frame cue identifies the
robotics adaptation. Each shot keeps the published playback
speed. The final flight uses medium framing that preserves both wings; feet
leave the lower crop. Its poster shows the two grippers separating the cups,
with the world-model descriptor rendered separately in the webpage.

Source selection prioritizes attractive lighting, composition, clear subjects,
and sustained movement. Real video results use short, carefully selected
sequences with restrained cuts or dissolves. Figure-only papers use larger
original images where available. Reward Lightning and Phased OAE use horizontal
reveals between paired official videos: both sides play at their original speed,
and the result keeps moving after the divider leaves. ResAdapter, IPA and
FaithfulFaces use published image comparisons with a subtle, matched camera
push-in that continues after the reveal. This is editorial camera movement,
not synthesized subject motion. The corresponding source conditions are recorded
in the manifests. Brief transparent annotations identify methods without separate
title bars. PersonaVlog uses quieter, sustained character action.

All visual results come from official project demos or published paper figures.
No intermediate model results are synthesized. Source URLs, crop coordinates,
time ranges, and selection notes are recorded in the
`scripts/*_motion_sources.json` manifests. `scripts/video_preview_sources.json`
indexes them.

Rebuild with Python 3, Pillow, NumPy, OpenCV, PyMuPDF, and FFmpeg.
PyMuPDF extracts the original images embedded in the IPA and FaithfulFaces papers:

```sh
python3 scripts/build_paper_previews.py
# Or rebuild one paper:
python3 scripts/build_paper_previews.py --paper hy-nomas
# Optionally choose an external cache and contact-sheet directory:
python3 scripts/build_paper_previews.py --source-dir /tmp/paper-sources --contact-dir /tmp/paper-contacts
```

The builders download missing original assets to the external cache. Only the
finished MP4s and JPEG posters belong in the site. Fonts are used for external
review sheets and transparent in-scene cues. `scripts/motion_common.py` contains the shared sampler
and encoder; each group has its own edit builder.

Hy-Nomas resolves temporary download URLs from the official model page at build
time. If automatic downloading fails, save the original official media in
`--source-dir` using the manifest filenames. Do not commit signed download URLs.

## University emblems

Education uses original official artwork from
[Beihang University](https://buaa.edu.cn/xygk/jrbh0116old/bhxh.htm) and
[Xidian University](https://xcb.xidian.edu.cn/info/1008/1094.htm).

## Page views

The copyright line displays total page views (PV) using
[Busuanzi's official counter](https://ibruce.info/2015/04/04/busuanzi/).
It uses the total returned by the provider without resetting it or adding an
offset. Visits that were never recorded cannot be recovered retroactively.
Repeated page loads count as additional views; this is not a count of people.
Blocking extensions or browser privacy settings can affect totals.

The asynchronous third-party script loads only on the HTTPS production hostname
`jiaxiangc.github.io`. Local previews and forks show `— views`
without loading the service or submitting visits. On production, counters remain
hidden until data is available. No account or API key is
required. To disable collection, remove the `site-visits.js` script tag from
`index.html`.

## Acknowledgements

Built on the [Jon Barron website template](https://github.com/jonbarron/jonbarron_website).
