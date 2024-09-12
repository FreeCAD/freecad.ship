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
from . import PlotAux
from . import Tools
from .. import Ship_rc
from ..shipUtils import Selection


class TaskPanel:
    def __init__(self):
        self.name = "ship GZ stability curve plotter"
        self.ui = ":/ui/TaskPanel_shipGZ.ui"
        self.form = Gui.PySideUic.loadUi(self.ui)

    def accept(self):
        if self.lc is None:
            return False
        self.form.group_pbar.show()
        self.save()

        roll = Units.parseQuantity(self.form.angle.text())
        n_points = self.form.n_points.value()
        var_trim = self.form.var_trim.isChecked()
        self.form.pbar.setMinimum(0)
        self.form.pbar.setMaximum(n_points)
        self.form.pbar.setValue(0)

        # Compute some constants
        COG, W = Tools.weights_cog(self.weights)
        TW = Units.parseQuantity("0 kg")
        VOLS = []
        for t in self.tanks:
            # t[0] = tank object
            # t[1] = load density
            # t[2] = filling level
            vol = t[0].Proxy.getVolume(t[0], t[2])
            VOLS.append(vol)
            TW += vol * t[1]
        TW = TW * Tools.G

        # Start traversing the queried angles
        self.loop = QtCore.QEventLoop()
        self.timer = QtCore.QTimer()
        self.timer.setSingleShot(True)
        QtCore.QObject.connect(self.timer,
                               QtCore.SIGNAL("timeout()"),
                               self.loop,
                               QtCore.SLOT("quit()"))
        self.running = True
        rolls = []
        gzs = []
        drafts = []
        trims = []
        plt = None
        for i in range(n_points):
            App.Console.PrintMessage("{0} / {1}\n".format(i + 1, n_points))
            self.form.pbar.setValue(i + 1)
            rolls.append(roll * i / float(n_points - 1))
            point = Tools.solve_point(W, COG, TW, VOLS, self.ship, self.tanks,
                                      rolls[-1], var_trim)
            if point is None:
                gzs.append(Units.Quantity(0, Units.Length))
                drafts.append(Units.Quantity(0, Units.Length))
                trims.append(Units.Quantity(0, Units.Angle))
            else:
                gzs.append(point[0])
                drafts.append(point[1])
                trims.append(point[2])
            if plt is None:
                plt = PlotAux.Plot(rolls, gzs, drafts, trims)
            else:
                plt.update(rolls, gzs, drafts, trims)
            self.timer.start(0.0)
            self.loop.exec_()
            if(not self.running):
                break
        return True

    def reject(self):
        if not self.ship:
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
        self.form.angle = self.widget(QtGui.QLineEdit, "angle")
        self.form.n_points = self.widget(QtGui.QSpinBox, "n_points")
        self.form.var_trim = self.widget(QtGui.QCheckBox, "var_trim")
        self.form.pbar = self.widget(QtGui.QProgressBar, "pbar")
        self.form.group_pbar = self.widget(QtGui.QGroupBox, "group_pbar")
        if self.initValues():
            return True

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
        form = mw.findChild(QtGui.QWidget, "GZTaskPanel")
        return form.findChild(class_id, name)

    def initValues(self):
        """ Set initial values for fields
        """
        sel_lcs = Selection.get_lcs()
        if not sel_lcs:
            msg = QtGui.QApplication.translate(
                "ship_console",
                "A load condition instance must be selected before using this tool")
            App.Console.PrintError(msg + '\n')
            return True
        self.lc = sel_lcs[0]
        if len(sel_lcs) > 1:
            msg = QtGui.QApplication.translate(
                "ship_console",
                "More than one load condition have been selected (just the one"
                " labelled '{}' is considered)".format(self.lc.Label))
            App.Console.PrintWarning(msg + '\n')
        self.ship = Selection.get_lc_ship(self.lc)
        self.weights = Selection.get_lc_weights(self.lc)
        self.tanks = Selection.get_lc_tanks(self.lc)

        self.form.angle.setText(Units.parseQuantity("90 deg").UserString)
        # Try to use saved values
        props = self.ship.PropertiesList
        try:
            props.index("GZAngle")
            self.form.angle.setText(self.ship.GZAngle.UserString)
        except:
            pass
        try:
            props.index("GZNumPoints")
            self.form.n_points.setValue(self.ship.GZNumPoints)
        except ValueError:
            pass
        try:
            props.index("GZVariableTrim")
            if self.ship.GZVariableTrim:
                self.form.var_trim.setCheckState(QtCore.Qt.Checked)
            else:
                self.form.var_trim.setCheckState(QtCore.Qt.Unchecked)
        except ValueError:
            pass

        self.form.group_pbar.hide()
        return False

    def save(self):
        """ Saves the data into ship instance. """
        angle = Units.parseQuantity(self.form.angle.text())
        n_points = self.form.n_points.value()
        var_trim = self.form.var_trim.isChecked()

        props = self.ship.PropertiesList
        try:
            props.index("GZAngle")
        except ValueError:
            try:
                tooltip = QtGui.QApplication.translate(
                    "ship_gz",
                    "GZ curve tool angle selected [deg]")
            except:
                tooltip = "GZ curve tool angle selected [deg]"
            self.ship.addProperty("App::PropertyAngle",
                                  "GZAngle",
                                  "Ship",
                                  tooltip)
        self.ship.GZAngle = angle
        try:
            props.index("GZNumPoints")
        except ValueError:
            try:
                tooltip = QtGui.QApplication.translate(
                    "ship_gz",
                    "GZ curve tool number of points selected")
            except:
                tooltip = "GZ curve tool number of points selected"
            self.ship.addProperty("App::PropertyInteger",
                                  "GZNumPoints",
                                  "Ship",
                                  tooltip)
        self.ship.GZNumPoints = n_points
        try:
            props.index("GZVariableTrim")
        except ValueError:
            try:
                tooltip = QtGui.QApplication.translate(
                    "ship_gz",
                    "GZ curve tool variable trim angle selection")
            except:
                tooltip = "GZ curve tool variable trim angle selection"
            self.ship.addProperty("App::PropertyBool",
                                  "GZVariableTrim",
                                  "Ship",
                                  tooltip)
        self.ship.GZVariableTrim = var_trim


def createTask():
    panel = TaskPanel()
    Gui.Control.showDialog(panel)
    if panel.setupUi():
        Gui.Control.closeDialog()
        return None
    return panel
