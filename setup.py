import os, sys
from setuptools import setup, find_packages

rootdir = os.path.abspath(os.path.dirname(__file__))
version_path = os.path.join(rootdir, 'VERSION.txt')
player_version = open(version_path).readline().strip()

extra_library = ''
if sys.platform.startswith('darwin'):
      extra_library = 'Utilities/*.dylib'


setup(name='cc3d-player5',
      author='T.J. Sego, Maciek Swat',
      classifiers=[
            'Intended Audience :: Science/Research'
      ],
      description='CC3D Player: a real-time, interactive CompuCell3D simulation execution and visualization graphical user interface',
      url='https://compucell3d.org',
      version=player_version,
      packages=find_packages(
            include=['cc3d.player5', 'cc3d.player5.*']
      ),
      include_package_data=True,
      package_data={
            '': [
                  '*.information', '*.qrc', '*.sql', '*.xml'
            ],
            'cc3d.player5': [
                  'compucell3d.pyw',
                  'Configuration/*',
                  'Configuration_settings/*',
                  'Configuration_settings/osx/*',
                  'icons/*',
                  'Launchers/*',
                  'Plugins/ViewManagerPlugins/*',
                  extra_library

            ]
      },
      entry_points={
            'gui_scripts': ['cc3d-player5ParamScan = cc3d.player5.param_scan.parameter_scan_run:main',
                            'cc3d-player5 = cc3d.player5.__main__:main']
      }
      )
