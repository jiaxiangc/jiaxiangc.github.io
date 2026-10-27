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

Previews last 5–8 seconds. Covers show complete original paper figures on white, preserving every panel,
label and original aspect ratio. No architecture is redrawn and no promotional overlay is added.
Hunyuan-Game uses the complete original Figure 19 character-consistency pipeline.
Covers remain separate from the existing hover clips.

The selected artwork preserves each paper's own presentation:

- Hy-Nomas: complete Figure 1 from the official technical report.
- FaithfulFaces: complete published training and inference framework.
- Reward Lightning: complete dataset, reward modeling and distillation pipeline.
- IPA: complete original preference-alignment framework.
- Phased One-step: complete original diagram with all training phases.
- ResAdapter: complete original pipeline, including all method-detail panels.
- Hunyuan-Game: complete original character-consistency pipeline, Figure 19.
- HunyuanVideo: original model overview.
- Beyond Reward Margin: complete original Figure 2 with both analysis panels.
- PersonaVlog: complete published multimodal-agent framework.

Complete originals remain in `images/paper-methods/`. Current whole-figure
exports, source hashes and output hashes are recorded in
`scripts/full_paper_cover_sources.json`. Hy-Nomas Figure 1 extraction is recorded
in `scripts/full_figure_hynomas_sources.json`. The full-figure manifest also records
the official source URLs and figure identities.

Wide figures fit completely inside a white preview area. The minimum preview
height keeps the hover/tap videos visible without clipping or stretching either
medium. No extra text links are shown below the covers.

### Rebuilding

```sh
python3 scripts/build_full_paper_covers.py
```

This exports all ten whole figures from the saved originals, using proportional
scaling and white transparency compositing only. It performs no figure crops,
rearrangement, relabeling, or synthesis.
To rebuild current clips, follow `current_clip_rebuild_order` in
`scripts/video_preview_sources.json`: build the base clips, apply the Hunyuan-Game
batch, then rebuild the original ResAdapter clip with `--paper resadapter`.
Run the full-figure exporter last. Hunyuan-Game keeps its selected later preview;
the other nine use the previous base previews. The Game batch also writes a
ResAdapter clip, so rebuilding the selected castle comparison afterward is required.
Each step lists its source manifest; pass external cache/scratch directories to
the builders as required. Legacy builders also emit inactive cover drafts;
only the current whole-figure exports should be published as covers.

Hy-Nomas resolves temporary video download URLs from the official model page at
build time. If automatic downloading fails, save the original official media in
`--source-dir` using the relevant motion manifest filenames. Do not commit signed
URLs.

## University emblems

Education uses original official artwork from
[Beihang University](https://buaa.edu.cn/xygk/jrbh0116old/bhxh.htm) and
[Xidian University](https://xcb.xidian.edu.cn/info/1008/1094.htm).

## Acknowledgements

Built on the [Jon Barron website template](https://github.com/jonbarron/jonbarron_website).
