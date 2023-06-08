#***************************************************************************
#*                                                                         *
#*   Copyright (c) 2011, 2016 Jose Luis Cercos Pita <jlcercos@gmail.com>   *
#*                                                                         *
#*   This program is free software; you can redistribute it and/or modify  *
#*   it under the terms of the GNU Lesser General Public License (LGPL)    *
#*   as published by the Free Software Foundation; either version 2 of     *
#*   the License, or (at your option) any later version.                   *
#*   for detail see the LICENCE text file.                                 *
#*                                                                         *
#*   This program is distributed in the hope that it will be useful,       *
#*   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
#*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
#*   GNU Library General Public License for more details.                  *
#*                                                                         *
#*   You should have received a copy of the GNU Library General Public     *
#*   License along with this program; if not, write to the Free Software   *
#*   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
#*   USA                                                                   *
#*                                                                         *
#***************************************************************************

import FreeCAD
import FreeCADGui
import os

from . import Ship_rc
from .shipUtils import Selection


FreeCADGui.addLanguagePath(":/Ship/translations")
FreeCADGui.addIconPath(":/Ship/icons")


def QT_TRANSLATE_NOOP(context, text):
    return text


class LoadExample:
    def Activated(self):
        from . import shipLoadExample
        shipLoadExample.load()

    def GetResources(self):
        MenuText = QT_TRANSLATE_NOOP(
            'Ship_LoadExample',
            'Load an example ship geometry')
        ToolTip = QT_TRANSLATE_NOOP(
            'Ship_LoadExample',
            'Load an example ship hull geometry.')
        return {'Pixmap': 'Ship_Load',
                'MenuText': MenuText,
                'ToolTip': ToolTip}


class CreateShip:
    def IsActive(self):
        return bool(Selection.get_solids())

    def Activated(self):
        from . import shipCreateShip
        shipCreateShip.load()

    def GetResources(self):
        MenuText = QT_TRANSLATE_NOOP(
            'Ship_CreateShip',
            'Create a new ship')
        ToolTip = QT_TRANSLATE_NOOP(
            'Ship_CreateShip',
            'Create a new ship instance on top of the hull geometry')
        return {'Pixmap': 'Ship_Module',
                'MenuText': MenuText,
                'ToolTip': ToolTip}


class AreasCurve:
    def IsActive(self):
        return bool(Selection.get_ships())

    def Activated(self):
        from . import shipAreasCurve
        shipAreasCurve.load()

    def GetResources(self):
        MenuText = QT_TRANSLATE_NOOP(
            'Ship_AreasCurve',
            'Areas curve')
        ToolTip = QT_TRANSLATE_NOOP(
            'Ship_AreasCurve',
            'Plot the transversal areas curve')
        return {'Pixmap': 'Ship_AreaCurve',
                'MenuText': MenuText,
                'ToolTip': ToolTip}


class Hydrostatics:
    def IsActive(self):
        return bool(Selection.get_ships())

    def Activated(self):
        from . import shipHydrostatics
        shipHydrostatics.load()

    def GetResources(self):
        MenuText = QT_TRANSLATE_NOOP(
            'Ship_Hydrostatics',
            'Hydrostatics')
        ToolTip = QT_TRANSLATE_NOOP(
            'Ship_Hydrostatics',
            'Plot the ship hydrostatics')
        return {'Pixmap': 'Ship_Hydrostatics',
                'MenuText': MenuText,
                'ToolTip': ToolTip}


class CreateWeight:
    def IsActive(self):
        return bool(Selection.get_shapes()) and bool(Selection.get_doc_ships())

    def Activated(self):
        from . import shipCreateWeight
        shipCreateWeight.load()

    def GetResources(self):
        MenuText = QT_TRANSLATE_NOOP(
            'Ship_Weight',
            'Create a new ship weight')
        ToolTip = QT_TRANSLATE_NOOP(
            'Ship_Weight',
            'Create a new ship weight')
        return {'Pixmap': 'Ship_Weight',
                'MenuText': MenuText,
                'ToolTip': ToolTip}


class CreateTank:
    def IsActive(self):
        return bool(Selection.get_solids()) and bool(Selection.get_doc_ships())

    def Activated(self):
        from . import shipCreateTank
        shipCreateTank.load()

    def GetResources(self):
        MenuText = QT_TRANSLATE_NOOP(
            'Ship_Tank',
            'Create a new tank')
        ToolTip = QT_TRANSLATE_NOOP(
            'Ship_Tank',
            'Create a new tank')
        return {'Pixmap': 'Ship_Tank',
                'MenuText': MenuText,
                'ToolTip': ToolTip}


class TankCapacity:
    def IsActive(self):
        return bool(Selection.get_tanks())

    def Activated(self):
        from . import shipCapacityCurve
        shipCapacityCurve.load()

    def GetResources(self):
        MenuText = QT_TRANSLATE_NOOP(
            'Ship_Capacity',
            'Tank capacity curve')
        ToolTip = QT_TRANSLATE_NOOP(
            'Ship_Capacity',
            'Plot the tank capacity curve (level-volume curve)')
        return {'Pixmap': 'Ship_CapacityCurve',
                'MenuText': MenuText,
                'ToolTip': ToolTip}


class LoadCondition:
    def IsActive(self):
        return bool(Selection.get_ships())

    def Activated(self):
        from . import shipCreateLoadCondition
        shipCreateLoadCondition.load()

    def GetResources(self):
        MenuText = QT_TRANSLATE_NOOP(
            'Ship_LoadCondition',
            'Create a new loading condition')
        ToolTip = QT_TRANSLATE_NOOP(
            'Ship_LoadCondition',
            'Create a new load condition spreadsheet')
        return {'Pixmap': 'Ship_LoadCondition',
                'MenuText': MenuText,
                'ToolTip': ToolTip}


class SinkAndTrim:
    def IsActive(self):
        return bool(Selection.get_lcs())

    def Activated(self):
        from . import shipSinkAndTrim
        shipSinkAndTrim.load()

    def GetResources(self):
        MenuText = QT_TRANSLATE_NOOP(
            'Ship_SinkAndTrim',
            'Equilibrium draft and angle')
        ToolTip = QT_TRANSLATE_NOOP(
            'Ship_SinkAndTrim',
            'Create a eschematic view of the ship equilibrium state')
        return {'Pixmap': 'Ship_SinkAndTrim',
                'MenuText': MenuText,
                'ToolTip': ToolTip}


class GZ:
    def IsActive(self):
        return bool(Selection.get_lcs())

    def Activated(self):
        from . import shipGZ
        shipGZ.load()

    def GetResources(self):
        MenuText = QT_TRANSLATE_NOOP(
            'Ship_GZ',
            'GZ curve computation')
        ToolTip = QT_TRANSLATE_NOOP(
            'Ship_GZ',
            'Plot the GZ curve')
        return {'Pixmap': 'Ship_GZ',
                'MenuText': MenuText,
                'ToolTip': ToolTip}

class Amadeo:
    def IsActive(self):
        return True
    
    def Activated(self):
        from . import resistanceAmadeo
        resistanceAmadeo.load()

    def GetResources(self):
        MenuText = QT_TRANSLATE_NOOP(
            'Resistance_Amadeo',
            'Resistance Amadeo prediction')
        ToolTip = QT_TRANSLATE_NOOP(
            'Resistance_Amadeo',
            'Compute the resistance by Amadeo method')
        return {'Pixmap': 'Resistance_Amadeo',
                'MenuText': MenuText,
                'ToolTip': ToolTip}
    
class Holtrop:
    def IsActive(self):
        return True

    def Activated(self):
        from . import resistanceHoltrop
        resistanceHoltrop.load()

    def GetResources(self):
        MenuText = QT_TRANSLATE_NOOP(
            'Resistance_Holtrop',
            'Resistance Holtrop prediction')
        ToolTip = QT_TRANSLATE_NOOP(
            'Resistance_Holtrop',
            'Compute the resistance by Holtrop method')
        return {'Pixmap': 'Resistance_Holtrop',
                'MenuText': MenuText,
                'ToolTip': ToolTip}

class SetMesh:
    def IsActive(self):
        return bool(Selection.get_meshes()) and bool(Selection.get_doc_ships())

    def Activated(self):
        from . import seakeepingSetMesh
        seakeepingSetMesh.load()

    def GetResources(self):
        MenuText = QT_TRANSLATE_NOOP(
            'Seakeeping_SetMesh',
            'Set ship surface mesh')
        ToolTip = QT_TRANSLATE_NOOP(
            'Seakeeping_SetMesh',
            'Associate the surface mesh to the ship')
        return {'Pixmap': 'Seakeeping_SetMesh',
                'MenuText': MenuText,
                'ToolTip': ToolTip}


class RAOs:
    def IsActive(self):
        return bool(Selection.get_lcs_with_mesh())

    def Activated(self):
        from . import seakeepingRAOs
        seakeepingRAOs.load()

    def GetResources(self):
        MenuText = QT_TRANSLATE_NOOP(
            'Seakeeping_RAOs',
            'Plot RAOs')
        ToolTip = QT_TRANSLATE_NOOP(
            'Seakeeping_RAOs',
            'Compute and plot the RAOs')
        return {'Pixmap': 'Seakeeping_RAOs',
                'MenuText': MenuText,
                'ToolTip': ToolTip}


FreeCADGui.addCommand('Ship_LoadExample', LoadExample())
FreeCADGui.addCommand('Ship_CreateShip', CreateShip())
FreeCADGui.addCommand('Ship_AreasCurve', AreasCurve())
FreeCADGui.addCommand('Ship_Hydrostatics', Hydrostatics())
FreeCADGui.addCommand('Ship_Weight', CreateWeight())
FreeCADGui.addCommand('Ship_Tank', CreateTank())
FreeCADGui.addCommand('Ship_Capacity', TankCapacity())
FreeCADGui.addCommand('Ship_LoadCondition', LoadCondition())
FreeCADGui.addCommand('Ship_SinkAndTrim', SinkAndTrim())
FreeCADGui.addCommand('Ship_GZ', GZ())
FreeCADGui.addCommand('Resistance_Amadeo', Amadeo())
FreeCADGui.addCommand('Resistance_Holtrop', Holtrop())
FreeCADGui.addCommand('Seakeeping_SetMesh', SetMesh())
FreeCADGui.addCommand('Seakeeping_RAOs', RAOs())
