# Proof Trust Policy

## Trusted code

The trusted proof library is:

`FormalField/`

Rules:

* No `sorry`
* No `admit`
* No `axiom`
* No imports from untrusted obligation directories
* All trusted files must build with `lake build`
* The trusted grep must remain empty:

```bash
git grep -nE '\b(sorry|admit|axiom)\b' -- 'FormalField/*.lean' 'FormalField/**/*.lean' || true
```

## Frozen core

The frozen trusted core is:

tag:
`formalfield-core-l1-l15-frozen`

commit:
`e0d1604c90569672fb41ff2b34abbb90f75b6744`

The frozen core theorem statements must not be modified.

## Trusted applications shell

The trusted applications obligation-shell layer is:

tag:
`formalfield-applications-obligation-shells-v0`

commit:
`454f8d011c919bb64c164500d17c3ad72621dd73`

This layer registers application obligations only. It does not prove RH, TOE, RSA, or physics claims.

## Untrusted obligations

Unfinished proof worklists must live outside `FormalField/`, for example:

`UntrustedObligations/`
`ScratchObligations/`

These directories may contain `sorry` only as obligations to solve.

They are not trusted proof libraries.

## Promotion rule

A theorem may be promoted into `FormalField/` only after:

1. All `sorry/admit/axiom` occurrences are removed.
2. The theorem has a real Lean proof.
3. It does not rely on any untrusted theorem.
4. `lake build` succeeds.
5. The trusted grep over `FormalField/` is empty.

## Branch policy

The `main` branch should remain trusted.

Active untrusted worklists should be developed on a separate branch, for example:

`obligations/worklist`

## Core principle

UntrustedObligations is a solver worklist.

FormalField is the trusted proof library.
