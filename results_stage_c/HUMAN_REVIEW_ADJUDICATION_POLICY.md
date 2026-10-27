# Stage C Human Review Adjudication Policy

## 1. Principles of Adjudication Governance

When independent human reviewers evaluate benchmark tasks, disagreements will naturally arise on borderline prompts, naming interpretations, or subtle abstention cues.
This policy defines the adjudication pipeline to resolve inter-rater discordance deterministically without post-hoc author cherry-picking.

## 2. Discordance Trigger Criteria

A task instance is automatically routed to the Adjudication Queue if any of the following conditions occur between two assigned reviewers ($R_1$ and $R_2$):
1. **Tool Selection Discordance**: $R_1$ and $R_2$ select different candidate tools for a selection task.
2. **Abstention Conflict**: One reviewer selects explicit abstention while the other submits a tool invocation.
3. **Ambiguity Divergence**: One reviewer flags the task as ambiguous (`is_ambiguous == True`) while the other rates it unambiguous with high confidence (confidence $\ge 4$).
4. **Argument Mismatch**: For argument construction, reviewers disagree on required property values or nested container placement (field F1 $< 0.80$).

## 3. Adjudication Procedure

1. **Third Reviewer Assignment**: The discordant item is dispatched to an independent senior adjudicator ($R_3$) who reviews the item under the same blinded protocol.
2. **Consensus Resolution**:
   - If $R_3$ agrees with either $R_1$ or $R_2$, the majority decision is adopted.
   - If $R_3$ introduces a third distinct interpretation, or consensus cannot be achieved, the task is formally designated as `GENUINELY_AMBIGUOUS`.
3. **Action on Genuinely Ambiguous Tasks**:
   - Genuinely ambiguous tasks are documented in the revision register.
   - They are excluded from empirical model scoring to prevent noisy evaluation.
   - A versioned Release 2 task replacement is generated to resolve the ambiguity.

## 4. Current Operational Status
The adjudication queue is initialized and empty.
Status: `NO_HUMAN_REVIEW_RESULTS_PRESENT`.
