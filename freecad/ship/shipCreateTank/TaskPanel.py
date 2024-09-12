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

import FreeCAD as App
import FreeCADGui as Gui
from FreeCAD import Units
from PySide import QtGui, QtCore
from . import Tools
from .. import TankInstance as Instance
from .. import Ship_rc
from ..shipUtils import Selection

class TaskPanel:
    def __init__(self):
        """Constructor"""
        self.name = "ship tank creation"
        self.ui = ":/ui/TaskPanel_shipCreateTank.ui"
        self.form = Gui.PySideUic.loadUi(self.ui)

    def accept(self):
        """Create the ship instance"""
        ship = self.ships[self.form.ship.currentIndex()]
        Tools.createTank(self.solids, ship)

        return True

    def reject(self):
        """Cancel the job"""
        return True

    def clicked(self, index):
        pass

    def open(self):
        pass

    def needsFullSpace(self):
        return True

    def isAllowedAlterSelection(self):
        return False

    def isAllowedAlterView(self):
        return True

    def isAllowedAlterDocument(self):
        return False

    def helpRequested(self):
        pass

    def setupUi(self):
        """Create and configurate the user interface"""
        self.form.ship = self.widget(QtGui.QComboBox, "Ship")
        if self.initValues():
            return True

    def getMainWindow(self):
        toplevel = QtGui.QApplication.topLevelWidgets()
        for i in toplevel:
            if i.metaObject().className() == "Gui::MainWindow":
                return i
        raise Exception("No main window found")

    def widget(self, class_id, name):
        """Return the selected widget.

        Keyword arguments:
        class_id -- Class identifier
        name -- Name of the widget
        """
        mw = self.getMainWindow()
        form = mw.findChild(QtGui.QWidget, "CreateTankTaskPanel")
        return form.findChild(class_id, name)

    def initValues(self):
        """Setup the initial values"""
        # Ensure that there are at least one valid object to generate the
        # tank
        self.solids = Selection.get_solids()
        if not self.solids:
            msg = App.Qt.translate(
                "ship_tank",
                "Tanks objects can only be created on top of solids geometry")
            App.Console.PrintError(msg + '\n')
            return True

        # Ensure as well that exist at least one valid ship to create the
        # entity inside it
        self.ships = Selection.get_doc_ships()
        if not self.ships:
            msg = App.Qt.translate(
                "ship_tank",
                "There are not ship objects to create tanks into them")
            App.Console.PrintError(msg + '\n')
            return True

        # Fill the ships combo box
        icon = QtGui.QIcon(QtGui.QPixmap(":/icons/Ship_Instance.svg"))
        self.form.ship.clear()
        for ship in self.ships:
            self.form.ship.addItem(icon, ship.Label)
        self.form.ship.setCurrentIndex(0)

        return False


def createTask():
    panel = TaskPanel()
    Gui.Control.showDialog(panel)
    if panel.setupUi():
        Gui.Control.closeDialog()
        return None
    return panel
