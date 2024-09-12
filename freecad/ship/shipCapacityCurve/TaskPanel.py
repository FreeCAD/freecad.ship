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

import math
import FreeCAD as App
import FreeCADGui as Gui
from FreeCAD import Units
from PySide import QtGui, QtCore
from . import Tools
from . import PlotAux
from .. import Ship_rc
from ..shipUtils import Selection


class TaskPanel:
    def __init__(self):
        self.name = "ship tank loading capacity curve"
        self.ui = ":/ui/TaskPanel_shipCapacityCurve.ui"
        self.form = Gui.PySideUic.loadUi(self.ui)
        self.tank = None

    def accept(self):
        if not self.tank:
            return False
        self.form.group_pbar.show()

        n = self.form.points.value()
        self.form.pbar.setMinimum(0)
        self.form.pbar.setMaximum(n - 1)
        self.form.pbar.setValue(0)

        # Start iterating
        self.loop = QtCore.QEventLoop()
        self.timer = QtCore.QTimer()
        self.timer.setSingleShot(True)
        QtCore.QObject.connect(self.timer,
                               QtCore.SIGNAL("timeout()"),
                               self.loop,
                               QtCore.SLOT("quit()"))
        self.running = True
        # Get the hydrostatics
        msg = App.Qt.translate(
            "ship_console",
            "Computing capacity curve")
        App.Console.PrintMessage(msg + '...\n')
        l = [0.0]
        z = [Units.parseQuantity("0 m")]
        v = [Units.parseQuantity("0 m^3")]
        plt = None
        for i in range(1, n):
            App.Console.PrintMessage("\t{} / {}\n".format(i, n - 1))
            self.form.pbar.setValue(i)
            level = i / (n - 1)
            h, vol = Tools.compute_capacity(self.tank, level)
            l.append(100 * level)
            z.append(h)
            v.append(vol)
            if plt is None:
                plt = PlotAux.Plot(l, z, v)
            else:
                plt.update(l, z, v)
            self.timer.start(0.0)
            self.loop.exec_()
            if(not self.running):
                break
        return True

    def reject(self):
        if not self.tank:
            return False
        if self.running:
            self.running = False
            return
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
        self.form.points = self.widget(QtGui.QSpinBox, "points")
        self.form.pbar = self.widget(QtGui.QProgressBar, "pbar")
        self.form.group_pbar = self.widget(QtGui.QGroupBox, "group_pbar")
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
        form = mw.findChild(QtGui.QWidget, "CapacityCurveTaskPanel")
        return form.findChild(class_id, name)

    def initValues(self):
        """ Set initial values for fields
        """
        sel_tanks = Selection.get_tanks()
        if not sel_tanks:
            msg = App.Qt.translate(
                "ship_console",
                "A tank instance must be selected before using this tool")
            App.Console.PrintError(msg + '\n')
            return True
        self.tank = sel_tanks[0]
        if len(sel_tanks) > 1:
            msg = App.Qt.translate(
                "ship_console",
                "More than one tank have been selected (just the one labelled"
                " '{}' is considered)".format(self.tank.Label))
            App.Console.PrintWarning(msg + '\n')

        self.form.group_pbar.hide()
        return False


def createTask():
    panel = TaskPanel()
    Gui.Control.showDialog(panel)
    if panel.setupUi():
        Gui.Control.closeDialog()
        return None
    return panel
