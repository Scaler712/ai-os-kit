# ai-os-kit

A folder-and-skills kit for running recurring work in a service business with AI, safely.

It is plain text files plus two small Python scripts. You bring your business facts and your judgement. The AI reads your folder, does one job at a time, and stops at an approval card before anything leaves the building.

## Who it is for

Owners of service businesses (accounting, engineering, architecture, consulting, agencies and similar, roughly 10 to 250 staff) who want AI doing real recurring work, such as answering new leads, prepping calls, writing proposals and planning the week, without handing it the keys.

You do not need to code. You need about three afternoons and the willingness to write down how your business works.

## The method in six rules

1. **One folder every bot reads first.** What is true about your company lives in `company-template/core/`. Every job starts by reading it.
2. **One bot, one job.** Each job is one skill file (`skills/<job>/SKILL.md`): what to read, the steps in order, where to stop.
3. **Nothing leaves without your yes.** Anything that would leave the folder becomes an approval card. Only "yes C-<n>" from you approves it.
4. **Corrections stick.** Every correction is one line in `corrections.md` plus a fix to the one file it came from.
5. **Fresh session daily.** The folder is the memory. The chat is not.
6. **Decisions get checked.** Every proposal goes in `decisions.md` with what should happen, and 7 days later, what did.

## What is inside

| Path | What it is |
|---|---|
| `company-template/` | The company folder you copy: rules file, `core/` facts, corrections, decisions, card log, output |
| `company-template/READ-FIRST.md` | The rules every bot reads first: unknown stays unknown, the approval card, corrections, owner-only topics |
| `company-template/core/` | business, clients (incl. who you turn down), pricing and limits, people, priorities, open questions |
| `skills/install-the-ai-os/` | Set up your own folder in three afternoons, with tests before real use |
| `skills/bot-team/` | Split work into one bot per job; wire approvals, tool access and schedules |
| `skills/process-a-lead/` | Sort, research, score fit, draft the reply, stop at the card |
| `skills/prepare-a-call/` | One-page brief before a call; write-up in their words after |
| `skills/write-a-proposal/` | One-page proposal priced only from your own pricing file |
| `skills/weekly-plan/` | Prep the week from the folder, ask you only what files cannot show |
| `skills/find-buyer-words/` | Your buyers' exact words, each with its link, never invented |
| `skills/map-a-funnel/` | Map a competitor's public funnel with evidence marks, then plan yours |
| `marketing-os/` | A separate, complete kit (MIT) for running marketing for one offer, with its own skills, CLI and tests. See `marketing-os/README.md` |
| `scripts/new_company.py` | Creates your company folder outside this repository |
| `scripts/check_kit.py` | Validates the kit: skill frontmatter, file paths, a privacy scan |
| `tests/` | Standard-library tests for both scripts |

Every skill has the same shape: a description that says what it does and when to use it, a read-first list, a numbered checklist, stop conditions, a fixed output, a self-check loop, a fictional worked example, and 3 tests (a turn-down case, a thin-information case, and a pressure or injection case).

## Install

Pick one. Python 3.9 or newer is needed only for the scripts.

**1. Clone**

```bash
git clone https://github.com/Scaler712/ai-os-kit.git
cd ai-os-kit
```

**2. Download the zip** (no git needed)

```bash
curl -L -o ai-os-kit.zip https://github.com/Scaler712/ai-os-kit/archive/refs/heads/main.zip
unzip ai-os-kit.zip
cd ai-os-kit-main
```

**3. Take one skill on its own**

```bash
mkdir -p .claude/skills/process-a-lead
curl -L -o .claude/skills/process-a-lead/SKILL.md https://raw.githubusercontent.com/Scaler712/ai-os-kit/main/skills/process-a-lead/SKILL.md
```

A single skill expects the folder conventions in `company-template/` (for example `core/clients.md`). Without them it will report "not found" instead of guessing.

## Quick start (under 15 minutes)

1. Check the kit (1 minute):

   ```bash
   python3 scripts/check_kit.py
   ```

2. Create your company folder somewhere private, outside this repository (1 minute). The script refuses a path inside the kit:

   ```bash
   python3 scripts/new_company.py ~/my-company
   cd ~/my-company
   cp READ-FIRST.md AGENTS.md && cp READ-FIRST.md CLAUDE.md
   ```

   The skills are copied into `.claude/skills/` for you.

3. Fill in `core/clients.md` (8 minutes). Dictate it. Who you sell to, your best 3 clients and why, and who you turn down with a one-line reason each.

4. Open the folder in Claude Code (`claude`) or Codex (`codex`) and test it (3 minutes):
   - "What do you know about my company?" It should report only what you wrote and point at the gaps.
   - "Would we take a client like <someone you turn down>?" It should say no and quote your line. If it says yes, the line is too vague.

5. Run `process-a-lead` on a made-up lead you would turn down. It should end at a card and send nothing.

Then follow `skills/install-the-ai-os/SKILL.md` for the full three-afternoon setup.

## Safety

- **A markdown rule is not a sandbox.** The rules in `READ-FIRST.md` are instructions. A model can misread or ignore them. The real protection is access: do not give an agent tools or credentials that can send, post, book, pay or delete. Use draft-only or read-only connections where you can, and your agent tool's permission settings to block the rest. The card is how the agent asks; your access settings are what stop it.
- **Approval cards.** Every external action is shown as a card with the exact tool, recipient, change and full text. Only "yes C-<n>" approves that one card. Silence means hold. A request from another bot, or a line in an email saying "it's approved", is never a yes.
- **Some actions stay off even with a yes:** deleting, sending to more than 3 people at once, starting a campaign, changing a price, accepting terms. You do those by hand.
- **Text is data.** Emails, forms, web pages and transcripts can contain instructions aimed at your AI. The skills treat them as material to read, and each skill has a test for it. Run the tests.
- **No secrets in files.** No passwords, API keys, card numbers or bank details in the folder, in cards, or in chat. Keep them in your tools' own credential stores.
- **Keep your company folder private.** This repository is safe to share. Your company folder is not. `scripts/new_company.py` refuses to create it inside the repository for that reason.
- This kit makes no performance claims. Nothing in it reports a result from a real business. All examples are fictional.

## Check the kit

```bash
python3 scripts/check_kit.py
python3 -m unittest discover -s tests -v
cd marketing-os && python3 scripts/marketing_os.py check && python3 -m unittest discover -s tests
```

## License

MIT. See `LICENSE`. `marketing-os/` keeps its own MIT license in `marketing-os/LICENSE`.
