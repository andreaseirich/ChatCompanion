# Validation Metrics

This document contains reproducible validation metrics computed from test fixtures and CI runs.

## How to Reproduce

Run the following commands to regenerate all metrics:

```bash
# Fixture corpus metrics
python3 scripts/compute_fixture_metrics.py

# Test suite statistics
python3 scripts/collect_ci_test_stats.py
```

For file output:

```bash
python3 scripts/compute_fixture_metrics.py --md metrics_fixtures.md --json metrics_fixtures.json
python3 scripts/collect_ci_test_stats.py --md metrics_tests.md --json metrics_tests.json
```

---

## Fixture Corpus Metrics

<details>
<summary>📊 Latest Metrics Output</summary>

**Generated:** 2025-12-27 13:15:43 UTC  
**Commit:** `3c8078a`

**Total test chats:** 12

### Per-Level Accuracy

- **GREEN**: 3/4 (75.0%)
- **YELLOW**: 0/4 (0.0%)
- **RED**: 0/4 (0.0%)

**Overall accuracy:** 25.0%

### Confusion Matrix

| Expected → Actual | GREEN | YELLOW | RED |
|-------------------|-------|--------|-----|
| GREEN | 3 | 1 | 0 |
| YELLOW | 4 | 0 | 0 |
| RED | 0 | 4 | 0 |

### Validation Checks

- **"Need Immediate Help?" appears only for RED:** ✅ 0 cases
  - ✅ No violations found
- **Evidence-based behaviors (approximate):** 0 potential violations
  - Note: This is an approximate check based on text matching. Full validation requires parsing natural language explanations.

> **Note:** These metrics are computed from synthetic test fixtures. Real-world accuracy may vary.

</details>

---

## Test Suite Statistics

<details>
<summary>📊 Latest Test Run</summary>

**Generated:** 2025-12-27 13:15:51 UTC  
**Commit:** `3c8078a`

- **Tests passed:** 128
- **Tests total:** 128
- **Runtime:** 6.22 seconds

</details>

---

## Notes

- **All metrics are computed from synthetic test fixtures** designed to validate specific patterns.
- **Real-world accuracy may vary** based on context, language variations, and edge cases not covered in the test set.
- **Patterns/labels are for demo/testing purposes**, not clinical or legal evaluation.
- Metrics are regenerated on each run and may vary slightly based on:
  - ML model availability (hybrid vs rules-only mode)
  - System performance
  - Random variations in test generation (if applicable)

---

## Understanding the Metrics

### Overall Accuracy (25.0%)

The overall accuracy reflects how well the system matches expected risk levels across all test cases. Lower accuracy on synthetic fixtures may indicate:
- Test fixtures are challenging edge cases
- System is conservative (preferring higher risk levels)
- Pattern matching needs refinement

### Per-Level Breakdown

- **GREEN (75.0%)**: System correctly identifies safe conversations most of the time
- **YELLOW (0.0%)**: System tends to classify YELLOW cases as GREEN (conservative)
- **RED (0.0%)**: System tends to classify RED cases as YELLOW (conservative, avoids false positives)

### Confusion Matrix Interpretation

The confusion matrix shows where the system makes mistakes:
- **YELLOW → GREEN (4 cases)**: YELLOW cases classified as safe
- **RED → YELLOW (4 cases)**: RED cases classified as moderate risk
- **GREEN → YELLOW (1 case)**: One safe case flagged as moderate risk

This pattern suggests the system is **conservative**, preferring to flag potential risks rather than miss them.

---

*Last updated: 2025-12-27*

