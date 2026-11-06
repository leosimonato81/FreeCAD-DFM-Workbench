# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileNotice: Part of the DFM Workbench.

"""Read-only summaries of native FreeCAD FEM result objects.

This module intentionally does not inspect or modify FEM meshes, view objects,
solver state, or result files. It reads result arrays that FreeCAD has already
loaded into the document and reports only quantities that are present.
"""

from dataclasses import dataclass
import csv
import math
from pathlib import Path
from typing import Any, Iterable, Optional


RESULT_TYPE_ID = "Fem::FemResultObjectPython"


@dataclass(frozen=True)
class FEMQuantity:
    """Summary row for one scalar result field."""

    key: str
    label: str
    unit: str
    count: int
    minimum: float
    maximum: float
    node_at_minimum: Optional[int] = None
    node_at_maximum: Optional[int] = None


@dataclass(frozen=True)
class FEMNodeValue:
    node_number: int
    displacement_mm: Optional[float]
    von_mises_mpa: Optional[float]


@dataclass(frozen=True)
class FEMResultSummary:
    """Available scalar quantities from one native FEM result object."""

    object_name: str
    object_label: str
    quantities: tuple[FEMQuantity, ...]
    node_values: tuple[FEMNodeValue, ...] = ()


# The units match the native CalculiX result object conventions documented by
# FreeCAD. Fields are optional and omitted when the result array is empty.
_SCALAR_FIELDS = (
    ("DisplacementLengths", "Displacement magnitude", "mm", "displacement_mm"),
    ("vonMises", "von Mises stress", "MPa", "von_mises_mpa"),
)


def _finite_indexed_values(values: Iterable[Any]) -> list[tuple[int, float]]:
    result = []
    for index, value in enumerate(values):
        try:
            number = float(value)
        except (TypeError, ValueError, OverflowError):
            continue
        if math.isfinite(number):
            result.append((index, number))
    return result


def _read_field(obj: Any, name: str) -> Optional[Iterable[Any]]:
    try:
        values = getattr(obj, name)
    except (AttributeError, RuntimeError):
        return None
    if values is None:
        return None
    try:
        if len(values) == 0:
            return None
    except (TypeError, AttributeError):
        pass
    try:
        return iter(values)
    except TypeError:
        return None


def is_result_object(obj: Any) -> bool:
    """Return whether *obj* is FreeCAD's native FEM result object type."""
    return getattr(obj, "TypeId", None) == RESULT_TYPE_ID


def iter_result_objects(document: Any) -> tuple[Any, ...]:
    """Return native FEM result objects in document order; never run a solver."""
    if document is None:
        return ()
    try:
        objects = document.Objects
    except (AttributeError, RuntimeError):
        return ()
    return tuple(obj for obj in objects if is_result_object(obj))


def summarize_result(obj: Any) -> FEMResultSummary:
    """Read available scalar summaries from one result object.

    Empty, missing, non-numeric, NaN, and infinite entries are ignored. No
    guessed values are emitted for quantities absent from the result object.
    """
    node_numbers_raw = _read_field(obj, "NodeNumbers")
    node_numbers = []
    if node_numbers_raw is not None:
        for number in node_numbers_raw:
            try:
                node_numbers.append(int(number))
            except (TypeError, ValueError, OverflowError):
                node_numbers.append(None)

    rows = []
    columns: dict[str, list[Optional[float]]] = {}
    for attribute, label, unit, column in _SCALAR_FIELDS:
        values = _read_field(obj, attribute)
        if values is None:
            continue
        indexed = _finite_indexed_values(values)
        if not indexed:
            continue
        numeric = [value for _index, value in indexed]
        minimum_index, minimum = min(indexed, key=lambda pair: pair[1])
        maximum_index, maximum = max(indexed, key=lambda pair: pair[1])
        values_by_index: list[Optional[float]] = [None] * len(indexed)
        for index, value in indexed:
            if index >= len(values_by_index):
                values_by_index.extend([None] * (index + 1 - len(values_by_index)))
            values_by_index[index] = value
        columns[column] = values_by_index
        rows.append(FEMQuantity(
            key=attribute,
            label=label,
            unit=unit,
            count=len(numeric),
            minimum=minimum,
            maximum=maximum,
            node_at_minimum=(node_numbers[minimum_index]
                             if minimum_index < len(node_numbers) else None),
            node_at_maximum=(node_numbers[maximum_index]
                             if maximum_index < len(node_numbers) else None),
        ))

    # Map values back to FreeCAD node labels. If array lengths differ, retain
    # all numbered rows and leave unavailable/misaligned fields blank.
    node_values = tuple(
        FEMNodeValue(
            node_number=node_number,
            displacement_mm=(columns.get("displacement_mm", [])[index]
                             if index < len(columns.get("displacement_mm", [])) else None),
            von_mises_mpa=(columns.get("von_mises_mpa", [])[index]
                           if index < len(columns.get("von_mises_mpa", [])) else None),
        )
        for index, node_number in enumerate(node_numbers)
        if node_number is not None
    )

    return FEMResultSummary(
        object_name=str(getattr(obj, "Name", "")),
        object_label=str(getattr(obj, "Label", getattr(obj, "Name", "FEM result"))),
        quantities=tuple(rows),
        node_values=node_values,
    )


def write_nodal_csv(path: str | Path, summary: FEMResultSummary, language: str = "en") -> None:
    """Write displacement and von Mises values, one row per native node."""
    with open(path, "w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.writer(stream)
        if language == "pt_BR":
            writer.writerow(("Objeto de resultados", summary.object_label))
            writer.writerow(("Nó", "Magnitude do deslocamento (mm)", "Tensão de von Mises (MPa)"))
        else:
            writer.writerow(("Result object", summary.object_label))
            writer.writerow(("Node", "Displacement magnitude (mm)", "von Mises stress (MPa)"))
        for row in summary.node_values:
            writer.writerow((row.node_number, row.displacement_mm, row.von_mises_mpa))
