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

import FreeCADGui as Gui
import FreeCAD as App
import os


class ShipWorkbench(Gui.Workbench):
    """Ships design workbench."""

    def __init__(self):
        _dir = os.path.dirname(__file__)
        Gui.addLanguagePath(os.path.join(_dir, "resources", "translations"))
        Gui.updateLocale()
        self.__class__.Icon = os.path.join(
            _dir, "resources", "icons", "Ship_Workbench.svg"
        )
        self.__class__.MenuText = App.Qt.translate("Workbench", "Ship")
        self.__class__.ToolTip = App.Qt.translate(
            "Workbench",
            "Ship module provides some of the commonly used tools to design ship forms",
        )

    from . import ShipGui

    def Initialize(self):
        QT_TRANSLATE_NOOP = App.Qt.QT_TRANSLATE_NOOP

        try:
            import FreeCAD.Plot
        except ImportError:
            try:
                import freecad.plot
            except ImportError:
                App.Console.PrintWarning(
                    App.Qt.translate(
                        "ship_console",
                        "freecad.plot is disabled, tools cannot graph output curves, "
                        "install freecad.plot with addon-manager\n",
                    )
                )
        # ToolBar
        shiplist = ["Ship_LoadExample",
                    "Ship_CreateShip",
                    "Ship_AreasCurve",
                    "Ship_Hydrostatics"]
        weightslist = ["Ship_Weight",
                       "Ship_Tank",
                       "Ship_Capacity",
                       "Ship_LoadCondition",
                       "Ship_SinkAndTrim",
                       "Ship_GZ"]
        resistancelist = ["Ship_ResistanceAmadeo",
                          "Ship_ResistanceHoltrop"]
        seakeepinglist = ["Ship_SeakeepingSetMesh",
                         "Ship_SeakeepingRAOs"]

        self.appendToolbar(
            QT_TRANSLATE_NOOP("Workbench", "Ship design"), shiplist)
        self.appendToolbar(
            QT_TRANSLATE_NOOP("Workbench", "Weights"), weightslist)
        self.appendToolbar(
            QT_TRANSLATE_NOOP("Workbench", "Resistance"), resistancelist)
        self.appendToolbar(
            QT_TRANSLATE_NOOP("Workbench", "Seakeeping"), seakeepinglist)
        self.appendMenu(
            QT_TRANSLATE_NOOP("Workbench", "Ship design"), shiplist)
        self.appendMenu(
            QT_TRANSLATE_NOOP("Workbench", "Weights"), weightslist)
        self.appendMenu(
            QT_TRANSLATE_NOOP("Workbench", "Resistance"), resistancelist)
        self.appendMenu(
            QT_TRANSLATE_NOOP("Workbench", "Seakeeping"), seakeepinglist)

Gui.addWorkbench(ShipWorkbench())
