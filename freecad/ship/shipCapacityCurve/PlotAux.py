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
from PySide import QtGui, QtCore
import FreeCAD
import FreeCADGui
from FreeCAD import Base
import Spreadsheet
import matplotlib.ticker as mtick
from ..shipHydrostatics.PlotAux import autolim


class Plot(object):
    def __init__(self, l, z, v):
        """ Constructor. performs the plot and shows it.
        @param l Percentages of filling level.
        @param z Level z coordinates.
        @param v Volume of fluid.
        """
        z = [zz.getValueAs('m').Value for zz in z]
        v = [vv.getValueAs('m^3').Value for vv in v]
        self.plot(l, z, v)
        self.spreadSheet(l, z, v)

    def update(self, l, z, v):
        z = [zz.getValueAs('m').Value for zz in z]
        v = [vv.getValueAs('m^3').Value for vv in v]
        self.fillSpreadSheet(l, z, v)
        if self.plt is None:
            # No GUI? No Plot module? It does not matters, we cannot proceed
            return

        self.l.line.set_data(l, v)
        self.z.line.set_data(z, v)
        for ax in self.plt.axesList:
            autolim(ax)
        self.plt.update()


    def plot(self, l, z, v):
        """ Perform the areas curve plot.
        @param l Percentages of filling level.
        @param z Level z coordinates.
        @param v Volume of fluid.
        @return True if error happens.
        """
        try:
            from FreeCAD.Plot import Plot
        except ImportError:
            try:
                from freecad.plot import Plot
            except ImportError:
                msg = QtGui.QApplication.translate(
                    "ship_console",
                    "Plot module is disabled, so I cannot perform the plot",
                    None)
                FreeCAD.Console.PrintWarning(msg + '\n')
                return True
        plt = Plot.figure('Capacity curve')
        self.plt = plt

        # Plot the volume as a function of the level percentage
        vols = Plot.plot(l, v, 'Capacity')
        vols.line.set_linestyle('-')
        vols.line.set_linewidth(2.0)
        vols.line.set_color((0.0, 0.0, 0.0))
        self.l = vols
        Plot.xlabel(r'$\mathrm{level}$')
        Plot.ylabel(r'$V \; [\mathrm{m}^3]$')
        plt.axes.xaxis.label.set_fontsize(20)
        plt.axes.yaxis.label.set_fontsize(20)
        Plot.grid(True)

        # Special percentage formatter for the x axis
        fmt = '%.0f%%'
        xticks = mtick.FormatStrFormatter(fmt)
        plt.axes.xaxis.set_major_formatter(xticks)

        # Now duplicate the axes
        ax = Plot.addNewAxes()
        # Y axis can be placed at right
        ax.yaxis.tick_right()
        ax.spines['right'].set_color((0.0, 0.0, 0.0))
        ax.spines['left'].set_color('none')
        ax.yaxis.set_ticks_position('right')
        ax.yaxis.set_label_position('right')
        # And X axis can be placed at top
        ax.xaxis.tick_top()
        ax.spines['top'].set_color((0.0, 0.0, 1.0))
        ax.spines['bottom'].set_color('none')
        ax.xaxis.set_ticks_position('top')
        ax.xaxis.set_label_position('top')

        # Plot the volume as a function of the level z coordinate
        vols = Plot.plot(z, v, 'level')
        vols.line.set_linestyle('-')
        vols.line.set_linewidth(2.0)
        vols.line.set_color((0.0, 0.0, 1.0))
        self.z = vols
        Plot.xlabel(r'$z \; [\mathrm{m}]$')
        Plot.ylabel(r'$V \; [\mathrm{m}^3]$')
        ax.xaxis.label.set_fontsize(20)
        ax.yaxis.label.set_fontsize(20)
        ax.xaxis.label.set_color((0.0, 0.0, 1.0))
        ax.tick_params(axis='x', colors=(0.0, 0.0, 1.0))
        Plot.grid(True)

        # End
        plt.update()
        return False

    def fillSpreadSheet(self, l, z, v):
        s = self.sheet
        # Print the header
        s.set("A1", "Percentage of filling level")
        s.set("B1", "Level [m]")
        s.set("C1", "Volume [m^3]")

        # Print the data
        for i in range(len(l)):
            s.set("A{}".format(i + 2), str(l[i]))
            s.set("B{}".format(i + 2), str(z[i]))
            s.set("C{}".format(i + 2), str(v[i]))

        # Recompute
        FreeCAD.activeDocument().recompute()        

    def spreadSheet(self, l, z, v):
        """ Write the output data file.
        @param l Percentages of filling level.
        @param z Level z coordinates.
        @param v Volume of fluid.
        """
        self.sheet = FreeCAD.activeDocument().addObject('Spreadsheet::Sheet',
                                               'Capacity curve')
        self.fillSpreadSheet(l, z, v)
