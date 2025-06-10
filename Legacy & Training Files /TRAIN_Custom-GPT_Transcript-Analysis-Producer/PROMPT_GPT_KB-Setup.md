**📚 Meeting-Transcription-Specific_KB Setup & Maintenance Guide**  
*How to build and evolve the dynamic knowledge base your GPT relies on*

---

### ⏱️ 00:00 – Purpose of the KB

The `Meeting-Transcription-Specific_KB` is a **living, structured textdoc** that captures essential project-specific data—facts, phrasing, insights, and evolving themes—from client meeting transcripts and supplementary materials. This persistent reference ensures GPT can consistently produce accurate, aligned, and context-aware outputs.

---

### 🛠️ 00:01 – Initial Setup Phase

#### ✅ Step 1: Create the Knowledge Base Document
- **Name:** `Meeting-Transcription-Specific_KB`
- **Type:** `document`
- **Initial Template:**
  ```markdown
  # 🧠 Meeting Transcription Specific Knowledge Base
  > 📎 GPT should extract and organize key project elements from each transcript submission.

  ## 🔑 Brand Phrases & Established Timelines
  -

  ## 📝 Approved Stats & Claims
  -

  ## 🧩 Tasks, Pillars & Focus Areas
  -

  ## 🎯 Target Personas, Pain Points & Expectations
  -

  ## 📌 Competitor Voice Notes
  -

  ## 📚 Attached Client Docs + Transcript Reference
  - [SDG_yyyymmdd] - brief title/summary here
  ```

#### ✅ Step 2: Define Entry Format for Each Transcript
- Use the following naming and structure to ensure clarity:
  ```markdown
  ### Entry: [SDG_yyyymmdd_ClientMeeting]

  - **Insight Type:** [Insight description or quote]
  - **Client Expectation:** [Direct quote or paraphrased task/goal]
  - **Thematic Cue:** [Tag for tracking recurring topics]
  - **Notes:** [Contextual relevance or connection to prior sessions]
  ```

#### ✅ Step 3: Link Transcripts
- Include direct quote snippets or high-level summaries from:
  - `[ClientName_yyyymmdd.txt]` (e.g., SDG_20250508.txt)

---

### 🔁 00:02 – Maintenance Phase

#### 🔄 How to Add New Content:
When new media is submitted:
- **Client Meeting Transcription** → Extract as per entry format above.
- **Case Study** → Summarize outcomes and metrics.
- **White Paper or Slide Deck** → Pull key claims or CTAs.
- **Internal Memo** → Capture rationale, compliance language, or terminology.

> 📎 Use the command: “Ingest this doc into the KB”  
> GPT will extract and insert information using the standardized entry format.

#### 📅 Recommended Update Schedule:
- **Monthly Quick Review:** Spot and remove irrelevant items.
- **Quarterly KB Audit:** Refresh deliverables, stats, tone. Consider reorganizing high-usage insights into "pinned" categories.

---

### 🤖 00:03 – GPT Capabilities Using the KB

GPT will:
- **Auto-reference past insights** when building deliverables.
- **Maintain cross-convo context** across multiple transcripts.
- **Recognize recurring topics or shifts in tone** to improve predictive suggestions.
- **Minimize hallucinations** by citing consistent source data from the KB.
- **Adapt formatting** based on structure and client-aligned phrasing stored within.

---

### 🧠 00:04 – Optional Feedback & Structure Evolution

As your project develops:
- After **3 repeat inclusions** of a BONUS deliverable (e.g., `Flow-Chart-Legend`), GPT may prompt:
  > “Would you like to add 'Flow-Chart-Legend' to the list of CORE Deliverables?”
- To remove any section or modify structure, use:
  > “Update the KB structure to include/remove [Section Name].”
- Use feedback loops to improve the document’s usability and strategic value.

---

### ✅ Top 5 KB Success Practices

1. **Use short entries, consistently tagged** for ease of reference.
2. **Keep evolving the format**—make it yours, not static.
3. **Feed it frequently**—more entries = smarter GPT output.
4. **Keep hierarchy clean**—top-level headings for categories, sub-bullets for nuance.
5. **Let GPT help maintain it**—it’s your analyst, not just your assistant.

---
