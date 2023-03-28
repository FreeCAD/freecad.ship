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

import numpy as np
import FreeCAD as App
import FreeCADGui as Gui
from FreeCAD import Units
from PySide import QtGui, QtCore
from . import Preview
from . import PlotAux
from . import Amadeo
from .. import Ship_rc
from ..import Instance
from ..shipUtils import Locale
from ..shipUtils import Selection
from ..shipHydrostatics import Tools as Hydrostatics
from ..init_gui import QT_TRANSLATE_NOOP


class TaskPanel:
    def __init__(self):
        self.name = "Compute resistance prediction Amadeo method"
        self.ui = ":/ui/TaskPanel_resistanceAmadeo.ui"
        self.form = Gui.PySideUic.loadUi(self.ui)
        self.preview = Preview.Preview()
        self.ship = None

    def accept(self):
        if not self.ship:
            return False
        
        has_rudder = self.form.rudder.isChecked()
        prot = Units.parseQuantity(Locale.fromString(self.form.protuberance.text()))
        Sw = Units.parseQuantity(Locale.fromString(self.form.Sw.text()))
        Lw = Units.parseQuantity(Locale.fromString(self.form.Lw.text()))
        V = Units.parseQuantity(Locale.fromString(self.form.volume.text()))

        Cb = Units.parseQuantity(Locale.fromString(self.form.Cb.text())).Value
        d = Units.parseQuantity(Locale.fromString(self.form.d_diameter.text()))
        l = Units.parseQuantity(Locale.fromString(self.form.d_length.text()))
        umax = Units.parseQuantity(Locale.fromString(self.form.max_speed.text()))
        umin = Units.parseQuantity(Locale.fromString(self.form.min_speed.text()))

        #data preparation for Amadeo's method
        prot = prot.getValueAs("m").Value
        Sw = Sw.getValueAs("m^2").Value
        Lw = Lw.getValueAs("m").Value
        V = V.getValueAs("m^3").Value
        d = d.getValueAs("m").Value
        l = l.getValueAs("m").Value
        umax = umax.getValueAs("m/s").Value
        umin = umin.getValueAs("m/s").Value
        n = self.form.n_speeds.value()
        L = self.ship.Length.getValueAs("m").Value
        B = self.ship.Breadth.getValueAs("m").Value
        T = self.ship.Draft.getValueAs("m").Value

        if Lw == 0: Lw = ()
        if Sw == 0: Sw = ()
        if d == 0: d = None
        if l == 0: l = None

        vel = np.linspace(umin, umax, num = n)
        resis, speed = Amadeo.Amadeo(L, B, T, Cb, V, vel, prot, Sw, Lw, 
                                        d, l, has_rudder = has_rudder)
        
        
        PlotAux.Plot(speed, resis, self.ship)          
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
        self.form.protuberance = self.widget(QtGui.QLineEdit, "protuberance")
        self.form.Sw = self.widget(QtGui.QLineEdit, "Sw")
        self.form.Lw = self.widget(QtGui.QLineEdit, "Lw")
        self.form.volume = self.widget(QtGui.QLineEdit, "volume")
        self.form.Cb = self.widget(QtGui.QLineEdit, "Cb")
        self.form.d_length = self.widget(QtGui.QLineEdit, "d_length")
        self.form.d_diameter = self.widget(QtGui.QLineEdit, "d_diameter")
        self.form.max_speed = self.widget(QtGui.QLineEdit, "max_speed")
        self.form.min_speed = self.widget(QtGui.QLineEdit, "min_speed")
        self.form.n_speeds = self.widget(QtGui.QSpinBox, "n_speeds")
        self.form.rudder = self.widget(QtGui.QCheckBox, "rudder")
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
        form = mw.findChild(QtGui.QWidget, "AmadeoTaskPanel")
        return form.findChild(class_id, name)

    def initValues(self):
        """ Set initial values for fields
        """
        sel_ships = Selection.get_ships()
        if not sel_ships:
            msg = App.Qt.translate(
                "ship_console",
                "A ship instance must be selected before using this tool")
            App.Console.PrintError(msg + '\n')
            return True
        self.ship = sel_ships[0]
        if len(sel_ships) > 1:
            msg = App.Qt.translate(
                "ship_console",
                "More than one ship have been selected (just the one labelled"
                "'{}' is considered)".format(self.ship.Label))
            App.Console.PrintWarning(msg + '\n')
            
        
        disp,_,cb = Hydrostatics.displacement(self.ship,
                                               self.ship.Draft,
                                               Units.parseQuantity("0 deg"),
                                               Units.parseQuantity("0 deg"))
        vol = disp / Hydrostatics.DENS
        
        sw = Hydrostatics.wettedArea(self.ship.Shape.copy(), self.ship.Draft, 
                                     Units.parseQuantity("0 deg"),
                                     Units.parseQuantity("0 deg"))


        shape, _ = Hydrostatics.placeShipShape(self.ship.Shape.copy(),
                                               self.ship.Draft,
                                               Units.parseQuantity("0 deg"),
                                               Units.parseQuantity("0 deg"))
        shape = Hydrostatics.getUnderwaterSide(shape)
        bbox = shape.BoundBox
        
        prot = Units.Quantity(bbox.XMax - bbox.XMin, Units.Length) 
        prot = prot - self.ship.Length
        if prot < 0: prot = 0
        prot = Units.Quantity(prot, Units.Length)
        
        area, cf, f = Hydrostatics.floatingArea(self.ship, self.ship.Draft,
                                                Units.parseQuantity("0 deg"),
                                                Units.parseQuantity("0 deg"))
        bbox = f.BoundBox
        lw = Units.Quantity(bbox.XMax - bbox.XMin, Units.Length)
        
        self.form.protuberance.setText(prot.UserString)
        self.form.Lw.setText(lw.UserString)
        self.form.Sw.setText(sw.UserString)
        self.form.volume.setText(vol.UserString)
        self.form.Cb.setText(str(cb))
        return False
    
def createTask():
    panel = TaskPanel()
    Gui.Control.showDialog(panel)
    if panel.setupUi():
        Gui.Control.closeDialog()
        return None
    return panel
