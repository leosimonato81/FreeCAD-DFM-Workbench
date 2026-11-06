# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileNotice: Part of the DFM Workbench.

"""FEM report task panel, usable without running a DFM analysis."""

import os
import tempfile

from PySide6 import QtGui, QtWidgets

import FreeCAD as App  # type: ignore
import FreeCADGui as Gui  # type: ignore

from ..fem.results import iter_result_objects, summarize_result
from .report.data import fem_only_report_data
from .report.settings import ReportSettings
from .results.tabs.fem_report import FEMReportTab


class FEMReportTaskPanel(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FEM report")
        root = QtWidgets.QVBoxLayout(self)
        self.tab = FEMReportTab()
        self.tab.include_dfm_highlights.setEnabled(False)
        self.tab.set_dfm_available(False)
        self.tab.capture_requested.connect(self.capture_view)
        self.tab.export_requested.connect(self.open_report)
        self.tab.configure_requested.connect(self.open_report)
        self.tab.selection_changed.connect(self.refresh_summary)
        root.addWidget(self.tab)
        doc = getattr(App, "ActiveDocument", None)
        self.tab.set_results(list(iter_result_objects(doc)))
        self.refresh_summary()

    def selected_object(self):
        doc = getattr(App, "ActiveDocument", None)
        name = self.tab.result_name()
        try:
            return doc.getObject(name) if doc is not None and name else None
        except Exception:
            return None

    def refresh_summary(self, *_args):
        obj = self.selected_object()
        try:
            self.tab.set_summary(summarize_result(obj) if obj is not None else None)
        except Exception as exc:
            self.tab.set_summary(None)
            App.Console.PrintWarning(f"DFM: could not read FEM result values: {exc}\n")

    def capture_view(self):
        gui_doc = getattr(Gui, "ActiveDocument", None)
        view = getattr(gui_doc, "ActiveView", None) if gui_doc is not None else None
        if view is None:
            QtWidgets.QMessageBox.warning(self, "FEM viewport", "No active 3D view is available.")
            return
        path = None
        try:
            size = view.getSize()
            width, height = int(size[0]), int(size[1])
            if width <= 0 or height <= 0:
                raise RuntimeError("The active viewport has no drawable size.")
            fd, path = tempfile.mkstemp(prefix="dfm_fem_view_", suffix=".png")
            os.close(fd)
            Gui.updateGui()
            view.saveImage(path, width, height, "Current")
            result = self.selected_object()
            caption = (f"{result.Label} — vista FEM"
                       if result is not None else "Vista FEM")
            self.tab.add_capture(QtGui.QImage(path), caption)
        except Exception as exc:
            App.Console.PrintWarning(f"DFM: FEM viewport capture failed: {exc}\n")
            QtWidgets.QMessageBox.warning(self, "FEM viewport capture", str(exc))
        finally:
            if path:
                try:
                    os.remove(path)
                except OSError:
                    pass

    def open_report(self):
        obj = self.selected_object()
        if obj is None:
            QtWidgets.QMessageBox.information(
                self, "FEM report", "No FEM result object is selected in the document.")
            return
        from .report.dialog import ReportDialog

        doc = getattr(App, "ActiveDocument", None)
        data = fem_only_report_data(
            (doc.Label if doc is not None else ""),
            getattr(obj, "Label", "FEM result"),
            summarize_result(obj),
            self.tab.selected_images(),
        )
        settings = ReportSettings.load().copy(
            title="FEM report: {model}",
            file_name="{document}_FEM_{date}",
            include_dfm_images=False,
            include_dfm_tables=False,
            include_fem_images=self.tab.include_images.isChecked(),
            include_fem_tables=self.tab.include_tables.isChecked(),
            include_fem_csv=self.tab.include_csv.isChecked(),
            dfm_highlights_in_fem_view=False,
        )
        dialog = ReportDialog(data, settings, parent=Gui.getMainWindow())
        dialog.exec()
        self.tab.include_dfm_images.setChecked(dialog.settings.include_dfm_images)
        self.tab.include_dfm_tables.setChecked(dialog.settings.include_dfm_tables)
        self.tab.include_images.setChecked(dialog.settings.include_fem_images)
        self.tab.include_tables.setChecked(dialog.settings.include_fem_tables)
        self.tab.include_csv.setChecked(dialog.settings.include_fem_csv)


class FEMReportCommand:
    def GetResources(self):
        return {
            "Pixmap": ":/icons/dfm_analysis.svg",
            "MenuText": "FEM Report",
            "ToolTip": "Create a FEM report from results already in the active document.",
        }

    def Activated(self):
        Gui.Control.showDialog(FEMReportTaskPanel())

    def IsActive(self):
        return getattr(App, "ActiveDocument", None) is not None


Gui.addCommand("DFM_FEMReport", FEMReportCommand())
