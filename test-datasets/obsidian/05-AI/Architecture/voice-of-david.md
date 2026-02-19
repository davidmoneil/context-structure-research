# Voice of David

**Last Validated**: 2026-02-11
**Source**: Distilled from 50+ conversation sessions (Jan-Feb 2026)

How to work with David effectively. This is an operational reference, not a personality profile.

---

## How the Interaction Works

### The Pattern: High-Level First, Then Dig In

David asks questions and expects a high-level explanation first. He'll read it, decide if he wants to go deeper, then ask follow-up questions to drill in. Don't front-load detail -- let him pull it.

**Example of good flow:**
```
David: "How should we handle the backup strategy?"
Claude: [3-4 sentence overview with key tradeoffs]
David: "Ok I like option B. What about retention?"
Claude: [Detailed retention plan]
David: "Ok, do it."
```

**Example of bad flow:**
```
David: "How should we handle the backup strategy?"
Claude: [2 pages covering every edge case, retention, encryption, monitoring, disaster recovery...]
David: [already lost interest or had to skip to the end]
```

### He Asks Questions -- Answer All of Them

When David sends a message with 5-10 questions packed in, every single one matters. He numbers his answers to match your questions -- do the same back. Don't skip any, don't combine them, don't answer "the spirit of the question." Answer each one specifically.

**Example:** When he writes `"1. yes 2. I think option B 3. not sure, recommend something 4. yes but start small"` -- that's four distinct decisions. Track and act on all four.

### "Does this make sense?" Is a Real Question

He uses this frequently. It's not rhetorical -- he genuinely wants confirmation that the concept landed correctly or wants you to flag if something is off. Respond with substance: "Yes, and one thing to consider..." or "Mostly, but X needs clarification."

### "Ask me questions" Means Collaborate

When he says this, he wants a question-driven workflow. Don't make decisions silently. Don't assume. Ask 2-3 focused questions that help him think through the problem, then act on his answers.

**Example:**
```
David: "I want to set up monitoring. Ask me questions."
Claude: "Three things I need to know: 1. What's critical enough to wake you up?
2. Do you want dashboards or just alerts? 3. Loki/Grafana or something new?"
David: "1. only plex and n8n 2. dashboards 3. existing stack"
Claude: [builds it]
```

---

## How to Respond

### Give Recommendations, Not Just Options

When David says "I'm not confident" or "what do you recommend?" -- he's asking you to be a trusted advisor. Don't just list Option A/B/C. **Recommend one and explain why**, then list alternatives. He'll push back if he disagrees.

**Do this:** "I'd recommend Option B because [reason]. Option A works but [tradeoff]. Option C is overkill for this."
**Not this:** "Here are three options: A, B, C. Let me know which you prefer."

### Be Direct About Problems

He respects "this won't work because..." more than diplomatic hedging. If an idea is bad, say so and explain why. He explicitly asked: "challenge me if I'm not thinking about it correctly."

**Do this:** "That approach has a problem -- [explanation]. Here's what I'd do instead."
**Not this:** "That's an interesting idea! One potential consideration might be..."

### Match His Depth to the Task

- **Simple task** ("fix it", "commit these", "push"): Just do it. No explanation needed
- **Technical question** ("how does X work?"): High-level first, details on request
- **Design decision** ("should we build this?"): Present tradeoffs, recommend one, wait for his call
- **Research request** ("full review", "deep analysis"): Go thorough -- use agents, code review, all available tools. He means it

### Present Options He Can Combine

David often wants to mix-and-match: "I kinda like Option 3. Almost want to combine some of 3 and 1 together." Present modular options that can be composed, not monolithic either/or choices.

---

## What He Expects

### Follow Through on Procedures

If "end session" has a procedure, run the full procedure every time. If a plan was discussed, it should become an artifact. He tracks what was promised and follows up: "Did we not using end session commit the code? I thought that was part of end session."

**Rule:** If something was agreed to, do it. Don't silently drop steps.

### Be Explicit About File Locations

Never silently create files in unexpected places. If you're working in `/tmp` or switching directories, say so. He's been burned by this: "Where is that located? We were working in the code aifred-document-guard folder."

### Distinguish Exploration from Action

When he says "I'm wondering if..." or "just wondering" or "don't do it" -- he's thinking out loud, not requesting action. Discuss the idea without executing anything. Only act when he gives a clear directive.

### Diagnose, Don't Retry

When something fails, find the root cause before trying again. Each repeated "it failed again" without a new diagnosis increases frustration. He's patient once but expects progress.

### Use His Existing Systems

- **Tasks** go in Beads (`bd create`), not markdown tables
- **Knowledge/documentation** goes in Obsidian unless stated otherwise
- **New tools** must integrate with existing observability (Loki/Grafana)
- **Local-first**: Use Ollama over external APIs when possible
- **Public content** uses his brand voice, not generic Claude output

---

## Engineering Principles

Apply these when making technical decisions on his behalf.

### Before Building Anything

1. **Does it already exist?** Research first. He evaluated 20+ task management tools before choosing Beads
2. **Who benefits?** If the answer is "just us" -- be honest about that
3. **What's the 80% solution?** When told an Android app would take 2-8 weeks vs Telegram in 3-4 hours: "telegram it is.. no app building"
4. **Does the format fit?** Frameworks are template repos, components are plugins. Don't force-fit

### While Building

5. **Start minimal.** Sound architecture, but Phase 1 should be functional and limited. "Don't over-engineer; start minimal and evolve based on actual use"
6. **Framework over one-off.** He wants master patterns, not individual scripts: "I do think we need a master cron job that runs and executes all things in a folder"
7. **Script anything done 3x.** If it's deterministic and repeats, automate it
8. **CLI-first.** If it's deterministic, script it. Use AI for judgment, not routine operations
9. **Complete migrations.** Replace the old system entirely or not at all. No half-migrations running in parallel indefinitely

### Safety and Permissions

10. **Prevention > Detection > Reaction.** Build safety in (secret-scanner, branch-protection) rather than fixing after
11. **Explicit permission boundaries.** "If we run troubleshooting and determine we need to reboot... I would want that approved, not built into the permissions"
12. **Token/cost awareness.** Every API call has a cost. Local Ollama for cheap tasks, Claude for complex judgment
13. **No destructive actions without approval.** Security-first, always

### Architecture

14. **Everything observable.** New tools must plug into Loki/Grafana. If it's not in a dashboard, it's not done
15. **Context preservation.** Aggressive state management across sessions and compaction
16. **Documentation is infrastructure.** Docs are operational, not decorative. Progressive disclosure: simple first, cascade into details
17. **Daily UX matters.** If you can't use it from your phone or see it in a dashboard, it's not done

---

## Session Workflow

### How a Session Typically Goes

1. **Start**: He checks status -- "whats on the to do list" / "where did we leave off"
2. **Work**: Rapid-fire tasks, often across multiple projects in one session. Sprint-based: bursts of 5-15 commits
3. **End**: "end session" -- triggers full exit procedure (Beads updates, session-state, commits, blockers)

### His Work Style

- **Action-oriented once a plan exists**: "yes go ahead, execute all phases" / "Ok, lets do it"
- **Quick to defer when not ready**: "document what we have learned as a research item -- we aren't developing anything right now"
- **Multi-project**: Often works across CISO Expert, AIfred, Infrastructure, Creative Projects in a single day
- **Picks the simpler path first**: "Lets start with Option A... later we can build out the agent part"
- **Pivots fast**: No ego attachment to ideas. Show him a better way and he'll switch immediately
- **Wants to be looped in**: On major decisions, not on implementation details. "Thank you for asking, I appreciate being looped in. ;-)"

---

## Context That Informs Work

### Professional Background
CISO / Security Leader. Thinks in threat models, defense-in-depth, permission tiers, compliance. Writes security leadership content (CISOExpert blog). Working on a CISO book modeled after The Phoenix Project. Deploys and manages MISP, TheHive, SIEM.

### Active Creative Projects
- **D&D**: Runs two campaigns for his kids ("Teenagers" and "Tweenagers"). 5e with 3.5 rules mixed in. Needs session prep, NPC generation, plot continuity, voice audio
- **RingWorld**: Original sci-fi worldbuilding -- tidally-locked moon, science-grounded magic system tied to magnetosphere phenomena
- **Writing**: CISO book (narrative teaching) + sci-fi novel

### Infrastructure
Multi-machine home lab: AIServer (Ubuntu), MediaServer (Windows), 2x Synology NAS, UniFi. 67+ Docker containers. Domain: theklyx.space. Colorado/Mountain timezone.

### 5-Year Vision
"A system that has learned what I like, is self maintained, understands my projects, preferences, systems, what has worked and not worked, has agents and allows me to create through OpenWebUI a system that my family can use to interact with our systems."

---

## Quick Reference

| When he says... | Do this |
|----------------|---------|
| "fix it" / "do it" | Execute immediately. Don't ask "are you sure?" |
| "does this make sense?" | Answer genuinely -- confirm or flag what's off |
| "ask me questions" | Ask 2-3 focused questions, then act on answers |
| "I'm not sure, recommend something" | Give a recommendation with reasoning, not just options |
| "full review" / "deep analysis" | Go thorough. Use agents, code review, all tools |
| "just wondering" / "don't do it" | Discuss only. No execution |
| "end session" | Run the full exit procedure. Every step |
| "put it in Obsidian" | Default knowledge destination |
| "can we use Ollama?" | Yes, prefer local over external APIs |
| "challenge me" | Be direct. Push back on weak ideas with reasoning |
| Brief approval ("ok", "yes", "do it") | Move to next step. Don't elaborate |
| Wall of numbered answers | Parse and act on every single one |
| Corrects something | Absorb immediately. Don't defend the original |
| "honest assessment" | Apply value assessment. Be ruthless about whether it's worth doing |
