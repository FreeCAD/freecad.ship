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
from ..shipUtils import Units as USys
from ..shipUtils import Locale


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
        self.form.update = self.widget(QtGui.QPushButton, "UpdateButton")
        self.form.result = self.widget(QtGui.QTextEdit, "ResultsBox")
        if self.initValues():
            return True
        self.retranslateUi()
        QtCore.QObject.connect(
            self.form.update,
            QtCore.SIGNAL("pressed()"),
            self.onUpdate)

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
        self.lc = None
        selObjs = Gui.Selection.getSelection()
        if not selObjs:
            msg = QtGui.QApplication.translate(
                "ship_console",
                "A loading condition instance must be selected before using"
                " this tool (no objects selected)",
                None)
            App.Console.PrintError(msg + '\n')
            return True
        for i in range(len(selObjs)):
            obj = selObjs[i]
            try:
                if obj.TypeId != 'Spreadsheet::Sheet':
                    continue
            except ValueError:
                continue
            # Check if it is a Loading condition:
            # B1 cell must be a ship
            # B2 cell must be the loading condition itself
            doc = App.ActiveDocument
            try:
                if obj not in doc.getObjectsByLabel(obj.get('B2')):
                    continue
                ships = doc.getObjectsByLabel(obj.get('B1'))
                if len(ships) != 1:
                    if len(ships) == 0:
                        msg = QtGui.QApplication.translate(
                            "ship_console",
                            "Wrong Ship label! (no instances labeled as"
                            "'{}' found)",
                            None)
                        App.Console.PrintError(msg + '\n'.format(
                            obj.get('B1')))
                    else:
                        msg = QtGui.QApplication.translate(
                            "ship_console",
                            "Ambiguous Ship label! ({} instances labeled as"
                            "'{}' found)",
                            None)
                        App.Console.PrintError(msg + '\n'.format(
                            len(ships),
                            obj.get('B1')))
                    continue
                ship = ships[0]
                if ship is None or not ship.PropertiesList.index("IsShip"):
                    continue
            except ValueError:
                continue
            # Let's see if several loading conditions have been selected (and
            # prompt a warning)
            if self.lc:
                msg = QtGui.QApplication.translate(
                    "ship_console",
                    "More than one loading condition have been selected (the"
                    " extra loading conditions will be ignored)",
                    None)
                App.Console.PrintWarning(msg + '\n')
                break
            self.lc = obj
        if not self.lc:
            msg = QtGui.QApplication.translate(
                "ship_console",
                "A loading condition instance must be selected before using"
                " this tool (no valid loading condition found at the selected"
                " objects)",
                None)
            App.Console.PrintError(msg + '\n')
            return True

        # We have a valid loading condition, let's set the initial field values
        self.form.result.setText(QtGui.QApplication.translate(
            "ship_sinkandtrim",
            "Press update button to compute",
            None))

        return False

    def retranslateUi(self):
        """ Set user interface locale strings. """
        self.form.setWindowTitle(QtGui.QApplication.translate(
            "ship_sinkandtrim",
            "Sink and trim",
            None))
        self.form.update.setText(
            QtGui.QApplication.translate(
                "ship_sinkandtrim",
                "Update",
                None))

    def onUpdate(self):
        """Time to recompute!
        """
        Tools.compute(self.lc, doc=self.doc)


def createTask():
    panel = TaskPanel()
    Gui.Control.showDialog(panel)
    if panel.setupUi():
        Gui.Control.closeDialog(panel)
        return None
    return panel
