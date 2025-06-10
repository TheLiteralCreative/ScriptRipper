# 🧠 CORE Deliverables for Transcript Intelligence

**Source**: System Instruction · **Last Updated**: 2025-05-11
**Purpose**: Defines the structure, purpose, and unique logic for each GPT-generated deliverable. Serves as a reference model for all transcript-based outputs.

---

## 🔄 1. Transcription Markdown

**Purpose**: Foundational deliverable that transforms a raw transcript into structured, clean Markdown.

**Key Features**:
- Timecode-aligned summaries
- Speaker-tagged commentary
- Technical clarity + readability
- Markdown-optimized formatting
- Clean export for .md, docs, or web use

**Long-Term Uses**:
- Training LLM agents
- Source for blogs/podcasts
- Client proof-of-work
- Citation-ready history
- Conflict resolution + recall
- Onboarding context

---

## 📘 2. Deep-Outline

**Purpose**: Strategic blueprint of the full conversation. Built with timestamp segments, it reveals logical flow, decisions, and concept arcs.

**Key Features**:
- Chronological segments
- System architecture insights
- Technical recommendations
- Quote, CTA, and takeaways

**Best For**:
- Product planning
- Sprint scoping
- Architecting implementation flows

---

## 🧾 3. CONVO-Summary

**Purpose**: Executive-friendly one-pager summarizing the meeting’s essence: tone, purpose, themes, and decisions.

**Key Features**:
- No timestamps
- Narrative style
- Mood & tone metadata
- Quote highlight + forward motion

**Best For**:
- Strategic alignment
- Partner onboarding
- Briefing stakeholders

---

## 📋 4. Client-Expectations

**Purpose**: Translates conversation into a scoped expectations document — short-term tasks, long-term goals, constraints, and tools.

**Key Features**:
- Two-section format: Tactical + Vision
- Framed in client’s voice and logic
- Clear formatting of formats, timelines, and value signals

**Best For**:
- Consultants, contractors, PMs
- Weekly scoping and sprint validation

---

## 🗃️ 5. Project-Update

**Purpose**: Long-memory synthesis that grows with every transcript. Captures progress, contradictions, history, and metrics across all sessions.

**Key Features**:
- Comparative patterns across time
- Strategic drift detection
- Timeline and deadline recall
- KB signal integration
- Memory-aware insight referencing

**Best For**:
- OKR alignment
- Stakeholder retrospectives
- Accountability tracking
- High-context decision support

**Examples of what it tracks**:
- 📆 Milestones and slippage
- 🔁 Stalled or repeated ideas
- 📊 Performance indicators
- 📍 Forgotten “side quests”
- 🧠 Vocabulary evolution
- 🤝 Role shifts and task ownership

---

## 🧠 Summary

> These 5 deliverables represent a complete intelligence system for transforming meeting transcripts into structured knowledge.
> Each one offers a different strategic lens — together, they convert conversation into continuity, and memory into momentum.

---

## 📂 File Output Standards

| Deliverable         | Naming Format                            |
|---------------------|-------------------------------------------|
| Transcription       | `[Client]_[Date]_Transcription.md`        |
| Deep-Outline        | `[Client]_[Date]_Deep-Outline.md`         |
| CONVO-Summary       | `[Client]_[Date]_CONVO-Summary.md`        |
| Client-Expectations | `[Client]_[Date]_Client-Expectations.md`  |
| Project-Update      | `[Client]_[Date]_Project-Update.md`       |

---
