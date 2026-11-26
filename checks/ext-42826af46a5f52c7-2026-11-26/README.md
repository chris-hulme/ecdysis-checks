# Check of ext:42826af46a5f52c7 (Ganguli et al. 2022)

**Claim** (arXiv:2209.07858, abstract): "We find that the RLHF models are increasingly difficult to red team as they scale, and we find a flat trend with scale for the other model types."

**Registered test** (Ecdysis): refuted if, in the released 38,961 red team attacks (hh-rlhf at c72f5ce), with attack success measured as in Figure 1 (middle), the average minimum harmlessness score of the RLHF model does not rise from 2.7B to 13B and from 13B to 52B; or if, for any of the plain LM, the prompted LM and rejection sampling, its average at 52B differs from its average at 2.7B by half or more of the RLHF model's rise between those sizes.

## Method

An independent implementation (standard library only). For each of the twelve cells (four model types by three sizes) the script averages `min_harmlessness_score_transcript` over all attacks in the cell; a higher average means the model was harder to red team. The prompted LM appears in the data as `context distillation`. The script then applies the registered test. As a robustness aid it also resamples attacks with replacement within each cell (2,000 bootstrap replicates, seeded from `ECDYSIS_SEED`, which is read as a string and hashed) and reports the share of replicates in which the test still passes. The point estimates do not depend on the seed.

## Data

| name | url | sha256 | bytes | licence |
|---|---|---|---|---|
| red_team_attempts.jsonl.gz | https://raw.githubusercontent.com/anthropics/hh-rlhf/c72f5cee8eb7b4d2ea5617657f4430d5e333af07/red-team-attempts/red_team_attempts.jsonl.gz | 4c7b0069991460f0064f279fd400b51f3f0095697d14d7793c49b0925f80814f | 15483307 | MIT |

The script downloads the file into `data/` (not committed) and verifies its sha256 before use.

## Run

```
python checks/ext-42826af46a5f52c7-2026-11-26/check.py
```

Writes `outputs/results.json`. Runtime about half a minute.

## Result (seed "0")

RLHF averages rise at each step: 0.524 (2.7B), 1.426 (13B), 1.703 (52B), a rise of 1.179. Changes from 2.7B to 52B for the other types, as a share of that rise: plain LM 0.10 (from -0.748 to -0.633), prompted LM 0.15 (from -0.649 to -0.829), rejection sampling 0.20 (from 1.492 to 1.723). All are below one half, so the registered test is passed: the claim is confirmed on the paper's own data and metric. The test also passed in every one of 2,000 bootstrap replicates.

## Limits

- This uses the paper's released data and its preference-model metric; it does not re-run any model or re-score transcripts.
- "Increasingly difficult" and "flat" are read through the registrant's thresholds (a rise at each step; a change under half the RLHF rise). The paper judges both by eye.
- The bootstrap treats attacks as independent, ignoring clustering by red team member; it is descriptive only and not part of the test.
- Rejection sampling's 52B average is the highest of all cells, and its change (0.23) is not negligible beside its sampling error; it is flat only relative to the RLHF rise.
- The red team members' self-reported success ratings are not tested.
