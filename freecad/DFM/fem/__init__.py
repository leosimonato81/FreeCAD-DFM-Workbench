# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileNotice: Part of the DFM Workbench.

"""Read-only adapters for optional FEM result data."""

from .results import (
    FEMNodeValue,
    FEMQuantity,
    FEMResultSummary,
    iter_result_objects,
    summarize_result,
    write_nodal_csv,
)

__all__ = [
    "FEMNodeValue",
    "FEMQuantity",
    "FEMResultSummary",
    "iter_result_objects",
    "summarize_result",
    "write_nodal_csv",
]
