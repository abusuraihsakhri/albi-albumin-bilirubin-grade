# ALBI Albumin Bilirubin Grade

> **Domain:** Diagnostic Radiology & Medical Imaging AI  
> **Reference Guidelines & Standards:** `American College of Radiology (ACR) RADS & Fleischner Society`

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

ALBI (Albumin-Bilirubin) Grade for Hepatocellular Carcinoma

Calculates the ALBI score and grade for objective assessment of liver
function in HCC patients, without subjective ascites/encephalopathy scoring.

Formula:
  ALBI score = log10(bilirubin_µmol/L) × 0.66 + albumin_g/L × (-0.085)

Grading:
  Grade 1: ALBI ≤ -2.60  (best prognosis)
  Grade 2: -2.60 < ALBI ≤ -1.39
  Grade 3: ALBI > -1.39  (worst prognosis)

Unit conversions:
  Bilirubin: mg/dL → µmol/L  (× 17.1)
  Albumin:   g/dL → g/L      (× 10)

Zero-dependency Python implementation.
License: MIT

Longitudinal ALBI enrichment features for albi-albumin-bilirubin-grade.

Implements the top three items from specifications on top of the canonical
Albumin-Bilirubin (ALBI) model (Johnson et al., J Clin Oncol 2015):

    ALBI score = 0.66 * log10(bilirubin [umol/L]) - 0.085 * albumin [g/L]
    Grade 1: score <= -2.60
    Grade 2: -2.60 < score <= -1.39
    Grade 3: score > -1.39

1. Longitudinal ALBI trend tracking with grade transitions and change-point
   detection for sudden deterioration.
2. Alert escalation protocols (advisory / urgent / critical) driven by grade
   step changes and rate of change over a sliding window.
3. Patient stratification cross-referencing ALBI grade with tumor-burden
   criteria (Milan eligibility tiers, transplant vs locoregional pathways).

Author: Dr. Abu Suraih Sakhri
License: MIT

---

## ⚙️ Key Capabilities & Algorithmic Modules

### 🔬 Core Algorithmic & Evaluation Engines

- **`ALBIAssessment`** — dedicated module for a l b i assessment evaluation and state verification.
- **`GradeTransition`** — dedicated module for grade transition evaluation and state verification.
- **`ChangePoint`** — dedicated module for change point evaluation and state verification.

---

## 📐 Mathematical Formulation & Logic

```text
  Calculates the ALBI score and grade for objective assessment of liver
  Formula:
  ALBI score = log10(bilirubin_µmol/L) × 0.66 + albumin_g/L × (-0.085)
  Calculate ALBI score and grade.
  ALBI formula
```

---

## 💻 CLI Quickstart & Usage

### 1. Guided Interactive Mode
```bash
python cli.py
```

### 2. Direct Parameterized Evaluation
```bash
python cli.py --input data.csv
```

### Parameter Reference
- `--interactive`: Launch guided terminal interactive wizard.
- `--input <path>`: Evaluate input from JSON or CSV specification.
- `--json`: Output deterministic structured results in JSON format.

### Input Data Schema

| Field | Description | Requirement |
|:------|:------------|:------------|
| `Patient_ID` | Parameter / observation metric | Required |
| `v1` | Parameter / observation metric | Required |
| `v2` | Parameter / observation metric | Required |
| `v3` | Parameter / observation metric | Required |

---

## 🛡️ Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active AST and regex inspection blocking SSNs, MRNs, phone numbers, and patient identifiers.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation and state transition.
* **Air-Gapped LLM Reasoning Adapter:** Agnostic integration for local Ollama instances (`llama3`, `mistral`), Claude 3.5 Sonnet, GPT-4o, and deterministic test mocks.
* **Active Learning Bayesian Calibration:** Dynamic tracker updating worker reliability weights and monitoring Brier calibration drift.
* **FastAPI & Prometheus Telemetry:** Exposes OpenAPI 3.1 REST endpoints and operational Prometheus metrics (`/metrics`).

---

## 🧪 Testing & Verification

Run the automated test suite:

```bash
pytest -v
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py --tasks 1000 --concurrency 8
```

---

## 🐳 Container Deployment

```bash
docker build -t albi-albumin-bilirubin-grade .
docker run -p 8000:8000 albi-albumin-bilirubin-grade
```
