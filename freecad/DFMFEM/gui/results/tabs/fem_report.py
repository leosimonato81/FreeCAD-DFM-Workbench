# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileNotice: Part of the DFM Workbench.

"""Controls for adding existing FEM results and viewport captures to reports."""

from typing import Any

from PySide6 import QtCore, QtGui, QtWidgets

from ....fem.results import FEMResultSummary
from ....gui.report.data import ReportImage


class FEMReportTab(QtWidgets.QWidget):
    capture_requested = QtCore.Signal()
    export_requested = QtCore.Signal()
    configure_requested = QtCore.Signal()
    selection_changed = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._images: dict[str, ReportImage] = {}

        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(8)

        intro = QtWidgets.QLabel(
            "Relatório combinado DFM + FEM. Selecione um resultado FEM já calculado e deixe "
            "a visualização FEM ativa antes de capturar. As capturas FEM preservam o mapa de "
            "cores e a câmera; os realces DFM ficam desligados por padrão. No PDF, DFM e FEM "
            "aparecem em seções separadas para avaliação profissional."
        )
        intro.setWordWrap(True)
        root.addWidget(intro)

        result_row = QtWidgets.QHBoxLayout()
        result_row.addWidget(QtWidgets.QLabel("Resultado"))
        self.result_combo = QtWidgets.QComboBox()
        self.result_combo.currentIndexChanged.connect(self.selection_changed)
        result_row.addWidget(self.result_combo, 1)
        root.addLayout(result_row)

        self.summary_label = QtWidgets.QLabel("Nenhum resultado FEM detectado.")
        self.summary_label.setWordWrap(True)
        root.addWidget(self.summary_label)

        options = QtWidgets.QGroupBox("Conteúdo FEM")
        options_layout = QtWidgets.QVBoxLayout(options)
        self.include_images = QtWidgets.QCheckBox("Incluir imagens FEM selecionadas")
        self.include_images.setChecked(True)
        self.include_tables = QtWidgets.QCheckBox("Incluir resumo de deslocamento e von Mises")
        self.include_tables.setChecked(True)
        self.include_csv = QtWidgets.QCheckBox("Exportar também os valores por nó em CSV")
        self.include_dfm_highlights = QtWidgets.QCheckBox("Mostrar realces DFM nas capturas FEM")
        self.include_dfm_highlights.setChecked(False)
        options_layout.addWidget(self.include_images)
        options_layout.addWidget(self.include_tables)
        options_layout.addWidget(self.include_csv)
        options_layout.addWidget(self.include_dfm_highlights)
        root.addWidget(options)

        dfm_options = QtWidgets.QGroupBox("Conteúdo DFM (quando disponível)")
        dfm_layout = QtWidgets.QVBoxLayout(dfm_options)
        self.include_dfm_images = QtWidgets.QCheckBox("Incluir imagens DFM")
        self.include_dfm_images.setChecked(True)
        self.include_dfm_tables = QtWidgets.QCheckBox("Incluir tabelas DFM")
        self.include_dfm_tables.setChecked(True)
        dfm_layout.addWidget(self.include_dfm_images)
        dfm_layout.addWidget(self.include_dfm_tables)
        root.addWidget(dfm_options)
        self._dfm_options = dfm_options

        image_header = QtWidgets.QHBoxLayout()
        image_header.addWidget(QtWidgets.QLabel("Imagens FEM para o relatório"))
        image_header.addStretch(1)
        self.capture_button = QtWidgets.QPushButton("Adicionar captura FEM da vista atual")
        self.capture_button.setToolTip(
            "Salva a câmera e o mapa FEM atualmente visíveis. Faça uma captura por vista desejada.")
        self.capture_button.clicked.connect(self.capture_requested)
        image_header.addWidget(self.capture_button)
        root.addLayout(image_header)

        self.image_list = QtWidgets.QListWidget()
        self.image_list.setToolTip("Edite as legendas e marque as imagens que deseja colocar no PDF.")
        self.image_list.itemChanged.connect(self._image_item_changed)
        self.image_list.setMinimumHeight(130)
        root.addWidget(self.image_list, 1)

        image_actions = QtWidgets.QHBoxLayout()
        self.remove_button = QtWidgets.QPushButton("Remover captura selecionada")
        self.remove_button.clicked.connect(self.remove_selected_capture)
        image_actions.addWidget(self.remove_button)
        image_actions.addStretch(1)
        root.addLayout(image_actions)

        buttons = QtWidgets.QHBoxLayout()
        self.configure_button = QtWidgets.QPushButton("Configurar relatório…")
        self.configure_button.clicked.connect(self.configure_requested)
        self.export_button = QtWidgets.QPushButton("Revisar e exportar relatório…")
        self.export_button.setDefault(True)
        self.export_button.clicked.connect(self.export_requested)
        buttons.addWidget(self.configure_button)
        buttons.addStretch(1)
        buttons.addWidget(self.export_button)
        root.addLayout(buttons)

    def set_results(self, objects: list[Any], selected_name: str = "") -> None:
        self.result_combo.blockSignals(True)
        current = selected_name or self.result_name()
        self.result_combo.clear()
        for obj in objects:
            self.result_combo.addItem(str(obj.Label), str(obj.Name))
        index = self.result_combo.findData(current)
        if index >= 0:
            self.result_combo.setCurrentIndex(index)
        self.result_combo.blockSignals(False)
        self.result_combo.setEnabled(bool(objects))
        if not objects:
            self.summary_label.setText("Nenhum objeto FEM de resultados foi encontrado neste documento.")
            self.export_button.setEnabled(False)
            self.configure_button.setEnabled(False)
            self.capture_button.setEnabled(False)
        else:
            self.export_button.setEnabled(True)
            self.configure_button.setEnabled(True)
            self.capture_button.setEnabled(True)
        self.selection_changed.emit()

    def set_dfm_available(self, available: bool) -> None:
        self._dfm_options.setEnabled(bool(available))
        if not available:
            self.include_dfm_images.setChecked(False)
            self.include_dfm_tables.setChecked(False)

    def result_name(self) -> str:
        value = self.result_combo.currentData()
        return str(value) if value else ""

    def set_summary(self, summary: FEMResultSummary | None) -> None:
        if summary is None:
            self.summary_label.setText("Nenhum resultado FEM selecionado.")
            return
        parts = []
        for quantity in summary.quantities:
            parts.append(
                f"{quantity.label}: min {quantity.minimum:.6g} {quantity.unit} "
                f"(nó {quantity.node_at_minimum or '—'}), max {quantity.maximum:.6g} "
                f"{quantity.unit} (nó {quantity.node_at_maximum or '—'})"
            )
        self.summary_label.setText("\n".join(parts) or "Sem valores de deslocamento/von Mises.")

    def add_capture(self, image: QtGui.QImage, caption: str | None = None) -> None:
        if image is None or image.isNull():
            return
        key = f"fem:{len(self._images) + 1}"
        while key in self._images:
            key = f"fem:{len(self._images) + 1}-{len(self._images)}"
        caption = caption or f"Vista FEM {len(self._images) + 1}"
        entry = ReportImage(key=key, caption=caption, image=image, include=True)
        self._images[key] = entry
        item = QtWidgets.QListWidgetItem(caption)
        item.setFlags(item.flags() | QtCore.Qt.ItemFlag.ItemIsUserCheckable
                      | QtCore.Qt.ItemFlag.ItemIsEditable)
        item.setCheckState(QtCore.Qt.CheckState.Checked)
        item.setData(QtCore.Qt.ItemDataRole.UserRole, key)
        thumb = image.scaled(128, 72, QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                             QtCore.Qt.TransformationMode.SmoothTransformation)
        item.setIcon(QtGui.QIcon(QtGui.QPixmap.fromImage(thumb)))
        self.image_list.addItem(item)
        self.selection_changed.emit()

    def selected_images(self) -> list[ReportImage]:
        images = []
        for index in range(self.image_list.count()):
            item = self.image_list.item(index)
            key = item.data(QtCore.Qt.ItemDataRole.UserRole)
            image = self._images.get(key)
            if image is not None:
                image.caption = item.text().strip() or image.caption
                image.include = item.checkState() == QtCore.Qt.CheckState.Checked
                images.append(image)
        return images

    def remove_selected_capture(self) -> None:
        row = self.image_list.currentRow()
        if row < 0:
            return
        item = self.image_list.takeItem(row)
        self._images.pop(item.data(QtCore.Qt.ItemDataRole.UserRole), None)
        self.selection_changed.emit()

    def _image_item_changed(self, _item: QtWidgets.QListWidgetItem) -> None:
        self.selected_images()
        self.selection_changed.emit()
