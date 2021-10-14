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

import PySide
from PySide import QtCore, QtGui
import FreeCAD
import FreeCADGui
import os

from . import Ship_rc
from .shipUtils import Selection


FreeCADGui.addLanguagePath(":/Ship/translations")
FreeCADGui.addIconPath(":/Ship/icons")


class LoadExample:
    def Activated(self):
        from . import shipLoadExample
        shipLoadExample.load()

    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            'Ship_LoadExample',
            'Load an example ship geometry')
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
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
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            'Ship_CreateShip',
            'Create a new ship')
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            'Ship_CreateShip',
            'Create a new ship instance on top of the hull geometry')
        return {'Pixmap': 'Ship_Module',
                'MenuText': MenuText,
                'ToolTip': ToolTip}


class OutlineDraw:
    def IsActive(self):
        return bool(Selection.get_ships())

    def Activated(self):
        from . import shipOutlineDraw
        shipOutlineDraw.load()

    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            'Ship_OutlineDraw',
            'Outline draw')
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            'Ship_OutlineDraw',
            'Plots the ship hull outline draw')
        return {'Pixmap': 'Ship_OutlineDraw',
                'MenuText': MenuText,
                'ToolTip': ToolTip}


class AreasCurve:
    def IsActive(self):
        return bool(Selection.get_ships())

    def Activated(self):
        from . import shipAreasCurve
        shipAreasCurve.load()

    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            'Ship_AreasCurve',
            'Areas curve')
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
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
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            'Ship_Hydrostatics',
            'Hydrostatics')
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
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
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            'ship_weight',
            'Create a new ship weight')
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            'ship_weight',
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
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            'ship_tank',
            'Create a new tank')
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            'ship_tank',
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
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            'ship_capacity',
            'Tank capacity curve')
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            'ship_capacity',
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
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            'ship_loadcondition',
            'Create a new loading condition')
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            'ship_loadcondition',
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
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            'ship_sinkandtrim',
            'Equilibrium draft and angle')
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            'ship_sinkandtrim',
            'Create a eschematic view of the ship equilibrium state')
        return {'Pixmap': 'Ship_SinkAndTrim',
                'MenuText': MenuText,
                'ToolTip': ToolTip}


class GZ:
    def Activated(self):
        from . import shipGZ
        shipGZ.load()

    def GetResources(self):
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            'ship_gz',
            'GZ curve computation')
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            'ship_gz',
            'Plot the GZ curve')
        return {'Pixmap': 'Ship_GZ',
                'MenuText': MenuText,
                'ToolTip': ToolTip}


FreeCADGui.addCommand('Ship_LoadExample', LoadExample())
FreeCADGui.addCommand('Ship_CreateShip', CreateShip())
FreeCADGui.addCommand('Ship_OutlineDraw', OutlineDraw())
FreeCADGui.addCommand('Ship_AreasCurve', AreasCurve())
FreeCADGui.addCommand('Ship_Hydrostatics', Hydrostatics())
FreeCADGui.addCommand('Ship_Weight', CreateWeight())
FreeCADGui.addCommand('Ship_Tank', CreateTank())
FreeCADGui.addCommand('Ship_Capacity', TankCapacity())
FreeCADGui.addCommand('Ship_LoadCondition', LoadCondition())
FreeCADGui.addCommand('Ship_SinkAndTrim', SinkAndTrim())
FreeCADGui.addCommand('Ship_GZ', GZ())
