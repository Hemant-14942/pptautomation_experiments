run.py
  └─→ build_deck(input, template, output) [builder.py:1112]
        ├─→ _read_template_archive() → template ke raw parts
        ├─→ parse_template()                    → har slide ka design info
        ├─→ parse_input_slide_signature()       → input slides ka fingerprint
        ├─→ get_design_spec()                   → colors, logo, pills (cached)
        ├─→ _collect_inputs()                   → input ka actual content
        ├─→ _ask_azure_for_plan()               → AI se match karwao
        ├─→ _build_output()                     → sab merge karo, restyle karo
        └─→ ZIP mein pack karke save → final .pptx file


2
run.py
  └─→ build_deck()  [builder.py]
 ├─→ _read_template_archive() → raw ZIP parts
        ├─→ parse_template()  [style_parser.py]
        │     ├─→ _extract_theme() → theme font/colors
        │     └─→ per slide: bg + shapes → SlideDesign list
        ├─→ parse_input_slide_signature()  [style_parser.py]
        │     └─→ per slide: lightweight fingerprint
        ├─→ get_design_spec()  [design_spec.py]
        ├─→ _collect_inputs()  [builder.py]
        ├─→ _ask_azure_for_plan()  [builder.py]
        ├─→ _build_output()  [builder.py]
        └─→ ZIP pack → final .pptx

3
build_deck()
 ├─→ _read_template_archive()         [ZIP parts]
 ├─→ parse_template()                  [SlideDesign list, style_parser]
 ├─→ parse_input_slide_signature()     [lightweight fingerprints, style_parser]
 ├─→ get_design_spec() ← AI HERE │     ├─→ _scan_template() [raw XML fragments + heuristic colors]
 │     ├─→ disk cache check (.designspec.json)
 │     ├─→ if miss → _ask_azure_for_tokens()  [Azure AI,1 call]
 │     └─→ build & cache DesignSpec object
 ├─→ _collect_inputs()                 [next step]
 ├─→ _ask_azure_for_plan()             [AI again, but for slide matching]
 ├─→ _build_output()                   [merge + restyle]
 └─→ ZIP pack

 4
 Step 1: Python (backend)
    Input PPTX → [build_deck + JSX export] → PPTX + JSX files

Step 2: User browser mein:
    React app open kare
    Slide preview dikhe (components.jsx se rendered)
    User text edit kare directly
    
Step 3: Download again:
    Edited JSX → [compile back] → New PPTX