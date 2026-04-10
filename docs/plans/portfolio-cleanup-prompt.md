# Portfolio Cleanup Prompt (Reusable)

A drop-in prompt for Claude Code (or any agent) to apply the same "clean up for portfolio viewing" treatment to another cloud-provider lab project (AWS, Azure, GCP, etc.).

Copy everything between the `---` lines and paste it into a new agent session inside the target repo.

---

You are helping me clean up a multi-phase cloud lab project so the public repo shows only the phase I'm actively working on, hides detailed implementation guides without losing them, and sets a professional portfolio-facing tone. Files stay on disk — nothing gets deleted from the filesystem. Git history is intentionally left alone.

## Context you need to gather first

1. Read the top-level `README.md`.
2. List the `phases/` directory (or equivalent — may be called `projects/`, `labs/`, `modules/`).
3. Run `git ls-files phases/` to see what's currently tracked per phase.
4. Identify:
   - Which phase is "in progress" (the user will tell you, or you can ask).
   - Which phase directories should be hidden (not yet started).
   - The filename pattern of the large implementation/build guides inside each phase (commonly `implementation-guide.md`, `build-guide.md`, `walkthrough.md`).

## Apply these changes

### 1. Hide the big implementation guides via `.git/info/exclude` (invisible, local-only)

Append the full paths of the implementation guides (for every phase, including the in-progress one) to `.git/info/exclude`. This file is never committed — the filenames leak nowhere. Example entry:

```
phases/phase-1-<name>/docs/implementation-guide.md
phases/phase-2-<name>/docs/implementation-guide.md
phases/phase-3-<name>/docs/implementation-guide.md
```

**Reasoning:** The user wants the guides on disk locally but not publicly visible. Sanitized SOPs will be published per phase as each phase completes.

### 2. Gitignore the not-yet-started phase directories via `.gitignore`

Add directory-level ignores so the entire not-started phases disappear from the tracked tree. Example:

```
# Phases not yet in progress — hidden from public view until work begins.
# Files remain on disk locally; they're just untracked.
phases/phase-2-<name>/
phases/phase-3-<name>/
```

**Reasoning:** User accepts that phase names appear in `.gitignore` (they're not secret, just not-yet-started). The `.git/info/exclude` trick is reserved for the implementation guides.

### 3. `git rm --cached` the now-ignored files

Run `git rm --cached` (NOT `git rm`) for every currently-tracked file that is now covered by the ignore rules:
- The implementation guides in every phase
- Every file under the not-yet-started phase directories

**Critical:** Use `--cached` only. This untracks without deleting from disk. Verify files still exist on disk with `ls` after the command.

### 4. Rewrite the top-level `README.md`

Transform the README to show ONLY the in-progress phase. Specifically:

- **Intro paragraph:** Remove phrases like "Three independent phases progressively build..." — replace with a single-phase framing.
- **Project Themes section:** Collapse to a single "Current Focus" section describing only the in-progress phase. Remove the subsections describing phases 2 and 3.
- **Results table:** Remove rows for hidden phases.
- **Tech Stack table:** Remove technologies that only appear in hidden phases. Rename the section heading to include the active phase name (e.g., "Tech Stack (Phase 1)").
- **Project Structure tree:** Remove the hidden phase directories from the ASCII tree.
- **How to Use:** Remove references to "each phase" — rephrase around the current phase.
- **Phase Status table:** Remove rows and Guide column (the guide is now private). Keep only the in-progress phase and any scoped sub-tracks.
- **Design Decisions:** Remove bullets that reference hidden phases (e.g., "Phase 3 Appendix B") and cross-phase rationale.
- **Add a "Future Work" section** (new): 2–4 sentences alluding to the broader themes that remaining phases will eventually cover. No phase-specific names, no implementation detail, no tech stack leaks. Say something like "Details and documentation will be published as each phase is started and completed."

Write in a neutral, professional tone. Don't delete history or make the repo feel incomplete — frame it as "focused on the active phase, more coming."

### 5. Preserve in-flight edits

Before committing, verify that any uncommitted edits to the in-progress phase's implementation guide (which is now untracked) are still on disk — grep for a few recent changes you know about, or ask the user to confirm.

### 6. Commit

Use a brief, generic commit message:

```
Clean up project for portfolio viewing
```

Do NOT push automatically. Leave the commit local unless the user asks to push.

### 7. Verify

Run `git check-ignore -v` against one representative file from each ignore category to confirm the correct rule fires. Example:

```
git check-ignore -v phases/phase-1-<name>/docs/implementation-guide.md    # should hit .git/info/exclude
git check-ignore -v phases/phase-2-<name>/terraform/main.tf               # should hit .gitignore
```

Then `git status` — should be clean.

## Things to NOT do

- Do NOT `git rm` without `--cached`. Never delete files from disk.
- Do NOT rewrite git history (no `filter-repo`, no `filter-branch`, no `rebase -i`).
- Do NOT push to origin.
- Do NOT touch the in-progress phase's actual code directories (terraform/, ansible/, app/, docker/) — only untrack its implementation guide.
- Do NOT edit project-wide docs (ADRs, pillar matrices, known-issues, lessons-learned) unless the user explicitly asks. Scope creep.
- Do NOT sweep other markdown files for phase-2/3 mentions. The README is the public entry point; that's enough.

## Ask before acting on ambiguity

- If there are multiple candidate implementation-guide filenames, ask which to hide.
- If there's only one phase in the repo, confirm the user still wants this cleanup (probably not needed).
- If a phase directory is mostly empty scaffold with no real work, ask whether to hide it or keep it visible as a structural placeholder.
