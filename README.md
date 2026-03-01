# AI Research Feedback

A collection of [Claude Code](https://claude.ai/code) skills for academic economics paper review.

## Skills

### `review-paper` — Pre-Submission Referee Report

Runs a rigorous pre-submission review of an academic paper, simulating the scrutiny of a specific journal's editorial board. Six specialized review agents run in parallel and their findings are consolidated into a single structured report.

**What it reviews:**

| Agent | Focus |
|---|---|
| 1 | Spelling, grammar, and academic style |
| 2 | Internal consistency and cross-reference verification |
| 3 | Unsupported claims and identification integrity |
| 4 | Mathematics, equations, and notation |
| 5 | Tables, figures, and their documentation |
| 6 | Contribution evaluation (adversarial journal-specific referee) |

**Usage:**

From within the paper's directory, run:

```
/review-paper                        # auto-detect paper, generic standards
/review-paper QJE                    # QJE-specific referee persona
/review-paper JF path/to/main.tex    # Journal of Finance persona + explicit file path
```

Recognized journal names (case-insensitive):

| Category | Journals |
|---|---|
| Top-5 economics | `AER`, `QJE`, `JPE`, `Econometrica`, `REStud` |
| Finance | `JF`, `JFE`, `RFS`, `JFQA` |
| Macro | `AEJMacro`, `JME`, `RED` |

If no journal is specified, the review applies high general standards without a specific journal persona. The file path is also optional — the skill auto-detects the main `.tex` file if not provided.

The consolidated report is saved to `PRE_SUBMISSION_REVIEW_[YYYY-MM-DD].md` in the current directory. If you prefer a specific folder, edit "review-paper.md". 

**Customization:**

The skill is designed to be extended in two ways.

*Adding journals or fields:* Open the skill file and add your journal's abbreviation to the recognized names list in Phase 1. Agent 6 will automatically adopt the appropriate editorial persona based on its training knowledge of that journal. The same approach works for other disciplines — sociology, political science, psychology — by specifying the target journal when invoking the skill.

*Adding project-specific context:* You can ask Claude to inject context about your specific paper before running the skill. For example: "Before running /review-paper, note that this paper uses a regression discontinuity design and the main identification concern is sorting around the threshold." Claude will carry that context into the review. A more durable approach is to put project-specific instructions in a `CLAUDE.md` file in your project directory — Claude Code reads this automatically and the agents will have access to it when reviewing your paper.

**Requirements:**

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) with access to the `general-purpose` subagent (i.e., the Agent tool must be available).
- The paper must be in LaTeX format. The skill reads `.tex` files and optionally inspects figure and table files.

**Installation:**

Copy [Paper-review/review-paper.md](Paper-review/review-paper.md) into your Claude Code skills directory:

```
~/.claude/commands/review-paper.md
```

or into a project-level skills directory (`.claude/commands/review-paper.md` relative to the project root) if you prefer per-project installation.

## License

MIT — free to use, adapt, and share. 
