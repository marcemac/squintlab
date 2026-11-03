# Decisions

One entry per decision, oldest first. Each entry records what was decided, why, and what it costs. Entries are never deleted: a later entry that changes an earlier one says so, and the earlier one gets a "Superseded by" line.

Master copy: this Doc. To update the repo, export it as Markdown and replace DECISIONS.md.

## 2026-10-26: Equiluminance is defined on luminance

squintlab flags equiluminant neighbours by their difference in relative luminance Y, with the threshold expressed as ΔL\*, because L\* compresses Y roughly the way lightness perception does. It does not use a brightness model or CAM16 lightness J. Reason: *Vision and Art* attributes shimmer and spatial instability to the luminance pathway, and the magnocellular cells behind it reach their response minimum at the balance point of heterochromatic flicker photometry (Lee, Martin and Valberg, 1988). That balance point is luminance, not apparent brightness. Consequence: saturated colours that look lighter than their L\* (Helmholtz–Kohlrausch) get a separate, optional flag that never enters the equiluminance test. CAM16 stays available for appearance-oriented value reports. Thresholds remain parameters with literature defaults until calibrated in validation layer 3.

Superseded in part by 2026-10-28: Equiluminance threshold in luminance contrast (threshold unit only; the luminance definition stands).

## 2026-10-26: Cone-opponent channels: MacLeod–Boynton inside, CIELAB in reports

Mechanism analyses (equiluminance, colour-only edges, chromatic induction, M4 channel filtering) represent colour as luminance plus MacLeod–Boynton chromaticity, l = L/(L+M) and s = S/(L+M) (MacLeod and Boynton, 1979), with LMS from the Smith–Pokorny transform so that L+M equals CIE Y and stays consistent with the ΔY equiluminance definition. Applying that transform to CIE 1931 XYZ from sRGB input is an approximation, accepted to keep one luminance definition throughout; coefficients are checked against the source when M1 is coded. Reports describe hue in CIELAB a\*, b\*, because cone-opponent axes do not match perceived red–green and blue–yellow (Webster et al., 2000). Chromatic-adaptation matrices (CAT02, Bradford) are never used as cone signals: they give S cones weight in luminance, which the M1 property tests would catch.

## 2026-10-26: M5 scope for v0.1 includes countershading and simultaneous contrast

M5 adds a Cornsweet (countershading) edge-profile detector and each region's lightness and cone-opponent colour against its surround, alongside edge hardness, colour-only edges and local contrast. Induced shifts are reported as direction and measured difference, never as a predicted appearance, because induction-magnitude models disagree. Accepted cost: M5 grows from three measures to five; the synthetic Cornsweet, simultaneous-contrast and isoluminant-edge stimuli define done.

## 2026-10-26: Benchmark annotations are hand-drawn

Benchmark regions and profile lines are hand-drawn polygons and lines stored as data files beside each image's provenance record. Nothing detects figures or faces, keeping the project inside its no-recognition non-goal. Accepted cost: annotating a new benchmark takes manual work, and annotations carry the annotator's judgement, so each file records who drew it and when.

## 2026-10-26: Open stand-ins replace book examples that are not open

No painting discussed in chapters 1–6 of *Vision and Art* is released for open reuse by its holding museum, so the benchmark set uses open paintings that show the same effect. Reuse terms are checked for each image, not inferred from the artist's death date. Stand-ins so far: La Tour's *The Repentant Magdalene* (National Gallery of Art) for ter Brugghen's candle-lit lightness; Monet's *Wheatstacks, Snow Effect, Morning* (Getty, CC0, licence confirmed on getty.edu) for the MFA's *Grainstack (Snow Effect)*; and Renoir's *Lunch at the Restaurant Fournaise* (Art Institute of Chicago, CC0) with Monet's *Woman with a Parasol* (National Gallery of Art) for Renoir's *Young Woman in the Sun*. Remington's *Fired On* (Smithsonian American Art Museum) covers only the dim-light half of *The End of the Day* and waits for M12. Accepted cost: a stand-in tests the mechanism, not the book's exact observation, so benchmark reports name both the stand-in and the example it replaces.

## 2026-10-26: Backlog scope after chapters 1–6

v0.1 (M1–M6) is unchanged. M11 (v0.2) adds a colour-vision-deficiency view, a deterministic dichromat simulation on the LMS core (Brettel, Viénot and Mollon, 1997), and contour continuity built on M5's edge maps. M12 (v0.3) adds the dim-light and relighting views, which need reflectance estimated from RGB by analytic spectral recovery (Jakob and Hanika, 2019), never a data-trained method. M12 ships only if recovered spectra of measured paint swatches predict their luminance under CIE illuminant A and the scotopic function V′(λ) within a stated tolerance; without measured swatch spectra it stays out. The painted-cast measure joins M8, because a painted cast cannot be separated from camera white balance before grey-card normalisation. Tilt and afterimage effects stay out: neither gives a measurement on a still image. New milestones are appended with stable numbers rather than renumbering M7–M10, so references in issues and documents stay valid; each milestone's title states its target release.

## 2026-10-28: M4 is a contrast-threshold, per-channel viewing simulation

M4 filters each octave band of the luminance, L−M and S−(L+M) channels with a published contrast-threshold model, from stated fixation points and viewing distance, and mixes colour in linear light. A single cut-off is not enough, because what stays visible depends on contrast and channel, and colour resolves less finely than luminance (Mullen, 1985). M3 records each equiluminant pair's size in degrees, so sub-acuity equiluminant texture gets a blending card rather than a shimmer card. Colour-to-contour registration and edge-carried colour join M11, and a crowding view goes to the backlog. Done-when uses synthetic gratings, dot fields and a fixation sweep. The Mona Lisa stays a local run because the Louvre's terms keep its image out of the repo. Accepted cost: the threshold model and the gallery portrait must be chosen before M4 can close.

## 2026-10-28: castleCSF is M4's contrast-threshold model

M4 uses castleCSF (Ashraf et al., 2024) to decide which band-limited components stay visible from a fixation point. It is ported to Python from its MIT-licensed MATLAB code, with the notice kept. It is the one published analytic model found that covers luminance and both chromatic directions across eccentricity, luminance level and stimulus area. Its directions match squintlab's L−M and S−(L+M) channels. Geisler and Perry (1998) stays as an analytic cross-check for luminance; its constants (α 0.106, e₂ 2.3°, CT₀ 1/64) are verified as cited. The port is done when it reproduces the model's published error on its bundled data. Nothing is trained in squintlab: both models are closed-form formulas with published constants. Accepted cost: a porting task in M4, and two new config parameters, adaptation luminance and patch area per band, whose defaults are assumptions until validated.

## 2026-10-28: Luini replaces the Mona Lisa in M4's gallery

The Louvre allows free reuse only for listed non-commercial purposes, so the *Mona Lisa* cannot enter the repo or the docs gallery. M4's gallery instead renders Luini's *Portrait of a Lady* (National Gallery of Art, 1937.1.37, public domain per the NGA) from stated fixation points. It is a Leonardesque panel of the same height, and its shadowed, slightly upturned mouth corners suit the comparison. A person judges expression; nothing analyses the face. The *Mona Lisa* stays a documented local run on a user-supplied image. Accepted cost: the benchmark tests Livingstone's mechanism on a follower's painting, not on her own example.

## 2026-10-28: CC BY-SA benchmark images stay out for now

Benchmark images remain public domain or CC0 in the holding museum's open-access programme. The Neue Pinakothek's Degas, *Die Büglerin*, is CC BY-SA 4.0. That licence allows any use with attribution, but renderings and overlays made from it would have to carry the same licence, which would split the gallery's licensing. Renoir's *Madame Henriot* (NGA) already covers the same claim, so nothing is lost. Revisit this if a book example has no public-domain or CC0 substitute; such images would then sit in a separately licensed folder outside the PyPI package.

## 2026-10-28: Open stand-ins for chapters 7–8

Following the 26 October rule, book examples from chapters 7–8 that are not open get open substitutes, with terms checked per image:

- Manet's *The Rue Mosnier with Flags* (Getty, CC0) for Monet's *Rue Montorgueil*
- Seurat's *A Sunday on La Grande Jatte* (AIC, CC0) for *Le Cirque*
- Monet's *Venice, Palazzo Dario* (AIC, CC0) for the Kunsthaus *Palazzo Ducale*
- Signac's *Les Andelys, Côte d'Aval* (AIC, CC0) for both Met Signacs
- Cézanne's *Mont Sainte-Victoire Seen beyond the Wall of the Jas de Bouffan* (NGA) for *The Lime Kiln*
- Rodin's *Rear View of Female Figure in Action* (NGA) for Walkowitz's *Isadora Duncan #29*
- Luini's *Portrait of a Lady* (NGA) for the *Mona Lisa* in M4's gallery

Open book examples are used directly: Poussin's *The Abduction of the Sabine Women* (Met), Renoir's *Madame Henriot* and Ingres's *Mrs Charles Badham* (NGA), Ingres's *Portrait of Jean-Louis Robin* (AIC) and Cézanne's *The Card Player* (RISD). Accepted cost: the NGA Cézanne is more filled-in than the book's example, so its edge-carried colour is measured before it enters the benchmark.

## 2026-10-28: Detail and contrast maps never predict fixations

Cards built on M5's fine-scale contrast and detail maps report where that contrast peaks and never predict where viewers will look; they say that people and meaning usually draw the eye more, which squintlab deliberately does not model. Gaze tests in validation layer 3 include a centre-bias baseline (Tatler, 2007). Reason: in the check of the book's Yarbus figure, local contrast correlated only weakly with the density of eye-movement traces (Spearman 0.21) against 0.39 for a centre bias, and with salience controlled only meaning explained where people looked (Henderson and Hayes, 2017). Accepted cost: squintlab says less about gaze and composition than artists may expect, by design, because modelling meaning would need the recognition the project excludes. Approved with the chapter 7–8 changes on 28 October; entry added during the batch 4 check of this file.

## 2026-10-28: M3 benchmarks and region scale

M3 is validated on synthetic stimuli (an equiluminant disc ladder, a dot field, a pair equal in HSL lightness but 12 L\* apart, and small dabs) and on two open paintings: the poppies in Monet's *Poppy Field (Giverny)* (Art Institute of Chicago, CC0), flagged at the share measured on hand-drawn regions, and the sun in Monet's *Sunrise (Marine)* (Getty, public domain per its object page), measured at two scales. *Impression, Sunrise*, named in the original done-when, is not open (Musée Marmottan Monet) and becomes a documented local run with no image in the repo. Regions are sized in degrees below the stroke scale, with a segmentation-free count of equiluminant stroke pairs inside each region, because a prototype with 11-pixel superpixels averaged strokes away. Reason: the open-image hard limit, and measurement showing the Getty sun's strokes equiluminant with their glow (median ΔL\* −0.8) while the sun area sits about 5 L\* above the sky. Accepted cost: the Getty sun is a weaker case than the Marmottan one, and region sizing needs a viewing distance. Book examples that failed measurement on reproductions (the Railway Bridge water, the yellow in *Broadway Boogie Woogie*) stay out of the positive set.

## 2026-10-28: Where view cut-off and contrast response

The Where view low-pass filters lightness at the luminance cut-off divided by k (default 2.5), in pixels per degree from the colour core, and stays linear in contrast in v0.1. Reason: *Vision and Art* puts the Where system's acuity two to three times below the form system's, and parvocellular lesions cut acuity three- to fourfold while a magnocellular lesion leaves it unchanged (Merigan, Katz and Maunsell, 1991). A compressive curve for magnocellular contrast saturation (Kaplan and Shapley, 1986) would add a parameter the report cannot yet justify. The Where view stays separate from M4's viewing simulation, in which luminance is the finest of the three channels (approved with the chapter 7–8 changes on 28 October). Accepted cost: the view shows where luminance structure survives, not how strongly the pathway responds; k stays a parameter until calibrated.

## 2026-10-28: Equiluminance threshold in luminance contrast

Supersedes the threshold clause of "2026-10-26: Equiluminance is defined on luminance"; the luminance definition stands. The default threshold is Michelson luminance contrast, ΔY/(Y1+Y2), set at 5% until calibrated in validation layer 3; cards report ΔL\* alongside it. Reason: magnocellular contrast gain, flicker-photometry settings and observer variation are all expressed in luminance contrast, while a fixed ΔL\* corresponds to about 6% contrast at L\* 30 and 3.4% at L\* 70; Michelson is symmetric between neighbours, so no region has to be treated as background. Accepted cost: the threshold is less intuitive for artists than a value step, so the report always shows the ΔL\* equivalent, and very dark regions, where photo noise dominates small ΔY, are marked uncertain.

## 2026-10-28: Illusory motion from luminance patterns goes to the backlog

The chapter 10 motion effects that do not come from equiluminance go to the backlog as one optional descriptor of motion-prone luminance texture, outside v0.1: peripheral drift from ordered luminance steps (Kitaoka's *Rotating Snakes*, the water Livingstone describes in Monet's *La Grenouillère*), relative motion between orthogonal high-contrast line textures (Ōuchi), and streaming beside high-contrast line fields (the MacKay effect in Leviant's *Enigma* and Riley's *Fall*, the floes in Monet's *Les Glaçons*). Shimmer and positional instability from equiluminance stay with M3. Reason: each effect needs eye movements or time to appear, so a still image gives a description of the pattern, not a measurement of the effect, and the primary research behind them is still unverified. Their book examples are in copyright or not open, and no open stand-in was found for *La Grenouillère* or *Les Glaçons*, so synthetic stimuli will stand in when the descriptor is scheduled. Accepted cost: Op-art-like passages in a user's painting get no observation card in v0.1.

## 2026-10-29: The decision log lives in a Claude Doc

This Doc is the master copy of the decision log. The repo's DECISIONS.md is a Markdown export of it, refreshed at the end of each review batch, and the copy in Project files is retired. Reason: Project files reach Claude as read-only snapshots and the repo is out of reach from chat, so the log drifted: the Project copy stopped at 26 October, and the chapter 7–8 entries had to be rebuilt from chat history. Claude can edit this Doc directly, as it does the proposal and the concept map. Accepted cost: the repo copy is current only after an export, so each batch ends with one.

## 2026-10-29: Shape from shading is measured on luminance gradients, with colour's role reported

The "Luminance carries form and depth" basis now says that shape from shading is driven by luminance gradients, that colour alone gives no shape (Cavanagh and Leclerc, 1989), and that colour varying independently of luminance helps a gradient read as shading while colour aligned with it reads as a change of material (Kingdom, 2003); M5 extends its colour-only measure from edges to smooth gradients inside regions and reports whether colour and luminance gradients align, and M2's Where view must render a disc shaded only in colour as uniform. Why: the book's colour-blind-system account overstates the case, and shading lives in gradients that an edge map misses. Accepted cost: one more low-frequency measure and test in M5, and alignment is reported only as a descriptor, so no card can say how deep a region will look.

## 2026-10-29: M2 measures value range per hand-drawn region

M2 adds, for each hand-drawn region, the value range (5th–95th percentile L\*), the slope of saturation (C\*/L\*) against L\*, the spread of ranges across regions and the share of clipped pixels; in v0.1 regions come only from hand-drawn region files, with M3 segments as a later option. Why: these quantities separate modelling by value from modelling by adding white or black (on the book's figures the range spread runs from 3.6 for Daddi to 1.1 for the Doni), and hand-drawn files keep M2 independent of M3 and reuse the decided benchmark format. Accepted cost: the per-region analysis does not run on a bare image in v0.1, and the CLI gains a region-file input.

## 2026-10-29: M5 reports surround gradients and reversal pairs

Beside one-dimensional Cornsweet profiles, M5 reports background gradients along hand-drawn lines and reversal pairs, regions whose L\* order is the opposite of their order in contrast with their own surrounds, stated as the measured differences and the model's direction, never as a predicted appearance. Why: the book's countershading examples hold up in measurement (the Shapley disc is uniform on a graded ground; Rembrandt's head is darker than the window crosspiece yet sits above its surround), and this extends the M5 scope decided on 26 October. Accepted cost: results depend on the hand-drawn lines and the surround size, which must be stated on every card, and the feedback engine has more pairs to filter.

## 2026-10-29: M3's poppy criterion uses the share measured on the AIC file

M3's done-when now requires the poppies in Monet's Poppy Field (Giverny) to be flagged at the share measured on the Art Institute of Chicago file with hand-drawn regions: 62% of 314 marks within 5% Michelson contrast of the surrounding grass, ±5 percentage points, with marks of median 0.13° at 1.5 m getting shimmer cards. Why: the museum file replaces the book's print, and the share stays between 55% and 62% across colour thresholds. Accepted cost: the criterion depends on the region file and the mark colour threshold, which must be versioned with the test, and the tolerance is an assumption until calibrated.

Superseded on 31 October 2026 by "M3's poppy criterion re-measured on the AIC original".

## 2026-10-29: Benchmarks from chapters 11–12

The benchmark set adds Ingres's Princesse de Broglie (Met, Public Domain), Seurat's Aman-Jean (Met, Open Access, for The Black Knot), Monet's grey and sunlit Rouen Cathedral, West Façade (NGA, both Public Domain, for the Met Portal and the MFA Façade) and Branch of the Seine near Giverny (Mist) (AIC, CC0, for Vétheuil in the Fog), and a Bernardo Daddi panel at the Getty or the NGA for the Orsanmichele Madonna once its terms are confirmed. The Met's Rouen Portal offers no download, so it stays out like the Italian state and church works and the Hermitage, Louvre, Orsay, Marmottan, MFA, SFMOMA and Tate images; Lichtenstein's dots (13% Michelson) and the fog Monets' supposed lower luminance contrast stay out of the positive set. Why: terms checked per image, and claims enter the positive set only when measurement supports them. Accepted cost: the Rouen comparison uses two NGA canvases rather than the book's pair, and the Doni, the Rembrandt and the Fauve faces have no open stand-in, so those claims rest on synthetic stimuli.

## 2026-10-29: Light direction and haze go to the backlog; mirrored and upside-down views go to M9

Light-direction consistency (concept 63) and haze zones (concept 78, stimulus S18) go to the backlog, and mirrored and upside-down views become an M9 option. Why: light direction needs convexity and light-source assumptions an image cannot supply, haze needs depth zones ordered by the user, both would widen v0.1, and the flipped views are interaction aids that belong with the front end. Accepted cost: v0.1 says nothing about inconsistent lighting or atmospheric recession, and painters keep using their own mirror until M9.

## 2026-10-29: Open stand-ins for the Doni, the Rembrandt and the Fauve faces

Three substitutes join the benchmark set: Domenico Beccafumi's The Holy Family with Angels (NGA 1943.4.28, public domain) for Michelangelo's Doni Holy Family; Rembrandt's etching Saint Jerome in a Dark Chamber (NGA 1994.60.52, public domain) for the Meditating Philosopher; and Van Gogh's 1887 Self-Portrait (Art Institute of Chicago 1954.326, flagged public domain in the AIC collection record) for Matisse's and Derain's faces. Why: none of the book's examples is open, and each substitute carries the quantity its claim needs (per-region value range and saturation slope, surround gradients and reversal pairs, hue against L\*). Accepted cost: none is the book's own example. The Beccafumi is Mannerist rather than Michelangelo and enters the positive set only if its lights measure desaturated. The etching tests luminance alone, within the narrow range of ink on paper. The Van Gogh is proto-Fauve, not Fauve.

## 2026-10-29: Open stand-ins for the Benois Madonna, gold edging and haze

Three more substitutes join the benchmark set, all marked free and in the public domain on their NGA object pages: Raphael's The Small Cowper Madonna (NGA 1942.9.57) for Leonardo's Benois Madonna (a common value range across colours); the Byzantine Enthroned Madonna and Child (NGA 1949.7.1) for the Pasquale mosaic and the Cimabue (gold edging carrying the folds of a dark robe); and Leonardo's Ginevra de' Benci (NGA 1967.6.1.a) for the Virgin of the Rocks (haze in a distant landscape). Why: the book's examples are not open (Hermitage, Italian state and church works, Louvre), and each substitute carries the quantity its claim needs. Accepted cost: the Raphael is Leonardesque, not Leonardo; gilding photographs unreliably, so the Byzantine panel must show its gold lines clear of the fabric in L\* on download; and the Ginevra serves only a Backlog item (haze zones), so it stays out of the v0.1 validation plan.

## 2026-10-30: The horizontal-periodicity measure goes to the backlog

A horizontal-periodicity measure for misfusion risk (the autocorrelation peak of high-pass lightness, with a local period map; concepts 89–90, stimuli S21 and S23) goes to the backlog as a possible new module, not into v0.1. Why: every painting measured from chapter 13 is aperiodic (r ≤ 0.03, the same as a random field), so in practice it would flag only op art, textiles and wallpaper patterns, and the book's claim that semiregular dabs give a sense of "air" is untested and unsupported by the measurements. Accepted cost: v0.1 says nothing about wallpaper-type misfusion, even in strongly repetitive work where it is real, and S21 and S23 stay unused until the module is scheduled.

## 2026-10-30: The dab-field descriptor goes to the backlog with the crowding view

The dab-field descriptor (dab size and nearest-neighbour spacing in degrees, spacing regularity; concept 90, stimulus S22) goes to the backlog, to be built together with the crowding view rather than added to M4 in v0.1. Why: the only perceptual consequence the book offers, a sense of "air" from false stereo matches, is unsupported by measurement; dab size is already covered by M4's mark-scale regime and gaps between dabs by the blending filter; and the one supported consequence of spacing, crowding when spacing falls below the critical spacing at a given eccentricity (Bouma; Pelli & Tillman), belongs with the crowding view. Detecting dabs reliably where they overlap or sit in impasto is also untested, and adding it would enlarge M4. Accepted cost: v0.1 reports no dab spacing or regularity, and S22 stays unused until the crowding view is scheduled.

## 2026-10-30: Stereo, motion parallax and paint relief are out of scope

A new non-goal excludes stereo, motion-parallax and paint-relief analysis, and chapter 13's viewing advice (one eye, a distance) goes to the docs. Why: a single photograph of a flat painting carries no disparity and no relief height, and a 1 mm impasto step gives only about 13″ of disparity at 1 m, near or below stereo threshold. Accepted cost: squintlab says nothing about how a canvas's flatness or real relief interacts with its painted depth, which the book treats as a central tension in chapter 13.

## 2026-10-30: The face non-goal is widened to face-specific measures

The non-goal now excludes face or person detection and recognition, any inference of identity or expression, and any face-specific measure (caricature, distinctiveness, inversion), even on hand-drawn regions; photographs of real people are never benchmarks, and M9's upside-down view is described as a value-and-shape check, not a face test. Why: chapter 15's mechanisms (face patches, norm-based coding, caricature, the inversion effect) only become measurable through face landmarks, which is face analysis under hard limit 2, and the proposal and Alignerr row should say so plainly. Accepted cost: portrait painters get no feedback specific to faces; faces are treated like any other region.

## 2026-10-30: Raking-light warning in M8

M8's capture guide asks for diffuse light from both sides at about 45° (or cross-polarised light), and the capture assistant warns when fine luminance gradients concentrate in one orientation, a sign of raking light; its done-when adds a synthetic relief rendered under raking and diffuse light (S25). Why: under raking light, impasto turns into cast shadows and highlights that M3–M5 would read as painted marks. Accepted cost: one more capture check that can misfire on paintings whose brushwork is itself strongly oriented, and no relief layer until a second raking-light photo is scheduled.

## 2026-10-30: No stereo-flatness card; two-pathway wording kept

No card is added for the book's hypothesis that low-detail paintings conflict less with stereo flatness: M4's per-band contrast already gives a fine-band summary, and the docs note that brushwork texture gives stereo something to match. The model-of-effects wording stays as it is, although the book gives fine stereo to the Where system; parvocellular lesions impair fine stereopsis and magnocellular lesions do not (Schiller, Logothetis & Charles 1990). Why: the measured Monet figure has more fine texture relative to its coarse structure than the stereo photograph, and stereo thresholds depend little on contrast once contrast is clearly visible (Legge & Gu 1989, as cited), so the hypothesis gives no reliable perceptual consequence to report. Accepted cost: an idea artists may find appealing appears only in the docs.

## 2026-10-30: Validation plan records the batch 6 benchmark results

The validation plan records the carry-over measurements: Beccafumi's pink lights are whitened while its red keeps chroma over a narrow dark range; the NGA Rouen pair's grey canvas has more luminance contrast than the sunlit one, so the roles are reversed; the Getty Daddi cloak spans 11 L\*, narrower than every coloured robe. Chapter 13's "air" from semiregular dabs and depth from paint relief stay out of the positive set, and Monet's Chrysanthemums is not added because the Met offers no download. Why: benchmarks should state what was measured, including results that run against the book's examples. Accepted cost: the Rouen pair now tests a weaker, reversed claim, and chapter 13 adds no new positive benchmark.

## 2026-10-30: One Where-view scale for figure checks

Figure checks use one Where-view scale: geometry from the canvas height given by the holding museum (or the book's credit when the museum gives none) viewed from 1.5 m, pixels per degree taken from the file after a 2% border crop, and a Gaussian low-pass on L\* (and on a\*, b\* for chromatic measures) with its half-amplitude point at 12 cycles per degree, which is the Where view's rule (luminance cut-off ÷ 2.5) applied to an assumed 30 cpd luminance cut-off until M4's castleCSF port supplies one; σ in degrees is 0.1874 ÷ 12. When a file cannot carry that scale (pixels per degree ÷ 4 below 12), the cut-off drops to pixels per degree ÷ 4 and the result is marked resolution-limited; two images are compared at the lower of their two cut-offs. The checks report low-pass L\* SD, Y RMS contrast, chromatic SD (square root of var a\* + var b\*) and the chromatic-to-luminance ratio. Why: batch 5 filtered at 1.2% of image width (about 0.6 cpd for the Rouens at 1.5 m) and batch 6 at 12 cpd, so their numbers could not be compared, and a scale tied to degrees follows the rule the tool itself will use. Accepted cost: book figures are almost always resolution-limited, so their numbers compare only with each other at a shared cut-off, and batch 5's recorded figure numbers stay at their own scale, because those figures are not available to re-measure.

## 2026-10-30 — Input provenance and chroma subsampling

The input loader records each file's format, pixel size, chroma subsampling, estimated JPEG quality, embedded profile and SHA-256 in the report and export, and warns when 4:2:0 subsampling meets marks or regions within two chroma samples (about 4 px). This is a small change to M1, whose done-when adds synthetic edges saved as 4:4:4 and 4:2:0 (S26). M3's pair statistics exclude a band one chroma sample wide along region borders, and M5 reports colour-edge hardness only at scales of at least two chroma samples. M8's capture guide asks for RAW, TIFF, PNG or a high-quality 4:4:4 JPEG, and HEIC and Display P3 photos are read through their profile. Why: in batch 7, sharp painted colour edges in the museum files were 2–3 times wider than luminance edges. On a synthetic sharp edge between equal-luminance red and green, 4:2:0 shifted true luminance by up to 25% at the boundary, because JPEG computes its brightness channel on gamma-encoded values; the files measured in batches 5–7 also look re-encoded on upload. Accepted cost: the border band discards pixels from small regions (about 40% of a 9-px mark under 4:2:0), colour-edge detail finer than 4 px goes unreported, and phone JPEGs, nearly always 4:2:0, carry a warning on small marks.

## 2026-10-30 — Benchmark provenance and M3's done-when

M3's done-when keeps the poppy share at 62% of 314 marks within 5% Michelson contrast (±5 points), tied to a named file recorded with its source URL, pixel size, chroma subsampling and checksum, and to the hand-drawn region file. It also adds an equiluminant dot field saved as 4:4:4 and 4:2:0 that must return its analytic share within ±2 points for dots of 8 px or more (S27). The Validation plan records the same provenance for every benchmark file, re-runs each benchmark on a half-size copy passed through 4:2:0 as a worst case, and keeps chapter 16's colour-field fading and chapter 17's Rembrandt self-portrait claim out of the positive set. Why: in batch 7 a second 4:2:0 pass moved the poppy share by under 1 point at the file's scale and by up to 4.4 points at half scale, while a different set of regions moved it by about 6 points, so the number means nothing without its file and regions. Accepted cost: the 62% was measured on a copy that may have been re-encoded on upload; if the original download differs, the figure must be re-measured and this entry superseded.

Superseded in part on 31 October 2026 by "M3's poppy criterion re-measured on the AIC original": the 62% value is retired; the provenance rule and the worst-case run stand.

## 2026-10-30 — Blending cards name the merging channel

M4 uses castleCSF's separate L−M and S−(L+M) cut-offs, and a blending card names the channel that merges, for example a blue–yellow texture that merges while its red–green contrast is still resolved. A triad mosaic of display primaries joins M4's done-when (S30). Why: chapter 16 rests colour TV's coding on lower colour acuity, lowest for blue. S cones are 7% of cones and absent from the central fovea (Curcio et al. 1991, not the book's 1%), and castleCSF models the channels separately. Accepted cost: the cards depend on castleCSF's S-cone cut-off, which has less data behind it than the luminance and L−M ones, and the cards get longer.

## 2026-10-30 — Display assumption

Overlays and renderings are clipped to sRGB for display only, while every analysis runs on the source colorimetry from the file's embedded profile. M9's live screen-capture overlay reads the display's profile and treats captures as display colours, not the painting's. Why: three real primaries cannot show every colour (chapter 16 implies they can), so a screen rendering is not the measurement, and a screen capture shows a reference through a display. Accepted cost: on an sRGB screen some reported colours will not look like their numbers, and captures from uncalibrated screens stay approximate.

## 2026-10-30 — No inferences about artists or viewers

A new non-goal: squintlab makes no inference about artists or viewers (dyslexia, stereoblindness, strabismus, synaesthesia, colour-vision type) from images, self-portraits or use, and M11's colour-deficiency view simulates an observer without ever testing the user. The Alignerr eligibility table repeats it. Why: chapter 17 reads strabismus from photographs and self-portraits and links dyslexia and stereoblindness to artistic talent; any such output would be face analysis and a health inference about real people, against hard limit 2 and the personal-data rule. Accepted cost: chapter 17 contributes documentation only, and squintlab cannot tailor feedback to a user's own vision even when asked.

## 2026-10-30 — Saccadic suppression in the model of effects

The Scientific basis keeps the model-of-effects wording and cites Burr, Morrone and Ross (1994): during saccades, sensitivity to coarse luminance contrast drops while equiluminant contrast is spared, consistent with the magnocellular part of the model. Squintlab says nothing about dyslexia. Why: chapter 16 assigns eye-movement effects, and chapter 17 dyslexia, to the Where system; the saccade finding supports the model as a description of effects, while the magnocellular theory of dyslexia rests on five post-mortem brains and later work points the other way (Olulade, Napoliello and Eden 2013). Accepted cost: one more citation to maintain; the two-pathway risks row stays as worded.

## 2026-10-30 — Fading-prone boundary descriptor to the backlog

A fading-prone boundary descriptor goes to the backlog as a possible new module: per boundary, blur width in degrees, luminance contrast and eccentricity from stated fixation points, with a docs card on Troxler fading and never a predicted fading time. S28 and S29 are its synthetic tests, and the AIC Branch of the Seine (Mist), already in the benchmark set, can be its open test image. Why: chapter 16's Troxler ring and colour-field figures are low in contrast and heavily blurred, which primary work links to fading (Martinez-Conde, Macknik and Hubel 2004; Martinez-Conde et al. 2006), but fading time depends on the viewer's fixation and microsaccades, which a still image cannot supply. Accepted cost: v0.1 has no fading card; M3 and M5 already report the contrast and the blur, but nothing combines them yet.

## 2026-10-31 — No Commons copy for Ice Floes

The Met's Ice Floes (1893, 29.100.108) is not used, although a Wikimedia Commons copy records the Met's earlier CC0 release. The Shelburne canvas the book discusses is not open either, so no ice-floe painting enters the benchmark set, and synthetic stimuli stand in for rows 58 and 60 when those backlog items are scheduled. Why: the rule is that an image must be open at its holding museum, checked per image, and a reviewer checking the Met page today finds no download, even though a CC0 dedication cannot be revoked. Accepted cost: no real painting tests the arrangement of horizontal luminance borders against vertical colour streams; the batch 4 in-chat measurements of the Met canvas stay in the concept map as notes only.

## 2026-10-31 — M3's poppy criterion re-measured on the AIC original

M3's done-when now uses the AIC's original download of Monet's Poppy Field (Giverny): 3000 × 1948 px, JPEG quality about 95, 4:2:0, no embedded profile, SHA-256 beginning 32adf0f2bd984c98. On that file, 463 marks are found, 53% of them within 5% Michelson contrast of the surrounding grass (±5 points), with a median mark of 0.11° at 1.5 m, so shimmer cards still apply. The batch 5 regions, colour threshold and grass ring are kept and scaled to the same physical size (boxes × 1.165, a 7-px ring, marks of 16 px or more). Why: the batch 5 code reproduces 314 marks and 62% on the 2576-px upload copy but gives 53% on the original, outside the ±5 tolerance. Downscaling the original without recompression also gives 53%, while recompressing at quality 85 with 4:2:0 gives 60% and drops about a quarter of the small marks, so the shift comes from the copy's re-encoding, not from resolution. Accepted cost: the criterion is tied to one file and its scaled regions; the share still moves between 50% and 56% across colour thresholds 12–18; and the 62% value is retired.

## 2026-10-31 — Measured notes for four benchmark stand-ins

The Validation plan carries short measured notes for four stand-ins checked on the museums' downloads. Renoir's Lunch at the Restaurant Fournaise (AIC): the whites carry cyan-green to blue tints, and green appears on shaded skin. Seurat's Aman-Jean (Met): the halo holds along the upper contour only, and the drawing stays in the positive set with that note. Raphael's The Small Cowper Madonna (NGA): the red, blue and green robes share an L\* band of about 15–41. The NGA's Byzantine Enthroned Madonna and Child: the gold lines sit 36 L\* above the blue, which itself spans under 7 L\*. Why: claims enter or stay in the positive set when measurement supports them, and a partial result is kept when the supported part is stated. Accepted cost: Aman-Jean's test must check the halo on the upper contour only, and the gold-line value depends on how the gilding was lit when photographed.

## 2026-10-31 — CI on Linux, macOS and Windows from M0

GitHub Actions runs the tests, ruff and mypy on Linux, macOS and Windows for Python 3.11–3.13 from M0-T02 onward. Why: artists use all three systems, and platform bugs (file paths, line endings, differences between Pillow builds) are cheapest to catch from the first commit. Accepted cost: each push runs nine jobs, so CI is slower, and some sessions will go to Windows-only fixes.

## 2026-10-31 — Benchmark cache path set per machine

The fetch script stores benchmark images in a cache whose path each machine sets (an environment variable or a config file), falling back to a suggested per-OS default folder when none is set; the images are never committed. Why: machines differ in operating system and storage layout, such as secondary or external drives, while less technical users need it to work with no setup. Accepted cost: one more setting to document and test, and a default folder that can fill a small system drive unless redirected.

## 2026-10-31 — HEIC photos through an optional extra

HEIC support comes through pillow-heif as an optional extra, squintlab\[heic\], in M1-T01; the base install reads JPEG, PNG and TIFF. Why: many artists photograph their work on phones that save HEIC with Display P3 profiles, which the colour core must honour, while the base install stays small. Accepted cost: one more dependency to test on three systems, and the licences of the codecs it bundles must be checked before the extra ships.

## 2026-11-02 — Early 0.0.1 release to hold the PyPI name

After M0-T05, a new task M0-T06 publishes squintlab 0.0.1, the real pre-alpha package with its benchmark fetch tool, to PyPI through trusted publishing, rehearsed first on TestPyPI. The Alignerr application then points to a released project, and v0.1's release (M6-T06) reuses the same workflow. Why: a pending trusted publisher does not reserve a name, since PyPI holds a name only once something is published, and a released package shows Alignerr a project already in development. Accepted cost: one more unpaid session before applying; a 0.0.1 with no analyses, whose README must say so; PyPI's name policy (PEP 541) discourages empty placeholders, so real releases must follow; and PyPI never accepts the same version twice, so mistakes cost a version number.

## 2026-11-02 — Benchmark images from hosts that block scripts are imported by hand

Each manifest entry has an access field, "script" or "manual". Manual entries are downloaded in a browser from the museum's object page and brought into the cache with the fetch tool's --import, which checks the SHA-256 and size against the manifest and refuses a mismatch. The tool never impersonates a browser or tries to get past a bot check; it sends an honest User-Agent and the museum's courtesy header. Benchmark tests that need images run on the developer's machine from the cache and are skipped in CI, which runs the synthetic tests; the benchmark gallery is built locally too. Why: AIC's image server answered scripted requests with a Cloudflare challenge (HTTP 403) until its courtesy header, AIC-User-Agent, was added, and the block may return, perhaps more readily from CI's shared servers (an assumption, untested); other museum hosts may block scripts too; M3's poppy criterion is tied to the exact AIC file, so a mirror would mean re-measuring; and evading bot detection is off limits. Accepted cost: CI no longer proves the benchmark results, so they must be run locally before each release; adding a manual image takes a browser step; the checksum still catches any change to the file.

## 2026-11-02 — Local-only processing, stated in the README and enforced by a test

The README states that squintlab runs entirely on the user's computer: it never uploads, collects or shares images, results or anything about the user, has no accounts or telemetry, and makes no network connection while analysing, so nothing analysed can be used to train AI models. The proposal's non-goal says the same, and M6-T04 adds an end-to-end run with network access blocked. The only network use is the optional fetch of public-domain benchmark images. Why: artists need to know their work stays private, and keeping analysis local makes that true by design rather than by policy. Accepted cost: telemetry, update checks, crash reports and any cloud feature are ruled out, however convenient, and the benchmark fetch must stay separate from analysis.
