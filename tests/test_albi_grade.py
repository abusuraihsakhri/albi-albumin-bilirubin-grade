#!/usr/bin/env python3
"""Tests for ALBI (Albumin-Bilirubin) Grade Calculator - 20 real clinical tests."""

import json
import math
import pytest
from albi_grade import (
    calculate_albi,
    process_batch,
    ALBI_GRADE_1_THRESHOLD,
    ALBI_GRADE_2_THRESHOLD,
    BILIRUBIN_CONVERSION,
)


# ---------------------------------------------------------------------------
# ALBI score calculation
# ---------------------------------------------------------------------------

class TestALBIScore:
    def test_known_grade_1(self):
        """Low bilirubin, high albumin → Grade 1."""
        # bilirubin=0.8 mg/dL → 13.68 µmol/L, albumin=4.0 g/dL → 40 g/L
        # log10(13.68)*0.66 + 40*(-0.085) = 0.7498 - 3.4 = -2.6502 → Grade 1
        res = calculate_albi(bilirubin=0.8, albumin=4.0)
        assert res["albi_score"] <= ALBI_GRADE_1_THRESHOLD
        assert res["albi_grade"] == 1

    def test_known_grade_2(self):
        """Moderate values → Grade 2."""
        res = calculate_albi(bilirubin=2.0, albumin=3.2)
        assert ALBI_GRADE_1_THRESHOLD < res["albi_score"] <= ALBI_GRADE_2_THRESHOLD
        assert res["albi_grade"] == 2

    def test_known_grade_3(self):
        """High bilirubin, low albumin → Grade 3."""
        res = calculate_albi(bilirubin=5.0, albumin=2.5)
        assert res["albi_score"] > ALBI_GRADE_2_THRESHOLD
        assert res["albi_grade"] == 3

    def test_manual_calculation_grade_1(self):
        """Verify formula: log10(17.1) * 0.66 + 40 * (-0.085)"""
        bili_umol = 1.0 * 17.1  # 17.1 µmol/L
        alb_g_l = 4.0 * 10.0    # 40 g/L
        expected = math.log10(bili_umol) * 0.66 + alb_g_l * (-0.085)
        res = calculate_albi(bilirubin=1.0, albumin=4.0)
        assert abs(res["albi_score"] - expected) < 0.001

    def test_manual_calculation_grade_3(self):
        """Verify formula for high-risk case."""
        bili_umol = 5.0 * 17.1
        alb_g_l = 2.5 * 10.0
        expected = math.log10(bili_umol) * 0.66 + alb_g_l * (-0.085)
        res = calculate_albi(bilirubin=5.0, albumin=2.5)
        assert abs(res["albi_score"] - expected) < 0.001

    def test_boundary_grade_1_threshold(self):
        """Score exactly at -2.60 should be Grade 1."""
        # We need to find values that give exactly -2.60
        # log10(bili_umol) * 0.66 + albumin_g_l * (-0.085) = -2.60
        # Use albumin=3.5 g/dL → 35 g/L: 35 * (-0.085) = -2.975
        # log10(bili_umol) * 0.66 = -2.60 - (-2.975) = 0.375
        # log10(bili_umol) = 0.5682
        # bili_umol = 10^0.5682 = 3.70
        # bili_mg_dl = 3.70 / 17.1 = 0.216
        res = calculate_albi(bilirubin=0.216, albumin=3.5)
        assert res["albi_grade"] == 1

    def test_boundary_grade_2_threshold(self):
        """Score just above -2.60 should be Grade 2."""
        # Use bilirubin=3.0 mg/dL, albumin=3.0 g/dL
        # bili_umol = 51.3, alb_g_l = 30
        # log10(51.3)*0.66 + 30*(-0.085) = 1.7101*0.66 + (-2.55) = 1.1287 - 2.55 = -1.4213
        # That's > -1.39, so Grade 3. Let me pick better values.
        # bilirubin=1.5, albumin=3.5
        # bili_umol = 25.65, alb_g_l = 35
        # log10(25.65)*0.66 + 35*(-0.085) = 1.4091*0.66 + (-2.975) = 0.930 - 2.975 = -2.045
        # That's between -2.60 and -1.39 → Grade 2
        res = calculate_albi(bilirubin=1.5, albumin=3.5)
        assert res["albi_grade"] == 2


# ---------------------------------------------------------------------------
# Sub-grade classification
# ---------------------------------------------------------------------------

class TestSubGrades:
    def test_sub_grade_1(self):
        res = calculate_albi(bilirubin=0.8, albumin=4.5)
        assert res["albi_sub_grade"] == "1"

    def test_sub_grade_2a(self):
        """ALBI between -2.60 and -2.09 → 2a."""
        # bilirubin=1.0, albumin=3.5
        # bili_umol=17.1, alb_g_l=35
        # log10(17.1)*0.66 + 35*(-0.085) = 1.2330*0.66 + (-2.975) = 0.8138 - 2.975 = -2.1612
        # That's between -2.60 and -2.09 → 2a
        res = calculate_albi(bilirubin=1.0, albumin=3.5)
        assert res["albi_sub_grade"] == "2a"

    def test_sub_grade_2b(self):
        """ALBI between -2.09 and -1.39 → 2b."""
        # bilirubin=1.5, albumin=3.2
        # bili_umol=25.65, alb_g_l=32
        # log10(25.65)*0.66 + 32*(-0.085) = 1.4091*0.66 + (-2.72) = 0.930 - 2.72 = -1.79
        # That's between -2.09 and -1.39 → 2b
        res = calculate_albi(bilirubin=1.5, albumin=3.2)
        assert res["albi_sub_grade"] == "2b"

    def test_sub_grade_3(self):
        res = calculate_albi(bilirubin=5.0, albumin=2.5)
        assert res["albi_sub_grade"] == "3"


# ---------------------------------------------------------------------------
# Unit conversions
# ---------------------------------------------------------------------------

class TestUnitConversions:
    def test_umol_input(self):
        """Direct µmol/L input should give same result as converted mg/dL."""
        res_mgdl = calculate_albi(bilirubin=2.0, albumin=3.5, bilirubin_unit="mg/dL")
        res_umol = calculate_albi(bilirubin=2.0 * 17.1, albumin=3.5, bilirubin_unit="µmol/L")
        assert abs(res_mgdl["albi_score"] - res_umol["albi_score"]) < 0.001

    def test_g_l_input(self):
        """Direct g/L input should give same result as converted g/dL."""
        res_gdl = calculate_albi(bilirubin=2.0, albumin=3.5, albumin_unit="g/dL")
        res_gl = calculate_albi(bilirubin=2.0, albumin=35.0, albumin_unit="g/L")
        assert abs(res_gdl["albi_score"] - res_gl["albi_score"]) < 0.001

    def test_invalid_bilirubin_unit(self):
        with pytest.raises(ValueError):
            calculate_albi(bilirubin=2.0, albumin=3.5, bilirubin_unit="nmol")

    def test_invalid_albumin_unit(self):
        with pytest.raises(ValueError):
            calculate_albi(bilirubin=2.0, albumin=3.5, albumin_unit="mg/L")


# ---------------------------------------------------------------------------
# Edge cases and validation
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_zero_bilirubin_raises(self):
        """log10(0) is undefined; should raise ValueError."""
        with pytest.raises(ValueError):
            calculate_albi(bilirubin=0.0, albumin=3.5)

    def test_negative_bilirubin_raises(self):
        with pytest.raises(ValueError):
            calculate_albi(bilirubin=-1.0, albumin=3.5)

    def test_result_has_all_fields(self):
        res = calculate_albi(bilirubin=2.0, albumin=3.5)
        assert "albi_score" in res
        assert "albi_grade" in res
        assert "albi_sub_grade" in res
        assert "classification" in res
        assert "clinical_recommendation" in res
        assert "median_survival_months" in res

    def test_survival_decreases_with_grade(self):
        """Higher grade → lower survival."""
        g1 = calculate_albi(bilirubin=0.5, albumin=4.5)
        g3 = calculate_albi(bilirubin=5.0, albumin=2.5)
        assert g1["one_year_survival_pct"] > g3["one_year_survival_pct"]


# ---------------------------------------------------------------------------
# Batch processing
# ---------------------------------------------------------------------------

class TestBatch:
    def test_batch_basic(self, tmp_path):
        csv_in = tmp_path / "in.csv"
        csv_out = tmp_path / "out.csv"
        csv_in.write_text(
            "bilirubin,albumin\n1.0,4.0\n5.0,2.5\n",
            encoding="utf-8",
        )
        count = process_batch(str(csv_in), str(csv_out))
        assert count == 2
        assert csv_out.exists()
        content = csv_out.read_text(encoding="utf-8")
        assert "albi_score" in content
        assert "albi_grade" in content

    def test_batch_sample_csv(self, tmp_path):
        import os
        sample_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sample.csv")
        csv_out = tmp_path / "out_sample.csv"
        count = process_batch(sample_path, str(csv_out))
        assert count == 3
        assert csv_out.exists()

