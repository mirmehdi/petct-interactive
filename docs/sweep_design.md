# Day-7 Threshold Sweep — pre-registered design
Date: 10 Aug 2026 · Status: FROZEN before any sweep code runs

## Question
Which probability threshold maximizes the COMPETITION score
(AUC over the 6 interaction steps), not just the step-0 Dice?

## Setup
- Model: shipped fold-0 baseline checkpoint, unchanged.
- Data: dev-40 manifest (frozen on Day 5).
- Thresholds tested: 0.2, 0.3, 0.4, 0.5, 0.6 on the step-0 probability map.

## Recorded per threshold
| thr | Dice@0 | DMM@0 | FP-voxels | FN-voxels | scribble type attracted (steps 1-5) | empty-prediction-on-positive rate | AUC-Dice | AUC-DMM |
|-----|--------|-------|-----------|-----------|--------------------------------------|-----------------------------------|----------|---------|
 0.2 |        |       |           |           |                                      |                            |          |         |
| 0.3 |        |       |           |           |                                      |                                   |          |         |
| 0.4 |        |       |           |           |                                      |                                   |          |         |
| 0.5 |        |       |           |           |                                      |                                   |          |         |
| 0.6 |        |       |           |           |                                      |                                   |          |         |

## Hypothesis (sealed before running)
<<< WRITE 3-5 SENTENCES HERE >>>

## Note
Hypothesis direction corrected from plan draft: FN-leaning means a HIGHER
threshold, not lower. Flagged for master ratification.