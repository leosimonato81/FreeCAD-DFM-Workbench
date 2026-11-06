# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2026 Leonardo Simonato
# SPDX-FileNotice: DFM + FEM add-on.

import FreeCAD as App  # type: ignore
import FreeCADGui as Gui  # type: ignore

from .gui import fem_report_task as _fem_report_task
from .gui import preferences
from .gui import task_setup, task_show_normals, process_library
from .gui.preferences import (
    DFMPreferencesGeneral,
    DFMPreferencesAnalyzers,
    DFMPreferencesContour,
    DFMPreferencesResults,
)
from .gui.report.preferences_page import DFMPreferencesReports
from .gui import tools as _dfm_contour_tools


class DFMFEMWorkbench(Gui.Workbench):
    """Standalone workbench that coexists with the original DFM add-on."""

    MenuText = "DFM + FEM"
    ToolTip = "DFM tools with reports that include saved FEM results"
    Icon = ":/icons/dfm_analysis.svg"

    def Initialize(self):
        self.list = [
            "DFMFEM_SetupAnalysis",
            "DFMFEM_ProcessLibrary",
            "DFMFEM_DraftAnalysis",
            "DFMFEM_ThicknessAnalysis",
            "DFMFEM_FEMReport",
        ]
        self.appendToolbar("DFM + FEM", self.list)
        self.appendMenu("DFM + FEM", self.list)

    def Activated(self):
        return

    def Deactivated(self):
        return

    def GetClassName(self):
        return "Gui::PythonWorkbench"


Gui.addWorkbench(DFMFEMWorkbench())
Gui.addPreferencePage(DFMPreferencesGeneral, "DFM + FEM")
Gui.addPreferencePage(DFMPreferencesResults, "DFM + FEM")
Gui.addPreferencePage(DFMPreferencesReports, "DFM + FEM")
Gui.addPreferencePage(DFMPreferencesAnalyzers, "DFM + FEM")
Gui.addPreferencePage(DFMPreferencesContour, "DFM + FEM")

# The original DFM add-on installs the document observer. Avoid registering a
# second observer for the same compatible DFM result objects when both add-ons
# are installed together.
