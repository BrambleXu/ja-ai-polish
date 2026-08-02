# Contributing to ja-ai-polish

Thank you for improving Japanese writing quality with us.

## Before opening a change

1. Keep the project focused on observable Japanese writing problems, not AI-authorship claims.
2. Preserve the fidelity contract and platform-neutral core.
3. Add or update evaluation cases for every behavior change.
4. Keep internal development material outside public documentation.

## Rule changes

For each added or changed rule, include:

- a stable `JA-*` ID;
- observable evidence and a minimal edit strategy;
- at least one rewrite candidate;
- at least one acceptable or false-positive example;
- scene-specific exceptions;
- a fidelity case when facts, modality, or protected spans could be affected.

A single word or phrase is not sufficient evidence for a rule.

## Documentation changes

Keep English, Simplified Chinese, and Japanese README or installation variants semantically aligned.
Platform commands must come from the platform's official documentation and include a verification
date.

## Local checks

```bash
python3 scripts/lint_skill.py
python3 scripts/check_fidelity.py
python3 -m unittest discover -s tests -v
```

Model and human review results must identify the evaluated revision, evaluator setup, and unrun
cases. Do not report a planned score as a measured result.

