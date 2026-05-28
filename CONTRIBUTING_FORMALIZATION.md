# Contributing Formalization in RhCore

This guide is the project-local policy for making Lean/mathlib-facing changes
that can survive review and CI over time.

## Scope

- Applies to `.lean` changes under `RhCore/`.
- Applies to workflows that affect Lean toolchain/dependency state.
- Applies to theorem statements used by RH reduction modules.

## Hard rules

- Keep `lean-toolchain` aligned with `mathlib` manifest state.
- Do not switch `mathlib` to a local `path` dependency in committed manifests.
- Prefer small, reviewable theorem additions over large rewrites.
- Do not hide open gates behind opaque helper theorems.

## Required local checks before PR

Run exactly:

```bash
lake update
python tools/check_lean_dependency_health.py
lake build
lake env lean test/li_pos_first50.lean
lake env lean --run test/closure_stub.lean
```

## PR structure expectations

1. State theorem-level goal in the PR description.
2. List assumptions explicitly when theorem is conditional.
3. Include changed files grouped by purpose:
   - API wrappers
   - theorem statements
   - proofs
   - CI/toolchain changes
4. Include at least one failing-case note if a gate is intentionally left open.

## Theorem hygiene

- Use descriptive names and stable namespaces.
- Keep assumptions explicit in theorem signatures.
- Avoid global `axiom` additions unless accompanied by an open-gate note in `PAPER.md`.
- If a proof is deferred, use a tracked TODO entry and reference a concrete blocker.

## Open-gate policy

For RH-reduction work, every unresolved gate must be represented as one of:

- `axiom` with explicit comment and rationale.
- theorem stub with TODO marker and blocker.
- external dependency note (mathlib missing lemma).

Never present unresolved gates as closed in CI summaries.
