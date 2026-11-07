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

Use **Análises** to run DFM or to open a FEM-only report from saved results. In
the DFM results panel, the **Análises** tab offers three report modes: DFM,
FEM, and DFM + FEM. A DFM-only report does not need FEM results in the file.
For FEM-only, use **Generate FEM-only report from saved results…** in the same
Análises task; it does not require a DFM run. The DFM + FEM mode uses DFM
findings to choose useful camera positions, then reports the two analyses in
separate sections.

FEM-only reads the currently open `.FCStd` file. It must contain a completed
native FEM result object, normally named `CCX_Results` with type
`Fem::FemResultObjectPython`, and the original CAD solid for camera framing.
Confirm the displayed document path before exporting; results are not loaded
from another file and no solver is run. In the DFM results panel, the FEM
visibility checkbox can show the selected result over the DFM model for visual
comparison. It restores the previous visibility and solid transparency when
turned off or when the task closes.

FEM report images hide the coincident solid, FEM pipeline, mesh and constraint
objects so the selected result map can be seen without those overlays. Combined
reports can reuse the selected automatic DFM camera positions; FEM-only reports
use the current camera direction. Additional FEM views can be captured
individually. The camera, object visibility and DFM highlights are restored
after report capture. Image and table inclusion are independently configurable.

Choose magnitude of displacement, von Mises stress, or both for the FEM
summary table and optional nodal CSV. The report uses the saved result values;
it does not run a solver or infer safety or failure without a material criterion.
PDF headings and supported DFM rule text are available in Brazilian Portuguese
and English. User-entered notes and company details keep their authored
language. The project logo remains configurable in the report layout.

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
