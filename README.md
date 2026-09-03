# ALBI (Albumin-Bilirubin) Grade Calculator

A pure Python clinical decision support tool implementing the Albumin-Bilirubin (ALBI) score and grading system for objective assessment of liver functional reserve in patients with hepatocellular carcinoma (HCC) and chronic liver disease:
- Objective prognostic staging without the subjective variables of Child-Pugh score (no ascites or hepatic encephalopathy scoring).
- High-precision clinical unit conversions for serum bilirubin (mg/dL $\leftrightarrow$ µmol/L) and albumin (g/dL $\leftrightarrow$ g/L).
- Sub-grade stratification (ALBI Grade 2a vs 2b) for fine-grained systemic and locoregional treatment selection.
- Median overall survival and 1-year survival probability projections calibrated to international clinical trial cohorts (Johnson et al., *J Clin Oncol* 2015).
- Longitudinal trend analysis, grade transitions, and acute deterioration change-point detection.
- Batch CSV cohort processing for clinical registries and oncology workflows.

Requires Python standard library only (zero external runtime dependencies).

---

## Clinical Formulation & Evidence Base

$$\text{ALBI Score} = (\log_{10} \text{Bilirubin } [\mu\text{mol/L}] \times 0.66) + (\text{Albumin } [\text{g/L}] \times -0.085)$$

### Conversion Factors
- **Serum Bilirubin:** $1\text{ mg/dL} = 17.1\ \mu\text{mol/L}$
- **Serum Albumin:** $1\text{ g/dL} = 10\text{ g/L}$

### Grading Tiers & Clinical Interpretation
| Grade | ALBI Score Range | Liver Function | Median Survival (HCC) | 1-Year Survival | Recommended Management Pathway |
|:-----:|:----------------:|:--------------:|:---------------------:|:---------------:|:-------------------------------|
| **Grade 1** | $\le -2.60$ | Good reserve | ~18.5 – 26 months | ~75 – 82% | Curative resection, RFA/ablation, full-dose systemic therapy |
| **Grade 2a** | $-2.60 < \text{score} \le -2.27$ | Intermediate (favorable) | ~14.5 – 16 months | ~62 – 68% | TACE, systemic therapy with routine toxicity monitoring |
| **Grade 2b** | $-2.27 < \text{score} \le -1.39$ | Intermediate (adverse) | ~8.0 – 11 months | ~40 – 48% | Dose-adjusted systemic therapy; evaluate for liver transplant |
| **Grade 3** | $> -1.39$ | Poor reserve | ~3.0 – 5.5 months | ~15 – 25% | Transplant evaluation if eligible; best supportive care |

---

## Features

- **Objective Evaluation:** Purely biochemical parameters eliminating inter-observer variability inherent in Child-Pugh scoring.
- **ALBI Sub-Grading:** Differentiates Grade 2 into 2a and 2b, aiding clinical trials and transarterial chemoembolization (TACE) candidacy decisions.
- **Longitudinal Tracking:** Monitors rate of change and flags rapid decompensation change-points.
- **Batch CSV Processing:** High-throughput cohort evaluation.

---

## Installation & Requirements

- Python 3.10+ (tested on 3.10, 3.11, 3.12)
- Zero external runtime dependencies. `pytest` is optional for running tests.

```bash
git clone https://github.com/abusuraihsakhri/albi-albumin-bilirubin-grade.git
cd albi-albumin-bilirubin-grade
```

---

## CLI Usage

### 1. Single Patient Evaluation
Evaluate single patient with conventional units:
```bash
python cli.py single --bilirubin 1.2 --albumin 3.8
```
Or specify SI units:
```bash
python cli.py single --bilirubin 20.5 --bilirubin-unit "µmol/L" --albumin 38.0 --albumin-unit "g/L"
```

### 2. Batch CSV Cohort Evaluation
```bash
python cli.py batch -i sample.csv -o results.csv
```

---

## Python API Quickstart

```python
from albi_grade import calculate_albi

# 1. Calculate ALBI Grade
result = calculate_albi(
    bilirubin=1.2,          # mg/dL
    albumin=3.8,            # g/dL
    bilirubin_unit="mg/dL",
    albumin_unit="g/dL",
)

print(f"ALBI Score: {result['albi_score']}")
print(f"ALBI Grade: {result['albi_grade']} ({result['albi_sub_grade']})")
print(f"Interpretation: {result['grade_description']}")
print(f"Clinical Guidance: {result['clinical_recommendation']}")
```

---

## Running Tests

Run the automated test suite using standard `unittest` or `pytest`:

```bash
pytest -v
```
