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
import FreeCAD
from FreeCAD import Base
import Spreadsheet


class Plot(object):
    def __init__(self, speeds, trims, drag, dfriction, dpressure, cfri, cpres, ctotal, EKW, BKW):
        """ Constructor. performs the plot and shows it.
        @param speeds, Ship speed.
        @param trims, Equilibrium trim computed.
        @param drag, Resistance computed.
        @param dfriction, Friction Resistance computed.
        @param dpressure, Pressure Resistance computed.
        @param cfri, Frictional resistance coefficient.
        @param cpres, Pressure coefficient.
        @param ctotal, Total resistance coefficient.
        @param EKW, Effective power.
        @param BKW, Break power.
        """
        self.plot(speeds, drag, dfriction, dpressure)
        self.plotTrim(speeds, trims)
        self.plotPower(speeds, EKW, BKW)
        self.plotCoeff(speeds, cfri, cpres, ctotal)
        self.spreadSheet(speeds, trims, drag, dfriction, dpressure, cfri, cpres, ctotal, EKW, BKW)

    def plot(self, speeds, drag, dfriction, dpressure):
        """ Perform Savitsky resistance plot.
        @param speeds, Ship speeds.
        @param drag, Resistance computed.
        @param dfriction, Friction Resistance computed.
        @param dpressure, Pressure Resistance computed.
        @return True if error happens.
        """
        try:
            from FreeCAD.Plot import Plot
        except ImportError:
            try:
                from freecad.plot import Plot
            except ImportError:
                msg = FreeCAD.Qt.translate(
                    "ship_console",
                    "Plot module is disabled")
                FreeCAD.Console.PrintWarning(msg + '\n')
                return True

        plt = Plot.figure('Resistance')
        self.plt = plt

        ax = Plot.axes()
        ax.set_position([0.1, 0.1, 0.65, 0.8])
        Plot.xlabel(r'$Speed \; \mathrm{[kn]}$')
        Plot.ylabel(r'$Resistance \; \mathrm{[kN]}$')
        ax.spines['right'].set_color((0.0, 0.0, 0.0))
        ax.spines['top'].set_color((0.0, 0.0, 0.0))
        ax.xaxis.label.set_fontsize(15)
        ax.yaxis.label.set_fontsize(15)
        ax.set_title('Savitsky: Resistance vs Speed', fontweight='bold')

        rtotal = Plot.plot(speeds, drag/1000, r'$Resistance \; Savitsky$')
        rtotal.line.set_linestyle('-')
        rtotal.line.set_linewidth(2.0)
        rtotal.line.set_color((0.0, 0.0, 0.0))
        self.rtotal = rtotal

        rfri = Plot.plot(speeds, dfriction/1000, r'$Frictional \; resistance \; component$')
        rfri.line.set_linestyle('-')
        rfri.line.set_linewidth(2.0)
        rfri.line.set_color((0.0, 0.0, 1.0))
        self.rfri = rfri

        rpress = Plot.plot(speeds, dpressure/1000, r'$Pressure \; resistance \; component$')
        rpress.line.set_linestyle('-')
        rpress.line.set_linewidth(2.0)
        rpress.line.set_color((1.0, 0.0, 0.0))
        self.rpress = rpress

        # Set axis limits
        ax.set_xlim(0, max(speeds) * 1.1)
        ax.set_ylim(0, max(drag/1000) * 1.1)
        # Show grid
        Plot.grid(True)
        # Show legend
        Plot.legend(True, pos=(1.05, 0.6))
        # End
        return False

    def plotTrim(self, speeds, trims):
        """ Perform Savitsky trim plot.
        @param speeds, Ship speeds.
        @param trims, Equilibrium trim computed.
        @return True if error happens.
        """
        try:
            from FreeCAD.Plot import Plot
        except ImportError:
            try:
                from freecad.plot import Plot
            except ImportError:
                msg = FreeCAD.Qt.translate(
                    "ship_console",
                    "Plot module is disabled")
                FreeCAD.Console.PrintWarning(msg + '\n')
                return True

        plt = Plot.figure('Trim')
        self.plt = plt

        ax = Plot.axes()
        ax.set_position([0.1, 0.1, 0.65, 0.8])
        Plot.xlabel(r'$Speeds \; \mathrm{[kn]}$')
        Plot.ylabel(r'$Trim \; \mathrm{[deg]}$')
        ax.spines['right'].set_color((0.0, 0.0, 0.0))
        ax.spines['top'].set_color((0.0, 0.0, 0.0))
        ax.xaxis.label.set_fontsize(15)
        ax.yaxis.label.set_fontsize(15)
        ax.set_title('Savitsky: Trim angle vs Speed', fontweight='bold')

        trim = Plot.plot(speeds, trims, 'Trim angle')
        trim.line.set_linestyle('-')
        trim.line.set_linewidth(2.0)
        trim.line.set_color((0.0, 0.0, 0.0))
        self.trim = trim

        # Set axis limits
        ax.set_xlim(0, max(speeds) * 1.1)
        ax.set_ylim(0, max(trims) * 1.1)
        # Show grid
        Plot.grid(True)
        # End
        return False

    def plotPower(self, speeds, _EKW, _BKW):
        """ Perform Savitsky power plot.
        @param speeds, Ship speeds.
        @param _EKW, Effective power.
        @param _BKW, Break power.
        @return True if error happens.
        """
        try:
            from FreeCAD.Plot import Plot
        except ImportError:
            try:
                from freecad.plot import Plot
            except ImportError:
                msg = FreeCAD.Qt.translate(
                    "ship_console",
                    "Plot module is disabled")
                FreeCAD.Console.PrintWarning(msg + '\n')
                return True

        plt = Plot.figure('Power')
        self.plt3 = plt

        # Write axes titles
        ax = Plot.axes()
        ax.set_position([0.1, 0.1, 0.65, 0.8])
        Plot.xlabel(r'$Speed \; \mathrm{[kn]}$')
        Plot.ylabel(r'$Power \; \mathrm{[kW]}$')
        ax.spines['right'].set_color((0.0, 0.0, 0.0))
        ax.spines['top'].set_color((0.0, 0.0, 0.0))
        ax.xaxis.label.set_fontsize(15)
        ax.yaxis.label.set_fontsize(15)
        ax.set_title('Savitsky: Power vs Speed', fontweight='bold')

        EKW = Plot.plot(speeds, _EKW / 1000, r'$EKW, \; Effective \; power$')
        EKW.line.set_linestyle('-')
        EKW.line.set_linewidth(2.0)
        EKW.line.set_color((0.0, 0.0, 1.0))
        self.EKW = EKW

        BKW = Plot.plot(speeds, _BKW / 1000, r'$BKW, \; Break \; power$')
        BKW.line.set_linestyle('-')
        BKW.line.set_linewidth(2.0)
        BKW.line.set_color((1.0, 0.0, 0.0))
        self.BKW = BKW

        # Set axis limits
        ax.set_xlim(0, max(speeds) * 1.1)
        ax.set_ylim(0, max(_BKW / 1000) * 1.1)
        # Show grid
        Plot.grid(True)
        # Show legend
        Plot.legend(True, pos=(1.05, 0.6))
        # End
        return False

    def plotCoeff(self, speeds, cfric, cpres, ctotal):
        """ Perform Savitsky coefficients plot.
        @param speeds, Ship speeds.
        @param cfric, Frictional resistance coefficient.
        @param cpres, Pressure coefficient.
        @param ctotal, Total resistance coefficient.
        """
        try:
            from FreeCAD.Plot import Plot
        except ImportError:
            try:
                from freecad.plot import Plot
            except ImportError:
                msg = FreeCAD.Qt.translate(
                    "ship_console",
                    "Plot module is disabled")
                FreeCAD.Console.PrintWarning(msg + '\n')
                return True

        plt = Plot.figure('Coefficient')
        self.plt2 = plt

        plt.axes.ticklabel_format(axis='y', scilimits=(0, 0))

        ax = Plot.axes()
        ax.set_position([0.05, 0.1, 0.62, 0.8])
        Plot.xlabel(r'$Speed \; \mathrm{[kn]}$')
        Plot.ylabel(r'$Resistance \; coefficient$')
        ax.spines['right'].set_color((0.0, 0.0, 0.0))
        ax.spines['top'].set_color((0.0, 0.0, 0.0))
        ax.xaxis.label.set_fontsize(15)
        ax.yaxis.label.set_fontsize(15)
        ax.set_title('Savitsky: Resistance Coefficients vs Speed', fontweight='bold')

        cfric = Plot.plot(speeds, cfric, r'$CF$, Schoenherr frictional coefficient')
        cfric.line.set_linestyle('-')
        cfric.line.set_linewidth(2.0)
        cfric.line.set_color((0.0, 0.0, 1.0))
        self.cfri = cfric

        cpres = Plot.plot(speeds, cpres, r'$CP$, Pressure coefficient')
        cpres.line.set_linestyle('-')
        cpres.line.set_linewidth(2.0)
        cpres.line.set_color((1.0, 0.0, 0.0))
        self.cpres = cpres

        ctotal = Plot.plot(speeds, ctotal, r'$CT$, Total resistance coefficient')
        ctotal.line.set_linestyle('-')
        ctotal.line.set_linewidth(2.0)
        ctotal.line.set_color((0.0, 0.0, 0.0))
        self.ctotal = ctotal

        # Show grid
        Plot.grid(True)
        # Show legend
        Plot.legend(True, pos=(1.35, 0.6))
        # End
        return False

    def spreadSheet(self, speeds, trims, drag, dfriction, dpressure, cfri, cpres, ctotal, EKW, BKW):
        """ Write the output data file.
        @param speeds, Ship speeds.
        @param trims, Equilibrium trim computed.
        @param drag, Total resistance.
        @param dfriction, Frictional resistance.
        @param dpressure, Pressure resistance.
        @param cfri, Frictional resistance coefficient.
        @param cpres, Pressure coefficient.
        @param ctotal, Total resistance coefficient.
        @param EKW, Effective power.
        @param BKW, Break power.
        """

        s = FreeCAD.activeDocument().addObject('Spreadsheet::Sheet', 'Resistance Savitsky method')

        # Print the header
        s.set("A1", "Speed [kn]")
        s.set("B1", "Trim [deg]")
        s.set("C1", "Total resistance [kN]")
        s.set("D1", "Friction resistance [kN]")
        s.set("E1", "Pressure resistance [kN]")
        s.set("F1", "CF * 10^3")
        s.set("G1", "CP * 10^3")
        s.set("H1", "CT * 10^3")
        s.set("I1", "EKW [kW]")
        s.set("J1", "BKW [kW]")

        # Print the data
        for i in range(len(drag)):
            s.set("A{}".format(i + 2), str(speeds[i]))
            s.set("B{}".format(i + 2), str(trims[i]))
            s.set("C{}".format(i + 2), str(drag[i] / 1000))
            s.set("D{}".format(i + 2), str(dfriction[i] / 1000))
            s.set("E{}".format(i + 2), str(dpressure[i] / 1000))
            s.set("F{}".format(i + 2), str(cfri[i] * 1000))
            s.set("G{}".format(i + 2), str(cpres[i] * 1000))
            s.set("H{}".format(i + 2), str(ctotal[i] * 1000))
            s.set("I{}".format(i + 2), str(EKW[i] / 1000))
            s.set("J{}".format(i + 2), str(BKW[i] / 1000))

        # Recompute
        FreeCAD.activeDocument().recompute()
