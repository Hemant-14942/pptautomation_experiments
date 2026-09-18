# Template Beautifier (pptautomation_experiments)

This project takes a plain, unstyled PowerPoint deck (the **input**) and a nicely
designed PowerPoint deck (the **template**) and produces a new deck where every
slide from the input has been redrawn using the colors, fonts, and shapes copied
from the template. Think of it as: "take my raw content, dress it up in this
template's look."

This README explains the folder structure, what each file is responsible for,
how the pipeline flows end to end, and — because this comes up a lot — exactly
how the code decides whether a run uses **defence layout** (extra top banner
spacing) versus normal layout, and how to pass that flag from an API in
production.

---

## 1. The big picture (in one paragraph)

You run the tool with three things: an input `.pptx`, a template `.pptx`, and
where to save the output `.pptx`. The tool reads the template once and builds
a "design spec" (colors, fonts, cloneable shapes, and whether it's a defence
template). Then it goes through every slide of the input deck, figures out
what kind of slide it is (a pure text slide, an MCQ question slide, an image
slide, a table slide, etc.), and re-draws that slide's shapes at the right
position/size using the template's colors and shapes. Finally, it stitches
everything into a new `.pptx` zip file and saves it.

```
input.pptx  +  template.pptx  --->  [ pipeline ]  --->  output.pptx
```

---

## 2. How to run it

### First-time setup (after unzipping the project)

The `.venv` folder is **not** included in the zip — each machine creates its own.
From the **project root** (the folder that contains `app/`, `data/`, and `pyproject.toml`):

```bash
cd template-beautifier   # or whatever you named the unzipped folder

# Install uv if needed: https://docs.astral.sh/uv/getting-started/installation/
uv sync                  # creates .venv and installs all dependencies
```

Requirements: **Python 3.11+** and **[uv](https://docs.astral.sh/uv/)**.

### Run the pipeline

```bash
# Dev shortcut (uses fixed paths inside data/* and IS_DEFENCE in app/main.py)
PYTHONPATH=. uv run python app/main.py
```

This calls `build_deck(input_path, template_path, output_path, is_defence=...)`
in [`app/dynamic_rendering/services/orchestrator.py`](app/dynamic_rendering/services/orchestrator.py).

Set defence mode in [`app/main.py`](app/main.py):

```python
IS_DEFENCE = False  # True = defence banner spacing; False = normal layout
```

---

## 3. Folder-by-folder guide

```
app/
├── main.py                       Dev entry point (fixed sample paths + IS_DEFENCE flag)
└── dynamic_rendering/            All the actual pipeline code lives here
    ├── log.py                    Sets up structured (ECS) logging
    ├── config/                   Path settings (where input/template/output folders are)
    ├── constants/                Fixed numbers: sizes, fonts, EMU thresholds, defence banner height
    ├── domain/models/            Plain data classes shared across the app (DesignSpec, TemplateArchive)
    ├── infrastructure/pptx/      Low-level zip/xml reading & writing of .pptx files
    ├── services/                 The actual pipeline logic (see below, this is the heart of the app)
    └── utils/xml/                Small XML helper functions used everywhere
data/                             Sample input decks, templates, and outputs (outside app/)
```

### 3.1 `data/` — sample data, not code
- `input/` — example raw/unstyled decks you can test with.
- `templates/` — example designed templates. Each template also gets a
  matching `*.designspec.json` file next to it — this is a **cache** (see
  §6) so the template doesn't have to be re-scanned every run.
- `output/` — where generated decks land when you run the dev script.
- `slide_text_analysis/` — leftover JSON dumps from earlier text-analysis
  experiments; not used by the current pipeline.

### 3.2 `app/dynamic_rendering/config/`
- `settings.py` — a `Paths` dataclass pointing at `data/input`,
  `data/output`, `data/templates`. Only used by the dev entry point
  (`app/main.py`).

### 3.3 `app/dynamic_rendering/constants/`
Fixed numbers used across the app so they aren't hard-coded in ten places:
- `shape_geometry.py` — size ranges (in EMU, PowerPoint's internal unit —
  914,400 EMU = 1 inch) used to recognize shapes by their size, e.g. "a
  question pill is roughly this wide and this tall." **This file also holds
  `DEFENCE_BANNER_HEIGHT_EMU`** — how far content is pushed down in defence
  mode (see §5).
- `template_design.py` — which slide index in the template is the "MCQ
  design" reference slide, which is the "title design" reference slide, and
  which slide is the "output shell" (the layout every generated slide is
  based on). Also holds fixed fonts/sizes the design team decided should
  never change per-template (font family, heading size, etc.).
- `design_tokens_defaults.py` — fallback colors used if the template scan
  can't find something (e.g. default pill color if no pill was found).
- `presentation_defaults.py` — default slide width/height and starting
  slide ID, used when the template's own `presentation.xml` doesn't specify
  them.
- `xml_namespaces.py` — the XML namespace prefixes PowerPoint's XML format
  uses (`p:`, `a:`, `r:`, ...), needed because `.pptx` files are just zipped
  XML.

### 3.4 `app/dynamic_rendering/domain/models/`
- `design_spec.py` — the `DesignSpec` dataclass. This is the single object
  that carries "everything we learned about the template": colors, fonts,
  cloneable shape XML (question pill, option circles, title banner), and
  the `is_defence` / `top_banner_reserved_emu` flags. It's built once per
  template and passed down into every formatter and emitter. See §5 for the
  defence-related fields in detail.
- `template_archive.py` — a small dataclass holding the template's raw zip
  parts (`parts`), how many slides it has, and which slide XML is being used
  as the "output shell" (the shell every output slide clones).

### 3.5 `app/dynamic_rendering/infrastructure/pptx/`
A `.pptx` file is really just a zip file full of XML. These two files are the
only place that touches the zip format directly:
- `archive_reader.py` — opens the template `.pptx`, reads every file inside
  the zip into memory (`parts: dict[str, bytes]`), and picks out the "output
  shell" slide (see `OUTPUT_TEMPLATE_SLIDE_INDEX` in `template_design.py` —
  currently the **second-to-last** slide of the template).
- `archive_writer.py` — takes the final in-memory zip parts and writes them
  back out as a real `.pptx` file on disk.

### 3.6 `app/dynamic_rendering/services/` — the pipeline itself
This is where almost all the logic lives. Read them roughly top-to-bottom in
the order the pipeline calls them:

| File | Job |
|---|---|
| `orchestrator.py` | Entry point `build_deck()`. Calls everything else in order: read template → build design spec → collect+classify input slides → assemble output → write to disk. |
| `design_spec/scanner.py` | Scans the template's reference slides for colors and cloneable shapes; applies `is_defence` passed in from the caller to set banner spacing (§5). |
| `design_spec/token_builder.py` | Turns the raw scanned dict into a proper `DesignSpec` object. |
| `design_spec/cache.py` | Reads/writes the `*.designspec.json` cache file next to a template so re-runs on the same template skip the XML scan. |
| `design_spec/service.py` | Public entry `get_design_spec(template_path)` — checks memory cache → disk cache → falls back to scanning. This is what `orchestrator.py` actually calls. |
| `input_collector.py` | Walks every slide of the **input** deck, detects its slide type, runs the matching formatter to reposition its shapes, then classifies each shape (heading / option / picture / table / body) into a plain dict the emitters understand. |
| `format_layout/` | Slide-type detection + one "formatter" per slide layout (see §3.7). |
| `classifiers/` | Shape-level recognizers: is this shape an MCQ option? A heading? A title banner? Used by `input_collector.py`. |
| `shape_emitters/` | Turn a classified item dict (`{"kind": "heading", ...}`) into actual XML shapes styled with the template colors, and inject them into the output slide. |
| `slide_builder.py` | Builds one output slide's XML by cloning the output shell and calling the right shape emitters for every classified item on that slide. |
| `output_assembler.py` | Loops over all input slides, calls `slide_builder` for each, and rebuilds `presentation.xml`, its rels, and `[Content_Types].xml` so the final zip is a valid `.pptx`. |
| `presentation_xml.py` | Builds/patches `ppt/presentation.xml` (slide list, slide size, notes size). |
| `content_types.py` | Updates `[Content_Types].xml` so every part in the new zip is registered correctly (PowerPoint refuses to open a `.pptx` with a broken content-types file). |
| `style_parser/theme.py` | Reads the template's `theme1.xml` to resolve scheme colors (`accent1`, `dk1`, `lt1`, ...) into real hex values. |
| `table_restyle.py` | Re-colors tables copied from the input using the template's table colors. |
| `text/` | Text-fitting helpers: shrink font size so long headings/body text/table text don't overflow their box. |
| `content_types.py`, `presentation_xml.py` | (see above) |

### 3.7 `format_layout/` in detail
This is the "which layout does this slide use, and how do I lay it out"
part of the app.

- `detection/slide_type_detector.py` — looks at what shapes exist on an
  **input** slide (has a picture? a table? an MCQ question pill? how many
  images?) and returns a `slide_type` string, e.g. `"qpill_qtext_mcq"`,
  `"title_body_single_image"`, `"table_only"`. This is pure detection, no
  drawing.
- `detection/*` (other files) — smaller helpers used during detection:
  finding MCQ option shapes, matching input option pills, finding title
  slide shapes, etc.
- `registry.py` — a dictionary mapping every `slide_type` string to its
  formatter function. `format_slide(slide, slide_type, prs, dspec)` looks up
  the formatter and calls it.
- `formatters/<slide_type>/` — one folder per slide type. Each folder has:
  - `constants.py` — the exact box positions/sizes for that layout (in EMU).
  - `shapes.py` — reads the actual shapes off the input slide.
  - `slide.py` — orchestrates: read shapes → compute new positions → move
    shapes in place on the input slide's XML.
  - `formatter.py` (some layouts) — extra shared logic for that layout
    family, e.g. MCQ variants.
- `shared/` — layout logic reused by more than one formatter: text-box
  sizing, image resizing, table utilities, MCQ option grid math, and
  **`qtext_shrink.py`** (new/untracked file — shrinks the question text font
  so long questions still fit inside the question pill; used by the
  `qpill_qtext_mcq` and `qpill_qtext_image_mcq` formatters, which is why
  `git status` shows those two `formatter.py` files as modified).
- `slide_signature.py` — reads a lightweight "signature" of an input slide
  (shape counts/types) before classification, used by the detector.

### 3.8 `app/dynamic_rendering/utils/xml/`
- `helpers.py` — small read-only XML helpers: get a shape's position/size
  (`off_ext`), get a shape's preset geometry (`prst_geom`, e.g. `roundRect`),
  get all text inside a shape (`text_of`), build a namespaced tag (`q`), etc.
- `shape_mutators.py` — write helpers: move/resize a shape, set its fill
  color, set its text, etc. Used by formatters and emitters to actually
  change XML in place.

---

## 4. Full pipeline, step by step

This is what happens inside `build_deck(input_path, template_path, output_path)`
in [`orchestrator.py`](app/dynamic_rendering/services/orchestrator.py):

1. **Read the template zip** — `read_template_archive()` opens the template
   `.pptx`, loads every internal file into memory, and picks the "output
   shell" slide (currently the second-to-last slide — see
   `OUTPUT_TEMPLATE_SLIDE_INDEX`). Every output slide will be a clone of this
   shell's background/layout.

2. **Build the design spec** — `get_design_spec()` scans two other reference
   slides in the template (the MCQ slide and the title slide — see
   `MCQ_DESIGN_SLIDE_INDEX` / `TITLE_DESIGN_SLIDE_INDEX`) to learn:
   - question pill color/shape, option circle colors/shapes
   - title banner shape + icon
   - table header/border/body colors
   - **defence banner spacing** when `is_defence=True` (§5)
   This also checks a cache file first so a template isn't re-scanned every
   single run (§6).

3. **Collect & classify input slides** — `collect_inputs()` opens the
   **input** deck with `python-pptx`, and for every slide:
   - detects the slide type (`detect_slide_type`)
   - runs the matching formatter to move/resize that slide's own shapes into
     the right positions for that layout (`format_slide`)
   - if `is_defence` is enabled and the slide type wasn't
     recognized, shifts every shape down so nothing overlaps the reserved
     top banner (`shift_shapes_down`)
   - classifies every remaining shape into a role: heading, option,
     picture, table, or plain body text

4. **Assemble the output** — `build_output()`:
   - copies every non-slide part of the template zip as-is (media, theme,
     master, layouts, etc.)
   - drops in the template's title-icon image if one was found
   - for every input slide, calls `slide_builder.build_slide()`, which
     clones the output shell XML and injects styled shapes for each
     classified item (via `shape_emitters/`)
   - rebuilds `presentation.xml`, its relationships file, and
     `[Content_Types].xml` so the slide count/order/size is correct

5. **Write to disk** — `write_archive()` zips all the in-memory parts back
   into a real `.pptx` file at `output_path`.

---

## 5. Defence vs. normal layout — how it works today

Some templates are a special **"defence" variant**: their master slide
reserves a banner area at the very top of every slide (for a logo/heading
bar), so all content on every generated slide has to be pushed down by a
fixed amount to avoid overlapping it. Normal templates don't reserve this
space.

**Defence mode is not auto-detected from the template file anymore.** The
caller sets it explicitly via `IS_DEFENCE` in `app/main.py` (dev) or
`is_defence=` on `build_deck()` / `get_design_spec()` (production/API).

### 5.1 Where the flag is set (dev)

File: [`app/main.py`](app/main.py)

```python
IS_DEFENCE = False  # True = defence layout; False = normal layout

run(..., is_defence=IS_DEFENCE)
```

That flows through:

1. `build_deck(..., is_defence=IS_DEFENCE)` in `orchestrator.py`
2. `get_design_spec(template_path, is_defence=IS_DEFENCE)` in `design_spec/service.py`
3. `scan_template(..., is_defence=IS_DEFENCE)` in `design_spec/scanner.py`

### 5.2 Where the banner height constant lives

File: [`app/dynamic_rendering/constants/shape_geometry.py`](app/dynamic_rendering/constants/shape_geometry.py):

```python
DEFENCE_BANNER_HEIGHT_EMU = 2_011_320   # how far down to push content (in EMU)
```

In `scanner.py`:

```python
top_banner_reserved_emu = DEFENCE_BANNER_HEIGHT_EMU if is_defence else 0
```

### 5.3 What happens once `is_defence` is known

1. The scan result sets `top_banner_reserved_emu` (banner height or `0`).
2. `is_defence` is stored in the cached `<template>.pptx.designspec.json`
   (see §6) and lands on the `DesignSpec` object as:
   - `dspec.top_banner_reserved_emu` — the raw number
   - `dspec.has_top_banner()` — convenience `True/False` accessor
   - `dspec.y_below_banner(y)` — shifts any Y coordinate down by the reserved
     amount (returns `y` unchanged for normal runs)
3. Every formatter and layout constant file that needs to be "defence-aware"
   calls `dspec.y_below_banner(y)` (or checks `dspec.has_top_banner()`)
   instead of hard-coding a Y position. Look for the word "defence" in:
   - `formatters/title_image_only/constants.py`
   - `formatters/title_table_only/constants.py`
   - `formatters/qpill_qtext_mcq/constants.py`
   - `formatters/qpill_qtext_table_mcq/constants.py` (this one also switches
     the MCQ options from a single column to a **2-column grid**, only for
     defence runs — because the defence banner eats vertical space)
   - `formatters/qpill_qtext_image_mcq/constants.py`
   - `formatters/qpill_qtext_single_image/constants.py`
   - `formatters/qpill_qtext_multiple_image/constants.py`
   - `formatters/title_body_multiple_images/constants.py`
   - `shared/mcq_option_layout.py`
   - `shared/title_heading_layout.py`
   - `input_collector.py` (shifts unrecognized slide types down as a
     fallback, see §4 step 3)

So `is_defence` is a **single flag that ripples through the whole layout
system** — nothing else needs to change if this flag flips.

### 5.4 How to test it locally

In `app/main.py`:

```python
IS_DEFENCE = True
template_path = data/templates/defence-red-final.pptx
```

vs normal:

```python
IS_DEFENCE = False
template_path = data/templates/red-final.pptx
```

Example cache files:

- `data/templates/defence-red-final.pptx.designspec.json` → `"is_defence": true`
- `data/templates/red-final.pptx.designspec.json` → `"is_defence": false`

---

## 6. The design-spec cache (`*.designspec.json`)

Scanning a template's XML on every run is wasted work if the template file
hasn't changed. So `design_spec/service.py` caches the *token* part of the
scan (colors, labels, `is_defence`) to a JSON file next to the template:

```
data/templates/red-final.pptx
data/templates/red-final.pptx.designspec.json   <-- cache
```

- The cache file stores an MD5 hash of the template file's bytes. If you
  re-run against the same template and the hash still matches, the cached
  tokens are reused instead of re-scanning.
- If the template file changes (even a single byte), the hash changes, the
  cache is treated as stale, and a fresh scan runs automatically.
- **Cloneable shape XML** (the actual pill/banner shapes to copy) and
  **images** (title icon bytes) are *never* cached — those are always
  re-read from the template file on every run, because caching raw XML
  elements/binary blobs in JSON isn't practical. Only small values (hex
  colors, labels, the `is_defence` boolean) go into the cache.
- If you ever need to force a fresh scan regardless of the cache, call
  `get_design_spec(template_path, force_refresh=True)`.
- If a design change is made to a template and the output still looks old,
  delete the matching `*.designspec.json` file (or bump the template's
  content) rather than editing the JSON by hand.

---

## 7. Passing `is_defence` from an API in production

The pipeline already accepts an explicit flag — no marker-slide scanning is
involved. Wire your API/database value through the same path as dev:

```python
build_deck(input_path, template_path, output_path, is_defence=is_defence_from_api)
```

Which calls:

```python
get_design_spec(template_path, is_defence=is_defence_from_api)
```

The in-memory cache key includes `:defence={is_defence}` so the same template
file with different flags does not share a stale cached `DesignSpec`.

**What you should NOT need to touch:** everything in §5.3 (formatters,
`input_collector.py`, etc.) reads `dspec.has_top_banner()` /
`dspec.y_below_banner()` — they don't care whether the flag came from
`app/main.py` or an API request.

---

## 8. Quick glossary

| Term | Meaning |
|---|---|
| EMU | English Metric Unit — PowerPoint's internal measurement unit. 914,400 EMU = 1 inch. |
| Design spec / `dspec` | The `DesignSpec` object holding everything learned from the template (colors, fonts, cloneable shapes, defence flag). |
| Output shell | The template slide (second-to-last, by default) whose background/layout every generated output slide clones. |
| Slide type | A string like `"qpill_qtext_mcq"` describing what kind of content an input slide has, used to pick a formatter. |
| Formatter | Code that repositions/resizes an input slide's own shapes to match a specific layout, before classification. |
| Emitter | Code that draws a *new*, template-styled shape into the output slide for a classified item (heading/option/picture/etc.). |
| `IS_DEFENCE` | Boolean flag in `app/main.py` (or API) that turns defence banner spacing on or off for a run (§5). |
