# SmartSVG Studio — Public single-repository migration

The canonical repository is **frenndak/SmartSVG-Studio** (public). The former
**frenndak/SmartSVG-Automation** repository is legacy orchestration; its
cross-repository dispatch token is not required for this repository's scheduled
free validation.

## Current implementation

- **Candidate only until PR #30 is merged:** `.github/workflows/public-autonomous-cycle.yml` is configured to run twice per hour on the default branch after integration: develop preflight at :05 UTC and repair preflight at :50 UTC. A green pull-request run is not evidence of an active schedule.
- Both proposed cycles validate the frozen roadmap, the original source archive and the repository's Python unit tests without OpenAI API usage. `tests/test_public_single_repo_preflight.py` adds negative checks to prevent accidental paid/privileged triggers and permission drift.
- These scheduled checks **do not implement AI code changes or merge PRs**.
  GitHub Actions schedules may be delayed or skipped; a scheduled run is not
  evidence of an agent execution.
- `.github/workflows/private-ai-development.yml` is legacy and still requires
  `SMARTSVG_AUTOMATION_ENABLED` and `OPENAI_API_KEY` for paid engineering.
  Do not activate it until replaced by a reviewed single-repo implementation
  with clear cost limits and explicit repository permissions.

## Security and publication

- Public Git history is visible. A commit deleting a secret does not remove it
  from history. Rotate any exposed credential; audit history and release assets.
- Never commit user photos, copyrighted third-party test assets, tokens, model
  weights, or personally identifying material without permission and licensing.
- `docs/CORPUS_UTILISATEUR_PRIVE.md` is a historical inventory; do not upload
  the referenced images to this public repository.
- Preserve original release ZIP, SHA-256 manifests and frozen roadmap unchanged.
- Pull requests and CI checks are review evidence, not automatic permission to
  merge. L2 GPU inference and L3 physical Cricut tests remain separately unverified.

## Migration follow-up

1. Review and integrate this free single-repo schedule. Its current `pull_request` checkout uses GitHub's default synthetic merge ref, so the successful PR CI is **not** proof of direct HEAD checkout. Require an explicit exact-HEAD validation before claiming that property; the frozen archive and roadmap checks are separate. Once merged, observe a real scheduled run on `main` before claiming scheduling is active.
2. Replace the legacy private-engineer workflow with a dedicated public-repo
   worker PR that uses scoped credentials, least privilege, budget enforcement
   and non-destructive PR-only changes.
3. Validate that the replacement creates and tests a draft PR, without a paid
   invocation until cost authorization and secrets are configured.
4. Only then disable the legacy cross-repo schedules and retire the old public
   automation repository.
