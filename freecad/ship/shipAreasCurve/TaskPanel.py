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
from . import Preview
from . import PlotAux
from .. import Ship_rc
from ..import Instance
from ..shipUtils import Locale
from ..shipUtils import Selection
from ..shipHydrostatics import Tools as Hydrostatics


class TaskPanel:
    def __init__(self):
        self.name = "ship areas plotter"
        self.ui = ":/ui/TaskPanel_shipAreasCurve.ui"
        self.form = Gui.PySideUic.loadUi(self.ui)
        self.preview = Preview.Preview()
        self.ship = None

    def accept(self):
        if not self.ship:
            return False
        self.save()
        # Plot data
        draft = Units.parseQuantity(Locale.fromString(self.form.draft.text()))
        trim = Units.parseQuantity(Locale.fromString(self.form.trim.text()))
        num = self.form.num.value()

        disp, B, _ = Hydrostatics.displacement(self.ship,
                                               draft,
                                               Units.parseQuantity("0 deg"),
                                               trim)
        xcb = Units.Quantity(B.x, Units.Length)
        data = Hydrostatics.areas(self.ship,
                                  num,
                                  draft=draft,
                                  trim=trim)
        x = []
        y = []
        for i in range(0, len(data)):
            x.append(data[i][0].getValueAs("m").Value)
            y.append(data[i][1].getValueAs("m^2").Value)
        PlotAux.Plot(x, y, disp, xcb, self.ship)
        self.preview.clean()
        return True

    def reject(self):
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
        self.form.draft = self.widget(QtGui.QLineEdit, "draft")
        self.form.trim = self.widget(QtGui.QLineEdit, "trim")
        self.form.num = self.widget(QtGui.QSpinBox, "num")
        self.form.output_data = self.widget(QtGui.QTextEdit, "output_data")
        self.form.doc = QtGui.QTextDocument(self.form.output_data)
        if self.initValues():
            return True
        QtCore.QObject.connect(self.form.draft,
                               QtCore.SIGNAL("valueChanged(const Base::Quantity&)"),
                               self.onData)
        QtCore.QObject.connect(self.form.trim,
                               QtCore.SIGNAL("valueChanged(const Base::Quantity&)"),
                               self.onData)

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
        form = mw.findChild(QtGui.QWidget, "AreasCurveTaskPanel")
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

        self.form.draft.setText(self.ship.Draft.UserString)

        # Try to use saved values
        props = self.ship.PropertiesList
        try:
            self.form.draft.setText(self.ship.AreaCurveDraft.UserString)
        except AttributeError:
            pass
        try:
            self.form.trim.setText(self.ship.AreaCurveTrim.UserString)
        except AttributeError:
            pass
        try:
            self.form.num.setValue(self.ship.AreaCurveNum)
        except AttributeError:
            pass

        # Update GUI
        draft = Units.Quantity(self.form.draft.text())
        trim = Units.Quantity(self.form.trim.text())
        self.preview.update(draft, trim, self.ship)
        self.onUpdate()
        return False

    def clampValue(self, widget, val_min, val_max, val):
        if val_min <= val <= val_max:
            return val
        val = min(val_max, max(val_min, val))
        widget.setText(val.UserString)
        return val

    def onData(self, value):
        """ Method called when the tool input data is touched.
        @param value Changed value.
        """
        draft = Units.parseQuantity(Locale.fromString(self.form.draft.text()))
        trim = Units.parseQuantity(Locale.fromString(self.form.trim.text()))
        if draft.Unit != Units.Length or trim.Unit != Units.Angle:
            return

        bbox = self.ship.Shape.BoundBox
        draft_min = Units.Quantity(bbox.ZMin, Units.Length)
        draft_max = Units.Quantity(bbox.ZMax, Units.Length)
        draft = self.clampValue(self.form.draft, draft_min, draft_max, draft)

        trim_min = Units.parseQuantity("-90 deg")
        trim_max = Units.parseQuantity("90 deg")
        trim = self.clampValue(self.form.trim, trim_min, trim_max, trim)

        self.onUpdate()
        self.preview.update(draft, trim, self.ship)

    def onUpdate(self):
        """ Method called when the data update is requested. """
        if not self.ship:
            return
        draft = Units.parseQuantity(Locale.fromString(self.form.draft.text()))
        trim = Units.parseQuantity(Locale.fromString(self.form.trim.text()))

        # Calculate the drafts at each perpendicular
        angle = trim.getValueAs("rad").Value
        draftAP = draft + 0.5 * self.ship.Length * math.tan(angle)
        if draftAP < 0.0:
            draftAP = 0.0
        draftFP = draft - 0.5 * self.ship.Length * math.tan(angle)
        if draftFP < 0.0:
            draftFP = 0.0
        # Calculate the involved hydrostatics
        disp, B, _ = Hydrostatics.displacement(self.ship,
                                               draft,
                                               Units.parseQuantity("0 deg"),
                                               trim)
        xcb = Units.Quantity(B.x, Units.Length)
        # Setup the html string
        string = u'L = {0}<BR>'.format(self.ship.Length.UserString)
        string += u'B = {0}<BR>'.format(self.ship.Breadth.UserString)
        string += u'T = {0}<HR>'.format(draft.UserString)
        string += u'Trim = {0}<BR>'.format(trim.UserString)
        string += u'T<sub>AP</sub> = {0}<BR>'.format(draftAP.UserString)
        string += u'T<sub>FP</sub> = {0}<HR>'.format(draftFP.UserString)
        string += u'&#916; = {0}<BR>'.format(disp.UserString)
        string += u'XCB = {0}'.format(xcb.UserString)
        self.form.output_data.setHtml(string)

    def save(self):
        """ Saves the data into ship instance. """
        draft = Units.parseQuantity(Locale.fromString(self.form.draft.text()))
        trim = Units.parseQuantity(Locale.fromString(self.form.trim.text()))
        num = self.form.num.value()

        props = self.ship.PropertiesList
        try:
            props.index("AreaCurveDraft")
        except ValueError:
            try:
                tooltip = QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Areas curve tool draft selected [m]")
            except:
                tooltip = "Areas curve tool draft selected [m]"
            self.ship.addProperty("App::PropertyLength",
                                  "AreaCurveDraft",
                                  "Ship",
                                  tooltip)
        self.ship.AreaCurveDraft = draft
        try:
            props.index("AreaCurveTrim")
        except ValueError:
            try:
                tooltip = QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Areas curve tool trim selected [deg]")
            except:
                tooltip = "Areas curve tool trim selected [deg]"
            self.ship.addProperty("App::PropertyAngle",
                                  "AreaCurveTrim",
                                  "Ship",
                                  tooltip)
        self.ship.AreaCurveTrim = trim
        try:
            props.index("AreaCurveNum")
        except ValueError:
            try:
                tooltip = QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Areas curve tool number of points")
            except:
                tooltip = "Areas curve tool number of points"
            self.ship.addProperty("App::PropertyInteger",
                                  "AreaCurveNum",
                                  "Ship",
                                  tooltip)
        self.ship.AreaCurveNum = num


def createTask():
    panel = TaskPanel()
    Gui.Control.showDialog(panel)
    if panel.setupUi():
        Gui.Control.closeDialog()
        return None
    return panel
