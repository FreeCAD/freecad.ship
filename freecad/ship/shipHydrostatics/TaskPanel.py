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
from FreeCAD import Base, Vector
import Part
from FreeCAD import Units
from PySide import QtGui, QtCore
from . import PlotAux
from . import Tools
from .. import Instance
from .. import Ship_rc
from ..shipUtils import Locale
from ..shipUtils import Selection
from ..init_gui import QT_TRANSLATE_NOOP


class TaskPanel:
    def __init__(self):
        self.name = "ship hydrostatic curves plotter"
        self.ui = ":/ui/TaskPanel_shipHydrostatics.ui"
        self.form = Gui.PySideUic.loadUi(self.ui)
        self.ship = None
        self.running = False

    def accept(self):
        if not self.ship:
            return False
        if self.running:
            return
        self.form.group_pbar.show()
        self.save()

        trim = Units.parseQuantity(Locale.fromString(self.form.trim.text()))
        min_draft = Units.parseQuantity(Locale.fromString(self.form.min_draft.text()))
        max_draft = Units.parseQuantity(Locale.fromString(self.form.max_draft.text()))
        n_draft = self.form.n_draft.value()
        self.form.pbar.setMinimum(0)
        self.form.pbar.setMaximum(n_draft)
        self.form.pbar.setValue(0)

        draft = min_draft
        drafts = [draft]
        dDraft = (max_draft - min_draft) / (n_draft - 1)
        for i in range(1, n_draft):
            draft = draft + dDraft
            drafts.append(draft)

        # Get external faces
        self.loop = QtCore.QEventLoop()
        self.timer = QtCore.QTimer()
        self.timer.setSingleShot(True)
        QtCore.QObject.connect(self.timer,
                               QtCore.SIGNAL("timeout()"),
                               self.loop,
                               QtCore.SLOT("quit()"))
        self.running = True
        faces = self.externalFaces(self.ship.Shape)
        if not self.running:
            return False
        if len(faces) == 0:
            msg = App.Qt.translate(
                "ship_console",
                "Failure detecting external faces from the ship object")
            App.Console.PrintError(msg + '\n')
            return False
        faces = Part.makeShell(faces)

        # Get the hydrostatics
        msg = App.Qt.translate(
            "ship_console",
            "Computing hydrostatics",
            None)
        App.Console.PrintMessage(msg + '...\n')
        points = []
        plt = None
        for i in range(len(drafts)):
            App.Console.PrintMessage("\t{} / {}\n".format(i + 1, len(drafts)))
            self.form.pbar.setValue(i + 1)
            draft = drafts[i]
            point = Tools.Point(self.ship,
                                faces,
                                draft,
                                trim)
            points.append(point)
            if plt is None:
                plt = PlotAux.Plot(self.ship, points)
            else:
                plt.update(self.ship, points)
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
        self.form.trim = self.widget(QtGui.QLineEdit, "trim")
        self.form.min_draft = self.widget(QtGui.QLineEdit, "min_draft")
        self.form.max_draft = self.widget(QtGui.QLineEdit, "max_draft")
        self.form.n_draft = self.widget(QtGui.QSpinBox, "n_draft")
        self.form.pbar = self.widget(QtGui.QProgressBar, "pbar")
        self.form.group_pbar = self.widget(QtGui.QGroupBox, "group_pbar")
        # Initial values
        if self.initValues():
            return True
        # Connect Signals and Slots
        QtCore.QObject.connect(self.form.trim,
                               QtCore.SIGNAL("valueChanged(const Base::Quantity&)"),
                               self.onData)
        QtCore.QObject.connect(self.form.min_draft,
                               QtCore.SIGNAL("valueChanged(const Base::Quantity&)"),
                               self.onData)
        QtCore.QObject.connect(self.form.max_draft,
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
        form = mw.findChild(QtGui.QWidget, "HydrostaticsTaskPanel")
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
                " '{}' is considered)".format(self.ship.Label))
            App.Console.PrintWarning(msg + '\n')

        props = self.ship.PropertiesList

        try:
            props.index("HydrostaticsTrim")
            self.form.trim.setText(self.ship.HydrostaticsTrim.UserString)
        except ValueError:
            self.form.trim.setText("0 deg")

        try:
            props.index("HydrostaticsMinDraft")
            self.form.min_draft.setText(
                self.ship.HydrostaticsMinDraft.UserString)
        except ValueError:
            self.form.min_draft.setText(
                (0.9 * self.ship.Draft).UserString)
        try:
            props.index("HydrostaticsMaxDraft")
            self.form.max_draft.setText(
                self.ship.HydrostaticsMaxDraft.UserString)
        except ValueError:
            self.form.max_draft.setText(
                (1.1 * self.ship.Draft).UserString)

        try:
            props.index("HydrostaticsNDraft")
            self.form.n_draft.setValue(self.ship.HydrostaticsNDraft)
        except ValueError:
            pass

        self.form.group_pbar.hide()
        return False

    def clampValue(self, widget, val_min, val_max, val):
        if val_min <= val <= val_max:
            return val
        val = min(val_max, max(val_min, val))
        widget.setText(val.UserString)
        return val

    def onData(self, value):
        """ Method called when input data is changed.
         @param value Changed value.
        """
        min_draft = Units.parseQuantity(Locale.fromString(
            self.form.min_draft.text()))
        max_draft = Units.parseQuantity(Locale.fromString(
            self.form.max_draft.text()))
        trim = Units.parseQuantity(Locale.fromString(self.form.trim.text()))
        if min_draft.Unit != Units.Length or \
            max_draft.Unit != Units.Length or \
            trim.Unit != Units.Angle:
            return

        # Clamp the values to the bounds
        bbox = self.ship.Shape.BoundBox
        draft_min = Units.Quantity(bbox.ZMin, Units.Length)
        draft_max = Units.Quantity(bbox.ZMax, Units.Length)
        min_draft = self.clampValue(
            self.form.min_draft, draft_min, draft_max, min_draft)
        max_draft = self.clampValue(
            self.form.max_draft, draft_min, draft_max, max_draft)
        # Check that the minimum value is lower than
        # the maximum one
        min_draft = self.clampValue(self.form.min_draft,
                                    draft_min,
                                    max_draft,
                                    min_draft)

        # Clamp the trim angle to sensible values
        trim = self.clampValue(self.form.trim,
                               Units.parseQuantity("-90 deg"),
                               Units.parseQuantity("90 deg"),
                               trim)

    def save(self):
        """ Saves data into ship instance.
        """
        trim = Units.Quantity(self.form.trim.text())
        min_draft = Units.Quantity(self.form.min_draft.text())
        max_draft = Units.Quantity(self.form.max_draft.text())
        n_draft = self.form.n_draft.value()

        props = self.ship.PropertiesList
        try:
            props.index("HydrostaticsTrim")
        except ValueError:
            tooltip = QT_TRANSLATE_NOOP(
                "App::Property",
                "Hydrostatics tool selected trim angle")
            self.ship.addProperty("App::PropertyAngle",
                                  "HydrostaticsTrim",
                                  "Ship",
                                  tooltip)
        self.ship.HydrostaticsTrim = trim

        try:
            props.index("HydrostaticsMinDraft")
        except ValueError:
            tooltip = QT_TRANSLATE_NOOP(
                "App::Property",
                "Hydrostatics tool selected minimum draft")
            self.ship.addProperty("App::PropertyLength",
                                  "HydrostaticsMinDraft",
                                  "Ship",
                                  tooltip)
        self.ship.HydrostaticsMinDraft = min_draft

        try:
            props.index("HydrostaticsMaxDraft")
        except ValueError:
            tooltip = QT_TRANSLATE_NOOP(
                "App::Property",
                "Hydrostatics tool selected maximum draft")
            self.ship.addProperty("App::PropertyLength",
                                  "HydrostaticsMaxDraft",
                                  "Ship",
                                  tooltip)
        self.ship.HydrostaticsMaxDraft = max_draft

        try:
            props.index("HydrostaticsNDraft")
        except ValueError:
            tooltip = QT_TRANSLATE_NOOP(
                "App::Property",
                "Hydrostatics tool number of points selected")
            self.ship.addProperty("App::PropertyInteger",
                                  "HydrostaticsNDraft",
                                  "Ship",
                                  tooltip)
        self.ship.HydrostaticsNDraft = self.form.n_draft.value()

    def lineFaceSection(self, line, surface):
        """ Returns the point of section of a line with a face
        @param line Line object, that can be a curve.
        @param surface Surface object (must be a Part::Shape)
        @return Section points array, [] if line don't cut surface
        """
        result = []
        vertexes = line.Vertexes
        nVertex = len(vertexes)

        section = line.cut(surface)

        points = section.Vertexes
        return points

    def externalFaces(self, shape):
        """ Returns detected external faces.
        @param shape Shape where external faces wanted.
        @return List of external faces detected.
        """
        result = []
        faces = shape.Faces
        bbox = shape.BoundBox
        L = bbox.XMax - bbox.XMin
        B = bbox.YMax - bbox.YMin
        T = bbox.ZMax - bbox.ZMin
        dist = math.sqrt(L*L + B*B + T*T)
        msg = App.Qt.translate(
            "ship_console",
            "Computing external faces")
        App.Console.PrintMessage(msg + '...\n')
        # Valid/unvalid faces detection loop
        for i in range(len(faces)):
            App.Console.PrintMessage("\t{} / {}\n".format(i + 1, len(faces)))
            f = faces[i]
            # Create a line normal to surface at middle point
            u = 0.0
            v = 0.0
            try:
                surf = f.Surface
                u = 0.5*(surf.getUKnots()[0]+surf.getUKnots()[-1])
                v = 0.5*(surf.getVKnots()[0]+surf.getVKnots()[-1])
            except:
                cog = f.CenterOfMass
                [u, v] = f.Surface.parameter(cog)
            p0 = f.valueAt(u, v)
            try:
                n = f.normalAt(u, v).normalize()
            except:
                continue
            p1 = p0 + n.multiply(1.5 * dist)
            line = Part.makeLine(p0, p1)
            # Look for faces in front of this
            nPoints = 0
            for j in range(len(faces)):
                f2 = faces[j]
                section = self.lineFaceSection(line, f2)
                if len(section) <= 2:
                    continue
                # Add points discarding start and end
                nPoints = nPoints + len(section) - 2
            # In order to avoid special directions we can modify line
            # normal a little bit.
            angle = 5
            line.rotate(p0, Vector(1, 0, 0), angle)
            line.rotate(p0, Vector(0, 1, 0), angle)
            line.rotate(p0, Vector(0, 0, 1), angle)
            nPoints2 = 0
            for j in range(len(faces)):
                if i == j:
                    continue
                f2 = faces[j]
                section = self.lineFaceSection(line, f2)
                if len(section) <= 2:
                    continue
                # Add points discarding start and end
                nPoints2 = nPoints + len(section) - 2
            # If the number of intersection points is pair, is a
            # external face. So if we found an odd points intersection,
            # face must be discarded.
            if (nPoints % 2) or (nPoints2 % 2):
                continue
            result.append(f)
            self.timer.start(0.0)
            self.loop.exec_()
            if(not self.running):
                break
        return result


def createTask():
    panel = TaskPanel()
    Gui.Control.showDialog(panel)
    if panel.setupUi():
        Gui.Control.closeDialog()
        return None
    return panel
