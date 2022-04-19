#***************************************************************************
#*                                                                         *
#*   Copyright (c) 2011, 2016                                              *
#*   Jose Luis Cercos Pita <jlcercos@gmail.com>                            *
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
from .. import Ship_rc
from ..shipUtils import Selection


class TaskPanel:
    def __init__(self):
        """Constructor"""
        self.name = "ship mesh association"
        self.ui = ":/ui/TaskPanel_seakeepingSetMesh.ui"
        self.form = Gui.PySideUic.loadUi(self.ui)

    def accept(self):
        """Create the ship instance"""
        ship = self.ships[self.form.ship.currentIndex()]
        ship.Mesh = [self.mesh.Name]
        self.mesh.Visibility = False
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
        self.form.ship = self.widget(QtGui.QComboBox, "ship")
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
        form = mw.findChild(QtGui.QWidget, "TaskPanel")
        return form.findChild(class_id, name)

    def initValues(self):
        """Setup the initial values"""
        # Ensure that there are at least one valid object to generate the
        # weight
        sel_meshes = Selection.get_meshes()
        if not sel_meshes:
            msg = App.Qt.translate(
                "ship_tank",
                "Please, select a mesh before executing this tool",
                None)
            App.Console.PrintError(msg + '\n')
            return True
        self.mesh = sel_meshes[0]
        if len(sel_meshes) > 1:
            msg = App.Qt.translate(
                "ship_console",
                "More than one mesh have been selected (just the one labelled"
                " '{}' is considered)".format(self.mesh.Label))
            App.Console.PrintWarning(msg + '\n')
        # Ensure as well that exist at least one valid ship to create the
        # entity inside it
        self.ships = Selection.get_doc_ships()
        if not self.ships:
            msg = App.Qt.translate(
                "seakeeping_setmesh",
                "There are not ship objects to attach meshes")
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
