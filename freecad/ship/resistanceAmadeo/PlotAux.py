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
import numpy as np
import FreeCAD
from FreeCAD import Base
import Spreadsheet

class Plot(object):
    def __init__(self, speed, resis, CF, CR, CA, CT, EKW, BKW):
        """ Constructor. performs the plot and shows it.
        @param Speed, Ship speed.
        @param Resis, Resistance computed.
        @param CF, Frictional resistance coefficient.
        @param CR, residual resistance coefficient.
        @param CA, Roughness coefficient
        @param CT, Total resistance coefficient.
        @param EKW, Efficient power.
        @param BKW, Break power.
        """
        self.plot(speed, resis)
        self.plotPower(speed, EKW, BKW)
        self.plotCoeff(speed, CF, CR, CT, CA)
        self.spreadSheet(speed, resis, CF, CR, CA, CT, EKW, BKW)

    def plot(self, speed, resis):
        """ Perform Amadeo resistance pplot.
        @param Speed, Ship speed.
        @param Resis, Resistance computed.
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
        
        # Write axes titles
        ax = Plot.axes()
        Plot.xlabel(r'$Speed \; \mathrm{m/s}$')
        Plot.ylabel(r'$Resistance \; \mathrm{kN}$')
        ax.spines['right'].set_color((0.0, 0.0, 0.0))
        ax.spines['top'].set_color((0.0, 0.0, 0.0))
        ax.xaxis.label.set_fontsize(15)
        ax.yaxis.label.set_fontsize(15)
        ax.set_title('Amadeo Resistance vs Speed', fontweight='bold')
        
        resis = Plot.plot(speed, resis, r'$Resistance \; \mathrm{kN}$')
        resis.line.set_linestyle('-')
        resis.line.set_linewidth(2.0)
        resis.line.set_color((0.0, 0.0, 0.0))
        
        # Show grid
        Plot.grid(True)
        # End
        return False
    
    def plotPower(self, speed, EKW, BKW):
        """ Perform Amadeo power plot.
        @param Speed, Ship speed.
        @param EKW, Efficient power.
        @param BKW, Break power.
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
        ax.set_position([0.1, 0.1,  0.65,  0.8])
        Plot.xlabel(r'$Speed \; \mathrm{m/s}$')
        Plot.ylabel(r'$Power \; \mathrm{kW}$')
        ax.spines['right'].set_color((0.0, 0.0, 0.0))
        ax.spines['top'].set_color((0.0, 0.0, 0.0))
        ax.xaxis.label.set_fontsize(15)
        ax.yaxis.label.set_fontsize(15)
        ax.set_title('Amadeo Power vs Speed', fontweight='bold')
        
        EKW = Plot.plot(speed, EKW, r'$EKW, \; Effective \; power$')
        EKW.line.set_linestyle('-')
        EKW.line.set_linewidth(2.0)
        EKW.line.set_color((0.0, 0.0, 1.0))
        self.EKW = EKW
        
        BKW = Plot.plot(speed, BKW, r'$BKW, \; Break \; power$')
        BKW.line.set_linestyle('-')
        BKW.line.set_linewidth(2.0)
        BKW.line.set_color((1.0, 0.0, 0.0))
        self.BKW = BKW
        
        
        # Show grid
        Plot.grid(True)
        Plot.legend(True, pos =(1.05,0.6))
        # End
        return False

    def plotCoeff(self, speed, CF, CR ,CT, CA):
        """ Perform Amadeo coefficients plot.
        @param speed, Ship speed.
        @param CF, Frictional resistance coefficient.
        @param CR, Residual resistance coefficient.
        @param CA, Roughness coefficient
        @param CT, Total resistance coefficient.
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
        
        ax = Plot.axes()
        ax.set_position([0.05, 0.1,  0.65,  0.8])
        Plot.xlabel(r'$Speed \; \mathrm{m/s}$')
        Plot.ylabel(r'$Resistance \; coefficients$')
        ax.spines['right'].set_color((0.0, 0.0, 0.0))
        ax.spines['top'].set_color((0.0, 0.0, 0.0))
        ax.xaxis.label.set_fontsize(15)
        ax.yaxis.label.set_fontsize(15)
        ax.set_title('Amadeo Resistance Coefficients vs Speed', fontweight='bold')
        
        
        plt.axes.ticklabel_format(axis = 'y', scilimits = (0,0))
        
        CT = Plot.plot(speed, CT, r'$CT$, Total resistance coefficient')
        CT.line.set_linestyle('-')
        CT.line.set_linewidth(2.0)
        CT.line.set_color((0.0, 0.0, 1.0))
        self.CT = CT

        CF = Plot.plot(speed, CF, r'$CF$, Frictional resistance coefficient')
        CF.line.set_linestyle('-')
        CF.line.set_linewidth(2.0)
        CF.line.set_color((0.0, 0.0, 0.0))
        self.CF = CF

        CR = Plot.plot(speed, CR, r'$CR$, Residual resistance coefficient')
        CR.line.set_linestyle('-')
        CR.line.set_linewidth(2.0)
        CR.line.set_color((1.0, 0.0, 0.0))
        self.CR = CR
        
        CA = Plot.plot(speed, CA, r'$CA$, Roughness coefficient')
        CA.line.set_linestyle('-')
        CA.line.set_linewidth(2.0)
        CA.line.set_color((0.2, 0.8, 0.2))
        self.CA = CA
        
        # Show grid
        Plot.grid(True)
        Plot.legend(True, pos =(1.025,0.6))
        # End
        return False

    def spreadSheet(self, speed, resis, CF, CR, CA, CT, EKW, BKW):
        """ Write the output data file.
        @param Speed, Ship speed.
        @param Resis, Resistance computed.
        @param CF, Frictional resistance coefficient.
        @param CR, residual resistance coefficient.
        @param CA, Roughness coefficient
        @param CT, Total resistance coefficient.
        @param EKW, Efficient power.
        @param BKW, Break power.
        """
        s = FreeCAD.activeDocument().addObject('Spreadsheet::Sheet',
                                               'Resistance Amadeo method')

        # Print the header
        s.set("A1", "Speed [m/s]")
        s.set("B1", "Resistance [kN]")
        s.set("C1", "CF * 10^3")
        s.set("D1", "CR * 10^3")
        s.set("E1", "CA * 10^3")
        s.set("F1", "CT * 10^3")
        s.set("G1", "EKW [kW]")
        s.set("H1", "BKW [kW]")
        

        # Print the data
        for i in range(len(resis)):
            s.set("A{}".format(i + 2), str(speed[i]))
            s.set("B{}".format(i + 2), str(resis[i]))
            s.set("C{}".format(i + 2), str(CF[i] * 1000))
            s.set("D{}".format(i + 2), str(CR[i] * 1000))
            s.set("E{}".format(i + 2), str(CA[i] * 1000))
            s.set("F{}".format(i + 2), str(CT[i] * 1000))
            s.set("G{}".format(i + 2), str(EKW[i]))
            s.set("H{}".format(i + 2), str(BKW[i]))

        # Recompute
        FreeCAD.activeDocument().recompute()