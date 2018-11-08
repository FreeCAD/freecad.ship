from setuptools import setup
import os
import subprocess as sub

version_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 
                            "freecad", "ship", "version.py")
with open(version_path) as fp:
    exec(fp.read())
    
# try to create a resource file
# assume either pyside2-rcc or pyside-rcc are available.
# if both are available pyside2-rcc is used.
rc_input = os.path.abspath(os.path.join("freecad", "ship", "resources", "Ship.qrc"))
rc_output = os.path.join("freecad", "plot", "Ship_rc.py")
try:
    proc = sub.Popen(["pyside2-rcc", "-o", rc_output, rc_input], stdout=sub.PIPE, stderr=sub.PIPE)
    out, err = proc.communicate()
except FileNotFoundError:
    proc = sub.Popen(["pyside-rcc", "-o", rc_output, rc_input], stdout=sub.PIPE, stderr=sub.PIPE)
    out, err = proc.communicate()

print(out.decode("utf8"))
print(err.decode("utf8"))

setup(name='freecad.ship',
      version=str(__version__),
      packages=['freecad',
                'freecad.ship',
                'freecad.ship.shipAreasCurve',
                'freecad.ship.shipCapacityCurve',
                'freecad.ship.shipCreateLoadCondition',
                'freecad.ship.shipCreateShip',
                'freecad.ship.shipCreateTank',
                'freecad.ship.shipCreateWeight',
                'freecad.ship.shipGZ',
                'freecad.ship.shipHydrostatics',
                'freecad.ship.shipLoadExample',
                'freecad.ship.shipOutlineDraw',
                'freecad.ship.shipUtils',
                ],
      maintainer="looooo",
      maintainer_email="sppedflyer@gmail.com",
      url="https://github.com/FreeCAD/plot",
      description="externalized ship workbench. Created by Jose Luis Cercos Pita",
      install_requires=['numpy', 'matplotlib', 'freecad.plot'],
      include_package_data=True)
