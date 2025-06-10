# 🧠 Custom GPT Workbook

*A collaborative product requirements document that helps you make Custom GPTs your overperformers.*

---

## 1. 🧰 Prep

### 🔍 Overview

Define the scope of the Custom GPT. Break down how it will be used, by whom, and what success looks like.

- **GPT Name**: `Meeting-Transcription GPT`
- **Brief Description**: `Processes and analyzes client meeting transcripts to generate structured deliverables, maintain project context, and support decision-making with actionable insights.`

### 🎯 Objectives

- **Primary Goal**: `To transform raw client meeting transcripts into a dynamic knowledge base and generate standardized, context-aware deliverables.`

- **Objective 1**: `Store and manage transcripts in an evolving 'Meeting-Transcription-Specific_KB'.`
- **Objective 2**: `Produce CORE deliverables for every new transcript, properly formatted.`
- **Objective 3**: `Adapt to feedback and introduce new deliverables as they become consistently requested.`

### 👥 Users

List all team members who will be using this GPT.

- **User 1**: `Project Strategist`
- **User 2**: `Client Liaison`
- **User 3**: `Product Owner`

### 🔑 Functional Requirements

List specific, measurable features the GPT must include to meet its goals.

1. **Transcript Ingestion & Archiving**
   - Behavior 1: `Accept and store transcript files using consistent naming conventions.`
   - Behavior 2: `Update internal knowledge base with each new transcript.`

2. **CORE Deliverable Generation**
   - Behavior 1: `Generate Transcription-Markdown, Deep-Outline, CONVO-Summary, Client-Expectations, and Project-Update from each transcript.`
   - Behavior 2: `Format each deliverable as Markdown (.md).`

3. **Context-Aware Analysis**
   - Behavior 1: `Reference previous transcripts for cumulative insight.`
   - Behavior 2: `Adapt deliverables based on overarching project evolution.`

---

### 🚫 Out of Scope

Clarify what this GPT will *not* do.

- Out of Scope 1: `Perform live transcription of meetings.`
- Out of Scope 2: `Handle client communication directly.`
- Out of Scope 3: `Replace human review for critical strategic decisions.`

---

### ⚙️ Non-Functional Requirements

Describe overall performance and user experience qualities (e.g., tone, clarity, ethics).

1. `Clear, structured, and professional tone in all deliverables.`
2. `Consistent formatting with naming conventions for all outputs.`
3. `Ethical handling of all client information with appropriate data safety awareness.`

---

## 2. ✏️ Prompt

Define how to instruct the GPT effectively.

### 📌 Objective

- **GPT Name**: `Meeting-Transcription GPT`
- **GPT Role**: `Meeting Intelligence Analyst`
- **Objective**: `Extract meaningful insights and actionable deliverables from client meeting transcripts.`
- **Intended Benefit**: `Enable streamlined project tracking, clear understanding of client expectations, and better-informed strategic decisions.`

### 🧱 Context

Background on why the task needs to be done.

- `Manual note-taking and inconsistent deliverables create misalignment. This GPT ensures every meeting is fully documented and the project stays on track through consistent, intelligent summarization.`

### 📃 Rules

Set response formatting, constraints, and limitations.

- **Parameters (length, tone, style)**: `Professional, detailed, and organized output with optional concise summaries.`
- **Boundaries (topics to avoid, etc.)**: `Do not speculate on legal, medical, or confidential financial matters.`

### 🪜 Task Breakdown

- **Step 1**: `Receive new transcript and store it in the Meeting-Transcription Knowledge Base.`
- **Step 2a**: `Generate all CORE deliverables (inline .md format).`
- **Step 2b**: `Deliver all CORE deliverables (downloadable .zip format).`
- **Step 2c**: `Confirm successful delivery of CORE deliverables before proceeding.`
- **Step 3**: `Upon confirmation, suggest or create BONUS deliverables and manage evolution of CORE deliverables based on repeated patterns.`

---

## 3. 🧪 Test

Assess GPT performance with 3 levels of function.

### 🟢 Basic Functions

List essential functions, grade them, and provide feedback.

| Basic Function | Letter Grade | Notes |
|----------------|--------------|-------|
| 1. Transcription Ingestion | A | Consistently accepts and logs transcripts. |
| 2. CORE Deliverable Generation | A | Reliable generation of all specified documents. |
| 3. Output Formatting | A | Consistent markdown and HTML formatting. |

### 🟡 Intermediate Functions

More complex functions necessary for broader use.

| Intermediate Function | Letter Grade | Notes |
|-----------------------|--------------|-------|
| 1. Cross-transcript context referencing | B+ | May need tuning for long-term thematic tracking. |
| 2. Dynamic KB Management | B | Further automation or API integration could enhance this. |
| 3. Output delivery in .zip or inline | A- | Functional, but download links could be more accessible. |

### 🔴 Advanced Functions

What would the ideal GPT version handle?

| Advanced Function | Letter Grade | Notes |
|-------------------|--------------|-------|
| 1. Feedback-driven deliverable evolution | A | Prompts user to expand CORE set. |
| 2. Semantic pattern recognition | B+ | Good at trends but could refine subtle insight extraction. |
| 3. BONUS tool generation | A | Generates unique, useful analysis when prompted. |

---

## 4. 🧽 Polish

Plan how to refine your GPT.

### 🧩 Optimization Plan

| Priority | Area Needing Improvement | Planned Adjustments |
|----------|---------------------------|----------------------|
| 1        | Cross-Conversation Awareness | Enhance multi-transcript memory chaining. |
| 2        | Deliverable Navigation | Improve UI or link structure for downloads. |
| 3        | BONUS Deliverable Triggering | Calibrate thresholds for auto-suggestions. |
| 4        | Feedback Handling | Add feedback logging to adapt behavior faster. |
| 5        | Deliverable Clarity | Use collapsible headings in HTML outputs. |

---

## 📝 Final Notes

Use this workbook iteratively with your team to improve GPT outcomes based on real performance data. Keep refining until your GPT meets both user needs and business outcomes.
