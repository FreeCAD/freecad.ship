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
import math
from PySide import QtGui, QtCore
import FreeCAD
import FreeCADGui
import Spreadsheet
from ..shipHydrostatics.PlotAux import autolim


class Plot(object):
    def __init__(self, roll, gz, draft, trim):
        """ Plot the GZ curve

        Position arguments:
        roll -- List of roll angles (in degrees).
        gz -- List of GZ values (in meters).
        draft -- List of equilibrium drafts (in meters).
        trim -- List of equilibrium trim angles (in degrees).
        """
        roll = [r.getValueAs('deg').Value for r in roll]
        gz = [l.getValueAs('m').Value for l in gz]
        draft = [t.getValueAs('m').Value for t in draft]
        trim = [t.getValueAs('deg').Value for t in trim]
        self.plot(roll, gz)
        self.spreadSheet(roll, gz, draft, trim)

    def update(self, roll, gz, draft, trim):
        roll = [r.getValueAs('deg').Value for r in roll]
        gz = [l.getValueAs('m').Value for l in gz]
        draft = [t.getValueAs('m').Value for t in draft]
        trim = [t.getValueAs('deg').Value for t in trim]
        self.fillSpreadSheet(roll, gz, draft, trim)
        if self.plt is None:
            # No GUI? No Plot module? It does not matters, we cannot proceed
            return
        self.gz.line.set_data(roll, gz)
        for ax in self.plt.axesList:
            autolim(ax)
        self.plt.update()


    def plot(self, roll, gz):
        """ Plot the GZ curve.

        Position arguments:
        roll -- List of roll angles (in degrees).
        gz -- List of GZ values (in meters).
        """
        try:
            from FreeCAD.Plot import Plot
        except ImportError:
            try:
                from freecad.plot import Plot
            except ImportError:
                msg = App.Qt.translate(
                    "ship_console",
                    "Plot module is disabled, so I cannot perform the plot")
                FreeCAD.Console.PrintWarning(
                    "Plot module is disabled, so I cannot perform the plot\n")
                return True
        plt = Plot.figure('GZ')
        self.plt = plt

        gz_plot = Plot.plot(roll, gz, 'GZ curve')
        gz_plot.line.set_linestyle('-')
        gz_plot.line.set_linewidth(1.0)
        gz_plot.line.set_color((0.0, 0.0, 0.0))
        self.gz = gz_plot

        ax = Plot.axes()
        Plot.xlabel(r'$\phi \; [\mathrm{deg}]$')
        Plot.ylabel(r'$GZ \; [\mathrm{m}]$')
        ax.xaxis.label.set_fontsize(20)
        ax.yaxis.label.set_fontsize(20)

        Plot.grid(True)
        plt.update()
        return False

    def fillSpreadSheet(self, roll, gz, draft, trim):
        s = self.sheet

        # Print the header
        s.set("A1", "roll [deg]")
        s.set("B1", "GZ [m]")
        s.set("C1", "draft [m]")
        s.set("D1", "trim [deg]")

        # Print the data
        for i in range(len(roll)):
            s.set("A{}".format(i + 2), str(roll[i]))
            s.set("B{}".format(i + 2), str(gz[i]))
            s.set("C{}".format(i + 2), str(draft[i]))
            s.set("D{}".format(i + 2), str(trim[i]))

        # Recompute
        FreeCAD.activeDocument().recompute()

    def spreadSheet(self, roll, gz, draft, trim):
        """ Create a Spreadsheet with the results

        Position arguments:
        roll -- List of roll angles (in degrees).
        gz -- List of GZ values (in meters).
        draft -- List of equilibrium drafts (in meters).
        trim -- List of equilibrium trim angles (in degrees).
        """
        self.sheet = FreeCAD.activeDocument().addObject('Spreadsheet::Sheet',
                                                        'GZ')
        self.fillSpreadSheet(roll, gz, draft, trim)
