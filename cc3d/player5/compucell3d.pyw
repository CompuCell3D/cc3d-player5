"""
CC3D main script that lunches CC#D in the GUI mode
When running automated testing f Demo suite use the following cml options:


 --exitWhenDone --testOutputDir=/Users/m/cc3d_tests --numSteps=100

 or for automatic starting of a particular simulation you use :
 --input=/home/m/376_dz/Demos/Models/cellsort/cellsort_2D/cellsort_2D.cc3d
"""

import sys
import vtk
from cc3d.player5.__main__ import main, except_hook


if __name__ == '__main__':
    # enable it during debugging in pycharm
    sys.excepthook = except_hook

    error_code = main(sys.argv[1:])

    # if error_code !=0 :
    #     print traceback.print_tb()

    # sys.excepthook = except_hook

    sys.exit(error_code)
