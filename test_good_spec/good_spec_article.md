# How to Write a Good Spec for AI Agents

**Article by Addy Osmani | Published January 13, 2026**

## Core Message

The article presents a comprehensive framework for writing effective specifications that guide AI coding agents. Rather than overwhelming agents with massive specs, developers should craft smart, modular documents that keep AI focused and productive.

## Five Key Principles

### 1. Start High-Level, Let AI Elaborate

Begin with a concise brief rather than over-engineering upfront. Use "Plan Mode" (read-only) to have the agent draft detailed specs from your vision, then refine collaboratively before execution.

### 2. Structure Like a Professional PRD

Organize specs with six essential areas: executable commands, testing procedures, project structure, code style examples, git workflow, and clear boundaries. Use consistent formatting (Markdown, XML tags) for better AI parsing.

### 3. Break Into Modular Prompts

Avoid monolithic specs. Research shows the "curse of instructions"—too many directives simultaneously reduces adherence. Address one focused task at a time, using hierarchical summaries and sub-agents for complex projects.

### 4. Build In Self-Checks and Constraints

Implement three-tier boundaries: Always do (safe actions), Ask first (high-impact changes), Never do (hard stops). Include conformance testing and leverage domain expertise to prevent predictable failures.

### 5. Test, Iterate, and Evolve

Treat specs as living documents. Run continuous tests after milestones, update specs based on findings, and use version control. Maintain feedback loops between AI output and specification refinement.

## Key Takeaway

"Vague prompts mean wrong results." Successful AI-assisted engineering requires discipline: clear specifications become executable artifacts that drive implementation, not afterthoughts.
