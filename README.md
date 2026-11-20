# Interview Company Researcher

A multi-agent research assistant for job interview prep. Give it a company name, and it researches the web and returns one **fact-checked company brief**, so you don't have to search a dozen sites before an interview.

```bash
python main.py "Input the company name here"
```

The brief covers:

- **What the company does**: the problem it solves, why it exists, and who its customers are
- **Size and stage**: startup, growth, late-stage, public or enterprise; funding rounds and investors; headcount; offices worldwide
- **Products and growth drivers**: core products, launches in the last 12 months, and which products bring in the money
- **AI strategy**: AI features already shipped, what's in beta, what's only announced, and leadership's stated direction
- **Competitive landscape**: the top 3 competitors, a side-by-side comparison, and whether the company is leading, at par, or lagging, and why
- **Interview angles**: 3–5 specific questions and talking points based on the findings
- **Caveats and sources**: what couldn't be verified, plus a citation (URL and date) for every number

---

## How it works

Built on [`deepagents`](https://github.com/langchain-ai/deepagents) using an orchestrator–worker pattern:

```
                        ┌──────────────────────┐
     company name ───▶  │      Lead agent       │  resolves the entity, plans,
                        │  (plan → delegate →   │  delegates, synthesizes
                        │   assess → write)     │
                        └──────────┬───────────┘
            ┌──────────────────────┼──────────────────────┐   (in parallel)
            ▼                      ▼                      ▼
   ┌─────────────────┐   ┌─────────────────┐   ┌──────────────────────┐
   │ product-        │   │ size-           │   │ competitor-          │
   │ researcher      │   │ researcher      │   │ discoverer           │
   │ overview,       │   │ stage, funding, │   │ market, top 3,       │
   │ products, AI    │   │ headcount,      │   │ comparison, verdict  │
   │                 │   │ offices         │   │                      │
   └────────┬────────┘   └────────┬────────┘   └──────────┬───────────┘
            └─────── findings/*.md ┴──────────────────────┘
                                   ▼
                        ┌──────────────────────┐
                        │     fact-checker      │  audits every claim:
                        │                       │  VERIFIED / CORRECTED /
                        └──────────┬───────────┘  OUTDATED / UNSUPPORTED /
                                   ▼              CONTRADICTED
                          final company brief
```

| Agent | What it does |
|---|---|
| **Lead agent** | Confirms which company is meant (and asks you if the name is ambiguous), writes a plan, sends out the three researchers in parallel, reviews their findings, drafts the brief, and applies the fact-checker's corrections. It never writes facts from its own knowledge. |
| **product-researcher** | Business overview, customers, product portfolio, recent launches, revenue and growth drivers, AI features and plans. |
| **size-researcher** | Ownership type and stage, funding rounds, valuation or market cap, headcount and trend, offices and countries, acquisitions. |
| **competitor-discoverer** | Defines the market, finds and ranks competitors, compares the top 3 on the same dimensions, and gives an evidence-backed verdict. |
| **fact-checker** | Checks that every claim can be traced to a source, is dated, current and not overstated, and is about the right company. It can run a few targeted searches to confirm high-stakes numbers. |

**How the agents keep facts reliable:**
- Every fact is recorded with a value, an "as of" date, a source URL, a source tier (T1 primary → T3 weak), a confidence level, and a label: fact, estimate, or inference.
- Inferences and third-party estimates are labeled; they are never presented as facts.
- AI features are kept strictly separate: shipped, beta, or announced.
- "Not publicly disclosed" is used instead of a guessed number.

---

## Requirements

- **Python 3.11+** (required by `deepagents`)
- A **[Tavily](https://tavily.com)** API key for web search
- An API key for the **LLM provider** configured in `agents.py` (this repo is set up for [Nebius AI Studio](https://studio.nebius.ai))

---

## Setup

```bash
# 1. Clone and enter the project folder
git clone <your-repo-url>
cd <repo-folder>/3_orchestrating_deep_research

# 2. Create a virtual environment with Python 3.11+
python3.12 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
python --version                   # should print 3.11 or higher

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4. Add your API keys
cp .env.example .env
# then open .env and fill in your keys
```

`.env` is loaded automatically. **Never commit it**: make sure `.env` is listed in `.gitignore`, and keep only placeholder values in `.env.example`.

---

## Usage

Pass the company name as an argument:

```bash
python main.py "Stripe"
```

Or run it with no arguments and it will ask:

```bash
python main.py
# Which company should I research? Stripe
```

If the name matches more than one company (for example, "Mercury"), the lead agent asks you which one you mean before it starts.

### Output

The final brief prints in the terminal. Each run also gets its own folder, so you can see exactly what the agents did:

```
runs/company-<id>/
├── plan.md                  # entity card + delegation plan
├── notes.md                 # draft brief before fact-checking
└── findings/
    ├── products.md          # product-researcher
    ├── size.md              # size-researcher
    ├── competitors.md       # competitor-discoverer
    └── fact-check.md        # fact-checker audit
```

### Optional: search trace

Set `AGENT_TRACE_DIR` to log every web search (query and summarized results) to `tool_calls.jsonl`. This is useful for debugging and evaluation:

```bash
export AGENT_TRACE_DIR=./traces && mkdir -p traces
python main.py "Stripe"
```

---

## Project structure

| File | Purpose |
|---|---|
| `main.py` | Entry point: reads the company name, creates the run folder, runs the agent |
| `agents.py` | Builds the lead agent and registers the sub-agents |
| `prompts.py` | System prompts for all five agents, plus shared evidence rules and sub-agent definitions |
| `tools.py` | Tavily `internet_search` tool (with error handling) and a tool-call logger |
| `.env.example` | Template for the required environment variables |

---

## Customizing

- **Change what the brief covers.** Edit the section list in step 5 of `LEAD_AGENT_PROMPT` in `prompts.py`.
- **Add a new specialist** (e.g., a culture and leadership researcher). Write its prompt in `prompts.py`, add it to `build_subagents()`, and give the lead a delegation entry for it.
- **Spend fewer or more searches.** Each worker prompt includes a rough tool-call budget (about 8–14 calls). Adjust it to balance cost and depth.
- **Swap the model or search provider.** Change the model in `agents.py`, or replace `internet_search` in `tools.py`.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `zsh: command not found: pip` | Use `python3 -m pip ...`, or activate the virtual environment first |
| `No matching distribution found for deepagents` | Your Python is older than 3.11. Recreate `.venv` with `python3.12 -m venv .venv` |
| `KeyError: 'TAVILY_API_KEY'` | Keys must be in a file named `.env`, not `.env.example` |
| Tavily `BadRequestError` about `site:` operators | Already handled in `tools.py`. Pull the latest version |
| Research is about the wrong company | Add context to the name, e.g. `python main.py "Mercury (fintech bank, mercury.com)"` |

---

## Limitations

- The brief is only as good as public information. Private companies often don't disclose revenue or exact headcount, and the brief will say so instead of guessing.
- Revenue drivers and competitive verdicts are often **inferences**, and are labeled as such.
- Always check the most important numbers against the cited sources before an interview.
