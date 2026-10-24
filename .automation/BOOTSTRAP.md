# Activation checklist

Repository initialized on 2026-10-24. **Development is intentionally gated.**

1. Import the actual verified SmartSVG V21.15.2 source from its release archive into this private repository. Do not replace the historical V21.14.1 B0 baseline.
2. Preserve the complete roadmap v3.2 and source metadata. Compare relevant hashes and run the package verification/tests recorded in the source archive.
3. Ensure `smartsvg_ai/` exists in the repo root or update the bootstrap gate in the public workflow to match the actual installable layout.
4. Add targeted regression/CI tests and assess what cannot run on GitHub's CPU runner (ComfyUI UI / real GPU / Cricut hardware).
5. On public `frenndak/SmartSVG-Automation`: configure repository Secrets `OPENAI_API_KEY` (separately billed API) and `SMARTSVG_PRIVATE_REPO_TOKEN` (fine-grained PAT limited to this private repo with Contents + Pull requests write); restrict access to the public workflow and protect main.
6. Once source and protections are validated, create `.automation/READY` with the verified source version, source checksum, author and date.
7. Finally, set public repository variable `SMARTSVG_AUTOMATION_ENABLED=true`. All other values leave development disabled.
8. Watch the first manual workflow run and review draft PRs before continuing the every-30-minute cadence.

Never put source code, secrets, input test images, or private diffs into the public repository or its logs/artifacts.
