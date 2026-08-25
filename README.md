# ALBI (Albumin-Bilirubin) Grade Calculator

Real implementation of the ALBI score for objective liver function assessment in hepatocellular carcinoma (HCC) patients.

## What It Does

Calculates the **ALBI score** and **grade (1, 2, 3)** using only two objective laboratory values — no subjective clinical assessment needed.

**Formula:**
```
ALBI = log₁₀(bilirubin_µmol/L) × 0.66 + albumin_g/L × (−0.085)
```

**Grading:**
| Grade | ALBI Score | Description | 1-Year Survival |
|-------|-----------|-------------|-----------------|
| 1 | ≤ −2.60 | Good liver function | ~83% |
| 2a | −2.60 to −2.09 | Intermediate (better) | ~62% |
| 2b | −2.09 to −1.39 | Intermediate (worse) | ~62% |
| 3 | > −1.39 | Poor liver function | ~40% |

Unit conversions handled automatically:
- Bilirubin: mg/dL → µmol/L (×17.1)
- Albumin: g/dL → g/L (×10)

## Installation

Zero dependencies — Python 3.7+ stdlib only.

## Usage

### Single Patient

```bash
python albi_grade.py single --bilirubin 2.0 --albumin 3.5
```

With explicit units:
```bash
python albi_grade.py single --bilirubin 34.2 --albumin 35 \
  --bilirubin-unit "µmol/L" --albumin-unit "g/L"
```

### Batch Processing

```bash
python albi_grade.py batch -i patients.csv -o results.csv
```

CSV columns: `bilirubin`, `albumin` (optional: `bilirubin_unit`, `albumin_unit`)

### Python API

```python
from albi_grade import calculate_albi

result = calculate_albi(bilirubin=2.0, albumin=3.5)
print(result["albi_score"])     # -2.045
print(result["albi_grade"])     # 2
print(result["albi_sub_grade"]) # "2b"
```

## Running Tests

```bash
python -m pytest test_albi_grade.py -v
```

## Clinical Reference

Johnson PJ et al. Assessment of liver function in patients with hepatocellular carcinoma: a new evidence-based approach—the ALBI grade. J Clin Oncol. 2015;33(6):550-8.

## License

MIT
