# FounderFit

**AI-powered co-founder compatibility analysis using a sequential multi-agent pipeline.**

FounderFit helps founders figure out whether they are the right building partners for each other — before they sign anything. It runs two founder profiles through eight specialized AI agents, each one an expert in a different facet of compatibility, and produces a scored report plus a plain-English narrative written directly to the founders.

---

## What it does

Most co-founder compatibility tools ask you to fill out a questionnaire and return a score. FounderFit goes further by pulling in real behavioral signals — GitHub commit patterns, LinkedIn career history — and reasoning across all three sources together. The result is not just a score. It is a layered analysis that can arrive at a conclusion different from what any single data source would have suggested on its own.

There are two analysis modes:

- **Compatibility Analysis** (two founders) — fill in two profiles, optionally attach GitHub usernames and LinkedIn PDFs, and run the full 8-agent pipeline to get a compatibility score, friction predictions, GTM archetype, recommendations, and a narrative
- **Individual Assessment** (one founder) — fill out a questionnaire about yourself and optionally enrich it with your GitHub and LinkedIn data to get your founder archetype and a personal narrative

---

## The 8-agent pipeline

Agents run in strict sequence. Each agent builds on the work of every agent before it. The Communicator at the end reads the full output of all seven preceding agents before writing a single word.

### Layer 1 — Enrichment

These three agents run first. They transform raw data into rich behavioral context so that all downstream agents reason from story and signal, not raw JSON.

| Agent | What it does |
|---|---|
| **Resume Analyst** | Reads a LinkedIn PDF export and extracts career signals: domain depth, operator vs. builder instinct, risk trajectory, and a compatibility note |
| **GitHub Storyteller** | Transforms raw GitHub API data into a vivid behavioral narrative covering velocity, craft, collaboration style, and a builder archetype |
| **Synthesis Agent** | Reads all three signals independently (questionnaire, GitHub story, LinkedIn story), looks for patterns that only emerge when combined, and assigns a final archetype — which may differ from what any single signal pointed to |

The Synthesis Agent is the most important part of Layer 1. Its instruction is explicit: *the correct archetype may be one that no single signal pointed to*. It reasons like a detective finding the hidden variable that explains all the evidence at once.

### Layer 2 — Compatibility Scoring

Four agents score the pair across ten dimensions, map their go-to-market strategy, evaluate the pairing holistically, and compare their GitHub signals side by side.

| Agent | What it does |
|---|---|
| **Compatibility Agent** | Scores the pair across ten operational dimensions, predicts the top friction points with timeline estimates, and assigns a GTM archetype |
| **GTM Strategist** | Maps the pair to one of four GTM archetypes and produces a tailored tool stack, weekly cadence, and 30-day roadmap |
| **Matchmaker Agent** | Evaluates complementarity (not just compatibility) — generates an introduction brief, maps combined strength coverage, flags gaps, and recommends a first sprint type |
| **RepoTale Agent** | Compares the GitHub stories of both founders side by side — detects stack overlap, build pace mismatches, and collaboration style tension |

### Layer 3 — Communication

| Agent | What it does |
|---|---|
| **Communicator Agent** | Reads the full output of all seven preceding agents and writes a flowing prose narrative addressed directly to the founders — no bullet points, no headers, no clinical summaries |

The Communicator writes in second person, like a smart advisor who has genuinely studied these two people and has something honest to say to them. For compatibility analyses it writes 4–5 paragraphs covering the partnership picture, combined strengths, where friction will come from, what to agree on before month three, and a closing sentence. For individual assessments it writes 3–4 paragraphs covering who they are as a builder, what the data revealed beyond self-assessment, the blind spot most worth knowing before choosing a co-founder, and a closing truth.

---

## Founder archetypes

The system classifies each founder into one of six archetypes based on their questionnaire answers, GitHub patterns, and career history:

| Archetype | Profile |
|---|---|
| **Rapid Builder** | Ships fast, iterates aggressively, tolerates tech debt — best for consumer apps, marketplaces, MVPs |
| **Systems Operator** | Infrastructure-first, scalability-focused, methodical — best for enterprise SaaS, fintech, infrastructure |
| **Experimental Hacker** | Explores widely, prototypes fast, low attachment to code — best for R&D, AI/ML products, innovation labs |
| **Vision Architect** | Designs for the future, documentation-heavy, strategic — best for platform companies, developer tools, deeptech |
| **Product Strategist** | Feature-driven, user-facing, pragmatic trade-offs — best for B2B SaaS, productivity tools, vertical software |
| **Growth Hunter** | Metrics-obsessed, A/B test heavy, conversion-focused — best for consumer growth, e-commerce, ad-tech |

---

## GTM archetypes

Every founder pair gets assigned to one of four go-to-market archetypes:

| Archetype | Best for |
|---|---|
| **Velocity Pair** | Fast decision + high risk tolerance. Ship fast, validate faster — consumer apps, marketplaces |
| **Craft Pair** | Deliberate + systems-first. Build for depth and quality — developer tools, B2B SaaS |
| **Scale Pair** | Data-driven + growth-led. Metrics and channel efficiency — growth-stage startups |
| **Research Pair** | Experimental + insight-first. Explore before committing — deep tech, AI/ML |

---

## Pages

| Page | Path | What it does |
|---|---|---|
| **Home** | `/` | Landing page |
| **Start Your Assessment** | `/onboarding.html` | Multi-step questionnaire (with optional GitHub and LinkedIn PDF fields) that creates a founder profile and saves it to localStorage |
| **Individual Assessment** | `/assessment.html` | Shows the founder's archetype, ten-dimension scores, Synthesis Agent breakdown ("Why this archetype?" toggle), and Communicator narrative |
| **Compatibility Dashboard** | `/dashboard.html` | Two-founder input form with GitHub and LinkedIn PDF fields, animated 8-agent pipeline visualization, radar chart, and full compatibility report |
| **Agent Portfolio** | `/portfolio.html` | Explains all 8 agents, the 3-layer pipeline architecture, the 4 GTM archetypes, and how the system is built |

### LinkedIn PDF upload

LinkedIn exports your profile as a PDF from **Me → Settings & Privacy → Data privacy → Get a copy of your data → select "Profile" → Request archive**. A helper video link is shown inline on both the onboarding and dashboard pages. The PDF is sent to `/api/upload/resume`, parsed server-side with `pypdf`, and the extracted text is stored in localStorage alongside the rest of the profile.

---

## API endpoints

All routes are prefixed with `/api`.

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/health` | Health check |
| `POST` | `/api/upload/resume` | Upload a LinkedIn PDF (max 5 MB). Returns extracted text and char count |
| `POST` | `/api/analyze/compatibility` | Run full 8-agent compatibility analysis for two founders. Accepts `FounderProfile` objects for both founders plus optional `github_data` and `resume_text` fields |
| `POST` | `/api/assessment/submit` | Submit a single founder profile. Runs archetype classification, ten-dimension scoring, and optionally the Layer 1 enrichment pipeline (Synthesis + Communicator) if GitHub or resume data is present |
| `POST` | `/api/analyze/single` | Run a single agent by name for testing. Accepts `agent_type` (one of: `compatibility`, `gtm`, `repotale`, `matchmaker`, `executor`, `github_storyteller`, `resume_analyst`) and `input_data` |
| `GET` | `/api/archetypes` | Returns the list of six founder archetypes with descriptions |

> **Note:** The `stack` field in `CompatibilityResponse` is populated from the GTM Strategist agent's JSON output. Each tool includes `tool`, `category`, `purpose`, and `why_this_pair` — a pair-specific rationale referencing the founders' actual profile signals. If the agent doesn't return parseable JSON, the dashboard falls back to a curated stack per GTM archetype.

### Founder profile schema

```json
{
  "name": "Alex Johnson",
  "email": "alex@example.com",
  "role": "CTO",
  "decision_speed": "fast | moderate | deliberate",
  "risk_tolerance": "high | moderate | low",
  "communication_style": "async | balanced | sync",
  "execution_style": "sprint | steady | flexible",
  "conflict_approach": "competing | collaborative | compromising",
  "tooling_affinity": "heavy | pragmatic | minimal",
  "domain_expertise": "generalist | specialist | collaborative",
  "ownership_philosophy": "equal | merit | flexible",
  "gtm_orientation": "product_led | sales_led | community_led",
  "github_username": "alexjohnson",
  "resume_text": "optional extracted text from LinkedIn PDF"
}
```

---

## Tech stack

| Layer | Technology |
|---|---|
| **Agent framework** | [ag2](https://github.com/ag2ai/ag2) (formerly AutoGen) — `ConversableAgent` with sequential pipeline orchestration |
| **LLM** | GPT-4o via [OpenRouter](https://openrouter.ai) |
| **API** | FastAPI with async endpoints and Pydantic validation |
| **PDF parsing** | pypdf — extracts text from LinkedIn PDF exports |
| **GitHub data** | httpx — async GitHub REST API client |
| **Frontend** | Vanilla HTML/CSS/JS — no framework, no build step |
| **Deployment** | Configured for Railway (`railway.toml`) and Render (`render.yaml`) |

---

## Project structure

```
let-us-git-along/
├── agents/
│   ├── orchestrator.py          # Pipeline coordinator — run_founder_analysis() and run_assessment_synthesis()
│   ├── resume_agent.py          # Layer 1: Resume Analyst
│   ├── github_storyteller.py    # Layer 1: GitHub Storyteller
│   ├── synthesis_agent.py       # Layer 1: Synthesis Agent (cross-signal reasoner)
│   ├── compatibility.py         # Layer 2: Compatibility Agent (ten-dimension scoring)
│   ├── gtm_strategist.py        # Layer 2: GTM Strategist (four archetypes)
│   ├── matchmaker.py            # Layer 2: Matchmaker Agent
│   ├── repotale.py              # Layer 2: RepoTale Agent (GitHub comparison)
│   ├── executor.py              # Utility agent (available via /analyze/single)
│   └── communicator_agent.py    # Layer 3: Communicator (prose narrative voice)
│
├── api/
│   ├── models.py                # Pydantic models: FounderProfile, CompatibilityRequest, etc.
│   └── routes.py                # FastAPI route handlers
│
├── tools/
│   ├── github_analyzer.py       # Async GitHub API client
│   └── resume_parser.py         # pypdf text extraction
│
├── frontend/
│   ├── index.html               # Landing page
│   ├── onboarding.html          # Multi-step founder questionnaire (Step 1 collects GitHub + LinkedIn)
│   ├── assessment.html          # Individual assessment results
│   ├── dashboard.html           # Two-founder compatibility dashboard with radar chart
│   └── portfolio.html           # Agent portfolio and architecture explainer
│
├── main.py                      # FastAPI app entry point
├── requirements.txt
└── .env.example
```

---

## Recommended Stack feature

The Compatibility Dashboard includes a **Recommended Stack** section that appears after every analysis. Tools are displayed as cards grouped by category (Communication, Project Management, Development, Analytics, Sales, Documentation) with category filter pills. Each card shows the tool name, what it does, and a pair-specific rationale that references the founders' actual profile signals.

The GTM Strategist agent produces the stack as part of its JSON output. The orchestrator parses it and passes it through `CompatibilityResponse.stack`. If the agent response can't be parsed, the dashboard falls back to a curated hardcoded stack per GTM archetype so the section always renders.

---

## Running locally

**1. Clone and install dependencies**

```bash
git clone https://github.com/your-org/let-us-git-along.git
cd let-us-git-along
pip install -r requirements.txt
```

**2. Set environment variables**

Copy `.env.example` to `.env` and fill in your keys:

```
OPENROUTER_API_KEY=your_openrouter_api_key_here
GITHUB_TOKEN=your_github_token_here
```

- Get an OpenRouter API key at [openrouter.ai](https://openrouter.ai) — the system uses `openai/gpt-4o`
- The GitHub token is optional but avoids rate limits when analyzing public GitHub profiles (create one at GitHub → Settings → Developer settings → Personal access tokens → Fine-grained tokens, no special scopes needed)

**3. Start the server**

```bash
uvicorn main:app --reload
```

The app runs at `http://localhost:8000`. The frontend is served as static files from `/frontend`. API docs (Swagger UI) are available at `http://localhost:8000/docs`.

---

## How a compatibility analysis works end to end

1. User fills in two founder profiles on the **Compatibility Dashboard** — name, role, and six behavioral dimensions for each
2. Optionally enters GitHub usernames and/or uploads LinkedIn PDFs for one or both founders
3. Clicks **Run Compatibility Analysis**
4. The frontend POSTs to `/api/analyze/compatibility`
5. The API fetches GitHub profile data in parallel (if usernames provided)
6. The orchestrator runs the 8-agent pipeline in sequence:
   - Resume Analyst processes any uploaded LinkedIn text
   - GitHub Storyteller converts raw GitHub JSON into a narrative
   - Synthesis Agent reads all signals and determines each founder's archetype
   - Compatibility, GTM Strategist, Matchmaker, and RepoTale each analyze the pair
   - Communicator reads every agent's output and writes the final narrative
7. Results are returned and rendered: overall score, animated radar chart, ten-dimension breakdown, friction predictions, strengths, recommendations, and the Communicator's prose narrative at the top

If the API is unavailable (e.g. missing API key), the dashboard falls back to a local calculation using the questionnaire answers directly — so the UI always renders something.

---

## How the individual assessment works

1. User completes the multi-step questionnaire in **onboarding.html** — Step 1 asks for name, role, and optionally GitHub username and LinkedIn PDF
2. Questionnaire answers are saved to `localStorage` as `founderProfile`
3. User lands on **assessment.html**, which reads the saved profile and POSTs to `/api/assessment/submit`
4. The API runs rule-based archetype classification and ten-dimension scoring immediately
5. If GitHub or LinkedIn data is present, it runs the enrichment pipeline: GitHub Storyteller → Resume Analyst → Synthesis Agent → Communicator
6. Results are displayed: archetype badge, score ring, dimension bars, and optionally:
   - A **"Why this archetype?"** collapsible toggle showing the Synthesis Agent's reasoning (signal-by-signal breakdown, emergent insight, confidence, partnership note)
   - The Communicator's personal narrative

The questionnaire answers are never overwritten or pre-filled from GitHub/LinkedIn data. The enrichment is additive — it only influences the synthesis and narrative, not the form the user filled out.
