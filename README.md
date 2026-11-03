# squintlab

[![CI](https://github.com/marcemac/squintlab/actions/workflows/ci.yml/badge.svg)](https://github.com/marcemac/squintlab/actions/workflows/ci.yml)

## What squintlab does

You give squintlab a photo of a painting, the painting's size and your viewing distance. It returns an HTML report of observation cards. Each card has a measurement, its perceptual consequence, the mechanism behind it, a source and a question about your intent. The cards describe what is in the image. They never grade it.

## What it measures

- Value structure, and a low-acuity luminance view of the painting.
- Equal-luminance colour pairs that may shimmer.
- What survives at a glance versus up close.
- Edge hardness, and edge contrast with the surroundings.

## What it never does

- No aesthetic scores or verdicts.
- No machine-learning models and no AI-generated text.
- No cloud service, accounts or uploads.
- No face or person detection, no inference of identity or expression, and no face-specific measures.
- No inferences about artists or viewers, such as dyslexia, stereoblindness or colour-vision type.
- No stereo, motion-parallax or paint-relief analysis.
- It is not a painting app: no style transfer and no automatic correction.

## Scientific basis

Perceptual lightness is CIELAB L\*, computed from luminance. It is never a naive greyscale average of the red, green and blue values. Vision is described with a two-pathway account: one route that is sensitive to luminance and to where things are, and one that carries colour and fine detail. This is used as a model of effects (why a picture can look unstable or flat), not as a map of the brain.

The ideas follow Margaret Livingstone's book *Vision and Art: The Biology of Seeing*, revised edition (Abrams, 2014), cited by reference only. Primary research is cited on each analysis. Design choices and their costs are recorded in [DECISIONS.md](DECISIONS.md), and planned work is in [ROADMAP.md](ROADMAP.md).

## Status

Pre-alpha, working towards v0.1.

## Development

```bash
uv sync
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy
```

## Licence

Apache-2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE).
