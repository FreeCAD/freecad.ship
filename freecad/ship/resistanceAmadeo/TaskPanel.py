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
from . import Amadeo
from ..import Instance
from ..shipUtils import Locale
from ..shipUtils import Selection
from ..shipHydrostatics import Tools as Hydrostatics

QT_TRANSLATE_NOOP = FreeCAD.Qt.QT_TRANSLATE_NOOP


class TaskPanel:
    def __init__(self):
        self.name = "Compute resistance prediction Amadeo method"
        self.ui = os.path.join(os.path.dirname(__file__),
                               "../resources/ui/",
                               "TaskPanel_resistanceAmadeo.ui")
        self.form = Gui.PySideUic.loadUi(self.ui)
        self.ship = None

    def accept(self):
        has_rudder = self.form.rudder.isChecked()
        L = Units.parseQuantity(Locale.fromString(self.form.Lpp.text())).Value
        B = Units.parseQuantity(Locale.fromString(self.form.Beam.text())).Value
        T = Units.parseQuantity(Locale.fromString(self.form.Draft.text())).Value
        prot = Units.parseQuantity(Locale.fromString(self.form.protuberance.text())).Value
        Sw = Units.parseQuantity(Locale.fromString(self.form.Sw.text())).Value
        Lw = Units.parseQuantity(Locale.fromString(self.form.Lw.text())).Value
        V = Units.parseQuantity(Locale.fromString(self.form.volume.text())).Value
        Cb = Units.parseQuantity(Locale.fromString(self.form.Cb.text())).Value
        d = Units.parseQuantity(Locale.fromString(self.form.d_diameter.text())).Value
        l = Units.parseQuantity(Locale.fromString(self.form.d_length.text())).Value
        umax = Units.parseQuantity(Locale.fromString(self.form.max_speed.text())).Value
        umin = Units.parseQuantity(Locale.fromString(self.form.min_speed.text())).Value
        eta_p = Units.parseQuantity(Locale.fromString(self.form.etap.text())).Value
        seamargin = Units.parseQuantity(Locale.fromString(self.form.seamargin.text())).Value
        n = self.form.n_speeds.value()

        
        if  1 >= eta_p >= 0:
            
            etap = eta_p
        
        elif eta_p > 1:
            msg = App.Qt.translate(
                "ship_console", "The propulsive coefficient cannot be higher than 1"
            )
            App.Console.PrintError(msg + "\n")

        if Cb > 1:
            msg = App.Qt.translate("ship_console", "The block coefficient cannot be higher than 1")
            App.Console.PrintError(msg + "\n")

        if Lw == 0:
            Lw = ()
            L_w = 1
        else: L_w = 0
        if Sw == 0: 
            Sw = ()
            S_w = 1
        else: S_w = 0
        if d == 0: d = None
        if l == 0: l = None
        seamargin = seamargin / 100

        speeds = np.linspace(umin, umax, num = n)
        resis, speed, CF, CA, CR, CT, EKW, BKW, Lw, Sw = Amadeo.Amadeo(L, B,T, 
         Cb, V, speeds, etap, seamargin, prot, Sw, Lw, d, l, has_rudder = has_rudder)
        
        if L_w == 1: App.Console.PrintMessage("Lw = " + str("{:.3f}".format(Lw)) + " m^2" + '\n')
        if S_w == 1: App.Console.PrintMessage("Sw = " + str("{:.3f}".format(Sw)) + " m^2" + '\n')
        
        PlotAux.Plot(speed, resis, CF, CR, CA, CT, EKW, BKW)   

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
        self.form.Lpp = self.widget(QtGui.QLineEdit, "Lpp")
        self.form.Beam = self.widget(QtGui.QLineEdit, "Beam")
        self.form.Draft = self.widget(QtGui.QLineEdit, "Draft")
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
        self.form.etap = self.widget(QtGui.QLineEdit, "etap")
        self.form.seamargin = self.widget(QtGui.QLineEdit, "seamargin")
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
        try:
            self.ship = sel_ships[0]
        except:
            pass
        if len(sel_ships) > 1:
            msg = App.Qt.translate(
                "ship_console",
                "More than one ship have been selected (just the one labelled"
                "'{}' is considered)".format(self.ship.Label))
            App.Console.PrintWarning(msg + '\n')
         
        etap = 0.6
        seamargin = 15
        self.form.etap.setText(str(etap))
        self.form.seamargin.setText(str(seamargin))
        
        try:
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
            
            Prot = prot.getValueAs("m").Value
            Sw = sw.getValueAs("m^2").Value
            Lw = lw.getValueAs("m").Value
            V = vol.getValueAs("m^3").Value
    
        except:
            Prot = 0.0
            Sw = 0.0
            Lw = 0.0
            V = 0.0
            cb = 0.0
        
        
        try: 
            lpp = self.ship.Length.getValueAs("m").Value
            B = self.ship.Breadth.getValueAs("m").Value
            T = self.ship.Draft.getValueAs("m").Value
        except:
            lpp = 0.0
            B = 0.0
            T = 0.0
            
        self.form.Lpp.setText(str(lpp))
        self.form.Beam.setText(str(B))
        self.form.Draft.setText(str(T))
        self.form.protuberance.setText(str(Prot))
        self.form.Lw.setText(str(Lw))
        self.form.Sw.setText(str(Sw))
        self.form.volume.setText(str(V))
        self.form.Cb.setText(str(cb))
        
        return False
    
def createTask():
    panel = TaskPanel()
    Gui.Control.showDialog(panel)
    if panel.setupUi():
        Gui.Control.closeDialog()
        return None
    return panel
