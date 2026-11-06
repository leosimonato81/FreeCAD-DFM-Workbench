# SPDX-License-Identifier: LGPL-2.1-or-later

import csv
import math
from pathlib import Path
import sys
import tempfile
import unittest
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "freecad"))

from DFM.fem.results import iter_result_objects, summarize_result, write_nodal_csv


class FEMResultSummaryTests(unittest.TestCase):
    def setUp(self):
        self.result = SimpleNamespace(
            TypeId="Fem::FemResultObjectPython",
            Name="CCX_Results",
            Label="CCX Results",
            NodeNumbers=[14, 18, 25],
            DisplacementLengths=[3.0, float("nan"), 1.5],
            vonMises=[4.0, 6.0, 2.0],
        )

    def test_summaries_retain_node_ids_and_skip_non_finite_values(self):
        summary = summarize_result(self.result)
        displacement, von_mises = summary.quantities

        self.assertEqual(displacement.key, "DisplacementLengths")
        self.assertEqual(displacement.count, 2)
        self.assertEqual((displacement.minimum, displacement.node_at_minimum), (1.5, 25))
        self.assertEqual((displacement.maximum, displacement.node_at_maximum), (3.0, 14))
        self.assertEqual((von_mises.minimum, von_mises.node_at_minimum), (2.0, 25))
        self.assertEqual((von_mises.maximum, von_mises.node_at_maximum), (6.0, 18))
        self.assertIsNone(summary.node_values[1].displacement_mm)

    def test_document_scan_only_returns_native_result_objects(self):
        other = SimpleNamespace(TypeId="Part::Feature")
        found = iter_result_objects(SimpleNamespace(Objects=[other, self.result]))
        self.assertEqual(found, (self.result,))

    def test_csv_contains_one_row_per_node_and_both_requested_fields(self):
        summary = summarize_result(self.result)
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "result.csv"
            write_nodal_csv(output, summary)
            with output.open(encoding="utf-8-sig", newline="") as stream:
                rows = list(csv.reader(stream))

        self.assertEqual(rows[1], ["Node", "Displacement magnitude (mm)", "von Mises stress (MPa)"])
        self.assertEqual(len(rows), 5)
        self.assertEqual(rows[2], ["14", "3.0", "4.0"])
        self.assertEqual(rows[3], ["18", "", "6.0"])


if __name__ == "__main__":
    unittest.main()
