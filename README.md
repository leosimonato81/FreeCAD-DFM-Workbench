<div align="center">

# DFM + FEM Workbench

![License](https://img.shields.io/badge/license-LGPL--2.1-blue)

A standalone FreeCAD workbench that combines Design for Manufacturing (DFM)
analysis with reports from FEM results already saved in the document. It can be
installed alongside the original DFM workbench.

<img src=".github/images/overview.png" alt="DFM Workbench results panel with findings highlighted on a model" width="100%">

</div>

The philosophy of this project is to give more power to hobbyists and small businesses to have access to powerful DFM tools that not only critique, but teach as well.

Another key point is customisability. Every rule is 100% customisable. The Process Library is the main way you can do this, but for experts, you can tweak the parameters for the geometric analyzers in the DFM Preferences page.

<table>
<tr>
<th align="left">Currently supported rules</th>
<th align="left">Supported manufacturing processes (currently)</th>
<th align="left">Supported contours</th>
<th align="left">Other features</th>
</tr>
<tr valign="top">
<td>

- Maximum and minimum wall thickness
- Minimum draft angle
- Undercut detection
- Sharp internal and external corners
- Maximum support material
- Maximum bridge span
- Maximum bed contact area
- Maximum overhang angle
- Maximum cusp height

</td>
<td>

- FDM 3D printing
- Plastic injection molding

</td>
<td>

- Thickness
- Draft angle

</td>
<td>

- Generate professional PDF reports
- Export to CSV

</td>
</tr>
</table>

<p align="center">
  <img src=".github/images/report_title.png" alt="PDF report cover page" width="49%">
  <img src=".github/images/report_thickness.png" alt="PDF report page for a wall thickness rule" width="49%">
</p>

## Contours

Analyse wall thickness or draft angles of your parts, and create nice graphics.

<p align="center">
  <img src=".github/images/thickness_analysis.png" alt="Wall thickness contour on a part" width="100%">
</p>

## Process Library

<p align="center">
  <img src=".github/images/process_library1.png" alt="Process Library in list layout" width="49%">
  <img src=".github/images/process_library.png" alt="Process Library in grid layout with rule diagrams" width="49%">
</p>

<p align="center">
  <img src=".github/images/edit_feedback.png" alt="Editing a rule's values and feedback messages" width="70%">
</p>

## Installation

Install directly from the **FreeCAD Addon Manager**.

After installation, the selector shows **DFM + FEM**. The original **DFM**
workbench remains installed separately and keeps its existing name and tools.

## DFM + FEM report beta

Start with **Análises** and complete the DFM analysis. The results panel's
**Análises** tab contains the report presets, CSV export and the optional FEM
section; there is no separate FEM report command. The DFM result is the source
for the report's automatic camera positions.

When the FEM section is enabled, choose a saved FEM result object. The combined
PDF presents the DFM findings and FEM results on separate pages. FEM images can
reuse each selected automatic DFM camera position while hiding DFM overlays and
other FEM result objects; the selected FEM color map remains visible. Additional
FEM views can be captured manually from the current camera. The viewport and
object visibility are restored after report capture.

The report reads saved displacement magnitude and von Mises stress values; it
does not run a solver or interpret material failure or safety criteria. Summary
tables and nodal CSV export are optional. PDF headings, standard DFM rule names
and descriptions, and FEM fields are available in Brazilian Portuguese and
English. Free text from project notes, company details and process feedback
keeps its authored language. The project logo remains configurable in the
report layout.

This combined report workflow is in beta. It has not yet been validated end to
end in FreeCAD 1.1.4 with multiple FEM result views and final PDF printing.

<div align="center">

| Version | Support |
|---------|---------|
| FreeCAD 1.1+ | Officially supported |
| FreeCAD 1.0 | Should work, not tested |
| FreeCAD 0.x | Not supported (requires PySide6) |

</div>

## Contributing

If you'd like to help out, here are some ways you might consider contributing:

- Creating bug reports
- Suggesting new features
- Submitting code to fix bugs or add new features
- Creating user documentation on FreeCAD Wiki
- Sharing DFM knowledge for any manufacturing process (through submitting an issue would be great!)
- Creating example models for manufacturing processes that can be bundled with the workbench
- Creating tutorials either through a website or a video
