# Question Slide Structure Explanation

## The 3 Shapes on a Question Slide (p5.pptx Slide 0)

### Visual Layout (Top to Bottom)

```
┌─────────────────────────────────────────────────────────────────┐
│                     Slide Canvas (40" × 22.5")                  │
│                                                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Shape 1: QUESTION PILL (roundRect)                        │  │
│  │ Position: (-2.039", 0.746") — extends LEFT of slide      │  │
│  │ Size: 7.745" × 1.717"                                     │  │
│  │ Color: Gradient fill (green)                              │  │
│  │ ┌─────────────────────────────────────────┐               │  │
│  │ │ Shape 2: QUESTION LABEL (TEXT inside)   │               │  │
│  │ │ Position: (1.137", 0.904")              │               │  │
│  │ │ Text: "Question"                        │               │  │
│  │ │ Size: 4.989" × 1.111"                   │               │  │
│  │ └─────────────────────────────────────────┘               │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                   │
│  Shape 0: QUESTION BODY TEXT                                    │
│  Position: (1.208", 2.621") — starts BELOW the pill            │
│  Text: "Let . Find the following cofactors of A."              │
│  Size: 38.0" × 3.8" (full width for multi-line text)           │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ Let . Find the following cofactors of A.                │    │
│  │                                                          │    │
│  │ (Room for more lines if question is longer)            │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Understanding the Shape Order

### Why is Shape 0 the Body Text?

PowerPoint saves shapes in the order they appear in the XML structure, not necessarily in visual order (top-to-bottom). The order depends on:
1. When each shape was created/added to the slide
2. Layer order in PowerPoint (back-to-front)
3. The slide's internal shape collection

### In p5.pptx Slide 0:

| Shape Index | Name | Type | Visual Position | Content |
|-------------|------|------|-----------------|---------|
| **0** | Google Shape;129 | TEXT_BOX | Bottom (below pill) | "Let . Find the cofactors of A." |
| **1** | Google Shape;131 | AUTO_SHAPE (roundRect) | Top (pill) | Empty (visual only) |
| **2** | Google Shape;132 | TEXT_BOX | Top (inside pill) | "Question" |

The body text (Shape 0) is listed FIRST in the XML, even though it appears VISUALLY below the pill.

---

## What We Format

### Current Implementation (Question Pill Formatter)

We format and position **TWO shapes**:

1. **Shape 1 (Question Pill)**
   - Clone it
   - Position at fixed: (-2.039", 0.746")
   - Size to fixed: (7.745", 1.717")

2. **Shape 2 (Question Label)**
   - Clone it
   - Position at fixed: (1.137", 0.904") [inside pill bounds]
   - Keep text: "Question"

**Result:** Pill + label text visible at the top of the slide ✓

---

## Future: Question Body Formatter

Later, we'll add a **separate formatter** for Shape 0:

1. **Shape 0 (Question Body Text)**
   - Clone it
   - Position at fixed: (1.208", 2.621") [below the pill]
   - Size to fixed: (38.0" × 3.8")
   - Enable text wrapping for multi-line questions

**Result:** Question body text visible below the pill ✓

---

## Summary

The question slide has 3 independent shapes working together:

```
SHAPE 1 (Pill)     ← Visual rounded rectangle
  └─ SHAPE 2       ← Label text "Question" (positioned inside pill)

SHAPE 0 (Body)     ← Question content (positioned below pill)
```

Each shape is:
- **Independent** (separate XML elements)
- **Repositionable** (can move to fixed layout)
- **Cloneable** (can copy and reuse)

The formatter currently handles **Shapes 1 + 2** (pill + label).
The body text **Shape 0** is separate and will be handled by a different formatter later.
