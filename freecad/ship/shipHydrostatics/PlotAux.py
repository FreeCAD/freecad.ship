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
import sys
import math
from PySide import QtGui, QtCore
import FreeCAD
import FreeCADGui
import Spreadsheet
from ..shipUtils import Paths


def autolim(ax):
    xmin, xmax = sys.float_info.max, -sys.float_info.max
    ymin, ymax = sys.float_info.max, -sys.float_info.max
    for l in ax.get_lines():
        xmin = min(xmin, min(l.get_xdata()))
        xmax = max(xmax, max(l.get_xdata()))
        ymin = min(ymin, min(l.get_ydata()))
        ymax = max(ymax, max(l.get_ydata()))
    try:
        ax.set_xlim(xmin, xmax)
    except TypeError:
        pass
    try:
        ax.set_ylim(ymin, ymax)
    except TypeError:
        pass


class Plot(object):
    def __init__(self, ship, points):
        """ Constructor. performs plot and show it (Using pyxplot).
        @param ship Selected ship instance
        @param points List of computed hydrostatics.
        """
        self.points = points[:]
        # Try to plot
        self.plotVolume()
        self.plotStability()
        self.plotCoeffs()
        self.spreadSheet(ship)

    def update(self, ship, points):
        self.points = points[:]
        disp = []
        draft = []
        warea = []
        t1cm = []
        xcb = []
        farea = []
        kbt = []
        bmt = []
        cb = []
        cf = []
        cm = []
        for i in range(len(self.points)):
            disp.append(self.points[i].disp.getValueAs("kg").Value / 1000.0)
            draft.append(self.points[i].draft.getValueAs("m").Value)
            warea.append(self.points[i].wet.getValueAs("m^2").Value)
            t1cm.append(self.points[i].mom.getValueAs("kg*m").Value / 1000.0)
            xcb.append(self.points[i].xcb.getValueAs("m").Value)
            farea.append(self.points[i].farea.getValueAs("m^2").Value)
            kbt.append(self.points[i].KBt.getValueAs("m").Value)
            bmt.append(self.points[i].BMt.getValueAs("m").Value)
            cb.append(self.points[i].Cb)
            cf.append(self.points[i].Cf)
            cm.append(self.points[i].Cm)

        self.draft1.line.set_data(draft, disp)
        self.warea.line.set_data(draft, disp)
        self.t1cm.line.set_data(t1cm, disp)
        self.xcb.line.set_data(xcb, disp)
        for ax in self.plt1.axesList:
            autolim(ax)
        self.plt1.update()
        self.draft2.line.set_data(draft, disp)
        self.farea.line.set_data(farea, disp)
        self.kbt.line.set_data(kbt, disp)
        self.bmt.line.set_data(bmt, disp)
        for ax in self.plt2.axesList:
            autolim(ax)
        self.plt2.update()
        self.draft3.line.set_data(draft, disp)
        self.cb.line.set_data(cb, disp)
        self.cf.line.set_data(cf, disp)
        self.cm.line.set_data(cm, disp)
        for ax in self.plt3.axesList:
            autolim(ax)
        self.plt3.update()

        self.fillSpreadSheet(ship)

    def plotVolume(self):
        """ Perform volumetric hydrostatics.
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
        plt = Plot.figure('Volume')
        self.plt1 = plt

        # Generate the set of axes
        Plot.grid(True)
        for i in range(0, 3):
            ax = Plot.addNewAxes()
            # Y axis can be placed at right
            ax.yaxis.tick_right()
            ax.spines['right'].set_color((0.0, 0.0, 0.0))
            ax.spines['left'].set_color('none')
            ax.yaxis.set_ticks_position('right')
            ax.yaxis.set_label_position('right')
            # And X axis can be placed at bottom
            for loc, spine in ax.spines.items():
                if loc in ['bottom', 'top']:
                    spine.set_position(('outward', (i + 1) * 35))
            Plot.grid(True)

        disp = []
        draft = []
        warea = []
        t1cm = []
        xcb = []
        for i in range(len(self.points)):
            disp.append(self.points[i].disp.getValueAs("kg").Value / 1000.0)
            draft.append(self.points[i].draft.getValueAs("m").Value)
            warea.append(self.points[i].wet.getValueAs("m^2").Value)
            t1cm.append(self.points[i].mom.getValueAs("kg*m").Value / 1000.0)
            xcb.append(self.points[i].xcb.getValueAs("m").Value)

        axes = Plot.axesList()
        for ax in axes:
            ax.set_position([0.1, 0.35, 0.8, 0.65])

        plt.axes = axes[0]
        serie = Plot.plot(draft, disp, r'$T$')
        serie.line.set_linestyle('-')
        serie.line.set_linewidth(2.0)
        serie.line.set_color((0.0, 0.0, 0.0))
        self.draft1 = serie
        Plot.xlabel(r'$T \; \left[ \mathrm{m} \right]$')
        Plot.ylabel(r'$\bigtriangleup \; \left[ \mathrm{tons} \right]$')
        plt.axes.xaxis.label.set_fontsize(15)
        plt.axes.yaxis.label.set_fontsize(15)
        plt.axes = axes[1]
        serie = Plot.plot(warea, disp, r'Wetted area')
        serie.line.set_linestyle('-')
        serie.line.set_linewidth(2.0)
        serie.line.set_color((1.0, 0.0, 0.0))
        self.warea = serie
        Plot.xlabel(r'$Wetted \; area \; \left[ \mathrm{m}^2 \right]$')
        Plot.ylabel(r'$\bigtriangleup \; \left[ \mathrm{tons} \right]$')
        plt.axes.xaxis.label.set_fontsize(15)
        plt.axes.yaxis.label.set_fontsize(15)
        plt.axes = axes[2]
        serie = Plot.plot(t1cm, disp, r'Moment to trim 1cm')
        serie.line.set_linestyle('-')
        serie.line.set_linewidth(2.0)
        serie.line.set_color((0.0, 0.0, 1.0))
        self.t1cm = serie
        Plot.xlabel(r'$Moment \; to \; trim \; 1 \mathrm{cm} \; \left['
                    r' \mathrm{tons} \; \times \; \mathrm{m} \right]$')
        plt.axes.xaxis.label.set_fontsize(15)
        plt.axes.yaxis.label.set_fontsize(15)
        plt.axes = axes[3]
        serie = Plot.plot(xcb, disp, r'$XCB$')
        serie.line.set_linestyle('-')
        serie.line.set_linewidth(2.0)
        serie.line.set_color((0.2, 0.8, 0.2))
        self.xcb = serie
        Plot.xlabel(r'$XCB \; \left[ \mathrm{m} \right]$')
        plt.axes.xaxis.label.set_fontsize(15)
        plt.axes.yaxis.label.set_fontsize(15)

        Plot.legend(True)
        plt.update()
        return False

    def plotStability(self):
        """ Perform stability hydrostatics.
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
        plt = Plot.figure('Stability')
        self.plt2 = plt

        # Generate the sets of axes
        Plot.grid(True)
        for i in range(0, 3):
            ax = Plot.addNewAxes()
            # Y axis can be placed at right
            ax.yaxis.tick_right()
            ax.spines['right'].set_color((0.0, 0.0, 0.0))
            ax.spines['left'].set_color('none')
            ax.yaxis.set_ticks_position('right')
            ax.yaxis.set_label_position('right')
            # And X axis can be placed at bottom
            for loc, spine in ax.spines.items():
                if loc in ['bottom', 'top']:
                    spine.set_position(('outward', (i + 1) * 35))
            Plot.grid(True)

        disp = []
        draft = []
        farea = []
        kbt = []
        bmt = []
        for i in range(len(self.points)):
            disp.append(self.points[i].disp.getValueAs("kg").Value / 1000.0)
            draft.append(self.points[i].draft.getValueAs("m").Value)
            farea.append(self.points[i].farea.getValueAs("m^2").Value)
            kbt.append(self.points[i].KBt.getValueAs("m").Value)
            bmt.append(self.points[i].BMt.getValueAs("m").Value)

        axes = Plot.axesList()
        for ax in axes:
            ax.set_position([0.1, 0.35, 0.8, 0.65])

        plt.axes = axes[0]
        serie = Plot.plot(draft, disp, r'$T$')
        serie.line.set_linestyle('-')
        serie.line.set_linewidth(2.0)
        serie.line.set_color((0.0, 0.0, 0.0))
        self.draft2 = serie
        Plot.xlabel(r'$T \; \left[ \mathrm{m} \right]$')
        Plot.ylabel(r'$\bigtriangleup \; \left[ \mathrm{tons} \right]$')
        plt.axes.xaxis.label.set_fontsize(15)
        plt.axes.yaxis.label.set_fontsize(15)
        plt.axes = axes[1]
        serie = Plot.plot(farea, disp, r'Floating area')
        serie.line.set_linestyle('-')
        serie.line.set_linewidth(2.0)
        serie.line.set_color((1.0, 0.0, 0.0))
        self.farea = serie
        Plot.xlabel(r'$Floating \; area \; \left[ \mathrm{m}^2 \right]$')
        Plot.ylabel(r'$\bigtriangleup \; \left[ \mathrm{tons} \right]$')
        plt.axes.xaxis.label.set_fontsize(15)
        plt.axes.yaxis.label.set_fontsize(15)
        plt.axes = axes[2]
        serie = Plot.plot(kbt, disp, r'$KB_T$')
        serie.line.set_linestyle('-')
        serie.line.set_linewidth(2.0)
        serie.line.set_color((0.0, 0.0, 1.0))
        self.kbt = serie
        Plot.xlabel(r'$KB_T \; \left[ \mathrm{m} \right]$')
        plt.axes.xaxis.label.set_fontsize(15)
        plt.axes.yaxis.label.set_fontsize(15)
        plt.axes = axes[3]
        serie = Plot.plot(bmt, disp, r'$BM_T$')
        serie.line.set_linestyle('-')
        serie.line.set_linewidth(2.0)
        serie.line.set_color((0.2, 0.8, 0.2))
        self.bmt = serie
        Plot.xlabel(r'$BM_T \; \left[ \mathrm{m} \right]$')
        plt.axes.xaxis.label.set_fontsize(15)
        plt.axes.yaxis.label.set_fontsize(15)

        Plot.legend(True)
        plt.update()
        return False

    def plotCoeffs(self):
        """ Perform stability hydrostatics.
        @return True if error happens.
        """
        # Create plot
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
        plt = Plot.figure('Coefficients')
        self.plt3 = plt

        # Generate the set of axes
        Plot.grid(True)
        for i in range(0, 3):
            ax = Plot.addNewAxes()
            # Y axis can be placed at right
            ax.yaxis.tick_right()
            ax.spines['right'].set_color((0.0, 0.0, 0.0))
            ax.spines['left'].set_color('none')
            ax.yaxis.set_ticks_position('right')
            ax.yaxis.set_label_position('right')
            # And X axis can be placed at bottom
            for loc, spine in ax.spines.items():
                if loc in ['bottom', 'top']:
                    spine.set_position(('outward', (i + 1) * 35))
            Plot.grid(True)

        disp = []
        draft = []
        cb = []
        cf = []
        cm = []
        for i in range(len(self.points)):
            disp.append(self.points[i].disp.getValueAs("kg").Value / 1000.0)
            draft.append(self.points[i].draft.getValueAs("m").Value)
            cb.append(self.points[i].Cb)
            cf.append(self.points[i].Cf)
            cm.append(self.points[i].Cm)

        axes = Plot.axesList()
        for ax in axes:
            ax.set_position([0.1, 0.35, 0.8, 0.65])

        plt.axes = axes[0]
        serie = Plot.plot(draft, disp, r'$T$')
        serie.line.set_linestyle('-')
        serie.line.set_linewidth(2.0)
        serie.line.set_color((0.0, 0.0, 0.0))
        self.draft3 = serie
        Plot.xlabel(r'$T \; \left[ \mathrm{m} \right]$')
        Plot.ylabel(r'$\bigtriangleup \; \left[ \mathrm{tons} \right]$')
        plt.axes.xaxis.label.set_fontsize(15)
        plt.axes.yaxis.label.set_fontsize(15)
        plt.axes = axes[1]
        serie = Plot.plot(cb, disp, r'$Cb$')
        serie.line.set_linestyle('-')
        serie.line.set_linewidth(2.0)
        serie.line.set_color((1.0, 0.0, 0.0))
        self.cb = serie
        Plot.xlabel(r'$Cb$ (Block coefficient)')
        Plot.ylabel(r'$\bigtriangleup \; \left[ \mathrm{tons} \right]$')
        plt.axes.xaxis.label.set_fontsize(15)
        plt.axes.yaxis.label.set_fontsize(15)
        plt.axes = axes[2]
        serie = Plot.plot(cf, disp, r'$Cf$')
        serie.line.set_linestyle('-')
        serie.line.set_linewidth(2.0)
        serie.line.set_color((0.0, 0.0, 1.0))
        self.cf = serie
        Plot.xlabel(r'$Cf$ (floating area coefficient)')
        plt.axes.xaxis.label.set_fontsize(15)
        plt.axes.yaxis.label.set_fontsize(15)
        plt.axes = axes[3]
        serie = Plot.plot(cm, disp, r'$Cm$')
        serie.line.set_linestyle('-')
        serie.line.set_linewidth(2.0)
        serie.line.set_color((0.2, 0.8, 0.2))
        self.cm = serie
        Plot.xlabel(r'$Cm$  (Main section coefficient)')
        plt.axes.xaxis.label.set_fontsize(15)
        plt.axes.yaxis.label.set_fontsize(15)

        Plot.legend(True)
        plt.update()
        return False

    def fillSpreadSheet(self, ship):
        s = self.sheet

        # Print the header
        s.set("A1", "displacement [ton]")
        s.set("B1", "draft [m]")
        s.set("C1", "wetted surface [m^2]")
        s.set("D1", "1cm trimming ship moment [ton*m]")
        s.set("E1", "Floating area [m^2]")
        s.set("F1", "KBl [m]")
        s.set("G1", "KBt [m]")
        s.set("H1", "BMt [m]")
        s.set("I1", "Cb")
        s.set("J1", "Cf")
        s.set("K1", "Cm")

        # Print the data
        for i in range(len(self.points)):
            point = self.points[i]
            s.set("A{}".format(i + 2),
                  str(point.disp.getValueAs("kg").Value / 1000.0))
            s.set("B{}".format(i + 2),
                  str(point.draft.getValueAs("m").Value))
            s.set("C{}".format(i + 2),
                  str(point.wet.getValueAs("m^2").Value))
            s.set("D{}".format(i + 2),
                  str(point.mom.getValueAs("kg*m").Value / 1000.0))
            s.set("E{}".format(i + 2),
                  str(point.farea.getValueAs("m^2").Value))
            s.set("F{}".format(i + 2),
                  str(point.xcb.getValueAs("m").Value))
            s.set("G{}".format(i + 2),
                  str(point.KBt.getValueAs("m").Value))
            s.set("H{}".format(i + 2),
                  str(point.BMt.getValueAs("m").Value))
            s.set("I{}".format(i + 2),
                  str(point.Cb))
            s.set("J{}".format(i + 2),
                  str(point.Cf))
            s.set("K{}".format(i + 2),
                  str(point.Cm))

        # Recompute
        FreeCAD.activeDocument().recompute()

    def spreadSheet(self, ship):
        """ Write data file.
        @param ship Selected ship instance
        @param trim Trim angle.
        @return True if error happens.
        """
        self.sheet = FreeCAD.activeDocument().addObject('Spreadsheet::Sheet',
                                                        'Hydrostatics')
        self.fillSpreadSheet(ship)
