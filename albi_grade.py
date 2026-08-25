#!/usr/bin/env python3
"""
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
"""

import argparse
import csv
import json
import math
import sys
from typing import Dict, Any, Optional


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BILIRUBIN_CONVERSION = 17.1  # mg/dL to µmol/L
ALBUMIN_CONVERSION = 10.0    # g/dL to g/L

# ALBI grade thresholds
ALBI_GRADE_1_THRESHOLD = -2.60
ALBI_GRADE_2_THRESHOLD = -1.39


# ---------------------------------------------------------------------------
# Core calculation
# ---------------------------------------------------------------------------

def calculate_albi(
    bilirubin: float,
    albumin: float,
    bilirubin_unit: str = "mg/dL",
    albumin_unit: str = "g/dL",
) -> Dict[str, Any]:
    """
    Calculate ALBI score and grade.

    Parameters:
        bilirubin: Serum bilirubin value
        albumin: Serum albumin value
        bilirubin_unit: 'mg/dL' or 'µmol/L' (default: mg/dL)
        albumin_unit: 'g/dL' or 'g/L' (default: g/dL)

    Returns:
        Dict with ALBI score, grade, sub-grade, survival estimate, and details.
    """
    # Convert to µmol/L and g/L
    if bilirubin_unit.lower() in ("mg/dl", "mg/dL"):
        bili_umol = bilirubin * BILIRUBIN_CONVERSION
    elif bilirubin_unit.lower() in ("umol/l", "µmol/l", "umol/L", "µmol/L"):
        bili_umol = bilirubin
    else:
        raise ValueError(f"Unknown bilirubin unit: {bilirubin_unit}")

    if albumin_unit.lower() in ("g/dl", "g/dL"):
        alb_g_l = albumin * ALBUMIN_CONVERSION
    elif albumin_unit.lower() in ("g/l", "g/L"):
        alb_g_l = albumin
    else:
        raise ValueError(f"Unknown albumin unit: {albumin_unit}")

    # Validate
    if bili_umol <= 0:
        raise ValueError("Bilirubin must be positive for log10 calculation")
    if alb_g_l < 0:
        raise ValueError("Albumin must be non-negative")

    # ALBI formula
    albi_score = math.log10(bili_umol) * 0.66 + alb_g_l * (-0.085)
    albi_score = round(albi_score, 4)

    # Grade assignment
    if albi_score <= ALBI_GRADE_1_THRESHOLD:
        grade = 1
        sub_grade = "1"
    elif albi_score <= ALBI_GRADE_2_THRESHOLD:
        grade = 2
        # Sub-grade 2a: -2.60 to -2.09, 2b: -2.09 to -1.39
        if albi_score <= -2.09:
            sub_grade = "2a"
        else:
            sub_grade = "2b"
    else:
        grade = 3
        sub_grade = "3"

    return {
        "tool": "albi-albumin-bilirubin-grade",
        "albi_score": albi_score,
        "albi_grade": grade,
        "albi_sub_grade": sub_grade,
        "grade_description": _grade_description(grade),
        "median_survival_months": _median_survival(grade),
        "one_year_survival_pct": _one_year_survival(grade),
        "inputs": {
            "bilirubin": bilirubin,
            "bilirubin_unit": bilirubin_unit,
            "bilirubin_umol_l": round(bili_umol, 2),
            "albumin": albumin,
            "albumin_unit": albumin_unit,
            "albumin_g_l": round(alb_g_l, 2),
        },
        "classification": f"ALBI Grade {grade} (score: {albi_score})",
        "clinical_recommendation": _recommendation(grade, sub_grade),
    }


def _grade_description(grade: int) -> str:
    """Return description for ALBI grade."""
    return {
        1: "Good liver function (best prognosis)",
        2: "Intermediate liver function",
        3: "Poor liver function (worst prognosis)",
    }[grade]


def _median_survival(grade: int) -> float:
    """Approximate median survival in months by ALBI grade."""
    return {1: 26.5, 2: 14.5, 3: 6.5}[grade]


def _one_year_survival(grade: int) -> float:
    """Approximate 1-year survival rate (%) by ALBI grade."""
    return {1: 83.0, 2: 62.0, 3: 40.0}[grade]


def _recommendation(grade: int, sub_grade: str) -> str:
    """Generate clinical recommendation based on ALBI grade."""
    if grade == 1:
        return (
            "Good liver function reserve. Eligible for all treatment modalities "
            "including resection, ablation, and systemic therapy. "
            "Standard HCC surveillance and treatment protocols apply."
        )
    elif grade == 2:
        if sub_grade == "2a":
            return (
                "Intermediate liver function (ALBI 2a). Most treatments feasible "
                "with careful monitoring. Consider dose adjustments for systemic therapy. "
                "Resection may be considered with adequate future liver remnant."
            )
        else:
            return (
                "Intermediate liver function (ALBI 2b). Treatment options more limited. "
                "Systemic therapy dose modifications likely needed. "
                "Transplant evaluation recommended if within criteria."
            )
    else:
        return (
            "Poor liver function reserve. High risk for treatment-related toxicity. "
            "Transplant evaluation strongly recommended. "
            "Best supportive care if transplant ineligible. "
            "Systemic therapy requires careful risk-benefit assessment."
        )


# ---------------------------------------------------------------------------
# Batch processing
# ---------------------------------------------------------------------------

def process_batch(input_csv: str, output_csv: str) -> int:
    """Process a CSV of patients and write ALBI results."""
    with open(input_csv, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)

    out_fields = fieldnames + [
        "albi_score", "albi_grade", "albi_sub_grade",
        "grade_description", "clinical_recommendation",
    ]
    out_rows = []
    for r in rows:
        try:
            bili_unit = r.get("bilirubin_unit", "mg/dL")
            alb_unit = r.get("albumin_unit", "g/dL")
            res = calculate_albi(
                bilirubin=float(r["bilirubin"]),
                albumin=float(r["albumin"]),
                bilirubin_unit=bili_unit,
                albumin_unit=alb_unit,
            )
            row_dict = dict(r)
            row_dict["albi_score"] = res["albi_score"]
            row_dict["albi_grade"] = res["albi_grade"]
            row_dict["albi_sub_grade"] = res["albi_sub_grade"]
            row_dict["grade_description"] = res["grade_description"]
            row_dict["clinical_recommendation"] = res["clinical_recommendation"]
        except (ValueError, KeyError) as e:
            row_dict = dict(r)
            row_dict["albi_score"] = f"ERROR: {e}"
            row_dict["albi_grade"] = ""
            row_dict["albi_sub_grade"] = ""
            row_dict["grade_description"] = ""
            row_dict["clinical_recommendation"] = ""
        out_rows.append(row_dict)

    with open(output_csv, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=out_fields)
        writer.writeheader()
        writer.writerows(out_rows)

    print(f"Processed {len(out_rows)} records -> {output_csv}")
    return len(out_rows)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv=None):
    parser = argparse.ArgumentParser(
        description="ALBI (Albumin-Bilirubin) Grade Calculator for HCC"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Single evaluation
    sp = subparsers.add_parser("single", help="Evaluate a single patient")
    sp.add_argument("--bilirubin", type=float, required=True,
                    help="Serum bilirubin (mg/dL by default)")
    sp.add_argument("--albumin", type=float, required=True,
                    help="Serum albumin (g/dL by default)")
    sp.add_argument("--bilirubin-unit", default="mg/dL",
                    choices=["mg/dL", "µmol/L"],
                    help="Bilirubin unit (default: mg/dL)")
    sp.add_argument("--albumin-unit", default="g/dL",
                    choices=["g/dL", "g/L"],
                    help="Albumin unit (default: g/dL)")

    # Batch processing
    bp = subparsers.add_parser("batch", help="Batch process CSV file")
    bp.add_argument("-i", "--input", required=True, help="Input CSV file")
    bp.add_argument("-o", "--output", default="results.csv", help="Output CSV file")

    args = parser.parse_args(argv)

    if args.command == "single":
        result = calculate_albi(
            bilirubin=args.bilirubin,
            albumin=args.albumin,
            bilirubin_unit=args.bilirubin_unit,
            albumin_unit=args.albumin_unit,
        )
        print(json.dumps(result, indent=2))
    elif args.command == "batch":
        process_batch(args.input, args.output)


if __name__ == "__main__":
    main()
