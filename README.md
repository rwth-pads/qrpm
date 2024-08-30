## Readme Still in Progress

# QRPM
This interactive Quantitative Process Mining-Tool (QRPM) allows for the basic analysis of quantity event logs (QELs) which extend the OCEL 2.0 standard.
Its functionalities encompass:
- the determination of the quantity state prior to every event as described in [tbd], 
- the discovery and visualisation of the corresponding quantity net (q-net) [tbd],
- functionalities for filtering the QEL and rediscovering the q-net based on the filtered log,
- basic processing and visualisations of the quantity data based on the (filtered) QEL, and
- functionalities for exporting the quantity data (csv), charts (png), and q-net (svg).

The following screencast shows the basic functionalities of QRPM:
 ---- coming soon ----

QRPM © 2024 by Nina Graves is licensed under CC BY 4.0. To view a copy of this license, visit http://creativecommons.org/licenses/by/4.0/

## Installation
The repository uses poetry for dependency management. If you do not have poetry installed, you can install it by running:
```pip install poetry```
Installation of the full tool has to occur in four steps:
1. Manually install PyGraphviz (needed for the visualisation of the underlying Q-net): https://gitlab.com/graphviz/graphviz/-/package_files/6164164/download
2. To install PyGraphviz in the poetry environment, you must follow the instructions on https://pygraphviz.github.io/documentation/stable/install.html
For Windows this means you must run:
```poetry run pip install --config-settings="--global-option=build_ext" `
              --config-settings="--global-option=-IC:\Program Files\Graphviz\include" `
              --config-settings="--global-option=-LC:\Program Files\Graphviz\lib" `
              pygraphviz```
3. Run ```poetry install``` again to synchronise the dependencies

## Functionality
QRPM is a tool for the analysis of quantity event logs (QELs) which extend the OCEL 2.0 standard. 
All quantity-related functionalities only show if the uploaded event log also contains quantity-related information; 
log filtering and (re-)discovery also work with normal OCEL 2.0s. 
Immediately after uploading a valid event log, QRPM 1) determines the quantity state prior to every event, 2) shows some basic statistics about the log, and 3) discovers and visualises the quantity 
net (q-net) as described in the paper.
You can zoom into the q-net, click on nodes to get information on the process elements (activities, object types, 
collection points), and export the displayed q-net as svg.
Beneath the q-net, there is a section for QEL filtering -- the user can expand the "Event & Object Selection"-Section.
Beneath the sublog creation, you find two tabs for processing and exporting data on the quantity state (Tab 1) and the quantity operations (Tab 2).
Each of these tabs includes various visualisations and tables that can be used for an interactive analysis of the QEL.
All Figures can be downloaded as PNGs by clicking on the camera icon in the top right corner of the figure.

[//]: # (### Sublog Creation)





