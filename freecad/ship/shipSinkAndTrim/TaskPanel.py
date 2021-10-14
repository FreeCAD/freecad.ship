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
from .. import Ship_rc
from ..shipUtils import Selection


class TaskPanel:
    def __init__(self):
        self.name = "ship equilibrium state plotter"
        self.ui = ":/ui/TaskPanel_shipSinkAndTrim.ui"
        self.form = Gui.PySideUic.loadUi(self.ui)
        self.doc = None
        self.plot = None

    def accept(self):
        return True

    def reject(self):
        self.clear()
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
        return True

    def helpRequested(self):
        pass

    def setupUi(self):
        self.form.update = self.widget(QtGui.QPushButton, "update")
        self.form.ref = self.widget(QtGui.QComboBox, "ref")
        self.form.result = self.widget(QtGui.QTextEdit, "result")
        if self.initValues():
            return True
        QtCore.QObject.connect(
            self.form.update,
            QtCore.SIGNAL("pressed()"),
            self.onUpdate)
        QtCore.QObject.connect(
            self.form.ref,
            QtCore.SIGNAL("activated(QString)"),
            self.onReference)

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
        form = mw.findChild(QtGui.QWidget, "TaskPanel")
        return form.findChild(class_id, name)

    def initValues(self):
        """ Set initial values for fields
        """
        self.doc = App.ActiveDocument
        # Look for selected loading conditions (Spreadsheets)
        sel_lcs = Selection.get_lcs()
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

        # We have a valid loading condition, let's set the initial field values
        self.form.result.setText(QtGui.QApplication.translate(
            "ship_sinkandtrim",
            "Press update button to compute",
            None))

        return False

    def onUpdate(self):
        """Time to recompute!
        """
        self.clear()
        fs_ref = self.form.ref.currentIndex() == 0
        self.plot, draft, trim, disp = Tools.compute(self.lc,
                                                     fs_ref=fs_ref,
                                                     doc=self.doc)
        if self.plot is None:
            self.form.result.setText(QtGui.QApplication.translate(
            "ship_sinkandtrim",
            "The ship cannot float!",
            None))
            return

        draft_str = QtGui.QApplication.translate(
            "ship_create",
            "Draft",
            None)
        trim_str = QtGui.QApplication.translate(
            "ship_hydrostatic",
            "Trim",
            None)
        self.form.result.setText(
            "\u0394 = {}\n".format(disp.UserString) + \
            "{} = {}\n".format(draft_str, draft.UserString) + \
            "{} = {}\n".format(trim_str, trim.UserString))

    def onReference(self):
        """ Function called when the section type is changed.
        """
        if self.plot:
            self.onUpdate()

    def clear(self):
        if self.plot is None:
            return

        for name in self.plot.getSubObjects():
            obj = self.plot.getSubObjectList(name)[1]
            App.ActiveDocument.removeObject(obj.Name)
        App.ActiveDocument.removeObject(self.plot.Name)
        self.plot = None


def createTask():
    panel = TaskPanel()
    Gui.Control.showDialog(panel)
    if panel.setupUi():
        Gui.Control.closeDialog()
        return None
    return panel
