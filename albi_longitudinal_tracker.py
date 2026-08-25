#!/usr/bin/env python3
"""
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
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional


def albi_score(bilirubin_umol_l: float, albumin_g_l: float) -> float:
    if bilirubin_umol_l <= 0 or albumin_g_l <= 0:
        raise ValueError("bilirubin and albumin must be positive")
    return round(0.66 * math.log10(bilirubin_umol_l) - 0.085 * albumin_g_l, 4)


def albi_grade(score: float) -> int:
    if score <= -2.60:
        return 1
    if score <= -1.39:
        return 2
    return 3


@dataclass
class ALBIAssessment:
    day: int
    bilirubin_umol_l: float
    albumin_g_l: float
    treatment: Optional[str] = None
    score: float = field(init=False)
    grade: int = field(init=False)

    def __post_init__(self) -> None:
        self.score = albi_score(self.bilirubin_umol_l, self.albumin_g_l)
        self.grade = albi_grade(self.score)


@dataclass
class GradeTransition:
    from_day: int
    to_day: int
    from_grade: int
    to_grade: int
    delta_score: float
    treatment_context: Optional[str]


@dataclass
class ChangePoint:
    day_index: int
    mean_shift: float
    z_score: float


def track_trajectory(assessments: List[ALBIAssessment]) -> Dict[str, object]:
    """Grade transitions plus a scan-statistic change point on the score series."""
    if len(assessments) < 2:
        raise ValueError("need at least two assessments for trajectory analysis")

    transitions: List[GradeTransition] = []
    for prev, curr in zip(assessments, assessments[1:]):
        if curr.grade != prev.grade:
            transitions.append(
                GradeTransition(
                    from_day=prev.day,
                    to_day=curr.day,
                    from_grade=prev.grade,
                    to_grade=curr.grade,
                    delta_score=round(curr.score - prev.score, 4),
                    treatment_context=curr.treatment,
                )
            )

    change_point = _detect_change_point([a.score for a in assessments])
    if change_point is not None:
        cp = ChangePoint(
            day_index=change_point[0],
            mean_shift=round(change_point[1], 4),
            z_score=round(change_point[2], 3),
        )
    else:
        cp = None

    return {
        "scores": [(a.day, a.score, a.grade) for a in assessments],
        "grade_transitions": transitions,
        "deterioration_change_point": cp,
    }


def _detect_change_point(scores: List[float], min_z: float = 2.0):
    """Max standardized two-segment mean shift; returns (index, shift, z)."""
    n = len(scores)
    best = None
    for split in range(2, n - 1):
        left, right = scores[:split], scores[split:]
        n1, n2 = len(left), len(right)
        m1, m2 = sum(left) / n1, sum(right) / n2
        var_pooled = (
            sum((x - m1) ** 2 for x in left) + sum((x - m2) ** 2 for x in right)
        ) / (n - 2)
        se = math.sqrt(var_pooled * (1.0 / n1 + 1.0 / n2))
        if se == 0.0:
            continue
        z = (m2 - m1) / se
        if best is None or abs(z) > abs(best[2]):
            best = (split, m2 - m1, z)
    if best is not None and abs(best[2]) >= min_z:
        return best
    return None


def alert_escalation(
    assessments: List[ALBIAssessment],
    window_days: int = 30,
) -> Dict[str, str]:
    """Tiered escalation: advisory / urgent / critical based on recent worsening."""
    if not assessments:
        raise ValueError("no assessments provided")
    latest = assessments[-1]
    window = [a for a in assessments if latest.day - a.day <= window_days]
    baseline = window[0] if window else assessments[0]

    rise = latest.score - baseline.score
    grade_steps = latest.grade - baseline.grade

    if latest.grade >= 3 and (rise >= 0.50 or grade_steps >= 2):
        tier = "critical"
    elif grade_steps >= 1 and rise >= 0.30:
        tier = "urgent"
    elif grade_steps >= 1 or rise >= 0.20:
        tier = "advisory"
    else:
        tier = "none"

    return {
        "tier": tier,
        "score_rise_in_window": round(rise, 4),
        "grade_steps_worsened": str(max(0, grade_steps)),
        "route": {
            "advisory": "hepatology review at next clinic",
            "urgent": "page hepatology/oncology within 24h",
            "critical": "transplant team + oncology immediate escalation",
            "none": "routine monitoring",
        }[tier],
    }


MILAN_CRITERIA = {"single_max_cm": 5.0, "max_total_cm": 8.0, "max_lesions": 3}


def stratify_patient(albi_grade_value: int, afp_ng_ml: float,
                     lesion_count: int, largest_tumor_cm: float,
                     total_diameter_cm: float) -> Dict[str, str]:
    """Composite ALBI x tumor burden stratification for HCC pathways."""
    milan_eligible = (
        afp_ng_ml < 1000
        and lesion_count <= MILAN_CRITERIA["max_lesions"]
        and largest_tumor_cm <= MILAN_CRITERIA["single_max_cm"]
        and total_diameter_cm <= MILAN_CRITERIA["max_total_cm"]
    )
    if albi_grade_value == 1 and milan_eligible:
        pathway = "transplant evaluation (Milan within, preserved liver)"
    elif albi_grade_value == 1:
        pathway = "locoregional therapy (TACE/ablation), liver function adequate"
    elif albi_grade_value == 2:
        pathway = "systemic therapy candidate (atezolizumab-bevacizumab class); caution TACE"
    else:
        pathway = "palliative/best supportive care; systemic trials only"
    return {
        "albi_grade": f"Grade {albi_grade_value}",
        "milan_within": str(milan_eligible),
        "recommended_pathway": pathway,
    }


def _demo() -> None:
    course = [
        ALBIAssessment(day=0, bilirubin_umol_l=15.0, albumin_g_l=42, treatment="baseline"),
        ALBIAssessment(day=45, bilirubin_umol_l=18.0, albumin_g_l=41, treatment="TACE cycle 1"),
        ALBIAssessment(day=90, bilirubin_umol_l=22.0, albumin_g_l=40, treatment="TACE cycle 2"),
        ALBIAssessment(day=120, bilirubin_umol_l=34.0, albumin_g_l=33, treatment="progression"),
        ALBIAssessment(day=150, bilirubin_umol_l=60.0, albumin_g_l=28, treatment="decompensation"),
    ]
    traj = track_trajectory(course)
    print({"scores": traj["scores"]})
    print({"transitions": [
        (t.from_day, t.to_day, t.from_grade, t.to_grade, t.delta_score)
        for t in traj["grade_transitions"]
    ]})
    print({"change_point": traj["deterioration_change_point"]})
    print(alert_escalation(course))
    print(stratify_patient(
        course[-1].grade, afp_ng_ml=420, lesion_count=2,
        largest_tumor_cm=3.1, total_diameter_cm=4.6,
    ))


if __name__ == "__main__":
    _demo()
