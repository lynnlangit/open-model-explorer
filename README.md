# Open Model Explorer

<img src="https://github.com/lynnlangit/open-model-explorer/blob/main/images/open-model-app.png">

A local chatbot harness for exploring open **foundational** and **medical** LLMs —
pick a model, chat with it, compare two side by side, upload medical images, and add
any model from Hugging Face live. Everything runs on your Mac via Ollama; **nothing
leaves the device.**  

Works with text (example above) or images (animated example below).  

<img src="https://github.com/lynnlangit/open-model-explorer/blob/main/images/demo-vision.gif">

## What it does

- Clean **white** chat UI at `http://localhost:8000`
- Model picker grouped into **Medical** and **General**, with 👁 vision and ⚡ fast
  icons and ✓ installed / ⬇ pull badges
- **Streaming** responses with a live **tokens/sec** readout under each answer
- **Compare mode** — run two models side by side on the same prompt
- **Image upload** for vision models (up to 3 images; PNG, JPG, WEBP, GIF, BMP, TIFF;
  ≤ 10 MB each) with in-browser normalization to lossless PNG
- **"Add model from Hugging Face"** — paste any `hf.co/...` GGUF repo and watch it
  pull live, then it appears in the picker
- Clinical example prompts on the welcome screen; persistent research-use disclaimer

## Requirements

- macOS on Apple Silicon (tuned for ~32 GB; runs 7–9B models comfortably)
- [Ollama](https://ollama.com/download) — install with `brew install ollama`
- Python 3.9+
- Internet access for the first model pulls and for TIFF decoding (UTIF.js via CDN)

## Run it

```bash
cd "Open Research"
chmod +x run.sh      # first time only
./run.sh
```

`run.sh` verifies Ollama, starts its server if needed, creates a Python venv, installs
dependencies, pre-pulls the demo models, launches the app (with auto-reload), and opens
your browser. First run downloads the demo models (a few minutes); later runs are fast.

To stop: press `Ctrl+C` in the terminal.

## Files

| File | Purpose |
|------|---------|
| `server.py` | FastAPI backend — proxies Ollama for chat, model list, and HF pulls |
| `index.html` | The white single-page chat UI (all HTML/CSS/JS in one file) |
| `models.json` | Curated model catalog + which models to pre-pull |
| `run.sh` | One-command launcher |
| `requirements.txt` | Python dependencies |
| `.gitignore` | Excludes `.venv/`, caches, and any future secret files |
| `LICENSE` | MIT license |

## Featured models

**Medical:** MedGemma 4B (vision), OpenBioLLM 8B, BioMistral 7B, Meditron 7B.
**General:** Pixtral 12B (vision, Mistral), Llama 3.2 Vision 11B, Gemma 3 4B (vision),
LLaVA 7B, Moondream, Llama 3.1 8B, Mistral 7B, Gemma 2 9B, Phi-3 Mini, Llama 3.2 3B.

Default model is **Gemma 3 4B** (multimodal — text + image). Pre-pulled on first run:
`phi3:mini`, BioMistral 7B, MedGemma, and Gemma 3 4B (see `models.json` → `preload`).

## Security & credentials

**This app does not store, read, or transmit any Hugging Face token or API key.**

- Model pulls go through your **local Ollama**, which downloads **public** GGUF repos
  from Hugging Face **without authentication**. Your personal HF login (if any) lives in
  Ollama/HF config outside this repo (`~/.ollama`, `~/.cache/huggingface`) and is never
  committed.
- The only environment variable the server reads is `OLLAMA_HOST` (defaults to
  `http://localhost:11434`) — not a secret.
- The repo has been checked for embedded tokens/secrets: none are present, and
  `.gitignore` guards against accidentally committing `.env` or token files later.

**If you ever add a *gated* HF model** (some require accepting a license), Ollama needs
an HF token. Set it as an environment variable on your own machine — never hardcode it:

```bash
export HF_TOKEN=hf_xxxxxxxx   # in your shell profile, not in this repo
```

The app itself still needs no changes; Ollama handles the auth.

> **Clinical disclaimer:** These open models are **research/demo tools only** and are
> **not validated for clinical use**. They must not inform patient-care decisions.
> Uploaded images are re-encoded to 8-bit for the models — this is exploration, not
> diagnostic-grade viewing of 16-bit or whole-slide scans.

## Try It!

1. Open the app — select one (or two) open models for testing from the drop down list(s).
2. Send a clinical prompt to a medical model, e.g. *"What are first-line treatments for
   stage 2 hypertension?"*, and note the tokens/sec readout.
3. Turn on **Compare**, put **MedGemma 4B vs. Llama 3.1 8B** on the same question —
   contrast a medical fine-tune against a general baseline.
4. Attach a medical image (chest X-ray / histology) and compare **MedGemma 4B (vision)
   vs. Llama 3.2 Vision** — the medical grounding shows.
5. Click **+ Add model from Hugging Face**, paste
   `hf.co/EnlistedGhost/Pixtral-12B-Ollama-GGUF`, and watch the model being pulled from HF live.
