from setuptools import setup
import os
from freecad.ship.compile_resources import compile_resources

version_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 
                            "freecad", "ship", "version.py")
with open(version_path) as fp:
    exec(fp.read())
    
compile_resources()

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
                'freecad.ship.shipSinkAndTrim',
                'freecad.ship.seakeepingSetMesh',
                'freecad.ship.shipUtils',
                ],
      maintainer="sanguinariojoe",
      maintainer_email="jlcercos@gmail.com",
      url="https://github.com/FreeCAD/ship",
      description="externalized ship workbench. Created by Jose Luis Cercos Pita",
      install_requires=['numpy', 'matplotlib'],
      include_package_data=True)
