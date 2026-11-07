# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2026 Leonardo Simonato
# SPDX-FileNotice: DFM + FEM add-on.

"""Launch the FEM-only report from the unified Análises task."""

from PySide6 import QtCore, QtWidgets

import FreeCAD as App  # type: ignore
import FreeCADGui as Gui  # type: ignore


def open_fem_only_report(parent=None) -> None:
    """Select saved FEM results and a reference solid, then open report options."""
    from ...fem.results import iter_result_objects, summarize_result
    from ..results.bridge import DFMViewProvider
    from .capture import ViewportCapture
    from .data import fem_only_report_data
    from .dialog import ReportDialog
    from .settings import ReportSettings

    doc = getattr(App, "ActiveDocument", None)
    if doc is None:
        QtWidgets.QMessageBox.information(
            parent, "Relatório FEM", "Abra o arquivo .FCStd da análise FEM na bancada FEM nativa.")
        return

    results = list(iter_result_objects(doc))
    if not results:
        path = getattr(doc, "FileName", "") or getattr(doc, "Label", "Documento sem nome")
        QtWidgets.QMessageBox.warning(
            parent, "Resultado FEM não encontrado",
            f"Documento aberto: {path}\n\n"
            "Não encontrei um objeto Fem::FemResultObjectPython, normalmente chamado "
            "CCX_Results. Execute a análise na bancada FEM nativa, salve o documento .FCStd "
            "específico que contém CCX_Results e abra esse arquivo antes de gerar o relatório. "
            "Este comando não executa o solver nem recupera dados de outro arquivo.")
        return

    candidates = []
    for obj in getattr(doc, "Objects", ()):
        if str(getattr(obj, "TypeId", "")).startswith("Fem::"):
            continue
        try:
            shape = obj.Shape
            if shape is not None and not shape.isNull() and len(shape.Solids) > 0:
                candidates.append(obj)
        except Exception:
            continue
    if not candidates:
        QtWidgets.QMessageBox.warning(
            parent, "Modelo de referência não encontrado",
            "O documento contém resultados FEM, mas não encontrei um sólido CAD para enquadrar "
            "a imagem. Mantenha no arquivo a peça original usada para criar a malha FEM.")
        return

    dialog = QtWidgets.QDialog(parent or Gui.getMainWindow())
    dialog.setWindowTitle("Relatório FEM — resultados salvos")
    dialog.setMinimumWidth(520)
    layout = QtWidgets.QVBoxLayout(dialog)
    intro = QtWidgets.QLabel(
        "Este fluxo gera um relatório FEM sem exigir uma execução DFM. Selecione o objeto "
        "de resultados da análise e o sólido original para enquadrar a vista.\n\n"
        "Use o arquivo .FCStd salvo pela bancada FEM nativa. O relatório lê o objeto "
        "CCX_Results do documento aberto e não recalcula a simulação.")
    intro.setWordWrap(True)
    layout.addWidget(intro)

    source_path = getattr(doc, "FileName", "")
    source_text = (f"Arquivo .FCStd aberto: {source_path}" if source_path else
                   f"Documento aberto: {doc.Label} (ainda não salvo como arquivo .FCStd)")
    file_label = QtWidgets.QLabel(source_text)
    file_label.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextSelectableByMouse)
    file_label.setWordWrap(True)
    layout.addWidget(file_label)

    result_combo = QtWidgets.QComboBox()
    for obj in results:
        result_combo.addItem(str(obj.Label), str(obj.Name))
    layout.addWidget(QtWidgets.QLabel("Resultado FEM salvo"))
    layout.addWidget(result_combo)

    solid_combo = QtWidgets.QComboBox()
    for obj in candidates:
        solid_combo.addItem(str(obj.Label), str(obj.Name))
    try:
        selected = Gui.Selection.getSelection()
        if selected:
            index = solid_combo.findData(str(selected[0].Name))
            if index >= 0:
                solid_combo.setCurrentIndex(index)
    except Exception:
        pass
    layout.addWidget(QtWidgets.QLabel("Sólido CAD original (referência de câmera)"))
    layout.addWidget(solid_combo)

    buttons = QtWidgets.QDialogButtonBox(
        QtWidgets.QDialogButtonBox.StandardButton.Cancel
        | QtWidgets.QDialogButtonBox.StandardButton.Ok)
    buttons.button(QtWidgets.QDialogButtonBox.StandardButton.Ok).setText("Revisar opções do PDF…")
    buttons.accepted.connect(dialog.accept)
    buttons.rejected.connect(dialog.reject)
    layout.addWidget(buttons)
    if dialog.exec() != QtWidgets.QDialog.DialogCode.Accepted:
        return

    result_obj = doc.getObject(result_combo.currentData())
    target_obj = doc.getObject(solid_combo.currentData())
    if result_obj is None or target_obj is None:
        QtWidgets.QMessageBox.warning(parent, "Documento alterado",
                                      "O objeto selecionado não está mais disponível no documento.")
        return

    data = fem_only_report_data(doc.Label, target_obj.Label, summarize_result(result_obj))
    data.fem_document_path = getattr(doc, "FileName", "")
    settings = ReportSettings.load().copy(
        report_mode="fem",
        title="FEM report: {model}",
        file_name="{document}_FEM_{date}",
        include_dfm_images=False,
        include_dfm_tables=False,
        fem_follow_dfm_views=False,
        overview_view="current",
        view_direction="current",
    )
    bridge = DFMViewProvider(target_obj)
    try:
        report = ReportDialog(
            data,
            settings,
            lambda report_settings: ViewportCapture(
                bridge, report_settings, fem_result_object=result_obj),
            parent=parent or Gui.getMainWindow(),
        )
        report.exec()
    finally:
        bridge.restore()
