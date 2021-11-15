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
from .. import WeightInstance as Instance
from .. import Ship_rc
from ..shipUtils import Locale, Selection
from ..shipUtils.Math import compute_inertia


class TaskPanel:
    def __init__(self):
        """Constructor"""
        self.name = "ship weight creation"
        self.ui = ":/ui/TaskPanel_shipCreateWeight.ui"
        self.form = Gui.PySideUic.loadUi(self.ui)

    def accept(self):
        """Create the ship instance"""
        ship = self.ships[self.form.ship.currentIndex()]
        density = None
        if self.elem_type == 1:
            density = Units.parseQuantity(Locale.fromString(
                self.form.weight.text()))
            I = Tools.matrix(3)
            I[0][0] = Units.parseQuantity(Locale.fromString(
                self.form.Ixx.text()))
            I[0][1] = Units.parseQuantity(Locale.fromString(
                self.form.Ixy.text()))
            I[0][2] = Units.parseQuantity(Locale.fromString(
                self.form.Ixz.text()))
            I[1][0] = Units.parseQuantity(Locale.fromString(
                self.form.Iyx.text()))
            I[1][1] = Units.parseQuantity(Locale.fromString(
                self.form.Iyy.text()))
            I[1][2] = Units.parseQuantity(Locale.fromString(
                self.form.Iyz.text()))
            I[2][0] = Units.parseQuantity(Locale.fromString(
                self.form.Izx.text()))
            I[2][1] = Units.parseQuantity(Locale.fromString(
                self.form.Izy.text()))
            I[2][2] = Units.parseQuantity(Locale.fromString(
                self.form.Izz.text()))
        elif self.elem_type == 2:
            density = Units.parseQuantity(Locale.fromString(
                self.form.dens_line.text()))
        elif self.elem_type == 3:
            density = Units.parseQuantity(Locale.fromString(
                self.form.dens_area.text()))
        elif self.elem_type == 4:
            density = Units.parseQuantity(Locale.fromString(
                self.form.dens_vol.text()))

        if self.elem_type != 1:
            I = compute_inertia(self.shapes, self.elem_type)
            for i,row in enumerate(I):
                for j,val in enumerate(row):
                    I[i][j] = val * density


        obj = Tools.createWeight(self.shapes, ship, density, I)
        guiobj = Gui.ActiveDocument.getObject(obj.Name)
        guiobj.PointSize = 10.00
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
        self.form.weight_label = self.widget(QtGui.QLabel, "weight_label")
        self.form.weight = self.widget(QtGui.QLineEdit, "weight")
        self.form.dens_line_label = self.widget(QtGui.QLabel, "dens_line_label")
        self.form.dens_line = self.widget(QtGui.QLineEdit, "dens_line")
        self.form.dens_area_label = self.widget(QtGui.QLabel, "dens_area_label")
        self.form.dens_area = self.widget(QtGui.QLineEdit, "dens_area")
        self.form.dens_vol_label = self.widget(QtGui.QLabel, "dens_vol_label")
        self.form.dens_vol = self.widget(QtGui.QLineEdit, "dens_vol")
        self.form.Ixx = self.widget(QtGui.QLineEdit, "Ixx")
        self.form.Ixy = self.widget(QtGui.QLineEdit, "Ixy")
        self.form.Ixz = self.widget(QtGui.QLineEdit, "Ixz")
        self.form.Iyx = self.widget(QtGui.QLineEdit, "Iyx")
        self.form.Iyy = self.widget(QtGui.QLineEdit, "Iyy")
        self.form.Iyz = self.widget(QtGui.QLineEdit, "Iyz")
        self.form.Izx = self.widget(QtGui.QLineEdit, "Izx")
        self.form.Izy = self.widget(QtGui.QLineEdit, "Izy")
        self.form.Izz = self.widget(QtGui.QLineEdit, "Izz")
        self.form.group_inertia = self.widget(QtGui.QGroupBox, "group_inertia")
        if self.initValues():
            return True

        # Show just the appropriate mass input
        self.form.weight_label.hide()
        self.form.weight.hide()
        self.form.dens_line_label.hide()
        self.form.dens_line.hide()
        self.form.dens_area_label.hide()
        self.form.dens_area.hide()
        self.form.dens_vol_label.hide()
        self.form.dens_vol.hide()
        self.form.group_inertia.hide()
        if self.elem_type == 1:
            self.form.weight_label.show()
            self.form.weight.show()
            self.form.group_inertia.show()
        elif self.elem_type == 2:
            self.form.dens_line_label.show()
            self.form.dens_line.show()
        elif self.elem_type == 3:
            self.form.dens_area_label.show()
            self.form.dens_area.show()
        elif self.elem_type == 4:
            self.form.dens_vol_label.show()
            self.form.dens_vol.show()

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
        form = mw.findChild(QtGui.QWidget, "CreateWeightTaskPanel")
        return form.findChild(class_id, name)

    def initValues(self):
        """Setup the initial values"""
        # Ensure that there are at least one valid object to generate the
        # weight
        backends = [Selection.get_solids, Selection.get_surfaces,
                    Selection.get_lines, Selection.get_points,]
        for i, backend in enumerate(backends):
            self.shapes = backend()
            self.elem_type = 4 - i
            if self.shapes:
                break
        if not self.shapes:
            msg = QtGui.QApplication.translate(
                "ship_weight",
                "No valid shapes selected",
                None)
            App.Console.PrintError(msg + '\n')
            return True

        # Ensure as well that exist at least one valid ship to create the
        # entity inside it
        self.ships = Selection.get_doc_ships()
        if not self.ships:
            msg = QtGui.QApplication.translate(
                "ship_weight",
                "There are not ship objects to create weights into them",
                None)
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
