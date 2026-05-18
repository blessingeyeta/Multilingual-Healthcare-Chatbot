# AI-Powered Multilingual Healthcare Chatbot
### Proof-of-Concept · Nigerian Primary Healthcare · 5 Languages

> **Agent/Bot Build Reference** — This README is the single source of truth for building this PoC.
> Follow the day-by-day plan in order. Do not add features outside the defined scope.

---

## Table of Contents
1. [Project Summary](#1-project-summary)
2. [Research Foundation](#2-research-foundation)
3. [Current State](#3-current-state)
4. [3-Day Build Plan](#4-3-day-build-plan)
5. [Architecture — 6 Layers](#5-architecture--6-layers)
6. [Tech Stack](#6-tech-stack)
7. [Scope Definition](#7-scope-definition)
8. [File Structure](#8-file-structure)
9. [Environment Variables](#9-environment-variables)
10. [Setup & Run](#10-setup--run)
11. [Sample Test Inputs](#11-sample-test-inputs)
12. [Design Rules & Constraints](#12-design-rules--constraints)

---

## 1. Project Summary

A **Streamlit-based conversational chatbot** that answers primary healthcare questions in five Nigerian languages: **English, Yoruba, Igbo, Hausa, and Nigerian Pidgin**.

The system is grounded in a 6-layer framework derived from academic evaluation of existing Nigerian healthcare chatbots (Honey, AwaDoc/Noura, AISHA Chat). It improves on their observed weaknesses in language handling, source transparency, free-text understanding, and clinical safety.

**Goal for this sprint:** A working, demo-ready PoC in 3 days — no cloud infrastructure, no vector database, no production deployment pipeline required.

---

## 2. Research Foundation

**Source:** Chapter 3 — Research Methodology (Academic Project, 2026)

### Why the existing chatbots were insufficient

| Gap Identified | Evidence |
|---|---|
| Poor response-language alignment | AISHA understood Yoruba/Igbo but always replied in English |
| No exact source grounding | Honey gave no sources; AwaDoc gave homepage URLs, not specific guidelines |
| Rigid menu-driven interaction | Honey could not answer free-text Yoruba questions |
| Heavy onboarding / access barriers | AwaDoc required subscription before health access |
| Limited Nigerian clinical adaptation | AISHA did not recommend malaria testing before treatment |
| Inconsistent emergency escalation | No uniform urgent-care routing across any system |

### The 6 Framework Layers (derived from gaps above)

| Layer | Purpose |
|---|---|
| 1. User Access & Interface | Language selection, quick access, optional profile |
| 2. Language Management | Language detection, switching, response-language matching |
| 3. Multilingual Input Processing | Handle Yoruba, Igbo, Hausa, Pidgin, code-switching, informal spelling |
| 4. Intent Recognition & Triage | Classify intent; detect emergency symptoms; trigger escalation |
| 5. Verified Medical Knowledge (RAG) | Source-backed responses from WHO/NCDC/FMOH/NPHCDA |
| 6. Response Generation & Safety | Safe, language-matched, source-cited, non-diagnostic responses |

---

## 3. Current State

`app.py` already implements a functional PoC shell. **Do not rewrite it — extend it.**

### What is already built

| Feature | Status |
|---|---|
| Streamlit UI with full styling | Done |
| Language selection (5 languages) | Done |
| Optional user profile (name, age, sex) | Done |
| Translation dictionary for all UI labels | Done |
| Keyword-based intent detection (6 categories) | Done |
| Follow-up question flow (duration, severity, extra) | Done |
| Context-aware notes (age < 5, age ≥ 60, female) | Done |
| Emergency fast-path (no follow-up required) | Done |
| Hardcoded multilingual response bank | Done |
| Placeholder source + next-step attribution | Done |
| Sidebar framework layer display | Done |
| Session reset button | Done |

### What is missing (this sprint)

| Feature | Priority | Day |
|---|---|---|
| `requirements.txt` populated | Critical | Day 1 |
| `.env` / secrets management | Critical | Day 1 |
| LLM integration (Groq or Gemini) | High | Day 1 |
| JSON knowledge base (per domain) | High | Day 2 |
| Real source injection into LLM prompt | High | Day 2 |
| Multilingual system prompt engineering | High | Day 2 |
| Safety guardrails on LLM output | High | Day 3 |
| All 5 languages tested end-to-end | High | Day 3 |
| Streamlit Cloud deployment | Medium | Day 3 |

---

## 4. 3-Day Build Plan

### Day 1 — Foundation: Get a Running, LLM-Powered App

**Objective:** Replace hardcoded responses with real LLM-generated answers. App must run locally with `streamlit run app.py`.

#### Tasks

1. **Populate `requirements.txt`**
   ```
   streamlit>=1.35.0
   groq>=0.9.0
   python-dotenv>=1.0.0
   ```

2. **Create `.env.example`**
   ```
   GROQ_API_KEY=your_groq_api_key_here
   ```

3. **Add `.env` loading at the top of `app.py`**
   - Use `python-dotenv` to load `GROQ_API_KEY`
   - Fall back to `st.secrets` if running on Streamlit Cloud

4. **Create a `llm.py` module** with a single function:
   ```python
   def ask_llm(system_prompt: str, user_message: str) -> str:
       """Call Groq API and return response text. Handle errors gracefully."""
   ```
   - Use `groq` Python SDK
   - Model: `llama-3.3-70b-versatile` (free tier, good multilingual support)
   - Max tokens: 400 (keep responses concise)
   - Temperature: 0.2 (factual, consistent)
   - On API error or timeout: return the matching hardcoded response from the existing response bank (graceful fallback)

5. **Wire `llm.py` into `app.py`**
   - Replace the `get_final_response()` return value with an LLM call
   - Keep the existing hardcoded response bank as the fallback only
   - The LLM call should receive: intent, language, age, sex, duration, severity, extra details

6. **Write a base system prompt in `prompts.py`** (see Day 2 for full version)
   - For Day 1: basic system prompt that instructs the model to reply in the user's language and avoid diagnosis

**Day 1 Definition of Done:**
- [ ] `pip install -r requirements.txt` succeeds
- [ ] `streamlit run app.py` launches without errors
- [ ] An English malaria question returns an LLM-generated (not hardcoded) response
- [ ] Emergency keywords still trigger immediate escalation (no LLM call for emergencies)

---

### Day 2 — Knowledge Base + Multilingual Prompting

**Objective:** Ground LLM responses in real Nigerian healthcare knowledge. Improve language fidelity across all 5 languages.

#### Tasks

1. **Create `knowledge_base.py`**

   A Python dictionary (`KNOWLEDGE`) keyed by intent. Each entry contains:
   - `summary`: 3–5 sentence plain-English summary from official source
   - `source_name`: Display name of the source (e.g. "Nigeria Centre for Disease Control and Prevention (NCDC)")
   - `source_note`: Short citation string shown to the user
   - `next_step`: Recommended action

   Domains to cover (no others):
   | Key | Source |
   |---|---|
   | `Malaria` | NCDC / Federal Ministry of Health malaria guidelines |
   | `Immunization` | NPHCDA routine immunization schedule |
   | `Family Planning` | WHO / FMOH family planning guidance |
   | `Medication Safety` | WHO antimicrobial resistance / medication safety |
   | `General Health` | Generic primary healthcare guidance |
   | `Emergency` | Standard emergency triage (no LLM call — direct escalation only) |

   Knowledge content must be factual summaries, not copied text. Keep each summary under 150 words.

2. **Update `prompts.py` with full system prompt**

   The system prompt must instruct the LLM to:
   - Respond **only** in the language specified (`{language}`)
   - Use the knowledge excerpt provided — do not invent medical facts
   - Never say "You have [disease]" — say "your symptoms may be related to..."
   - Always end with the recommended next step
   - Keep the response under 200 words
   - If the user is under 5 or over 60, add a note recommending medical review
   - If the user is female and the intent is malaria or family planning, add pregnancy-awareness note

   Template:
   ```
   SYSTEM:
   You are a multilingual Nigerian healthcare information assistant.
   Language: {language}
   User profile: Age {age}, Sex {sex}
   Health domain: {intent}

   Use ONLY the following verified knowledge to answer:
   ---
   {knowledge_excerpt}
   ---

   Rules:
   - Reply in {language} only.
   - Do not diagnose. Do not prescribe.
   - Say "your symptoms may be related to..." not "you have...".
   - End your response with: "Next step: {next_step}"
   - If you cannot answer safely, say so and recommend seeing a healthcare professional.
   - Maximum 200 words.

   USER: {user_message}
   Additional context: Duration: {duration}. Severity: {severity}. Extra: {extra}.
   ```

3. **Update `llm.py`** to accept and inject the knowledge excerpt from `knowledge_base.py` based on intent

4. **Test all 5 languages** using the sample questions in Section 11
   - Verify response language matches input language
   - Verify source label is shown in the UI

**Day 2 Definition of Done:**
- [ ] All 6 intents return a response sourced from `knowledge_base.py`
- [ ] Source label (e.g. "Source: NCDC Malaria Guidelines") appears in every non-emergency response
- [ ] A Yoruba question receives a Yoruba response
- [ ] An Igbo question receives an Igbo response
- [ ] Hardcoded fallback still works when `GROQ_API_KEY` is not set

---

### Day 3 — Safety, Polish, and Demo Readiness

**Objective:** Harden safety guardrails, verify all languages, and make the app demo-ready.

#### Tasks

1. **Safety audit of LLM outputs**
   - Add a `safety_check(response_text: str) -> str` function in `llm.py`
   - If response contains any of these strings (case-insensitive): `"you have"`, `"you are diagnosed"`, `"take [drug]"`, `"prescription"` — replace with: `"I'm not able to confirm a diagnosis. Please consult a healthcare professional."`
   - Emergency intent must never call the LLM — verify this is enforced

2. **UI polish (minimal)**
   - Add a language badge in the chat header showing the active language
   - Add a loading spinner (`st.spinner`) during LLM calls
   - Confirm the disclaimer banner is visible on every page state

3. **End-to-end language testing** — run all sample questions from Section 11 manually
   - Check: response language matches input language
   - Check: source attribution displayed
   - Check: emergency keywords trigger immediate referral
   - Check: follow-up form collects context before LLM is called

4. **Populate `.streamlit/secrets.toml.example`** for Streamlit Cloud deployment:
   ```toml
   GROQ_API_KEY = "your_key_here"
   ```

5. **Deploy to Streamlit Cloud** (optional but recommended)
   - Push repo to GitHub
   - Connect to share.streamlit.io
   - Add `GROQ_API_KEY` in Streamlit Cloud secrets

**Day 3 Definition of Done:**
- [ ] Safety check function is active and tested
- [ ] All sample questions in Section 11 produce safe, language-correct, source-cited responses
- [ ] App loads in under 3 seconds on first run
- [ ] No hardcoded API keys in any committed file
- [ ] `README.md` reflects final setup instructions

---

## 5. Architecture — 6 Layers

```
┌─────────────────────────────────────────────────────────┐
│  Layer 1: User Access & Interface                        │
│  → Streamlit UI, language selector, optional profile     │
│  → File: app.py (UI sections)                            │
├─────────────────────────────────────────────────────────┤
│  Layer 2: Language Management                            │
│  → st.session_state.language, t() translation function  │
│  → LLM prompted to respond in selected language          │
│  → File: app.py (translations dict, t() function)        │
├─────────────────────────────────────────────────────────┤
│  Layer 3: Multilingual Input Processing                  │
│  → Keyword lists include Yoruba/Igbo/Pidgin expressions  │
│  → LLM handles informal spelling and code-switching      │
│  → File: app.py (detect_intent), llm.py                  │
├─────────────────────────────────────────────────────────┤
│  Layer 4: Intent Recognition & Triage                    │
│  → detect_intent() classifies into 6 categories         │
│  → Emergency → immediate escalation, no LLM call        │
│  → Non-emergency → follow-up form → LLM call            │
│  → File: app.py (detect_intent function)                 │
├─────────────────────────────────────────────────────────┤
│  Layer 5: Verified Medical Knowledge (RAG-Lite)          │
│  → KNOWLEDGE dict keyed by intent                        │
│  → Excerpt injected into LLM system prompt               │
│  → No vector DB for PoC — curated summaries only         │
│  → File: knowledge_base.py                              │
├─────────────────────────────────────────────────────────┤
│  Layer 6: Response Generation & Safety                   │
│  → Groq (Llama-3.3-70b) generates final response        │
│  → safety_check() post-processes output                  │
│  → Source + next-step appended to every response         │
│  → Hardcoded bank is fallback if LLM unavailable         │
│  → File: llm.py, prompts.py                             │
└─────────────────────────────────────────────────────────┘
```

---

## 6. Tech Stack

| Component | Choice | Reason |
|---|---|---|
| UI Framework | Streamlit | Already in use; fast for demos |
| LLM Provider | Groq (free tier) | Fast inference, good multilingual, generous free limits |
| LLM Model | `llama-3.3-70b-versatile` | Best multilingual quality on Groq free tier |
| Language | Python 3.10+ | Existing codebase |
| Secrets | `python-dotenv` + Streamlit Secrets | Works locally and on Streamlit Cloud |
| Vector DB | None (PoC) | RAG-lite via prompt injection is sufficient for PoC |
| Deployment | Streamlit Community Cloud | Free, one-click from GitHub |

**Alternative LLM if Groq is unavailable:** Google Gemini 1.5 Flash via `google-generativeai` (also free tier). Keep Groq as primary.

---

## 7. Scope Definition

### In Scope (PoC — build these only)

- [x] 5 languages: English, Yoruba, Igbo, Hausa, Nigerian Pidgin
- [x] 5 health domains: Malaria, Immunization, Family Planning, Medication Safety, General Health
- [x] 1 safety domain: Emergency escalation
- [x] Keyword-based intent detection with LLM as response engine
- [x] Follow-up question flow before LLM call
- [x] Source attribution from curated knowledge base
- [x] Basic context-awareness (age group, sex)
- [x] Streamlit UI — no mobile app, no WhatsApp integration
- [x] Graceful fallback to hardcoded responses if LLM fails

### Out of Scope (do not build these in this sprint)

- ❌ Real vector database (FAISS, Pinecone, Chroma, etc.)
- ❌ Document ingestion pipeline (PDF parsing, embeddings)
- ❌ WhatsApp or Telegram integration
- ❌ Voice input or text-to-speech
- ❌ User authentication or login
- ❌ Database / persistent chat history
- ❌ Doctor or human agent escalation (live handoff)
- ❌ Payment or subscription logic
- ❌ Custom fine-tuned models
- ❌ Admin dashboard or analytics
- ❌ Additional health domains beyond the 5 listed
- ❌ Clinical diagnosis or treatment plans (by design — never build this)

---

## 8. File Structure

```
Multilingual-Healthcare-Chatbot/
├── app.py                    # Main Streamlit app (DO NOT rewrite — extend only)
├── llm.py                    # LLM client: ask_llm(), safety_check()
├── prompts.py                # System prompt template and builder
├── knowledge_base.py         # Curated knowledge dict keyed by intent
├── requirements.txt          # Python dependencies
├── .env.example              # Template for local secrets (committed)
├── .env                      # Actual secrets (NOT committed — add to .gitignore)
├── .gitignore                # Must include .env and __pycache__
├── .streamlit/
│   └── secrets.toml.example  # Template for Streamlit Cloud secrets
└── README.md                 # This file
```

---

## 9. Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | Yes | Get free key at console.groq.com |

Loading order in `app.py`:
1. Try `os.getenv("GROQ_API_KEY")` (works when `.env` is loaded via `python-dotenv`)
2. Fall back to `st.secrets["GROQ_API_KEY"]` (works on Streamlit Cloud)
3. If neither is set: log a warning and use hardcoded response bank — do not crash

---

## 10. Setup & Run

### Local Development

```bash
# 1. Clone the repo
git clone <repo-url>
cd Multilingual-Healthcare-Chatbot

# 2. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create your .env file
copy .env.example .env
# Edit .env and add your GROQ_API_KEY

# 5. Run the app
streamlit run app.py
```

### Streamlit Cloud Deployment

1. Push repo to a public or private GitHub repository
2. Go to share.streamlit.io → New app → select repo and `app.py`
3. Under Advanced → Secrets, add:
   ```
   GROQ_API_KEY = "gsk_..."
   ```
4. Deploy. App will be live at `https://your-app-name.streamlit.app`

---

## 11. Sample Test Inputs

Use these to verify every layer works correctly. All must produce safe, source-cited, language-correct responses.

| Language | Domain | Input |
|---|---|---|
| English | Malaria | `"I have had fever, headache, and chills for two days. What could it be?"` |
| Yoruba | Malaria | `"Mo ni iba, ori fifo, ati otutu fun ojo meji. Kini o le je?"` |
| Igbo | Malaria | `"Achoro m ima ma enwere m malaria. Ahu mgbu na isi awa m."` |
| Hausa | Malaria | `"Ina da zazzabi da ciwon kai tun jiya. Me za a yi?"` |
| Nigerian Pidgin | Malaria | `"I get fever and body pain since yesterday. Wetin fit cause am?"` |
| English | Emergency | `"I have severe chest pain and difficulty breathing right now."` |
| English | Immunization | `"When should my child get the polio vaccine?"` |
| Yoruba | Family Planning | `"Kini awon ipa ti pills le ni lori ara?"` |
| English | Medication Safety | `"Can I take antibiotics without doing a test first?"` |
| English | Source request | `"What is your source for this information?"` |

**Expected behaviours:**
- Emergency input → immediate referral message, no follow-up form, no LLM call
- All non-emergency inputs → follow-up form shown first, then LLM response
- Every response shows a Source label and a Next Step label
- Yoruba input → Yoruba response; Igbo input → Igbo response
- No response says "You have [disease]" — always "may be related to"

---

## 12. Design Rules & Constraints

These rules must be enforced throughout the build. They are non-negotiable.

### Medical Safety
- The chatbot **never diagnoses**. Use language like "may be related to", "symptoms suggest", "could indicate".
- The chatbot **never prescribes**. Do not name specific drug dosages.
- Every non-emergency response **must** end with a next step that recommends professional care.
- Emergency detection must **bypass** the LLM entirely — hardcoded escalation message only.

### Language Fidelity
- The LLM system prompt must explicitly state the target language.
- If the LLM returns a response in the wrong language, treat it as an error and use the hardcoded fallback.

### Source Grounding
- Every health response must cite a source (even if it is a domain-level label like "Source: NCDC Malaria Guidelines").
- The LLM must never invent sources. Source names come from `knowledge_base.py` only.

### No Scope Creep
- Do not add new health domains without updating `knowledge_base.py`, `detect_intent()`, the translations dict, and the test inputs.
- Do not integrate new platforms (WhatsApp, Telegram) in this sprint.
- Do not add a real vector database in this sprint — knowledge injection via prompt is sufficient for PoC.

### Security
- API keys must never be hardcoded in any Python file.
- `.env` must be in `.gitignore` before the first commit.
- No user personal data (name, age, sex) should be logged or persisted beyond the session.

### Code Style
- Keep all logic in the 4 files defined in Section 8.
- `app.py` handles UI and session state only — no direct LLM calls inside `app.py`.
- All LLM calls go through `llm.py`.

---

## Appendix: Intent Categories Reference

| Intent Key | Trigger Keywords (partial) | LLM Used | Emergency |
|---|---|---|---|
| `Emergency` | chest pain, difficulty breathing, severe bleeding, convulsion, unconscious | No | Yes |
| `Malaria` | malaria, fever, headache, chills, iba, body pain, zazzabi | Yes | No |
| `Immunization` | polio, vaccine, vaccination, immunization, ajesara | Yes | No |
| `Family Planning` | family planning, contraceptive, pills, birth control, implant | Yes | No |
| `Medication Safety` | antibiotics, self medication, can I take, without test | Yes | No |
| `General Health` | (default — no keyword match) | Yes | No |

---

*Last updated: May 2026 · Based on Chapter 3 Research Methodology · Framework: Context-Aware Multilingual Healthcare Chatbot for Nigerian Primary Healthcare Communication*
