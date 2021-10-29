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

import numpy as np
import FreeCAD as App
import FreeCADGui as Gui
from FreeCAD import Units
from PySide import QtGui, QtCore
from .. import Ship_rc
from ..shipUtils import Selection
from ..shipGZ import Tools as GZ
from ..shipHydrostatics import Tools as Hydrostatics
from . import Tools, PlotAux


class TaskPanel:
    def __init__(self):
        """Constructor"""
        self.name = "seakeeping RAOs computation"
        self.ui = ":/ui/TaskPanel_seakeepingRAOs.ui"
        self.form = Gui.PySideUic.loadUi(self.ui)
        self.running = False

    def accept(self):
        """Compute the RAOs and plot them"""
        if not self.lc:
            return False
        if self.running:
            return
        self.form.group_pbar.show()

        min_period = Units.parseQuantity(self.form.min_period.text())
        max_period = Units.parseQuantity(self.form.max_period.text())
        n_period = self.form.n_period.value()
        periods = [min_period + (max_period - min_period) * i / (n_period - 1) \
            for i in range(n_period)]
        omegas = [2.0 * np.pi / T.getValueAs('s').Value for T in periods]

        # Generate the simulations
        sims = Tools.simulation(
            self.lc, self.ship, self.weights, self.tanks, self.mesh, omegas)

        # Start solving the problems
        self.loop = QtCore.QEventLoop()
        self.timer = QtCore.QTimer()
        self.timer.setSingleShot(True)
        QtCore.QObject.connect(self.timer,
                               QtCore.SIGNAL("timeout()"),
                               self.loop,
                               QtCore.SLOT("quit()"))
        self.running = True
        n = len(periods) * len(Tools.DIRS)
        self.form.pbar.setMinimum(0)
        self.form.pbar.setMaximum(n)
        self.form.pbar.setValue(0)
        msg = QtGui.QApplication.translate(
            "ship_console",
            "Computing RAOs",
            None)
        App.Console.PrintMessage(msg + '...\n')
        points = []
        plts = {}
        for dof in Tools.DOFS:
            plts[dof] = PlotAux.Plot(dof, periods)
        for i, data in enumerate(Tools.solve_sim(sims, omegas)):
            App.Console.PrintMessage("\t{} / {}\n".format(i + 1, n))
            self.form.pbar.setValue(i + 1)
            ii, jj, dataset = data
            for dof in Tools.DOFS:
                plts[dof].rao[ii, jj + 1] = abs(
                    dataset.sel(radiating_dof=dof).data[0])
                plts[dof].update()
            self.timer.start(0.0)
            self.loop.exec_()
            if(not self.running):
                break
        return True

    def reject(self):
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
        """Create and configurate the user interface"""
        self.form.min_period = self.widget(QtGui.QLineEdit, "min_period")
        self.form.max_period = self.widget(QtGui.QLineEdit, "max_period")
        self.form.n_period = self.widget(QtGui.QSpinBox, "n_period")
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
        form = mw.findChild(QtGui.QWidget, "TaskPanel")
        return form.findChild(class_id, name)

    def initValues(self):
        """Setup the initial values"""
        # Ensure that there are at least one valid object to generate the
        # weight
        sel_lcs = Selection.get_lcs_with_mesh()
        if not sel_lcs:
            msg = QtGui.QApplication.translate(
                "ship_console",
                "A load condition instance must be selected before using this tool",
                None)
            App.Console.PrintError(msg + '\n')
            return True
        self.lc = sel_lcs[0]
        if len(sel_lcs) > 1:
            msg = QtGui.QApplication.translate(
                "ship_console",
                "More than one load condition have been selected (just the one"
                " labelled '{}' is considered)".format(self.lc.Label),
                None)
            App.Console.PrintWarning(msg + '\n')
        self.ship = Selection.get_lc_ship(self.lc)
        self.weights = Selection.get_lc_weights(self.lc)
        self.tanks = Selection.get_lc_tanks(self.lc)
        self.mesh = Selection.get_lc_mesh(self.lc)

        # Compute the minimum wavelength (i.e. period) that the mesh would
        # support
        radiuses = Tools.freecad_mesh_to_captain(self.mesh).faces_radiuses
        l_min = 8.0 * np.max(radiuses)
        g = GZ.G.getValueAs('m/s^2').Value
        t_min = np.sqrt(2.0 * np.pi / g * l_min) * Units.Second
        self.form.min_period.setText(t_min.UserString)
        
        # And the longest wave that make sense
        l_max = 10.0 * max(self.ship.Length.getValueAs('m').Value,
                           self.ship.Breadth.getValueAs('m').Value)
        t_max = np.sqrt(2.0 * np.pi / g * l_max) * Units.Second
        self.form.max_period.setText(t_max.UserString)

        return False


def createTask():
    panel = TaskPanel()
    Gui.Control.showDialog(panel)
    if panel.setupUi():
        Gui.Control.closeDialog()
        return None
    return panel
