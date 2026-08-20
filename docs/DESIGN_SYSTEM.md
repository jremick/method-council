# Method Council design system

Version: 0.1.0

Status: public-alpha foundation

## Design thesis

Method Council should feel like a contemporary methodology workbench: calm,
precise, inspectable, and built for revision. It should not resemble a chamber of
personalities, a classified-government interface, or a futuristic control room.

The visual posture is **quiet proof, visible judgment**. The work and its limits
take priority over decoration.

## Experience principles

1. **Show the work path.** Make scope, method selection, separate passes,
   challenge, synthesis, and checkpoint visible.
2. **Lead with the result.** Reports begin with the decision-relevant output,
   then expose evidence and analytical seams.
3. **Make uncertainty legible.** Unknowns, dissent, invalid output, and partial
   validation remain visible in words and symbols—not color alone.
4. **Use architectural structure.** Datums, tracing overlays, ruled sections,
   registration marks, and revision blocks are functional metaphors.
5. **Avoid authority theatre.** Do not use seals, crests, classification marks,
   faces, council chambers, or institutional branding.

## Palette

| Token | Value | Role |
| --- | --- | --- |
| Paper | `#F7F8F6` | Primary field |
| Surface | `#FFFFFF` | Rare raised or writing surface |
| Paper Muted | `#E8EDF0` | Neutral wash and inactive regions |
| Ink | `#11131A` | Primary text and structure |
| Ink Muted | `#536070` | Metadata and secondary labels |
| Clay | `#A9563D` | Small datum or revision accent |
| Deep Clay | `#843820` | Accessible text link and focus emphasis |
| Steel | `#2C4258` | Neutral method paths and boundaries |
| Line | `rgba(17, 19, 26, 0.14)` | Dividers and construction lines |

Clay is an accent, not a theme. Large surfaces stay Paper or Surface. Avoid
neon, purple-blue AI palettes, sepia, glossy gradients, and heavy shadow.

## Typography

- **Editorial/display:** Source Serif 4.
- **Interface/body:** Sora.
- **Metadata and identifiers:** JetBrains Mono.

Repository SVGs use system fallbacks and do not embed or vendor font files. Text
must remain readable if the preferred fonts are unavailable. Mono is reserved for
stage numbers, versions, IDs, and compact technical metadata.

## Composition

- Prefer ruled rows and simple columns to grids of equal cards.
- Keep reading copy near 65 characters per line.
- Establish hierarchy through weight, spacing, and rules before scale.
- Use one clay revision point per composition where possible.
- Leave enough paper field around dense evidence to make scanning calm.
- Diagrams should remain meaningful in grayscale and at narrow widths.

## Method Datum mark

The mark represents three separate method paths passing through explicit frames
and meeting at one shared review datum. The open corner denotes revision: the
result is inspectable and not sealed by consensus.

It does not represent seats, people, a voting ring, a brain, or a government
emblem. It must remain legible at 24 px, work in one color, and never rely on
animation.

Files:

- `assets/source/method-datum-mark.svg` — editable source with construction metadata.
- `assets/exported/method-datum-mark.svg` — README/public-surface asset.

## Diagram language

Diagrams use:

- Steel for neutral paths and method boundaries.
- Ink for labels and primary structure.
- Clay for the active datum, challenge, or decision checkpoint.
- Dashed rules only for proposed, unknown, or unverified relationships.
- Explicit words such as `INCOMPLETE`, `CORRELATED`, or `CHECKPOINT`; color never
  carries state by itself.

Every standalone SVG includes a `<title>` and `<desc>` linked through
`aria-labelledby`. Markdown that embeds an SVG must also include useful alt text
because not every renderer exposes internal SVG accessibility metadata.

## Initial asset register

| Asset | Purpose | Status |
| --- | --- | --- |
| Method Datum mark | Project identity | Original code-native SVG |
| Method Council workflow | Explain the six-stage path | Original code-native SVG |
| Traceable report cutaway | Explain the report contract | Original code-native SVG |
| Council in practice | Show source material feeding separate methods that converge on one recommendation and checkpoint | Original code-native SVG |
| Complex council in practice | Show a nuanced problem using varied source material and six complementary checks | Original code-native SVG |
| Analysis Bench hero | Editorial atmosphere for the public surface | Generated bitmap committed; representative concept art only |
| Social preview PNG | Future GitHub sharing surface | Original SVG and 1280 × 640 PNG committed; GitHub upload not applied |

The diagrams and hero are explanatory artifacts, not screenshots of a shipped
interface. The social-preview PNG is a prepared repository asset; committing it
does not apply GitHub's custom social-preview setting.

## Bitmap direction and review

The committed hero shows a top-down contemporary architecture analysis desk:
paper plans, tracing overlays, a metal scale, binder clips, and one restrained
clay registration mark. It contains no intentional people, screens, readable
text, government insignia, or sci-fi interface elements. Essential labels remain
outside the generated image.

The generation host exposed the image-generation capability but did not expose
a reliable model identifier, so the provenance records the model state as
unknown rather than inferring a product or version name. Visual inspection at
native size found the intended paper, steel, ink, and clay composition; no
obvious private data, logos, readable text, people, screens, or watermarks were
observed. The 1280 × 640 social preview was also inspected for legibility and
private-data absence. This is observational review, not proof of accessibility,
usability, originality against all existing works, or GitHub rendering quality.

## Accessibility and review

- Use Deep Clay rather than Clay for text links.
- Keep body text at least 16 px in rendered interfaces.
- Provide a visible 2 px focus outline with offset for interactive elements.
- Do not place text on a busy bitmap.
- Do not communicate status by color alone.
- Use ordered headings and semantic lists around diagrams.
- Check diagrams at approximately 390 px and 1440 px widths.
- Check grayscale legibility, long-label wrapping, and horizontal overflow.
- Respect reduced motion; no motion is required for the core identity.

Visual review is observational evidence, not proof of accessibility conformance
or usability. Those claims require separate testing with rendered surfaces and
representative users or assistive technology.

## Asset provenance and export

The files in `assets/source/` are canonical editable SVG sources. Files in
`assets/exported/` are durable public-surface exports derived from those sources.
The social preview remains inspectable as SVG source; the generated hero is a
bitmap with its prompt summary, model-state limit, digest, and review notes
recorded in `assets/PROVENANCE.md`.

Before release:

1. Validate every SVG as XML.
2. Render at target sizes and inspect visually.
3. Confirm exported content matches its source.
4. Confirm Markdown alt text and internal SVG descriptions are present.
5. Confirm generated or third-party assets have current provenance and claim
   limits.
6. After any GitHub upload, read back the live custom social-preview state.
