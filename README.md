# LSST_GUI
Code for controlling the f/1.2 LSST Optical Simulator at UC Davis.

This Python-based code is used to control the f/1.2 LSST Optical Simulator at UC Davis.  The Optical Simulator is described in the paper J.A. Tyson et al., LSST optical beam simulator, Proc. SPIE 9154 (2014) 915415, of which a copy is in the docs directory.

The code controls the mechanical and electronic operation of the system, allowing automated taking of images while controlling the light intensity, X,Y,Z positioning of the stage which carries the CCD.  It also monitors the CCD temperature.

Since the code is controlling a physical system, there are many aspects of the code which are specific to the syatem at UC Davis, and it is not anticipated that it could be run elsewhere without significant modification.  It is uploaded here to github for the purposes of archiving the code and providing it as a starting point for similar projects.

Since the code is Python based, installation should be straightforward.  The code is launched with the command:

python LSST_GUI.py

Instructions for operating the simulator are in docs/instructions/GUI_Instructions.pdf

A screenshot of the code in operation is shown at LSST_GUI_Screenshot_16Nov16.png.

For questions contact Craig Lage at cslage@ucdavis.edu

Acknowledgements:
This research was supported by DOE grant DE-SC0009999 and NSF/AURA grant N56981C.