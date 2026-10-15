# Portfolio description

## Short introduction

This is my compact water-management portfolio demo, developed with AI assistance. It makes a customer-site workflow reviewable through synthetic data and local execution: validated readings and structure records enter a shared data foundation, and a bounded assistant returns scoped answers with source evidence. The repository includes reproducible inputs and outputs, tests, architecture decisions and clear production boundaries.

## What to demonstrate

1. Ingest the sample and show that one exact duplicate is removed.
2. Ask for a management summary and trace the high-water alert to R003.
3. Run the Indonesian field summary for ESTATE_A and show that ESTATE_B is absent from metrics and evidence.
4. Retrieve the synthetic high-water guidance, then request that guidance for ESTATE_B to demonstrate `no_data`.
5. Ask for a forecast to demonstrate an explicit unsupported response.
6. Run the tests and explain the difference between local scope simulation and production authorization.

## Contribution and provenance

Portfolio owner: Frederick Alfhendra. The portfolio brief, domain direction, requirement for a mini version, confidentiality constraints and presentation intent were supplied by the owner. AI assistance was used substantially for implementing this standalone adaptation, generating synthetic examples, writing tests and drafting documentation.

This note does not assign unverified roles or achievements on the original customer project. The repository is a portfolio demonstration, not proof of production ownership, deployment, measured customer outcomes or an unaided implementation. Specific professional contributions should be described separately using the owner's actual experience.

## Discussion points for a technical assessment

- Why place validation and scoping before analysis and retrieval?
- Why keep numerical calculations outside a language model?
- How do source IDs and deterministic fixtures make answers reviewable?
- What would change when replacing a local scope parameter with authenticated identity?
- Why does a small reproducible example provide stronger evidence than an architecture diagram alone?

The runnable work supports discussion of data engineering, tool boundaries, assistant reliability and integration design. It does not present a general-purpose AI agent or customer infrastructure replica.
