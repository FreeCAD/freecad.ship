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
from . import Holtrop
from .. import Ship_rc
from ..import Instance
from ..shipUtils import Locale
from ..shipUtils import Selection
from ..shipHydrostatics import Tools as Hydrostatics
from ..init_gui import QT_TRANSLATE_NOOP


class TaskPanel:
    def __init__(self):
        self.name = "Compute resistance prediction Holtrop method"
        self.ui = ":/ui/TaskPanel_resistanceHoltrop.ui"
        self.form = Gui.PySideUic.loadUi(self.ui)
        self.preview = Preview.Preview()
        self.ship = None

    def accept(self):
        if not self.ship:
            return False
        
        test = self.form.form.currentIndex()
        
        App.Console.PrintMessage(test )

        Sw = Units.parseQuantity(Locale.fromString(self.form.Sw.text()))
        Lw = Units.parseQuantity(Locale.fromString(self.form.Lw.text()))
        V = Units.parseQuantity(Locale.fromString(self.form.volume.text()))

        Cb = Units.parseQuantity(Locale.fromString(self.form.Cb.text())).Value
        umax = Units.parseQuantity(Locale.fromString(self.form.max_speed.text()))
        umin = Units.parseQuantity(Locale.fromString(self.form.min_speed.text()))
        rbskeg = Units.parseQuantity(Locale.fromString(self.form.rbskeg.text()))
        rbstern = Units.parseQuantity(Locale.fromString(self.form.rbstern.text()))
        twsbr = Units.parseQuantity(Locale.fromString(self.form.twsbr.text()))
        sbr = Units.parseQuantity(Locale.fromString(self.form.sbr.text()))
        skeg = Units.parseQuantity(Locale.fromString(self.form.skeg.text()))
        strut_bossing = Units.parseQuantity(Locale.fromString(self.form.strut_bossing.text()))
        hull_bossings = Units.parseQuantity(Locale.fromString(self.form.hull_bossings.text()))
        shafts = Units.parseQuantity(Locale.fromString(self.form.shafts.text()))
        stab_fins = Units.parseQuantity(Locale.fromString(self.form.stab_fins.text()))
        dome = Units.parseQuantity(Locale.fromString(self.form.dome.text()))
        bkl = Units.parseQuantity(Locale.fromString(self.form.bkl.text()))
        
        #data preparation for Amadeo's method
        Sw = Sw.getValueAs("m^2").Value
        Lw = Lw.getValueAs("m").Value
        V = V.getValueAs("m^3").Value
        umax = umax.getValueAs("m/s").Value
        umin = umin.getValueAs("m/s").Value
        rbskeg = rbskeg.getValueAs("m^2").Value
        rbstern = rbstern.getValueAs("m^2").Value
        twsbr = twsbr.getValueAs("m^2").Value
        sbr = sbr.getValueAs("m^2").Value
        skeg = skeg.getValueAs("m^2").Value
        strut_bossing = strut_bossing.getValueAs("m^2").Value
        hull_bossings = hull_bossings.getValueAs("m^2").Value
        shafts = shafts.getValueAs("m^2").Value
        stab_fins = stab_fins.getValueAs("m^2").Value
        dome = dome.getValueAs("m^2").Value
        bkl = bkl.getValueAs("m^2").Value
        n = self.form.n_speeds.value()
        L = self.ship.Length.getValueAs("m").Value
        B = self.ship.Breadth.getValueAs("m").Value
        T = self.ship.Draft.getValueAs("m").Value

        if Lw == 0: Lw = ()
        if Sw == 0: Sw = ()

        Sapplist = [rbskeg, rbstern, twsbr, sbr, skeg, strut_bossing,
                    hull_bossings, shafts, stab_fins, dome, bkl]
        
        App.Console.PrintMessage(Sapplist)
        
        vel = np.linspace(umin, umax, num = n)
        resis, speed = Amadeo.Amadeo(L, B, T, Cb, V, vel, prot, Sw, Lw,
                                     l, has_rudder = has_rudder)
        
        
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
        
        self.form.Sw = self.widget(QtGui.QLineEdit, "Sw")
        self.form.Lw = self.widget(QtGui.QLineEdit, "Lw")
        self.form.volume = self.widget(QtGui.QLineEdit, "volume")
        self.form.Cb = self.widget(QtGui.QLineEdit, "Cb")
        self.form.Cm = self.widget(QtGui.QLineEdit, "Cm")
        self.form.Cf = self.widget(QtGui.QLineEdit, "Cf")
        self.form.form = self.widget(QtGui.QComboBox, "form")
        self.form.iE = self.widget(QtGui.QLineEdit, "iE")
        self.form.xcb = self.widget(QtGui.QLineEdit, "xcb")
        self.form.ABT = self.widget(QtGui.QLineEdit, "ABT")
        self.form.AT = self.widget(QtGui.QLineEdit, "AT")
        self.form.hb = self.widget(QtGui.QLineEdit, "hb")
        self.form.max_speed = self.widget(QtGui.QLineEdit, "max_speed")
        self.form.min_speed = self.widget(QtGui.QLineEdit, "min_speed")
        self.form.n_speeds = self.widget(QtGui.QSpinBox, "n_speeds")
        self.form.rbskeg = self.widget(QtGui.QLineEdit, "rbskeg")
        self.form.rbstern = self.widget(QtGui.QLineEdit, "rbstern")
        self.form.twsbr = self.widget(QtGui.QLineEdit, "twsbr")
        self.form.sbr = self.widget(QtGui.QLineEdit, "sbr")
        self.form.skeg = self.widget(QtGui.QLineEdit, "skeg")
        self.form.strut_bossing = self.widget(QtGui.QLineEdit, "strut_bossing")
        self.form.hull_bossings = self.widget(QtGui.QLineEdit, "hull_bossings")
        self.form.shafts = self.widget(QtGui.QLineEdit, "shafts")
        self.form.stab_fins = self.widget(QtGui.QLineEdit, "stab_fins")
        self.form.dome = self.widget(QtGui.QLineEdit, "dome")
        self.form.bkl = self.widget(QtGui.QLineEdit, "bkl")
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
        form = mw.findChild(QtGui.QWidget, "HoltropTaskPanel")
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
            
        
        disp,Vector,cb = Hydrostatics.displacement(self.ship,
                                               self.ship.Draft,
                                               Units.parseQuantity("0 deg"),
                                               Units.parseQuantity("0 deg"))
        vol = disp / Hydrostatics.DENS
        
        sw = Hydrostatics.wettedArea(self.ship.Shape.copy(), self.ship.Draft, 
                                     Units.parseQuantity("0 deg"),
                                     Units.parseQuantity("0 deg"))
        
        area, cf, f = Hydrostatics.floatingArea(self.ship, self.ship.Draft,
                                                Units.parseQuantity("0 deg"),
                                                Units.parseQuantity("0 deg"))
        bbox = f.BoundBox
        lw = Units.Quantity(bbox.XMax - bbox.XMin, Units.Length)
        
        cm = Hydrostatics.mainFrameCoeff(self.ship)
            
        xcb = Units.Quantity(Vector[0], Units.Length)
  
        cp = cb / cm
        Lw = lw.getValueAs("m").Value
        XCB = xcb.getValueAs("m").Value
        Bie = self.ship.Breadth.getValueAs("m").Value
        Vie = vol.getValueAs("m^3").Value
        
        Lr = Lw * (1 - cp + ( 0.06 * cp * XCB) / (4 * cp - 1))
        
        try: 
            iE = 1 + 89 * np.exp(- (Lw / Bie) ** 0.80856 * (1 - cf) ** 0.30484
                            * (1 - cp - 0.0225 * XCB) ** 0.6367 * (Lr / Bie) ** 
                             0.34574 * ((100 * Vie) / (Lw ** 3)) ** 0.16302)
            
        except ZeroDivisionError:
            msg = App.Qt.translate(
            "ship_console",
            "ZeroDivisionError: Null ship floating area found during the"
            " floating area computation!")
            App.Console.PrintError(msg + '\n')
        
            iE = 0.0
            
        iE = Units.Quantity(iE, Units.Angle)
        
        self.form.Lw.setText(lw.UserString)
        self.form.Sw.setText(sw.UserString)
        self.form.volume.setText(vol.UserString)
        self.form.Cb.setText(str(cb))
        self.form.Cm.setText(str(cm))
        self.form.Cf.setText(str(cf))
        self.form.iE.setText(iE.UserString)
        self.form.xcb.setText(xcb.UserString)
        return False
    
def createTask():
    panel = TaskPanel()
    Gui.Control.showDialog(panel)
    if panel.setupUi():
        Gui.Control.closeDialog()
        return None
    return panel
