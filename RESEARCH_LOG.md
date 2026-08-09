# Research Log — petct-interactive (autoPET V)

One entry per working day. Newest on top.
Each entry: what was done, what was measured, what was decided, what is open.

---

## Day 4 — Sunday 10 Aug 2026

### Done
- Verified download byte-for-byte (150,293,961,309 bytes, wget "saved" line).
- Extracted archive; census: 1,611 studies = 1,014 FDG + 597 PSMA (matches page).
- Archived zip to S3 (`s3://mirmehdi-petct-archive`, Standard-IA, ~$1.75/mo).
- Deleted local zip after verified copy. Disk steady state: 143G used / 590G.
- fstab entry via UUID + nofail: /data now auto-mounts on every boot.
- IAM role `petct-ec2-s3` created, attached to instance, tested (aws s3 ls works).
- Wrote and ran `tools/census.py` on full dataset.

### Measured (my own tool, not inherited)
| | FDG | PSMA |
|---|---|---|
| Studies | 1,014 | 597 |
| Unique patients | 900 | 378 |
| Patients with >1 study | 81 | 164 (43%!) |
| Empty labels | 513 (50.6%) | 58 (9.7%) |

- Discrepancy found: datasets page claims 60 PSMA-negative studies; actual empty
  masks = 58. Measured truth wins for the sampler.
- Leakage headcount: 245 patients with multiple studies — patient-level splits mandatory.

### Decided
- Cache design FROZEN (reviewed): at step 0 write to /cache: (a) preprocessed
  input arrays, (b) probability map in float16 (~104 MB), (c) tracer + geometry
  facts. Steps 1–5 read back and edit locally around scribbles. Safety rule 1:
  cache is optimization, never dependency — on any failure, full recompute,
  never crash. Safety rule 2: if step 0 predicted empty, later steps must seed
  and grow at foreground scribbles — never repeat "empty" under correction.
- arXiv fallback (proposal to master): TechRxiv; try one endorsement email first;
  Zenodo as third option.

### Open
- GC join still pending → nudge email Monday noon; 4 submission-page questions blocked.
- GPU quota still pending ("case opened").
- Day-7 sweep design note (owed).
- 400-case sampler consumes today's census numbers (Day 5).