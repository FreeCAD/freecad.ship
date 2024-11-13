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
from . import Holtrop
from ..import Instance
from ..shipUtils import Locale
from ..shipUtils import Selection
from ..shipHydrostatics import Tools as Hydrostatics

QT_TRANSLATE_NOOP = App.Qt.QT_TRANSLATE_NOOP


class TaskPanel:
    def __init__(self):
        self.name = "Compute resistance prediction Holtrop method"
        self.ui = os.path.join(os.path.dirname(__file__),
                               "../resources/ui/",
                               "TaskPanel_resistanceHoltrop.ui")
        self.form = Gui.PySideUic.loadUi(self.ui)
        self.ship = None

    def accept(self):
        B = Units.parseQuantity(Locale.fromString(self.form.Beam.text())).Value
        T = Units.parseQuantity(Locale.fromString(self.form.Draft.text())).Value
        Sw = Units.parseQuantity(Locale.fromString(self.form.Sw.text())).Value
        Lw = Units.parseQuantity(Locale.fromString(self.form.Lw.text())).Value
        V = Units.parseQuantity(Locale.fromString(self.form.volume.text())).Value
        Cb = Units.parseQuantity(Locale.fromString(self.form.Cb.text())).Value
        Cm = Units.parseQuantity(Locale.fromString(self.form.Cm.text())).Value
        Cw = Units.parseQuantity(Locale.fromString(self.form.Cf.text())).Value
        cstern = self.form.form.currentIndex()
        iE = Units.parseQuantity(Locale.fromString(self.form.iE.text())).Value
        xcb = Units.parseQuantity(Locale.fromString(self.form.xcb.text())).Value
        ABT = Units.parseQuantity(Locale.fromString(self.form.ABT.text())).Value
        AT = Units.parseQuantity(Locale.fromString(self.form.AT.text())).Value
        hb = Units.parseQuantity(Locale.fromString(self.form.hb.text())).Value
        umax = Units.parseQuantity(Locale.fromString(self.form.max_speed.text())).Value
        umin = Units.parseQuantity(Locale.fromString(self.form.min_speed.text())).Value
        eta_p = Units.parseQuantity(Locale.fromString(self.form.etap.text())).Value
        seamargin = Units.parseQuantity(Locale.fromString(self.form.seamargin.text())).Value
        rbskeg = Units.parseQuantity(Locale.fromString(self.form.rbskeg.text())).Value
        rbstern = Units.parseQuantity(Locale.fromString(self.form.rbstern.text())).Value
        twsbr = Units.parseQuantity(Locale.fromString(self.form.twsbr.text())).Value
        sbr = Units.parseQuantity(Locale.fromString(self.form.sbr.text())).Value
        skeg = Units.parseQuantity(Locale.fromString(self.form.skeg.text())).Value
        strut_bossing = Units.parseQuantity(Locale.fromString(self.form.strut_bossing.text())).Value
        hull_bossings = Units.parseQuantity(Locale.fromString(self.form.hull_bossings.text())).Value
        shafts = Units.parseQuantity(Locale.fromString(self.form.shafts.text())).Value
        stab_fins = Units.parseQuantity(Locale.fromString(self.form.stab_fins.text())).Value
        dome = Units.parseQuantity(Locale.fromString(self.form.dome.text())).Value
        bkl = Units.parseQuantity(Locale.fromString(self.form.bkl.text())).Value
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

        if Cw > 1:
            msg = App.Qt.translate(
                "ship_console", "The waterplane coefficient cannot be higher than 1"
            )
            App.Console.PrintError(msg + "\n")

        if Sw == 0:
            Sw = ()
            S_w = 1
        else: S_w = 0
        seamargin = seamargin / 100

        Sapplist = [rbskeg, rbstern, twsbr, sbr, skeg, strut_bossing,
                    hull_bossings, shafts, stab_fins, dome, bkl]
        
        
        speeds = np.linspace(umin, umax, num = n)
        Rtotal, speed, CT, CF, CAPP, Cw, CB, CTR, CA, EKW, BKW, Sw = Holtrop.Holtrop( B, 
            T, Lw, V, Cb, Cm, Cw, cstern, iE, xcb, speeds, hb, etap, seamargin,
                                                        Sapplist, ABT, AT, Sw)
        
        if S_w == 1: App.Console.PrintMessage("Sw = " + str("{:.3f}".format(Sw)) + " m^2" + '\n')
        
        PlotAux.Plot(speed, Rtotal, CT, CF, CAPP, Cw, CB, CTR, CA, EKW, BKW)          
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
        self.form.Draft = self.widget(QtGui.QLineEdit, "Draft")
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
        self.form.etap = self.widget(QtGui.QLineEdit, "etap")
        self.form.seamargin = self.widget(QtGui.QLineEdit, "seamargin")
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
            Xcb = xcb.getValueAs("m").Value
            Bie = self.ship.Breadth.getValueAs("m").Value
            V = vol.getValueAs("m^3").Value
            Sw = sw.getValueAs("m^2").Value
            
            Lr = Lw * (1 - cp + ( 0.06 * cp * Xcb) / (4 * cp - 1))
            
            try: 
                iE = 1 + 89 * np.exp(- (Lw / Bie) ** 0.80856 * (1 - cf) ** 0.30484
                                * (1 - cp - 0.0225 * Xcb) ** 0.6367 * (Lr / Bie) ** 
                                 0.34574 * ((100 * V) / (Lw ** 3)) ** 0.16302)
                
            except ZeroDivisionError:
                msg = App.Qt.translate(
                "ship_console",
                "ZeroDivisionError: Null ship floating area found during the"
                " floating area computation!")
                App.Console.PrintError(msg + '\n')
            
                iE = 0.0
        except:
            Lw = 0.0
            Sw = 0.0
            V = 0.0
            Xcb = 0.0
            cb = 0.0
            cm = 0.0
            cf = 0.0
            iE = 0.0
        
        try: 
            B = self.ship.Breadth.getValueAs("m").Value
            T = self.ship.Draft.getValueAs("m").Value
        except:
            B = 0.0
            T = 0.0
        
        self.form.Beam.setText(str(B))
        self.form.Draft.setText(str(T))
        self.form.Lw.setText(str(Lw))
        self.form.Sw.setText(str(Sw))
        self.form.volume.setText(str(V))
        self.form.Cb.setText(str(cb))
        self.form.Cm.setText(str(cm))
        self.form.Cf.setText(str(cf))
        self.form.iE.setText(str(iE))
        self.form.xcb.setText(str(Xcb))
        return False
    
def createTask():
    panel = TaskPanel()
    Gui.Control.showDialog(panel)
    if panel.setupUi():
        Gui.Control.closeDialog()
        return None
    return panel
