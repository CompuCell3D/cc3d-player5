Release Notes
=============


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


