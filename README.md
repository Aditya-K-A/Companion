# Companion

> **Status: Active Development**

Companion is an AI companion designed for warm, emotionally attentive conversation with support for both **platonic and romantic companionship**.

The system combines conversational context, persistent memory, mood tracking, communication-preference learning, and a dedicated safety layer to provide context-aware interactions while maintaining boundaries around dependency, diagnosis, and crisis handling.

---

## ✨ Features

- Warm, non-judgmental, active-listening conversations
- Platonic and romantic companionship
- Short-term conversational memory
- Persistent long-term memory across sessions
- Semantic retrieval of relevant memories
- Communication-preference learning
  - Listening / venting
  - Problem-solving / advice
- Persistent mood tracking and history
- User-provided daily mood check-ins
- Crisis-language detection and safety bypass
- Healthy-engagement safeguards
- Local SQLite + ChromaDB persistence
- Configurable LLM provider architecture

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| UI | Streamlit |
| LLM | Google Gemini |
| LLM Integration | Google GenAI SDK |
| Long-term structured storage | SQLite |
| Semantic memory | ChromaDB |
| Configuration | Pydantic Settings |
| Language | Python |

---

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone <repository-url>
cd companion
```

### 2. Create a virtual environment

**Windows**

```powershell
python -m venv .venv
.venv\Scripts\activate
```

**Linux / macOS**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Gemini

Create a `.env` file:

```env
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=your_model_name
```

### 5. Run

```bash
streamlit run streamlit_app.py
```

SQLite and ChromaDB data are persisted locally.

---

## 🧠 Memory & Personalization

### Long-term Memory

SQLite stores structured information such as memories, mood events, confidence values, and timestamps.

ChromaDB provides semantic retrieval so that only memories relevant to the current conversation are brought into context rather than sending the entire memory store to the LLM.

Memory extraction is intentionally conservative. The system selectively extracts useful information such as personal facts, relationships, important events, interests, recurring problems, and communication preferences while avoiding unnecessary conversational details or unsupported assumptions.

Exact duplicate memories are prevented from being repeatedly stored.

### Mood Tracking

Mood information can come from both:

1. **Conversational inference**, where the system extracts an observed emotion and intensity from the conversation.
2. **Explicit user check-ins**, where the user directly selects their emotion and intensity through the UI.

Mood history is persisted and summarized before being provided to the LLM as conversational context.

The system treats mood information as context, **not as a diagnosis**.

### Communication Preferences

The companion can gradually learn whether the user generally prefers:

- Emotional listening and space to vent, or
- Practical advice and problem-solving.

This allows the response style to adapt without requiring the user to explicitly configure a permanent preference.

---

## 🛡️ Safety & Crisis Handling

Safety is handled **before normal LLM generation**.

The current prototype uses a lightweight deterministic, phrase-based crisis detector. If explicit crisis language is detected, the normal conversational path is bypassed and a predefined supportive crisis response is returned.

```text
User Message
     │
     ▼
Crisis Detector
     │
     ├── Crisis → Safety Response
     │
     └── Normal → Gemini
```

### Why a deterministic detector?

For the current prototype, this approach provides:

- Very low latency
- No additional LLM/API call
- Predictable behavior
- Easy auditing
- Simple implementation

Running another LLM for every user message would introduce additional latency and cost even when the conversation is completely normal. This is particularly relevant because Companion also supports ordinary platonic and romantic conversations.

The detector is intentionally conservative in scope: it is designed to identify explicit crisis-language signals rather than infer a user's overall mental-health state.

### Limitations

Phrase-based detection can produce both:

- **False negatives:** a crisis statement may use language not covered by the detector.
- **False positives:** a phrase may occur in a non-crisis context.

The current detector should therefore be considered a lightweight crisis-language safeguard, **not a clinical risk assessment or diagnosis**.

The crisis response currently uses a **resource placeholder**, as specified by the assignment. A production implementation could resolve location-appropriate crisis resources or integrate with an appropriate emergency-support service.

---

## 🤝 Healthy Engagement & Boundaries

Companion is intentionally designed not to maximize engagement at the expense of user wellbeing.

The system avoids:

- Guilt-tripping users for leaving
- Manufactured urgency
- Dependency-oriented engagement tactics
- Presenting the AI as a replacement for human relationships
- Medical or psychiatric diagnosis
- Sexual roleplay

Where appropriate, the companion can gently encourage connection with friends, family, community, or professional support.

---

## 🏗️ Key Design Decisions

### Gemini behind an LLM abstraction

The LLM integration is separated behind a provider interface so that different models/providers can be evaluated without rewriting the rest of the application.

### SQLite + ChromaDB

SQLite handles structured persistent state, while ChromaDB handles semantic memory retrieval. This keeps deterministic data operations separate from similarity-based retrieval.

### Safety before generation

Safety checks happen before the normal LLM pipeline so that an explicit crisis signal does not depend on the conversational model correctly deciding how to respond.

### Explicit + inferred mood

User-provided mood is treated as a direct signal, while conversational mood is treated as an inferred signal with associated confidence.

### No agent framework

The current workflow is intentionally kept as explicit orchestration rather than introducing an agent framework. The current problem does not require autonomous tool selection or complex routing, so adding another abstraction layer would increase complexity without enough benefit at this stage.

---

## 🔮 Future Enhancements

The current implementation is intentionally scoped as a prototype. With additional time and resources, I would prioritize:

- **Hybrid crisis detection:** combine deterministic phrase detection with a lightweight local binary ML classifier to improve semantic coverage while retaining the low-latency deterministic path. The deterministic layer would remain the first-pass fast path, while the local classifier could improve coverage of semantic paraphrases without requiring another remote LLM call.
- **Improved safety evaluation:** build a dedicated evaluation set covering indirect crisis language, negation, historical statements, third-person references, and non-suicidal distress.
- **Semantic memory deduplication:** identify and merge memories that are semantically equivalent rather than only exact duplicates.
- **Location-aware crisis resources:** provide region-appropriate crisis and emergency resources rather than relying on a generic placeholder.
- **Mood visualization:** allow users to optionally review their mood history over time.
- **Production infrastructure and evaluation:** move beyond local persistence and introduce stronger privacy, security, multi-user infrastructure, and automated evaluation for memory retrieval, emotional response quality, safety detection, and preference adaptation.

---

## ⚠️ Limitations

This is an **active-development prototype**, not a clinical, therapeutic, or emergency-support system.

In particular:

- Mood inference is not diagnosis.
- Crisis detection is not clinical risk assessment.
- LLM responses may still occasionally be inappropriate or overly reassuring.
- Long-term memory extraction is probabilistic and may be imperfect.
- The current crisis detector has limited semantic coverage.
- Persistent memory requires additional privacy and security considerations for production deployment.

Companion is intended to provide supportive conversation and companionship, **not to replace human relationships, professional care, or emergency services.**
