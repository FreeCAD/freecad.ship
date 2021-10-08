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
from . import Preview
from . import Tools
from .. import Instance  # from .ship
from .. import Ship_rc
from ..shipUtils import Units as USys
from ..shipUtils import Locale
from ..shipUtils import Selection

class TaskPanel:
    def __init__(self):
        """Constructor"""
        self.name = "ship creation"
        self.ui = ":/ui/TaskPanel_shipCreateShip.ui"
        self.form = Gui.PySideUic.loadUi(self.ui)
        self.preview = Preview.Preview()

    def accept(self):
        """Create the ship instance"""
        self.preview.clean()
        Tools.createShip(self.solids,
                         Locale.fromString(self.form.length.text()),
                         Locale.fromString(self.form.breadth.text()),
                         Locale.fromString(self.form.draft.text()))
        return True

    def reject(self):
        """Cancel the job"""
        self.preview.clean()
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
        self.form.length = self.widget(QtGui.QLineEdit, "length")
        self.form.breadth = self.widget(QtGui.QLineEdit, "breadth")
        self.form.draft = self.widget(QtGui.QLineEdit, "draft")
        if self.initValues():
            return True
        self.preview.update(self.L, self.B, self.T)
        QtCore.QObject.connect(
            self.form.length,
            QtCore.SIGNAL("valueChanged(const Base::Quantity&)"),
            self.onLength)
        QtCore.QObject.connect(
            self.form.breadth,
            QtCore.SIGNAL("valueChanged(const Base::Quantity&)"),
            self.onBreadth)
        QtCore.QObject.connect(
            self.form.draft,
            QtCore.SIGNAL("valueChanged(const Base::Quantity&)"),
            self.onDraft)

    def getMainWindow(self):
        toplevel = QtGui.QApplication.topLevelWidgets()
        for i in toplevel:
            if i.metaObject().className() == "Gui::MainWindow":
                return i
        raise RuntimeError("No main window found")

    def widget(self, class_id, name):
        """Return the selected widget.

        Keyword arguments:
        class_id -- Class identifier
        name -- Name of the widget
        """
        mw = self.getMainWindow()
        form = mw.findChild(QtGui.QWidget, "CreateShipTaskPanel")
        return form.findChild(class_id, name)

    def initValues(self):
        """Setup the initial values"""
        self.solids = Selection.get_solids()
        if not self.solids:
            msg = QtGui.QApplication.translate(
                "ship_console",
                "Ship objects can only be created on top of hull geometry",
                None)
            App.Console.PrintError(msg + '\n')
            msg = QtGui.QApplication.translate(
                "ship_console",
                "Please create or load a ship hull geometry before using"
                " this tool",
                None)
            App.Console.PrintError(msg + '\n')
            return True
        # Get the ship bounds. The ship instance can not have dimensions
        # out of these values.
        self.bounds = [0.0, 0.0, 0.0]
        bbox = self.solids[0].BoundBox
        minX = bbox.XMin
        maxX = bbox.XMax
        minY = bbox.YMin
        maxY = bbox.YMax
        minZ = bbox.ZMin
        maxZ = bbox.ZMax
        for i in range(1, len(self.solids)):
            bbox = self.solids[i].BoundBox
            if minX > bbox.XMin:
                minX = bbox.XMin
            if maxX < bbox.XMax:
                maxX = bbox.XMax
            if minY > bbox.YMin:
                minY = bbox.YMin
            if maxY < bbox.YMax:
                maxY = bbox.YMax
            if minZ > bbox.ZMin:
                minZ = bbox.ZMin
            if maxZ < bbox.ZMax:
                maxZ = bbox.ZMax
        self.bounds[0] = maxX - minX
        self.bounds[1] = max(maxY - minY, abs(maxY), abs(minY))
        self.bounds[2] = maxZ - minZ

        input_format = USys.getLengthFormat()

        qty = Units.Quantity(self.bounds[0], Units.Length)
        self.form.length.setText(Locale.toString(input_format.format(
            qty.getValueAs(USys.getLengthUnits()).Value)))
        self.L = self.bounds[0] / Units.Metre.Value
        qty = Units.Quantity(self.bounds[1], Units.Length)
        self.form.breadth.setText(Locale.toString(input_format.format(
            qty.getValueAs(USys.getLengthUnits()).Value)))
        self.B = self.bounds[1] / Units.Metre.Value
        qty = Units.Quantity(self.bounds[2], Units.Length)
        self.form.draft.setText(Locale.toString(input_format.format(
            0.5 * qty.getValueAs(USys.getLengthUnits()).Value)))
        self.T = 0.5 * self.bounds[2] / Units.Metre.Value
        return False

    def clampVal(self, widget, val_min, val_max, val):
        if val >= val_min and val <= val_max:
            return val
        input_format = USys.getLengthFormat()
        val = min(val_max, max(val_min, val))
        qty = Units.Quantity('{} m'.format(val))
        widget.setText(Locale.toString(input_format.format(
            qty.getValueAs(USys.getLengthUnits()).Value)))
        return val

    def onData(self, widget, val_max):
        """Updates the 3D preview on data changes.

        Keyword arguments:
        value -- Edited value. This parameter is required in order to use this
        method as a callback function, but it is not useful.
        """
        val_min = 0.001
        qty = Units.Quantity(Locale.fromString(widget.text()))
        try:
            val = qty.getValueAs('m').Value
        except ValueError:
            return
        return self.clampVal(widget, val_min, val_max, val)

    def onLength(self, value):
        """Answer to length changes

        Keyword arguments:
        value -- Edited value. This parameter is required in order to use this
        method as a callback function, but it is not useful.
        """
        L = self.onData(self.form.length,
                        self.bounds[0] / Units.Metre.Value)
        if L is not None:
            self.L = L
            self.preview.update(self.L, self.B, self.T)

    def onBreadth(self, value):
        """Answer to breadth changes

        Keyword arguments:
        value -- Edited value. This parameter is required in order to use this
        method as a callback function, but it is not useful.
        """
        B = self.onData(self.form.breadth,
                        self.bounds[1] / Units.Metre.Value)
        if B is not None:
            self.B = B
            self.preview.update(self.L, self.B, self.T)

    def onDraft(self, value):
        """Answer to draft changes

        Keyword arguments:
        value -- Edited value. This parameter is required in order to use this
        method as a callback function, but it is not useful.
        """
        T = self.onData(self.form.draft,
                        self.bounds[2] / Units.Metre.Value)
        if T is not None:
            self.T = T
            self.preview.update(self.L, self.B, self.T)


def createTask():
    panel = TaskPanel()
    Gui.Control.showDialog(panel)
    if panel.setupUi():
        Gui.Control.closeDialog()
        return None
    return panel
