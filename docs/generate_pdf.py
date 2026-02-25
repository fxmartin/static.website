"""Generate a professional PDF from the research-agent-explained.md content."""

import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether, HRFlowable
)
from reportlab.platypus.flowables import Flowable


# ── Colors ──────────────────────────────────────────────────────────
DARK = HexColor("#1a1a2e")
ACCENT = HexColor("#3a86ff")
ACCENT_LIGHT = HexColor("#e8f0fe")
GRAY = HexColor("#4a4a6a")
LIGHT_GRAY = HexColor("#f0f0f5")
MID_GRAY = HexColor("#666680")
TABLE_HEADER_BG = HexColor("#2d2d5e")
TABLE_ALT_ROW = HexColor("#f5f5fa")
CODE_BG = HexColor("#f8f8fc")


# ── Custom flowable for the architecture diagram ────────────────────
class ArchitectureDiagram(Flowable):
    """Draw the multi-agent architecture as a visual diagram."""

    def __init__(self, width=460, height=340):
        Flowable.__init__(self)
        self.width = width
        self.height = height

    def draw(self):
        c = self.canv
        w, h = self.width, self.height

        # Background
        c.setFillColor(HexColor("#fafafe"))
        c.setStrokeColor(HexColor("#e0e0e8"))
        c.roundRect(0, 0, w, h, 8, fill=1, stroke=1)

        # ── User Prompt box ──
        c.setFillColor(ACCENT)
        c.roundRect(130, h - 45, 200, 30, 6, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(230, h - 35, "USER PROMPT")

        # Arrow down
        c.setStrokeColor(GRAY)
        c.setLineWidth(1.5)
        c.line(230, h - 45, 230, h - 65)
        c.line(225, h - 60, 230, h - 65)
        c.line(235, h - 60, 230, h - 65)

        # ── Lead Agent box ──
        c.setFillColor(TABLE_HEADER_BG)
        c.roundRect(100, h - 115, 260, 45, 6, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 11)
        c.drawCentredString(230, h - 88, "LEAD AGENT (Orchestrator)")
        c.setFont("Helvetica", 8)
        c.drawCentredString(230, h - 100, "Model: Haiku  |  Tools: Task only")

        # Arrows to researchers
        y_research = h - 135
        positions = [60, 160, 260, 360]
        labels = ["RESEARCHER-1", "RESEARCHER-2", "RESEARCHER-3", "RESEARCHER-4"]
        for x in positions:
            c.setStrokeColor(ACCENT)
            c.setLineWidth(1)
            c.line(230, h - 115, x + 50, y_research)

        # ── Researcher boxes ──
        for i, (x, label) in enumerate(zip(positions, labels)):
            c.setFillColor(HexColor("#4a9eff"))
            c.roundRect(x, y_research - 40, 100, 38, 5, fill=1, stroke=0)
            c.setFillColor(white)
            c.setFont("Helvetica-Bold", 7.5)
            c.drawCentredString(x + 50, y_research - 17, label)
            c.setFont("Helvetica", 6.5)
            c.drawCentredString(x + 50, y_research - 27, "WebSearch + Write")

        # Step label
        c.setFillColor(ACCENT)
        c.setFont("Helvetica-BoldOblique", 7)
        c.drawString(10, y_research - 15, "STEP 1")
        c.setFont("Helvetica-Oblique", 6.5)
        c.drawString(10, y_research - 25, "Parallel")

        # Arrow down to files
        y_files = y_research - 60
        c.setStrokeColor(GRAY)
        c.setLineWidth(1)
        c.line(230, y_research - 42, 230, y_files + 15)
        c.setFillColor(HexColor("#e8e8f0"))
        c.roundRect(140, y_files - 5, 180, 18, 4, fill=1, stroke=0)
        c.setFillColor(MID_GRAY)
        c.setFont("Helvetica-Oblique", 8)
        c.drawCentredString(230, y_files, "files/research_notes/*.md")

        # Arrow to Data Analyst
        y_analyst = y_files - 55
        c.setStrokeColor(GRAY)
        c.line(230, y_files - 7, 230, y_analyst + 38)

        # ── Data Analyst box ──
        c.setFillColor(HexColor("#7c3aed"))
        c.roundRect(130, y_analyst, 200, 38, 5, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(230, y_analyst + 22, "DATA ANALYST -1")
        c.setFont("Helvetica", 7)
        c.drawCentredString(230, y_analyst + 10, "Glob, Read, Bash, Write  |  matplotlib")

        c.setFillColor(ACCENT)
        c.setFont("Helvetica-BoldOblique", 7)
        c.drawString(10, y_analyst + 18, "STEP 2")
        c.setFont("Helvetica-Oblique", 6.5)
        c.drawString(10, y_analyst + 8, "Charts")

        # Arrow to charts
        y_charts = y_analyst - 25
        c.setStrokeColor(GRAY)
        c.line(230, y_analyst, 230, y_charts + 15)
        c.setFillColor(HexColor("#e8e8f0"))
        c.roundRect(120, y_charts - 5, 220, 18, 4, fill=1, stroke=0)
        c.setFillColor(MID_GRAY)
        c.setFont("Helvetica-Oblique", 8)
        c.drawCentredString(230, y_charts, "files/charts/*.png + data_summary.md")

        # Arrow to Report Writer
        y_writer = y_charts - 50
        c.setStrokeColor(GRAY)
        c.line(230, y_charts - 7, 230, y_writer + 38)

        # ── Report Writer box ──
        c.setFillColor(HexColor("#059669"))
        c.roundRect(130, y_writer, 200, 38, 5, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(230, y_writer + 22, "REPORT WRITER -1")
        c.setFont("Helvetica", 7)
        c.drawCentredString(230, y_writer + 10, "Skill, Write, Glob, Read, Bash  |  reportlab")

        c.setFillColor(ACCENT)
        c.setFont("Helvetica-BoldOblique", 7)
        c.drawString(10, y_writer + 18, "STEP 3")
        c.setFont("Helvetica-Oblique", 6.5)
        c.drawString(10, y_writer + 8, "PDF")

        # Final output
        y_output = y_writer - 30
        c.setStrokeColor(GRAY)
        c.line(230, y_writer, 230, y_output + 15)
        c.setFillColor(ACCENT)
        c.roundRect(120, y_output - 5, 220, 20, 5, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(230, y_output + 1, "files/reports/*_report.pdf")


def build_pdf(output_path):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=54, leftMargin=54,
        topMargin=54, bottomMargin=54,
    )

    styles = getSampleStyleSheet()

    # ── Custom styles ───────────────────────────────────────────────
    styles.add(ParagraphStyle(
        name="CoverTitle", fontName="Helvetica-Bold", fontSize=28,
        textColor=DARK, alignment=TA_CENTER, spaceAfter=8, leading=34
    ))
    styles.add(ParagraphStyle(
        name="CoverSubtitle", fontName="Helvetica", fontSize=14,
        textColor=GRAY, alignment=TA_CENTER, spaceAfter=4, leading=20
    ))
    styles.add(ParagraphStyle(
        name="CoverDate", fontName="Helvetica-Oblique", fontSize=10,
        textColor=MID_GRAY, alignment=TA_CENTER, spaceAfter=20
    ))
    styles.add(ParagraphStyle(
        name="SectionTitle", fontName="Helvetica-Bold", fontSize=18,
        textColor=DARK, spaceBefore=24, spaceAfter=10, leading=22
    ))
    styles.add(ParagraphStyle(
        name="SubSection", fontName="Helvetica-Bold", fontSize=13,
        textColor=HexColor("#2d2d5e"), spaceBefore=16, spaceAfter=6, leading=17
    ))
    styles.add(ParagraphStyle(
        name="SubSubSection", fontName="Helvetica-Bold", fontSize=11,
        textColor=GRAY, spaceBefore=12, spaceAfter=4, leading=14
    ))
    styles.add(ParagraphStyle(
        name="Body", fontName="Helvetica", fontSize=10,
        textColor=HexColor("#333355"), alignment=TA_JUSTIFY,
        spaceAfter=6, leading=14
    ))
    styles.add(ParagraphStyle(
        name="BulletCustom", fontName="Helvetica", fontSize=10,
        textColor=HexColor("#333355"), alignment=TA_LEFT,
        leftIndent=18, spaceAfter=3, leading=13,
        bulletFontName="Helvetica", bulletFontSize=10,
        bulletIndent=6
    ))
    styles.add(ParagraphStyle(
        name="CodeBlock", fontName="Courier", fontSize=7.5,
        textColor=HexColor("#333355"), backColor=CODE_BG,
        leftIndent=12, rightIndent=12, spaceBefore=4, spaceAfter=6,
        leading=10
    ))
    styles.add(ParagraphStyle(
        name="Caption", fontName="Helvetica-Oblique", fontSize=9,
        textColor=MID_GRAY, alignment=TA_CENTER, spaceAfter=12
    ))
    styles.add(ParagraphStyle(
        name="TableHeader", fontName="Helvetica-Bold", fontSize=8.5,
        textColor=white, alignment=TA_LEFT, leading=11
    ))
    styles.add(ParagraphStyle(
        name="TableCell", fontName="Helvetica", fontSize=8,
        textColor=HexColor("#333355"), alignment=TA_LEFT, leading=11
    ))
    styles.add(ParagraphStyle(
        name="SmallBold", fontName="Helvetica-Bold", fontSize=8.5,
        textColor=HexColor("#333355"), alignment=TA_LEFT, leading=11
    ))
    styles.add(ParagraphStyle(
        name="TOCEntry", fontName="Helvetica", fontSize=11,
        textColor=ACCENT, spaceBefore=4, spaceAfter=4, leftIndent=12, leading=16
    ))
    styles.add(ParagraphStyle(
        name="WhenToUse", fontName="Helvetica-Oblique", fontSize=9.5,
        textColor=HexColor("#444466"), leftIndent=12, spaceAfter=3, leading=13
    ))

    story = []

    # ═══════════════════════════════════════════════════════════════
    # COVER PAGE
    # ═══════════════════════════════════════════════════════════════
    story.append(Spacer(1, 2 * inch))
    story.append(Paragraph("Claude Agent SDK", styles["CoverTitle"]))
    story.append(Paragraph("Research Agent Demo", styles["CoverTitle"]))
    story.append(Spacer(1, 0.3 * inch))
    story.append(HRFlowable(width="40%", thickness=2, color=ACCENT, spaceAfter=12))
    story.append(Paragraph("A Deep Dive into Multi-Agent Orchestration", styles["CoverSubtitle"]))
    story.append(Paragraph("Architecture, Implementation &amp; Comparison with<br/>Perplexity, ChatGPT, and Claude Opus 4.6", styles["CoverSubtitle"]))
    story.append(Spacer(1, 0.5 * inch))
    story.append(Paragraph(datetime.now().strftime("Generated %B %d, %Y"), styles["CoverDate"]))
    story.append(Paragraph("Source: github.com/anthropics/claude-agent-sdk-demos/research-agent", styles["CoverDate"]))
    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════════════
    # TABLE OF CONTENTS
    # ═══════════════════════════════════════════════════════════════
    story.append(Paragraph("Table of Contents", styles["SectionTitle"]))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT_LIGHT, spaceAfter=12))
    toc_items = [
        "1. Overview",
        "2. Architecture Diagram",
        "3. How It Works Step-by-Step",
        "4. File Structure",
        "5. The Four Agents in Detail",
        "6. Key SDK Features",
        "7. Observability: Hooks and Logging",
        "8. Comparison: Perplexity, ChatGPT, Opus 4.6",
        "9. Cost Comparison",
        "10. Strengths and Limitations",
    ]
    for item in toc_items:
        story.append(Paragraph(item, styles["TOCEntry"]))
    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════════════
    # 1. OVERVIEW
    # ═══════════════════════════════════════════════════════════════
    story.append(Paragraph("1. Overview", styles["SectionTitle"]))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT_LIGHT, spaceAfter=8))

    story.append(Paragraph(
        "The <b>Research Agent</b> is a multi-agent system built on the "
        "<font color='#3a86ff'>Claude Agent SDK</font> (Python). It demonstrates how to "
        "orchestrate multiple specialized AI subagents that collaborate to research any topic, "
        "produce data visualizations, and generate a polished PDF report — all from a single user prompt.",
        styles["Body"]
    ))

    story.append(Paragraph("What It Produces", styles["SubSection"]))
    story.append(Paragraph(
        'Given a prompt like <i>"Research quantum computing developments in 2025"</i>, the system:',
        styles["Body"]
    ))
    steps = [
        "Breaks the topic into 2–4 subtopics",
        "Runs parallel web searches across those subtopics via multiple Researcher agents",
        "Saves structured research notes (Markdown files packed with statistics)",
        "Extracts quantitative data and generates matplotlib charts (PNG)",
        "Synthesizes everything into a professional PDF report with embedded visuals",
    ]
    for s in steps:
        story.append(Paragraph(f"• {s}", styles["BulletCustom"]))

    story.append(Paragraph("Output Structure", styles["SubSection"]))
    output_lines = [
        "<b>files/research_notes/</b> — Markdown files from researchers (one per subtopic)",
        "<b>files/data/</b> — data_summary.md from the analyst",
        "<b>files/charts/</b> — PNG visualizations (bar charts, line charts, etc.)",
        "<b>files/reports/</b> — Final PDF report",
        "<b>logs/session_*/transcript.txt</b> — Human-readable conversation log",
        "<b>logs/session_*/tool_calls.jsonl</b> — Structured tool usage log",
    ]
    for line in output_lines:
        story.append(Paragraph(f"• {line}", styles["BulletCustom"]))

    # ═══════════════════════════════════════════════════════════════
    # 2. ARCHITECTURE DIAGRAM
    # ═══════════════════════════════════════════════════════════════
    story.append(Spacer(1, 0.15 * inch))
    story.append(Paragraph("2. Architecture", styles["SectionTitle"]))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT_LIGHT, spaceAfter=8))

    story.append(Paragraph(
        "The key design insight: <b>the Lead Agent does zero actual work</b>. It only has access to "
        "the <font name='Courier'>Task</font> tool, which spawns subagents. Every piece of real work "
        "(searching, writing files, running Python scripts, creating PDFs) happens inside specialized subagents.",
        styles["Body"]
    ))
    story.append(Spacer(1, 0.1 * inch))
    story.append(ArchitectureDiagram(width=460, height=340))
    story.append(Paragraph("Figure 1: Multi-agent pipeline — parallel research, sequential analysis and reporting", styles["Caption"]))

    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════════════
    # 3. HOW IT WORKS
    # ═══════════════════════════════════════════════════════════════
    story.append(Paragraph("3. How It Works Step-by-Step", styles["SectionTitle"]))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT_LIGHT, spaceAfter=8))

    how_steps = [
        ("Initialization", "The entry point (agent.py) creates a ClaudeSDKClient configured with: permission_mode=\"bypassPermissions\", a system prompt for the Lead Agent, allowed_tools=[\"Task\"], a dictionary of 3 AgentDefinition objects, pre/post tool-use hooks, and model=\"haiku\" for cost efficiency."),
        ("User Sends Query", "The Lead Agent receives the prompt, breaks it into 2–4 subtopics (e.g., hardware/qubits, algorithms, industry/investments, challenges), and spawns 2–4 Researcher subagents in parallel via the Task tool."),
        ("Researchers Search the Web", "Each Researcher has WebSearch and Write tools only. It runs 5–10 web searches with data-focused queries (adding terms like \"statistics\", \"market size\"). It extracts every number, percentage, and metric, then writes a data-rich Markdown file with 10–15+ statistics."),
        ("Data Analyst Generates Charts", "Once all researchers finish, a single Data Analyst subagent reads all notes via Glob+Read, extracts quantitative data, and generates 2–4 matplotlib charts via Bash. Charts are saved as PNGs; a data_summary.md is written."),
        ("Report Writer Creates PDF", "Finally, a Report Writer subagent reads notes, data summaries, and chart paths. It uses the \"pdf\" Skill for reportlab guidance, then creates a professional PDF with embedded chart images via Bash."),
        ("Completion", "The Lead Agent reports: \"Complete. PDF report saved to files/reports/...\""),
    ]
    for title, desc in how_steps:
        story.append(Paragraph(title, styles["SubSubSection"]))
        story.append(Paragraph(desc, styles["Body"]))

    # ═══════════════════════════════════════════════════════════════
    # 4. FILE STRUCTURE
    # ═══════════════════════════════════════════════════════════════
    story.append(Paragraph("4. File Structure", styles["SectionTitle"]))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT_LIGHT, spaceAfter=8))

    file_data = [
        [Paragraph("<b>File</b>", styles["TableHeader"]), Paragraph("<b>Purpose</b>", styles["TableHeader"])],
        [Paragraph("agent.py", styles["SmallBold"]), Paragraph("Main entry point — SDK client setup, agent definitions", styles["TableCell"])],
        [Paragraph("prompts/lead_agent.txt", styles["SmallBold"]), Paragraph("Orchestrator instructions (176 lines, XML-structured)", styles["TableCell"])],
        [Paragraph("prompts/researcher.txt", styles["SmallBold"]), Paragraph("Web research specialist — data-focused search strategy", styles["TableCell"])],
        [Paragraph("prompts/data_analyst.txt", styles["SmallBold"]), Paragraph("Chart generation specialist — matplotlib via Bash", styles["TableCell"])],
        [Paragraph("prompts/report_writer.txt", styles["SmallBold"]), Paragraph("PDF creation specialist — reportlab via Bash", styles["TableCell"])],
        [Paragraph("utils/subagent_tracker.py", styles["SmallBold"]), Paragraph("Hook-based tool call tracking with JSONL logging", styles["TableCell"])],
        [Paragraph("utils/transcript.py", styles["SmallBold"]), Paragraph("Dual-output writer (console + file)", styles["TableCell"])],
        [Paragraph("utils/message_handler.py", styles["SmallBold"]), Paragraph("Message stream parser for subagent detection", styles["TableCell"])],
        [Paragraph(".claude/commands/*.md", styles["SmallBold"]), Paragraph("5 slash commands: research, competitive-analysis, market-trends, fact-check, summarize", styles["TableCell"])],
        [Paragraph(".claude/skills/pdf/", styles["SmallBold"]), Paragraph("PDF manipulation skill (reportlab, pypdf guides)", styles["TableCell"])],
    ]
    file_table = Table(file_data, colWidths=[2.2 * inch, 4.3 * inch])
    file_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), TABLE_HEADER_BG),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, TABLE_ALT_ROW]),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor("#d0d0e0")),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(file_table)

    # ═══════════════════════════════════════════════════════════════
    # 5. THE FOUR AGENTS
    # ═══════════════════════════════════════════════════════════════
    story.append(Spacer(1, 0.15 * inch))
    story.append(Paragraph("5. The Four Agents in Detail", styles["SectionTitle"]))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT_LIGHT, spaceAfter=8))

    agent_data = [
        [Paragraph("<b>Agent</b>", styles["TableHeader"]),
         Paragraph("<b>Model</b>", styles["TableHeader"]),
         Paragraph("<b>Tools</b>", styles["TableHeader"]),
         Paragraph("<b>Role</b>", styles["TableHeader"])],
        [Paragraph("Lead Agent", styles["SmallBold"]),
         Paragraph("Haiku", styles["TableCell"]),
         Paragraph("Task only", styles["TableCell"]),
         Paragraph("Decomposes topic into 2–4 subtopics, spawns and coordinates all subagents. Never does any work itself.", styles["TableCell"])],
        [Paragraph("Researcher (x2-4)", styles["SmallBold"]),
         Paragraph("Haiku", styles["TableCell"]),
         Paragraph("WebSearch, Write", styles["TableCell"]),
         Paragraph("Runs 5–10 data-focused web searches per subtopic. Writes Markdown notes with 10–15+ statistics, tables, and source URLs.", styles["TableCell"])],
        [Paragraph("Data Analyst (x1)", styles["SmallBold"]),
         Paragraph("Haiku", styles["TableCell"]),
         Paragraph("Glob, Read, Bash, Write", styles["TableCell"]),
         Paragraph("Reads research notes, extracts quantitative data, generates 2–4 matplotlib charts (PNG), writes data_summary.md.", styles["TableCell"])],
        [Paragraph("Report Writer (x1)", styles["SmallBold"]),
         Paragraph("Haiku", styles["TableCell"]),
         Paragraph("Skill, Write, Glob, Read, Bash", styles["TableCell"]),
         Paragraph("Reads notes + charts + data. Creates professional PDF via reportlab with embedded visualizations and citations.", styles["TableCell"])],
    ]
    agent_table = Table(agent_data, colWidths=[1.1 * inch, 0.6 * inch, 1.4 * inch, 3.4 * inch])
    agent_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), TABLE_HEADER_BG),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, TABLE_ALT_ROW]),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor("#d0d0e0")),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(agent_table)

    story.append(Spacer(1, 0.1 * inch))
    story.append(Paragraph(
        "The Lead Agent's system prompt uses XML-like tags (<font name='Courier'>&lt;role_definition&gt;</font>, "
        "<font name='Courier'>&lt;workflow&gt;</font>, <font name='Courier'>&lt;delegation_rules&gt;</font>, "
        "<font name='Courier'>&lt;parallel_spawning&gt;</font>) to enforce strict behavioral rules: "
        "always spawn researchers in parallel, never do sequential research, never skip the data-analyst step, "
        "and keep all responses to 2–3 sentences maximum.",
        styles["Body"]
    ))

    # ═══════════════════════════════════════════════════════════════
    # 6. KEY SDK FEATURES
    # ═══════════════════════════════════════════════════════════════
    story.append(PageBreak())
    story.append(Paragraph("6. Key SDK Features Demonstrated", styles["SectionTitle"]))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT_LIGHT, spaceAfter=8))

    sdk_features = [
        ("AgentDefinition — Specialized Subagents",
         "Each subagent is defined with a description (tells the orchestrator when to use it), "
         "a restricted tool list (principle of least privilege), a full system prompt, and a model choice. "
         "This enables clean separation of concerns."),
        ("Task Tool — Spawning Subagents",
         "The lead agent's only tool creates new Claude instances with the specified agent definition. "
         "The SDK handles independent conversations, tool sandboxing, result return, and parallel execution "
         "when multiple Task calls are made simultaneously."),
        ("HookMatcher — Tool Call Observability",
         "Hooks intercept every tool call before (PreToolUse) and after (PostToolUse) execution across ALL agents. "
         "The parent_tool_use_id links each call to its originating subagent, enabling full distributed tracing."),
        ("Skill Tool — Reusable Knowledge Packs",
         "The .claude/skills/pdf/ directory provides reportlab expertise that the report-writer invokes on demand. "
         "Skills deliver domain-specific knowledge without bloating every agent's system prompt."),
        ("Slash Commands — Predefined Workflows",
         "Five commands (research, competitive-analysis, market-trends, fact-check, summarize) expand into "
         "structured prompt templates with methodology frameworks. E.g., fact-check includes a full verification "
         "process with TRUE/FALSE/PARTIALLY TRUE/MISLEADING/UNVERIFIABLE verdicts."),
    ]
    for title, desc in sdk_features:
        story.append(Paragraph(title, styles["SubSubSection"]))
        story.append(Paragraph(desc, styles["Body"]))

    # ═══════════════════════════════════════════════════════════════
    # 7. OBSERVABILITY
    # ═══════════════════════════════════════════════════════════════
    story.append(Paragraph("7. Observability: Hooks and Logging", styles["SectionTitle"]))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT_LIGHT, spaceAfter=8))

    story.append(Paragraph(
        "The SubagentTracker maintains a map of sessions (parent_tool_use_id → SubagentSession) and "
        "tool call records (tool_use_id → ToolCallRecord). It auto-generates unique IDs like RESEARCHER-1, "
        "DATA-ANALYST-1. Attribution works through a chain:",
        styles["Body"]
    ))
    attr_steps = [
        "Lead Agent spawns a researcher via Task → the ToolUseBlock has an id (e.g., \"toolu_abc123\")",
        "message_handler.py detects the Task tool use and calls tracker.register_subagent_spawn()",
        "Every subsequent AssistantMessage from that subagent includes parent_tool_use_id = \"toolu_abc123\"",
        "Pre/post hooks check _current_parent_id to attribute tool calls to the correct subagent",
    ]
    for i, step in enumerate(attr_steps, 1):
        story.append(Paragraph(f"{i}. {step}", styles["BulletCustom"]))

    story.append(Paragraph(
        "This produces two log files per session: <b>transcript.txt</b> (human-readable, shows [AGENT] → Tool format) "
        "and <b>tool_calls.jsonl</b> (structured JSON Lines with timestamps, agent IDs, inputs, outputs, and success status).",
        styles["Body"]
    ))

    # ═══════════════════════════════════════════════════════════════
    # 8. COMPARISON
    # ═══════════════════════════════════════════════════════════════
    story.append(PageBreak())
    story.append(Paragraph("8. Comparison with Perplexity, ChatGPT, and Opus 4.6", styles["SectionTitle"]))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT_LIGHT, spaceAfter=8))

    # Feature matrix
    comp_data = [
        [Paragraph("<b>Capability</b>", styles["TableHeader"]),
         Paragraph("<b>Research Agent</b>", styles["TableHeader"]),
         Paragraph("<b>Perplexity</b>", styles["TableHeader"]),
         Paragraph("<b>ChatGPT</b>", styles["TableHeader"]),
         Paragraph("<b>Opus 4.6</b>", styles["TableHeader"])],
        [Paragraph("Architecture", styles["SmallBold"]),
         Paragraph("Multi-agent (4 roles)", styles["TableCell"]),
         Paragraph("Single-agent pipeline", styles["TableCell"]),
         Paragraph("Single-agent + tools", styles["TableCell"]),
         Paragraph("Single-agent + tools", styles["TableCell"])],
        [Paragraph("Parallel search", styles["SmallBold"]),
         Paragraph("2–4 simultaneous", styles["TableCell"]),
         Paragraph("Sequential (fast)", styles["TableCell"]),
         Paragraph("Sequential", styles["TableCell"]),
         Paragraph("Sequential", styles["TableCell"])],
        [Paragraph("Charts", styles["SmallBold"]),
         Paragraph("matplotlib (PNG)", styles["TableCell"]),
         Paragraph("None", styles["TableCell"]),
         Paragraph("Code Interpreter", styles["TableCell"]),
         Paragraph("None natively", styles["TableCell"])],
        [Paragraph("PDF output", styles["SmallBold"]),
         Paragraph("reportlab PDF", styles["TableCell"]),
         Paragraph("None", styles["TableCell"]),
         Paragraph("Via code only", styles["TableCell"]),
         Paragraph("None", styles["TableCell"])],
        [Paragraph("Customizable", styles["SmallBold"]),
         Paragraph("Fully (prompts, tools, hooks)", styles["TableCell"]),
         Paragraph("None", styles["TableCell"]),
         Paragraph("Limited (GPTs)", styles["TableCell"]),
         Paragraph("System prompts", styles["TableCell"])],
        [Paragraph("Audit trail", styles["SmallBold"]),
         Paragraph("Full JSONL logs", styles["TableCell"]),
         Paragraph("Inline citations", styles["TableCell"]),
         Paragraph("Inline citations", styles["TableCell"]),
         Paragraph("Inline citations", styles["TableCell"])],
        [Paragraph("Self-hosted", styles["SmallBold"]),
         Paragraph("Yes (local + API key)", styles["TableCell"]),
         Paragraph("No (SaaS)", styles["TableCell"]),
         Paragraph("No (SaaS)", styles["TableCell"]),
         Paragraph("No (API)", styles["TableCell"])],
    ]
    comp_table = Table(comp_data, colWidths=[1.1 * inch, 1.35 * inch, 1.2 * inch, 1.2 * inch, 1.2 * inch])
    comp_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), TABLE_HEADER_BG),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, TABLE_ALT_ROW]),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor("#d0d0e0")),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(comp_table)
    story.append(Spacer(1, 0.15 * inch))

    # Detailed comparisons
    story.append(Paragraph("vs. Perplexity Research Mode", styles["SubSection"]))
    story.append(Paragraph(
        "Perplexity is the gold standard for fast, citation-rich research. It's significantly faster "
        "(~10 seconds vs 2–5 minutes), has a purpose-built search index, and produces inline citations "
        "woven into polished web pages. However, the Research Agent can go <b>deeper</b> by design — "
        "2–4 parallel researchers each doing 5–10 searches covers far more ground. The Research Agent is also "
        "fully programmable (change prompts, add agents, modify workflow) while Perplexity is a black box.",
        styles["Body"]
    ))
    story.append(Paragraph("Use Perplexity for quick answers and daily research. Use the Research Agent for formal reports, custom workflows, and PDF/chart deliverables.", styles["WhenToUse"]))

    story.append(Paragraph("vs. ChatGPT (with Browsing &amp; Code Interpreter)", styles["SubSection"]))
    story.append(Paragraph(
        "ChatGPT browses one page at a time sequentially and runs everything in one context window, "
        "which gets crowded with long research. The Research Agent runs parallel searches across independent "
        "contexts. ChatGPT's approach is ad-hoc; the Research Agent enforces a rigid, repeatable pipeline "
        "(Research → Analyze → Report). ChatGPT's \"Deep Research\" (Plus/Pro) is more comparable but isn't "
        "programmable or customizable.",
        styles["Body"]
    ))
    story.append(Paragraph("Use ChatGPT for interactive sessions and iterative Q&A. Use the Research Agent for automated, reproducible report generation.", styles["WhenToUse"]))

    story.append(Paragraph("vs. Claude Opus 4.6 (Direct)", styles["SubSection"]))
    story.append(Paragraph(
        "Opus 4.6 is a <b>more capable model</b> than Haiku — a single Opus query may produce higher-quality "
        "reasoning than 4 Haiku subagents combined. It's simpler (no orchestration overhead) and supports "
        "extended thinking for extraordinarily deep analysis. However, it can only search sequentially, "
        "produces text rather than file artifacts, and can't demonstrate multi-agent patterns (hooks, skills, "
        "parallel execution) that are the real value of the SDK demo.",
        styles["Body"]
    ))
    story.append(Paragraph("Use Opus direct for complex reasoning and nuanced analysis. Use the Research Agent when you need structured deliverables and automated pipelines.", styles["WhenToUse"]))

    # ═══════════════════════════════════════════════════════════════
    # 9. COST COMPARISON
    # ═══════════════════════════════════════════════════════════════
    story.append(Spacer(1, 0.1 * inch))
    story.append(Paragraph("9. Cost Comparison (Estimated)", styles["SectionTitle"]))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT_LIGHT, spaceAfter=8))
    story.append(Paragraph("For a typical research query generating a 2-page PDF report:", styles["Body"]))

    cost_data = [
        [Paragraph("<b>System</b>", styles["TableHeader"]),
         Paragraph("<b>Est. Cost</b>", styles["TableHeader"]),
         Paragraph("<b>Est. Time</b>", styles["TableHeader"])],
        [Paragraph("Research Agent (Haiku)", styles["SmallBold"]),
         Paragraph("~$0.10–0.30", styles["TableCell"]),
         Paragraph("2–5 minutes", styles["TableCell"])],
        [Paragraph("Perplexity Pro", styles["SmallBold"]),
         Paragraph("$20/mo subscription", styles["TableCell"]),
         Paragraph("10–30 seconds", styles["TableCell"])],
        [Paragraph("ChatGPT Plus (Deep Research)", styles["SmallBold"]),
         Paragraph("$20/mo subscription", styles["TableCell"]),
         Paragraph("1–3 minutes", styles["TableCell"])],
        [Paragraph("Opus 4.6 (single query)", styles["SmallBold"]),
         Paragraph("~$0.15–0.50", styles["TableCell"]),
         Paragraph("30–90 seconds", styles["TableCell"])],
    ]
    cost_table = Table(cost_data, colWidths=[2.5 * inch, 1.8 * inch, 1.8 * inch])
    cost_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), TABLE_HEADER_BG),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, TABLE_ALT_ROW]),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor("#d0d0e0")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(cost_table)

    # ═══════════════════════════════════════════════════════════════
    # 10. STRENGTHS & LIMITATIONS
    # ═══════════════════════════════════════════════════════════════
    story.append(Spacer(1, 0.15 * inch))
    story.append(Paragraph("10. Strengths and Limitations", styles["SectionTitle"]))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT_LIGHT, spaceAfter=8))

    story.append(Paragraph("Strengths", styles["SubSection"]))
    strengths = [
        "<b>Separation of concerns</b> — Each agent has a focused role with restricted tool access, making the system predictable and auditable.",
        "<b>Parallel execution</b> — Multiple researchers run simultaneously, covering more ground faster than a single agent.",
        "<b>Full observability</b> — Hook system + JSONL logging provides a complete audit trail of every tool call across every agent.",
        "<b>Tangible output</b> — Produces real files (Markdown notes, PNG charts, PDF reports) rather than ephemeral chat responses.",
        "<b>Fully customizable</b> — Every aspect (prompts, tools, agent count, workflow) can be modified. Add a fact-checker agent, change chart style, swap report format.",
        "<b>Cost-efficient</b> — Using Haiku for all agents keeps per-token costs low while leveraging orchestration for breadth.",
    ]
    for s in strengths:
        story.append(Paragraph(f"• {s}", styles["BulletCustom"]))

    story.append(Paragraph("Limitations", styles["SubSection"]))
    limitations = [
        "<b>Latency</b> — Sequential pipeline (research → analysis → report) takes 2–5 minutes. Each phase must complete before the next.",
        "<b>No iterative refinement</b> — The pipeline is one-shot. If research misses something, the report won't include it.",
        "<b>Haiku reasoning limits</b> — Each individual agent has less reasoning power than Sonnet or Opus. Complex analytical tasks may suffer.",
        "<b>Search quality dependency</b> — Report quality is bounded by WebSearch results. Bad searches → bad report.",
        "<b>No mid-flow interaction</b> — Once launched, the pipeline runs to completion. Can't redirect researchers or refocus the analyst.",
        "<b>Local development only</b> — Production deployment would need additional infrastructure, error handling, and rate limiting.",
    ]
    for l in limitations:
        story.append(Paragraph(f"• {l}", styles["BulletCustom"]))

    # ── Final summary ───────────────────────────────────────────────
    story.append(Spacer(1, 0.2 * inch))
    story.append(HRFlowable(width="100%", thickness=2, color=ACCENT, spaceAfter=12))
    story.append(Paragraph(
        "The Claude Agent SDK Research Agent demo is a reference implementation for <b>multi-agent orchestration</b>. "
        "It's not meant to replace Perplexity or ChatGPT for quick research — it demonstrates the architecture "
        "patterns that enable building custom, production-grade research systems. The real value is in the pattern, "
        "not the demo itself.",
        styles["Body"]
    ))
    story.append(Spacer(1, 0.15 * inch))
    story.append(Paragraph(
        "Source: github.com/anthropics/claude-agent-sdk-demos/tree/main/research-agent",
        styles["CoverDate"]
    ))

    # ── Build ───────────────────────────────────────────────────────
    doc.build(story)
    print(f"PDF generated: {output_path}")


if __name__ == "__main__":
    os.makedirs("docs", exist_ok=True)
    build_pdf("docs/research-agent-explained.pdf")
