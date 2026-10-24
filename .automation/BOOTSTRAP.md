# SmartSVG Studio — private source admission and agent activation

Status: **NOT READY** until the exact V21.15.2 source archive is imported, checked and reviewed. This document is operational guidance, not an authorization to bypass the gates.

## 1. Admit the actual source

1. Review the current G0 admission PR and green CI at its exact HEAD.
2. In the **private** repository `frenndak/SmartSVG-Studio`, create a **private release** tagged `smartsvg-v21.15.2-source` with the original asset named exactly `ComfyUI_SmartSVG_Studio_V21_15_2_Installation.zip`.
3. Run `SmartSVG - Import private source release` from Actions. It imports into `engine/` (including `engine/smartsvg_ai/`) on a private bootstrap branch and opens a draft PR. The expected ZIP SHA-256 is `9369656f0216cebb6dccce0d0155bffa16d8c384da6a984bf848cdd8aa003c54`.
4. Independently inspect the import report, verify the full internal manifest (651 declared file digests), run relevant tests and examine the draft PR before any merge.
5. Record what was **not** tested: actual RTX 3070 inference, ComfyUI runtime/UI, Cricut Design Space import and physical Print Then Cut. A ZIP CRC or internal hash match alone does not prove runtime behaviour.
6. Only after provenance and test admission, have a maintainer create `.automation/READY` in the private repository. Never create this marker from an AI development cycle.

The roadmap at `docs/ROADMAP_MASTER_v3_2.md` and its freeze metadata remain immutable unless explicitly revised by the owner. Preserve the historical V21.14.1 baseline.

## 2. Configure the separation of secrets

- **Private SmartSVG-Studio only:** `OPENAI_API_KEY` for the private Codex runner (separately billed API). Do not expose its value in logs or PRs.
- **Public SmartSVG-Automation only:** `SMARTSVG_DISPATCH_TOKEN`, fine-grained and limited to dispatching events to the private repository. The public repository must **never** contain `OPENAI_API_KEY` or `SMARTSVG_PRIVATE_REPO_TOKEN`.
- **Both repos:** repository Actions variable `SMARTSVG_AUTOMATION_ENABLED=true` **after** checks and authorization; false or unset disables the corresponding scheduled job.
- Review permissions and costs; the public scheduler does **not** move private compute or private source out of the private repo.

## 3. Exercise the pipeline

1. Manually dispatch the public `SmartSVG - Secure half-hour orchestration` once.
2. Confirm the event is received by the private runner and that the private readiness and provenance checks actually pass.
3. Review the first private agent-created draft PR, its changed files, head SHA and test evidence before considering integration.
4. Start regular scheduling only after the end-to-end dry run. GitHub schedule events can be delayed or skipped.
5. Human/bootstrap PRs must not block autonomous WIP=1 routing; the runner repairs **only** `smartsvg/auto-*` branches and never merges them.

## 4. Failure and cost controls

- Missing source, required evidence, secrets, permission or GitHub Actions budget: stop and report the **actual** blocker; never assert that an autonomous change happened.
- Code/tests failing: repair only the current authorized agent branch, do not push to `main` or mark success.
- No material delta: do not create duplicate review comments, pointless PRs or retry identical blocked runs.
- Treat CPU unit tests, simulated tests, real GPU execution and physical Cricut cutting as distinct levels of evidence.

**Security:** keep source, user images and source archives out of the public repository and its logs.