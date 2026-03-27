# Litmous.ai 🧪
### The LLM Quality Arena

Litmous.ai is a lightweight tool for comparative testing of Large Language Models. It helps developers and content creators choose the best LLM provider based on real-world prompts, automated quality scoring, and response speed.

> **Name origin:** *Litmus* — a litmus test for AI content quality.

---

## 🚀 Features

**Multi-Provider Support**
Parallel requests to 7 models across 3 providers:
- Via [OpenRouter](https://openrouter.ai): GPT-4o, GPT-4o mini, Claude 3.5 Sonnet, Llama 3.3 70B (free), DeepSeek V3 (free)
- Direct API: Grok-2 (xAI), YandexGPT 3

**Automated Quality Scoring**
Each response is scored 0–100 using a rule-based evaluator:
- Text length (optimal range: 250–700 chars)
- First-person voice presence
- Concrete facts / numbers
- Structure (hook → body → punchline)
- Readability (avg word length)
- AI cliché detection with penalty (−5 per flagged word)

Zones: 🟢 Green (80–100) · 🟡 Orange (60–79) · 🔴 Red (0–59)

**Performance Metrics**
Real-time latency tracking per model. Free-tier models are staggered to avoid rate limits.

**Modern UI**
React dashboard with side-by-side results, visual score bars, and expandable scoring breakdown.

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11, FastAPI, httpx |
| Frontend | React, Vite, Tailwind CSS |
| LLM access | OpenRouter API, xAI API, Yandex Cloud API |
| Dev | uvicorn, python-dotenv |

---

## 📦 Quick Start

**1. Clone**
```bash
git clone https://github.com/TinaUma/litmous-ai.git
cd litmous-ai
```

**2. Set up environment**
```bash
cp .env.example .env
# Fill in your API keys in .env
```

```env
OPENROUTER_API_KEY=your_key   # covers GPT-4o, Claude, Llama, DeepSeek
GROK_API_KEY=your_key          # xAI Grok-2
YANDEXGPT_API_KEY=your_key     # Yandex Cloud
YANDEX_FOLDER_ID=your_folder   # Yandex Cloud folder ID
```

**3. Run backend**
```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

API available at `http://localhost:8000` · Swagger UI at `http://localhost:8000/docs`

---

## 🗺 Roadmap

- [ ] SQLite history — store and compare experiments over time
- [ ] Quorum scoring — multi-agent verdict (Editor + Fact-checker + Marketer)
- [ ] Prompt Lab — raw / unified / per-model prompt modes
- [ ] Cost tracking — token usage and estimated cost per run
- [ ] Docker Compose — one-command deployment

---

## 📄 License

MIT
