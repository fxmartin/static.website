# Claude Agent SDK - Research Agent Demo: Deep Dive

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [How It Works Step-by-Step](#how-it-works-step-by-step)
4. [File Structure and Components](#file-structure-and-components)
5. [The Four Agents in Detail](#the-four-agents-in-detail)
6. [Key SDK Features Demonstrated](#key-sdk-features-demonstrated)
7. [Slash Commands and Skills](#slash-commands-and-skills)
8. [Observability: Hooks and Logging](#observability-hooks-and-logging)
9. [Comparison with Perplexity, ChatGPT, and Opus 4.6](#comparison-with-perplexity-chatgpt-and-opus-46)
10. [Strengths and Limitations](#strengths-and-limitations)

---

## Overview

The **Research Agent** is a multi-agent system built on the [Claude Agent SDK](https://platform.claude.com/docs/en/agent-sdk/overview) (Python). It demonstrates how to orchestrate multiple specialized AI subagents that collaborate to research any topic, produce data visualizations, and generate a polished PDF report — all from a single user prompt.

**Source**: [github.com/anthropics/claude-agent-sdk-demos/tree/main/research-agent](https://github.com/anthropics/claude-agent-sdk-demos/tree/main/research-agent)

### What It Produces

Given a prompt like *"Research quantum computing developments in 2025"*, the system:

1. Breaks the topic into 2–4 subtopics
2. Runs parallel web searches across those subtopics
3. Saves structured research notes (Markdown files packed with statistics)
4. Extracts quantitative data and generates matplotlib charts (PNG)
5. Synthesizes everything into a professional PDF report with embedded visuals

### Output Structure

```
files/
├── research_notes/     # Markdown files from researchers (one per subtopic)
├── data/               # data_summary.md from the analyst
├── charts/             # PNG visualizations (bar charts, line charts, etc.)
└── reports/            # Final PDF report (e.g., quantum_computing_report_20260225.pdf)

logs/
└── session_YYYYMMDD_HHMMSS/
    ├── transcript.txt      # Human-readable conversation log
    └── tool_calls.jsonl    # Structured tool usage log (JSON Lines)
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          USER PROMPT                                │
│              "Research quantum computing developments"              │
└─────────────────────────┬───────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    LEAD AGENT (Orchestrator)                        │
│                                                                     │
│  Model: claude-haiku-4-5                                           │
│  Tools: Task (only)                                                │
│  Role:  Decomposes topic → spawns subagents → coordinates flow     │
│                                                                     │
│  Rules:                                                             │
│  - NEVER researches, writes reports, or generates charts itself     │
│  - ONLY delegates via the Task tool                                 │
│  - Keeps responses to 2-3 sentences max                             │
└────┬────────────┬────────────┬────────────┬─────────────────────────┘
     │            │            │            │
     │  STEP 1: Spawn 2-4 researchers IN PARALLEL
     ▼            ▼            ▼            ▼
┌──────────┐┌──────────┐┌──────────┐┌──────────┐
│RESEARCHER││RESEARCHER││RESEARCHER││RESEARCHER│
│    -1    ││    -2    ││    -3    ││    -4    │
│          ││          ││          ││          │
│Tools:    ││Tools:    ││Tools:    ││Tools:    │
│WebSearch ││WebSearch ││WebSearch ││WebSearch │
│Write     ││Write     ││Write     ││Write     │
│          ││          ││          ││          │
│Model:    ││Model:    ││Model:    ││Model:    │
│haiku     ││haiku     ││haiku     ││haiku     │
└────┬─────┘└────┬─────┘└────┬─────┘└────┬─────┘
     │            │            │            │
     ▼            ▼            ▼            ▼
   files/research_notes/*.md  (one file per subtopic)
                          │
                          │  STEP 2: All researchers done
                          ▼
              ┌───────────────────────┐
              │   DATA ANALYST -1     │
              │                       │
              │ Tools: Glob, Read,    │
              │        Bash, Write    │
              │ Model: haiku          │
              │                       │
              │ Reads research notes  │
              │ Extracts numbers      │
              │ Generates matplotlib  │
              │ charts via Python     │
              └───────────┬───────────┘
                          │
                          ▼
              files/charts/*.png + files/data/data_summary.md
                          │
                          │  STEP 3: Analyst done
                          ▼
              ┌───────────────────────┐
              │   REPORT WRITER -1    │
              │                       │
              │ Tools: Skill, Write,  │
              │   Glob, Read, Bash    │
              │ Model: haiku          │
              │                       │
              │ Reads notes + charts  │
              │ Creates PDF via       │
              │ reportlab             │
              └───────────┬───────────┘
                          │
                          ▼
              files/reports/*_report_YYYYMMDD.pdf
```

The key insight: **the Lead Agent does zero actual work**. It only has access to the `Task` tool, which spawns subagents. Every piece of real work (searching, writing files, running Python scripts, creating PDFs) happens inside specialized subagents.

---

## How It Works Step-by-Step

### 1. Initialization (`agent.py`)

```python
async with ClaudeSDKClient(options=options) as client:
    while True:
        user_input = input("\nYou: ").strip()
        await client.query(prompt=user_input)
        async for msg in client.receive_response():
            # stream and process response
```

The entry point creates a `ClaudeSDKClient` with:
- **`permission_mode="bypassPermissions"`** — subagents can freely execute tools (web search, file writes, bash commands) without user confirmation
- **`system_prompt`** — loaded from `prompts/lead_agent.txt`
- **`allowed_tools=["Task"]`** — the lead agent can ONLY spawn subagents
- **`agents`** — a dictionary of 3 `AgentDefinition` objects (researcher, data-analyst, report-writer)
- **`hooks`** — pre/post tool-use hooks for observability
- **`model="haiku"`** — uses Claude Haiku for cost efficiency

### 2. User Sends a Query

The lead agent receives *"Research quantum computing developments"* and, following its system prompt, immediately:
- Breaks it into 2–4 subtopics (e.g., hardware/qubits, algorithms/applications, industry/investments, challenges/timeline)
- Spawns 2–4 `researcher` subagents **in parallel** using the `Task` tool

### 3. Researchers Search the Web

Each researcher subagent:
- Has access to **`WebSearch`** and **`Write`** tools only
- Runs 5–10 web searches with data-focused queries (adding terms like "statistics", "market size", "growth rate")
- Extracts every number, percentage, and metric from search results
- Writes a data-rich Markdown file to `files/research_notes/{topic}.md`
- Must include at least 10–15 specific statistics per file

### 4. Data Analyst Generates Charts

Once all researchers finish, the lead agent spawns a single `data-analyst` subagent that:
- Uses **`Glob`** to find all research notes
- Uses **`Read`** to load them
- Extracts quantitative data (market sizes, growth rates, rankings, etc.)
- Uses **`Bash`** to execute Python scripts with matplotlib that generate 2–4 charts
- Saves PNG charts to `files/charts/`
- Writes a `data_summary.md` to `files/data/`

### 5. Report Writer Creates the PDF

Finally, the lead agent spawns a `report-writer` subagent that:
- Reads all research notes, data summaries, and chart file paths
- Can invoke the **`Skill`** tool (specifically the "pdf" skill) for guidance on reportlab
- Uses **`Bash`** to run a Python script that creates a professional PDF using `reportlab`
- Embeds the chart PNGs into the PDF document
- Saves to `files/reports/{topic}_report_YYYYMMDD.pdf`

### 6. Completion

The lead agent reports back with a one-liner: *"Complete. PDF report: files/reports/quantum_computing_report_20260225.pdf"*

---

## File Structure and Components

```
research-agent/
├── pyproject.toml                          # Dependencies: claude-agent-sdk, python-dotenv
├── .env.example                            # ANTHROPIC_API_KEY placeholder
├── README.md                               # Project documentation
├── .gitignore
│
├── research_agent/
│   ├── agent.py                            # Main entry point — sets up SDK client, defines agents
│   │
│   ├── prompts/                            # System prompts for each agent role
│   │   ├── lead_agent.txt                  # Orchestrator instructions (176 lines)
│   │   ├── researcher.txt                  # Web research specialist instructions (179 lines)
│   │   ├── data_analyst.txt                # Chart generation specialist instructions (216 lines)
│   │   └── report_writer.txt               # PDF creation specialist instructions
│   │
│   └── utils/
│       ├── subagent_tracker.py             # Hook-based tool call tracking system
│       ├── transcript.py                   # Dual-output writer (console + file)
│       └── message_handler.py              # Message stream parser for subagent detection
│
└── .claude/
    ├── commands/                            # Slash commands for common workflows
    │   ├── research.md                     # /research <topic>
    │   ├── competitive-analysis.md         # /competitive-analysis <company>
    │   ├── market-trends.md                # /market-trends <industry>
    │   ├── fact-check.md                   # /fact-check <claim>
    │   └── summarize.md                    # /summarize
    │
    └── skills/
        ├── executive-briefing/SKILL.md     # Executive briefing format skill
        └── pdf/                            # PDF manipulation skill (reportlab, pypdf, etc.)
            ├── SKILL.md
            ├── FORMS.md
            ├── REFERENCE.md
            ├── LICENSE.txt
            └── scripts/                    # Helper scripts for PDF operations
```

---

## The Four Agents in Detail

### Lead Agent (Orchestrator)

| Property | Value |
|----------|-------|
| **Model** | Claude Haiku |
| **Tools** | `Task` only |
| **System Prompt** | `prompts/lead_agent.txt` (176 lines) |
| **Role** | Decompose, delegate, coordinate |

The lead agent's prompt is heavily structured with XML-like tags (`<role_definition>`, `<workflow>`, `<delegation_rules>`, `<parallel_spawning>`, `<response_style>`) that enforce:
- Breaking topics into 2–4 subtopics
- Spawning researchers **in parallel** (explicitly told never to do sequential)
- Waiting for each phase to complete before the next
- Keeping responses to 2–3 sentences max (no greetings, no emojis)
- Never doing any research, analysis, or writing itself

### Researcher Subagent

| Property | Value |
|----------|-------|
| **Model** | Claude Haiku |
| **Tools** | `WebSearch`, `Write` |
| **System Prompt** | `prompts/researcher.txt` (179 lines) |
| **Role** | Gather quantitative data from the web |

The researcher prompt is laser-focused on **quantitative data collection**. It demands:
- 5–10 web searches per task with data-focused query modifiers
- At least 10–15 specific numbers/statistics per research note
- Tables for comparative data (market share, rankings)
- Source URLs for all data points
- Structured output: Key Statistics, Market Data, Rankings & Comparisons, Trends & Projections, Sources

### Data Analyst Subagent

| Property | Value |
|----------|-------|
| **Model** | Claude Haiku |
| **Tools** | `Glob`, `Read`, `Bash`, `Write` |
| **System Prompt** | `prompts/data_analyst.txt` (216 lines) |
| **Role** | Transform research into charts |

The data analyst:
- Reads all research notes via Glob + Read
- Identifies 2–4 best visualization opportunities (bar, line, pie, horizontal bar)
- Generates charts by writing and executing Python/matplotlib scripts via Bash
- Saves charts at 150 DPI as PNGs
- Writes a `data_summary.md` referencing all generated charts

### Report Writer Subagent

| Property | Value |
|----------|-------|
| **Model** | Claude Haiku |
| **Tools** | `Skill`, `Write`, `Glob`, `Read`, `Bash` |
| **System Prompt** | `prompts/report_writer.txt` |
| **Role** | Synthesize everything into a PDF |

The report writer:
- Reads research notes, data summaries, and chart paths
- Can invoke the "pdf" skill for reportlab guidance
- Creates PDFs using Python/reportlab via Bash
- Embeds PNG charts into the document
- Adds proper headings, executive summary, citations, and sources

---

## Key SDK Features Demonstrated

### 1. `AgentDefinition` — Defining Specialized Subagents

```python
agents = {
    "researcher": AgentDefinition(
        description="Use this agent when you need to gather research information...",
        tools=["WebSearch", "Write"],
        prompt=researcher_prompt,
        model="haiku"
    ),
    # ... data-analyst, report-writer
}
```

Each `AgentDefinition` specifies:
- **`description`**: Tells the lead agent WHEN to use this subagent type
- **`tools`**: Restricts what the subagent can do (principle of least privilege)
- **`prompt`**: Full system prompt with detailed behavioral instructions
- **`model`**: Can use different models per agent (all use Haiku here for cost)

### 2. `Task` Tool — Spawning Subagents

The lead agent's only tool is `Task`, which creates a new Claude instance with the specified agent definition. The SDK handles:
- Running subagents as independent conversations
- Tool execution within each subagent's sandbox
- Returning results to the parent agent when done
- Parallel execution when multiple Task calls are made simultaneously

### 3. `HookMatcher` — Tool Call Observability

```python
hooks = {
    'PreToolUse': [
        HookMatcher(matcher=None, hooks=[tracker.pre_tool_use_hook])  # match ALL tools
    ],
    'PostToolUse': [
        HookMatcher(matcher=None, hooks=[tracker.post_tool_use_hook])
    ]
}
```

Hooks intercept every tool call before and after execution across ALL agents (including subagents). The `parent_tool_use_id` links each tool call to its originating subagent, enabling full tracing.

### 4. `Skill` Tool — Reusable Knowledge Packs

The `.claude/skills/pdf/` directory contains a comprehensive PDF manipulation guide that the report-writer can invoke via the `Skill` tool. Skills are reusable prompt modules that provide domain-specific expertise without bloating every agent's system prompt.

### 5. Slash Commands — Predefined Workflows

The `.claude/commands/` directory defines 5 slash commands (research, competitive-analysis, market-trends, fact-check, summarize) that expand into structured prompts with specific frameworks (e.g., the fact-check command includes a full verification methodology with TRUE/FALSE/PARTIALLY TRUE/MISLEADING/UNVERIFIABLE verdicts).

---

## Observability: Hooks and Logging

### SubagentTracker (`utils/subagent_tracker.py`)

The tracker maintains:
- **`sessions`**: Map of `parent_tool_use_id` → `SubagentSession` (tracks each spawned agent)
- **`tool_call_records`**: Map of `tool_use_id` → `ToolCallRecord` (tracks each tool invocation)
- **Counters**: Auto-generates unique IDs like `RESEARCHER-1`, `RESEARCHER-2`, `DATA-ANALYST-1`

### How Subagent Attribution Works

1. Lead agent spawns a researcher via `Task` tool → the `ToolUseBlock` has an `id` (e.g., `"toolu_abc123"`)
2. The `message_handler.py` detects the `Task` tool use and calls `tracker.register_subagent_spawn(tool_use_id=block.id, ...)`
3. Every subsequent `AssistantMessage` from that subagent includes `parent_tool_use_id = "toolu_abc123"`
4. The pre/post hooks check `self._current_parent_id` to attribute tool calls to the correct subagent

### Log Outputs

**`transcript.txt`** (human-readable):
```
[RESEARCHER-1] → WebSearch
    Input: query='quantum computing 2025 market size statistics'
[RESEARCHER-1] → Write
    Input: file='quantum_hardware.md' (4523 chars)
[DATA-ANALYST-1] → Bash
    Input: python3 matplotlib chart generation
```

**`tool_calls.jsonl`** (structured, machine-readable):
```json
{"event":"tool_call_start","agent_id":"RESEARCHER-1","tool_name":"WebSearch","tool_input":{"query":"..."}}
{"event":"tool_call_complete","success":true,"output_size":15234}
```

---

## Comparison with Perplexity, ChatGPT, and Opus 4.6

### Feature Matrix

| Capability | Research Agent (SDK) | Perplexity Research Mode | ChatGPT (with browsing) | Claude Opus 4.6 (direct) |
|---|---|---|---|---|
| **Architecture** | Multi-agent orchestration (4 specialized roles) | Single-agent with built-in search pipeline | Single-agent with browsing tool | Single-agent with tools |
| **Web search** | Via WebSearch tool (multiple parallel agents) | Native, deeply integrated | Bing-based browsing tool | WebSearch tool (single agent) |
| **Parallel research** | 2–4 researchers run simultaneously | Sequential internally (fast due to optimization) | Sequential browsing | Sequential (one search at a time) |
| **Data visualization** | Generates matplotlib charts (PNG) | No chart generation | Can generate charts via Code Interpreter | No native chart generation |
| **PDF output** | Professional PDF via reportlab | No PDF export (web/markdown only) | No native PDF (can generate via code) | No native PDF |
| **Customizability** | Fully customizable (prompts, tools, agents, hooks) | Zero customization | Limited (Custom GPTs, instructions) | System prompts only |
| **Cost model** | API usage (pay per token across all agents) | Subscription ($20/mo Pro) | Subscription ($20/mo Plus) | API usage (pay per token) |
| **Latency** | Higher (multiple agent turns, sequential phases) | Low (optimized single pipeline) | Medium (browsing can be slow) | Low-medium |
| **Source transparency** | Full tool call logs + JSONL audit trail | Inline citations with URLs | Inline citations | Inline citations |
| **Offline/self-hosted** | Yes (runs locally, needs API key) | No (SaaS only) | No (SaaS only) | Partial (API, but not self-hosted) |

### Detailed Comparison

#### vs. Perplexity Research Mode

**Perplexity** is the gold standard for fast, citation-rich research:
- **Speed**: Perplexity is significantly faster — it's a single optimized pipeline rather than 4+ sequential agent phases. A query that takes Perplexity ~10 seconds might take the Research Agent 2–5 minutes.
- **Citations**: Perplexity has inline citations deeply woven into its responses. The Research Agent stores source URLs in Markdown files but citation quality depends on the researcher prompt adherence.
- **Search quality**: Perplexity has a purpose-built search index and ranking system. The Research Agent uses generic web search via the API.
- **Output format**: Perplexity gives you a polished web page instantly. The Research Agent gives you a PDF with charts — better for formal deliverables, but much slower.
- **Depth**: The Research Agent can go deeper by design — 2–4 parallel researchers each doing 5–10 searches covers more ground than Perplexity's single-pass approach. However, Perplexity's search quality often compensates.
- **Customization**: The Research Agent is fully programmable — you can change prompts, add new agent types, modify the workflow. Perplexity is a black box.

**When to use which**:
- **Perplexity**: Quick answers, fact-finding, staying current, daily research needs
- **Research Agent**: Formal reports, deep multi-angle research, custom workflows, when you need PDF/chart deliverables

#### vs. ChatGPT (with Browsing & Code Interpreter)

**ChatGPT** (GPT-4o with tools) is the closest general-purpose equivalent:
- **Browsing**: ChatGPT browses one page at a time, sequentially. The Research Agent runs parallel searches across multiple subtopics simultaneously.
- **Code execution**: ChatGPT's Code Interpreter can generate charts similarly to the Data Analyst subagent, but the Research Agent's approach is more structured (dedicated analyst phase, consistent chart style).
- **Report quality**: ChatGPT tends to produce Markdown-formatted responses. The Research Agent produces actual PDF documents with embedded images — more suitable for professional distribution.
- **Workflow structure**: ChatGPT's approach is ad-hoc (the model decides when to search, when to code). The Research Agent enforces a rigid pipeline: Research → Analyze → Report. This consistency is valuable for repeatable processes.
- **Context management**: ChatGPT runs everything in one context window, which can get crowded with long research. The Research Agent distributes work across independent subagent contexts, avoiding context pollution.
- **Deep Research**: ChatGPT's "Deep Research" feature (available to Plus/Pro subscribers) is more comparable — it also does multi-step research over several minutes. However, it's not programmable or customizable.

**When to use which**:
- **ChatGPT**: Interactive research sessions, iterative Q&A, when you want to steer the research in real-time
- **Research Agent**: Automated report generation, batch research, when you need reproducible structured output

#### vs. Claude Opus 4.6 (Direct / Claude Code)

**Claude Opus 4.6** used directly (via API or Claude Code) is the same underlying model, but single-agent:
- **Intelligence**: Opus 4.6 is a more capable model than Haiku (which the Research Agent uses for all agents). A single Opus query might produce higher-quality reasoning than 4 Haiku subagents combined.
- **Efficiency**: Direct Opus usage is simpler — no orchestration overhead, no sequential phase bottlenecks. But it can only run one search at a time.
- **Cost**: The Research Agent using Haiku for all agents is much cheaper per token than Opus. However, the multi-agent overhead (multiple conversations, repeated context) may offset this. The total token usage across 6+ agent invocations could approach or exceed a single detailed Opus response.
- **Depth**: Opus with extended thinking can produce extraordinarily deep analysis from a single prompt. The Research Agent's depth comes from breadth (multiple angles, more searches) rather than reasoning depth.
- **Output**: Direct Opus gives you text. The Research Agent gives you files: Markdown notes, PNG charts, PDF report — tangible artifacts.
- **Programmability**: The Research Agent demonstrates patterns (multi-agent, hooks, skills) that are impossible with a single Opus call. It's a framework, not just a query.

**When to use which**:
- **Opus 4.6 direct**: Complex reasoning tasks, nuanced analysis, one-shot deep thinking, when quality of reasoning matters more than breadth
- **Research Agent**: When you need structured deliverables (PDF + charts), parallel information gathering, automated pipelines, or are building a product on top of the SDK

### Cost Comparison (Estimated)

For a typical research query generating a 2-page PDF report:

| System | Estimated Cost | Estimated Time |
|--------|---------------|----------------|
| Research Agent (Haiku) | ~$0.10–0.30 (across all agents) | 2–5 minutes |
| Perplexity Pro | Included in $20/mo subscription | 10–30 seconds |
| ChatGPT Plus | Included in $20/mo subscription | 1–3 minutes (Deep Research) |
| Opus 4.6 (single query) | ~$0.15–0.50 (one response) | 30–90 seconds |

---

## Strengths and Limitations

### Strengths

1. **Separation of concerns**: Each agent has a clear, focused role with restricted tool access. This makes the system predictable and auditable.
2. **Parallel execution**: Multiple researchers run simultaneously, covering more ground faster than a single agent could.
3. **Full observability**: The hook system + JSONL logging provides a complete audit trail of every tool call across every agent.
4. **Tangible output**: Produces real files (Markdown notes, PNG charts, PDF reports) rather than ephemeral chat responses.
5. **Customizable**: Every aspect (prompts, tools, number of agents, workflow) can be modified. You could add a "fact-checker" agent, change the chart style, or swap in a different report format.
6. **Cost-efficient model choice**: Using Haiku for all agents keeps per-token costs low while leveraging the SDK's orchestration for quality.

### Limitations

1. **Latency**: The sequential pipeline (research → analysis → report) takes 2–5 minutes. Each phase must complete before the next begins.
2. **No iterative refinement**: Unlike a human researcher who goes back and forth, the pipeline is one-shot. If the research phase misses something, the report won't include it.
3. **Haiku reasoning limits**: Using Haiku for all agents means each individual agent has less reasoning power than Sonnet or Opus would provide. Complex analytical tasks may suffer.
4. **Search quality dependency**: The quality of the final report is bounded by what WebSearch returns. Bad search results → bad report.
5. **No user interaction mid-flow**: Once launched, the pipeline runs to completion. You can't redirect a researcher mid-search or ask the analyst to focus on different data.
6. **Local execution only**: The demo is designed for local development. Production deployment would require additional infrastructure, error handling, and rate limiting.

---

## Summary

The Claude Agent SDK Research Agent demo is a compelling reference implementation for **multi-agent orchestration**. It shows how to:

- Define specialized agents with restricted tool sets
- Coordinate parallel and sequential workflows via a lead orchestrator
- Use hooks for comprehensive observability
- Leverage skills and slash commands for reusable workflows
- Produce tangible file artifacts (not just chat responses)

It's not meant to replace Perplexity or ChatGPT for quick research — it's meant to demonstrate the **architecture patterns** that enable building custom, production-grade research systems. The real value is in the pattern, not the demo itself.
