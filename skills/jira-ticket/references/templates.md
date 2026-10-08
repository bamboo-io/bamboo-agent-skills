# Jira Ticket Templates & Quality Standards

Synced from Panda's `jira-ticket-creation` skill (BT-4305). The Spike type uses the Task template with Scope = what to investigate and AC = what "done" looks like.

## Task Template

**Title:** `[Epic/Area] Short description of what needs to be done`

**Context paragraph** *(no heading, 2–4 sentences)*:
- What is the current state?
- What is the problem or opportunity?
- Why does this need to be done now?

**Scope of the task:**
Numbered list of concrete things to implement. Each item = a specific, buildable output.
Use sub-items (a, b, c) where needed. Include formulas, examples, or edge cases inline.

**Acceptance Criteria:**
Numbered list of testable conditions. Each item must be independently verifiable by QA.
Do NOT duplicate Scope — AC is what QA checks, Scope is what devs build.
Cover edge cases, data formats, cross-platform behaviour.

**Resources *(optional)*:**
Figma links, related tickets, Google Sheets, external docs. Always note if design is available.

---

## Story Template

**Title:** `[Module/Area] Short description of the user-facing feature`

**User story:** As a [user type], I want to [do something] so that [goal/benefit].

**General look of the module** *(if design exists)*:
Link to Figma for each user type (Individual, SMSF) if they differ. Note if design is the same.

**Pre-condition:**
What state is the user/system in before this screen appears?
Include all possible trigger conditions. Use numbered list with OR where applicable.

**Scope of the ticket:**
Numbered list of what the UI should show/do. Describe behaviour, layout rules, interaction rules, animations, data display logic, ordering rules, edge cases. Use tables where multiple types/variants exist.

**Acceptance Criteria:**
Numbered list of testable outcomes. Each AC item must be independently verifiable.
Include design compliance, edge cases, navigation, expiry rules, platform-specific behaviour (iOS/Android), and user type differences.

---

## Bug Report Template

**Title:** One sentence — answers *What happened? Where? When?* (mirrors the Actual result)

**Description:**
Brief outline of the issue.

**Steps to Reproduce:**
Numbered list of all steps required to reproduce the issue. Be specific enough that another tester can follow without help.
If steps > 8, add a **Preconditions** section before the numbered list.

**Expected Result:**
How the system is supposed to work from the tester's perspective.

**Actual Result:**
What is not working correctly, where it occurs, and under what conditions.
Answer: *What? Where? When?*

---

## Quality Benchmarks (Gold Standard Examples)

### BT-2986 — Task gold standard
*[Portfolio] Replace the ABP logic with WABP logic*
- Context explains WHY the change is needed (ABP logic breaks with volatile crypto)
- Scope includes the exact formula with a worked numerical example (step-by-step BTC calculation)
- Edge cases covered inline: selling to $0 resets WABP, reinvestment restarts calculation
- 7 Acceptance Criteria covering all investment types, number formatting, and every edge case
- Properly labelled (Back-End), estimated (5 SP, M t-shirt), prioritised (Critical), and assigned

### BT-3947 — Task with tight business constraints
*[Incentive/CLI] Add bonus limit to bamboo user sendBonus [phoneNumber] CLI command*
- Context explains the business risk (no validation = potential for accidental huge bonuses)
- Scope is tight: 3 bullets with exact bolded values (AUD 5 min / AUD 600 max) and error handling
- AC is multi-layer: covers CLI, BE, and FE in one ticket
- AC item 5 includes a forward-looking note (future configurability) and asks dev to confirm estimate
- Error message wording is specified directly in the AC

### BT-3679 — Story gold standard
*(See Jira for full content)*
- Pre-conditions listed with all trigger states
- Scope describes UI behaviour and layout rules, not just feature goals
- AC covers both iOS and Android, both user types (Individual, SMSF)
- Figma links provided per user type

---

## Common Mistakes to Avoid

- Vague scope items like "implement the feature" — be specific and buildable
- Duplicating scope in AC — AC verifies, scope builds
- Missing edge cases (e.g., zero state, error states, both platforms)
- No context paragraph — devs need to know WHY, not just WHAT
- Bug titles that don't answer What/Where/When
