Release Notes
=============

Version 4.8.0
-------------
**2026-02-14**

New features:
 - New movie generation workflow with graphical dialog, toolbar integration, and asynchronous execution
 - Added support for optional display of physical units in 2D and 3D visualizations
 - Added option to open the folder containing generated movies directly from the Player
 - Added improved error handling framework with safe callback mechanism and enhanced error reporting

Improvements:
 - Improved stability and responsiveness of movie generation and file handling
 - Refactored movie generation code into reusable shared modules
 - Improved status reporting for long-running operations such as movie generation
 - Improved handling of Player settings, including movie, logging, and display configuration
 - Improved replay and simulation launch behavior, including CLI and relaunch options
 - Improved internal code structure, maintainability, and cross-platform compatibility

Bug fixes:
 - Fixed issues with movie generation folder handling and access
 - Fixed platform-specific issues, including Windows-only code fragments
 - Fixed visualization issues related to logarithmic plot scaling
 - Fixed configuration handling and settings persistence issues
 - Multiple minor bug fixes and stability improvements


Version 4.7.0
-------------
**2022-06-21**

New features:
 - Added support for shared numpy field visualization

Bug fixes:

Version 4.6.0
-------------
**2024-06-08**

New features:

 - Improved handling of screenshots
 - New Demos Browser
 - Added explicit setting to turn on/off cell-shell rendering optimization in 3D.
 - Implemented direct way to restore default settings directly from the Player

Changes:

Bug fixes:
    - Fixing screenshots settings handling
    - Fixed restoration of graphics windows on Windows OS
    - Multiple minor bug fixes




Version 4.5.0
-------------
**2024-01-06**

New features:
 - Added support for generation of simulation movies
 - Made Qscintilla Optional - it is not longer required to run Player.
 - Change license to MIT

Bug fixes:
 - Minor bug fixes



Version 4.4.1
-------------
**2023-07-01**

New features:
 - Changed the way updates are handled: we are now redirecting users to sourceforge to download new package
 - Added better conda builders that can utilize boa (mamba-based) builder
 - Added support for all Python versions >= 3.7

Bug fixes:
 - Fixed integration between Twedit and Player
 - Removed unneeded libcpposxhelper.dylib


Version 4.4.0
-------------
**2023-03-26**

New features:
 - Restored better glyph visualization (including replay mode)
 - Improved 3D visualization of scalar fields
 - Switched to VTK 9.x to fix offscreen rendering
 - Added C++ logger configurator in the Config dialog

Bug fixes:


Version 4.3.1
-------------
**2022-07-17**

New features:
 - Added Message Window
 - Improve cell type color handling
 - Added ability to pause simulation at specified intervals

Bug fixes:
 - Fixed integration of Twedit and Player


Version 4.3.0
-------------
**2022-02-26**

New features:
 - Split code into 3 separate packages - cc3d-core, Player, Twedit


