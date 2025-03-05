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

import os
import numpy as np
import FreeCAD as App
import FreeCADGui as Gui
from FreeCAD import Units
from PySide import QtGui, QtCore
from . import PlotAux
from . import Savitsky
from ..import Instance
from ..shipUtils import Locale
from ..shipUtils import Selection
from ..shipHydrostatics import Tools as Hydrostatics

QT_TRANSLATE_NOOP = App.Qt.QT_TRANSLATE_NOOP


class TaskPanel:
    def __init__(self):
        self.name = "Compute resistance prediction Savitsky method"
        self.ui = os.path.join(os.path.dirname(__file__),
                               "../resources/ui/",
                               "TaskPanel_resistanceSavitsky.ui")
        self.form = Gui.PySideUic.loadUi(self.ui)
        self.ship = None

    def accept(self):
        Beam = Units.parseQuantity(Locale.fromString(self.form.Beam.text())).Value
        Displacement = Units.parseQuantity(Locale.fromString(self.form.Displacement.text())).Value
        LCG = Units.parseQuantity(Locale.fromString(self.form.LCG.text())).Value
        DeadriseAngle = Units.parseQuantity(Locale.fromString(self.form.DeadriseAngle.text())).Value
        Vmin = Units.parseQuantity(Locale.fromString(self.form.min_speed.text())).Value
        Vmax = Units.parseQuantity(Locale.fromString(self.form.max_speed.text())).Value
        Nspeeds = self.form.n_speeds.value()
        eta_p = Units.parseQuantity(Locale.fromString(self.form.etap.text())).Value
        seamargin = Units.parseQuantity(Locale.fromString(self.form.seamargin.text())).Value
        trim_step = Units.parseQuantity(Locale.fromString(self.form.trim_step.text())).Value

        if 1 >= eta_p > 0:
            
            etap = eta_p
        
        elif eta_p > 1:
            msg = App.Qt.translate(
                "ship_console", "The propulsive coefficient cannot be higher than 1"
            )
            App.Console.PrintError(msg + '\n')
            
        if Vmin <= 0:
            msg = App.Qt.translate(
                "ship_console", "The minium ship velocity cannot be lower than 0 m/s"
            )
            App.Console.PrintError(msg + '\n')

        seamargin = seamargin / 100

        drag, speeds, trims, lift, dfriction, dpressure, lam, rein, cfri, cpres, ctotal, EKW, BKW = (
            Savitsky.savitsky(Beam, Vmin, Vmax, Nspeeds, Displacement, DeadriseAngle, LCG, trim_step, seamargin, etap))

        PlotAux.Plot(speeds, trims, drag, dfriction, dpressure, cfri, cpres, ctotal, EKW, BKW)
        return True

    def reject(self):
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
        self.form.Beam = self.widget(QtGui.QLineEdit, "Beam")
        self.form.Displacement = self.widget(QtGui.QLineEdit, "Displacement")
        self.form.LCG = self.widget(QtGui.QLineEdit, "LCG")
        self.form.DeadriseAngle = self.widget(QtGui.QLineEdit, "DeadriseAngle")
        self.form.min_speed = self.widget(QtGui.QLineEdit, "min_speed")
        self.form.max_speed = self.widget(QtGui.QLineEdit, "max_speed")
        self.form.n_speeds = self.widget(QtGui.QSpinBox, "n_speeds")
        self.form.etap = self.widget(QtGui.QLineEdit, "etap")
        self.form.seamargin = self.widget(QtGui.QLineEdit, "seamargin")
        self.form.trim_step = self.widget(QtGui.QLineEdit, "trim_step")

        self.form.edit_advanced_settings = self.widget(QtGui.QCheckBox, "edit_advanced_settings")

        # Initially disable the advanced fields
        self.form.trim_step.setEnabled(False)

        # Toggle checkbox to enable/disable advanced fields
        self.form.edit_advanced_settings.stateChanged.connect(self.toggleAdvancedSettings)

        if self.initValues():
            return True

    def toggleAdvancedSettings(self, state):
        """
        Method to enable/disable advanced fields depending on the status of the checkbox.
        """
        enabled = state == QtCore.Qt.Checked
        self.form.trim_step.setEnabled(enabled)

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
        form = mw.findChild(QtGui.QWidget, "SavitskyTaskPanel")
        return form.findChild(class_id, name)

    def initValues(self):
        """ Set initial values for fields
        """
        sel_ships = Selection.get_ships()
        try: 
            self.ship = sel_ships[0]
        except:
            pass
        if len(sel_ships) > 1:
            msg = App.Qt.translate(
                "ship_console",
                "More than one ship have been selected (just the one labelled)"
                "'{}' is considered)".format(self.ship.Label))
            App.Console.PrintWarning(msg + '\n')
            
        etap = 0.6
        seamargin = 15
        trim_step = 0.01
        self.form.etap.setText(str(etap))
        self.form.seamargin.setText(str(seamargin))
        self.form.trim_step.setText(str(trim_step))

        try:
            Beam = self.ship.Breadth.getValueAs("m").Value
            T = self.ship.Draft.getValueAs("m").Value

            disp, Vector, cb = Hydrostatics.displacement(self.ship,
                                                   self.ship.Draft,
                                                   Units.parseQuantity("0 deg"),
                                                   Units.parseQuantity("0 deg"))

            lcg = Units.Quantity(Vector[0], Units.Length)

            LCG = lcg.getValueAs("m").Value
            Displacement = disp.getValueAs("kg").Value / 1000

            DeadriseAngle = 90 - np.rad2deg(np.arctan(Beam/(2*T)))

        except:
            Displacement = 0.0
            LCG = 0.0
            Beam = 0.0
            DeadriseAngle = 0.0

        self.form.Displacement.setText(str(Displacement))
        self.form.Beam.setText(str(Beam))
        self.form.LCG.setText(str(LCG))
        self.form.DeadriseAngle.setText(str(DeadriseAngle))

        return False


def createTask():
    panel = TaskPanel()
    Gui.Control.showDialog(panel)
    if panel.setupUi():
        Gui.Control.closeDialog()
        return None
    return panel
