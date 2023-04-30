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
    def __init__(self, speed, resis, CF, CR, CA, CT, ship):
        """ Constructor. performs the plot and shows it.
        @param Speed, Ship speed.
        @param Resis, Resistance computed.
        @param CF, Frictional resistance coefficient.
        @param CR, residual resistance coefficient.
        @param CA, Roughness coefficient
        @param CT, Total resistance coefficient.
        @param ship Active ship instance.
        """
        self.plot(speed, resis, ship)
        self.plotCoeff(speed, CF, CR, CT, CA, ship)
        self.spreadSheet(speed, resis, CF, CR, CA, CT, ship)

    def plot(self, speed, resis, ship):
        """ Perform the areas curve plot.
        @param Speed, Ship speed.
        @param Resis, Resistance computed.
        @param ship Active ship instance.
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

        plt = Plot.figure('R - V')
        self.plt = plt
        
        areas = Plot.plot(speed, resis, 'Resistance Amadeo method')
        areas.line.set_linestyle('-')
        areas.line.set_linewidth(2.0)
        areas.line.set_color((0.0, 0.0, 0.0))

        # Write axes titles
        Plot.xlabel(r'$Speed \; \mathrm{m/s}$')
        Plot.ylabel(r'$Resistance \; \mathrm{kN}$')
        # Show grid
        Plot.grid(True)
        # End
        return False

    def plotCoeff(self, speed, CF, CR ,CT, CA, ship):
        """ Perform the areas curve plot.
        @param speed, Ship speed.
        @param CF, Frictional resistance coefficient.
        @param CR, residual resistance coefficient.
        @param CA, Roughness coefficient
        @param CT, Total resistance coefficient.
        @param ship Active ship instance.
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

        
        plt = Plot.figure('Coefficients')
        self.plt2 = plt
        
        for i in range(0, 3):
            ax = Plot.addNewAxes()
            for loc, spine in ax.spines.items():
                if loc in ['right', 'left']:
                    spine.set_position(('outward', (i + 1) * 35))
            Plot.grid(True)

        axes = Plot.axesList()
        for ax in axes:
            ax.set_position([0.1, 0.35,  0.65,  0.8])
        
        plt.axes = axes[0]
        CF = Plot.plot(speed, CF, r'$CF$')
        CF.line.set_linestyle('-')
        CF.line.set_linewidth(2.0)
        CF.line.set_color((0.0, 0.0, 0.0))
        self.CF = CF
        Plot.xlabel(r'$Speed \; \mathrm{m/s}$')
        Plot.ylabel(r'$CF$ (Friction coefficient)')
        ax.xaxis.label.set_fontsize(15)
        ax.yaxis.label.set_fontsize(15)
        
        plt.axes = axes[1]
        CR = Plot.plot(speed, CR, r'$CR$')
        CR.line.set_linestyle('-')
        CR.line.set_linewidth(2.0)
        CR.line.set_color((1.0, 0.0, 0.0))
        self.CR = CR
        Plot.xlabel(r'$Speed \; \mathrm{m/s}$')
        Plot.ylabel(r'$CR$ (Residual resistance coefficient)')
        ax.xaxis.label.set_fontsize(15)
        ax.yaxis.label.set_fontsize(15)
        
        plt.axes = axes[2]
        CT = Plot.plot(speed, CT, r'$CT$')
        CT.line.set_linestyle('-')
        CT.line.set_linewidth(2.0)
        CT.line.set_color((0.0, 0.0, 1.0))
        self.CT = CT
        Plot.xlabel(r'$Speed \; \mathrm{m/s}$')
        Plot.ylabel(r'$CT$ (Total resistance coefficient)')
        ax.xaxis.label.set_fontsize(15)
        ax.yaxis.label.set_fontsize(15)
        
        plt.axes = axes[3]
        CA = Plot.plot(speed, CA, r'$CA$')
        CA.line.set_linestyle('-')
        CA.line.set_linewidth(2.0)
        CA.line.set_color((0.2, 0.8, 0.2))
        self.CA = CA
        Plot.xlabel(r'$Speed \; \mathrm{m/s}$')
        Plot.ylabel(r'$CT$ (Total resistance coefficient)')
        ax.xaxis.label.set_fontsize(15)
        ax.yaxis.label.set_fontsize(15)
        
        # Show grid
        Plot.grid(True)
        Plot.legend(True)
        # End
        return False

    def spreadSheet(self, speed, resis, CF, CR, CA, CT, ship):
        """ Write the output data file.
        @param Speed, Ship speed.
        @param Resis, Resistance computed.
        @param CF, Frictional resistance coefficient.
        @param CR, residual resistance coefficient.
        @param CA, Roughness coefficient
        @param CT, Total resistance coefficient.
        @param ship Active ship instance.
        """
        s = FreeCAD.activeDocument().addObject('Spreadsheet::Sheet',
                                               'Resistance Amadeo method')

        # Print the header
        s.set("A1", "speed [m/s]")
        s.set("B1", "resistance [kN]")
        s.set("C1", "CF")
        s.set("D1", "CR")
        s.set("E1", "CA")
        s.set("F1", "CT")
        

        # Print the data
        for i in range(len(resis)):
            s.set("A{}".format(i + 2), str(speed[i]))
            s.set("B{}".format(i + 2), str(resis[i]))
            s.set("C{}".format(i + 2), str(CF[i]))
            s.set("D{}".format(i + 2), str(CR[i]))
            s.set("E{}".format(i + 2), str(CA[i]))
            s.set("F{}".format(i + 2), str(CT[i]))
            

        # Recompute
        FreeCAD.activeDocument().recompute()
