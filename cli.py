#!/usr/bin/env python3
"""
CLI entry point for ALBI (Albumin-Bilirubin) Grade Calculator.
Delegates to albi_grade.main() for all commands.
"""

import sys
from albi_grade import main

if __name__ == "__main__":
    main()
