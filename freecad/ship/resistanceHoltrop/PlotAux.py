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
    def __init__(self, speed, Rtotal, CT, CF, CAPP, Cw, CB, CTR, CA, ship):
        """ Constructor. performs the plot and shows it.
        @param Speed, Ship speed.
        @param Rtotal, Resistance computed.
        @param CT, Total resistance coefficient
        @param CF, Frictional resistance coefficient.
        @param CAPP, Appendage resistance coefficient.
        @param Cw, Wave resistance coefficient.
        @param CB, Additional resistance coefficient due to the presence of a 
                                                bulbous bow near the surface
        @param CTR, Additional resistance coefficient due to the inmersed.
                                                                    transom.
        @param CA, Model-ship correlation resistance coefficient.
        @param ship Active ship instance.
        """
        self.plot(speed, Rtotal, ship)
        self.plotCoeff(speed, CT, CF, CAPP, Cw, CB, CTR, CA, ship)
        self.spreadSheet(speed, Rtotal, CT, CF, CAPP, Cw, CB, CTR, CA, ship)

    def plot(self, speed, Rtotal, ship):
        """ Perform the areas curve plot.
        @param Speed, Ship speed.
        @param Rtotal, Resistance computed.
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
        
        areas = Plot.plot(speed, Rtotal, 'Resistance Holtrop method')
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

    def plotCoeff(self, speed, CT, CF, CAPP, Cw, CB, CTR, CA, ship):
        """ Perform the areas curve plot.
        @param speed, Ship speed.
        @param CT, Total resistance coefficient
        @param CF, Frictional resistance coefficient.
        @param CAPP, Appendage resistance coefficient.
        @param Cw, Wave resistance coefficient.
        @param CB, Additional resistance coefficient due to the presence of a 
                                                bulbous bow near the surface
        @param CTR, Additional resistance coefficient due to the inmersed.
                                                                    transom.
        @param CA, Model-ship correlation resistance coefficient.
        @param ship Active ship instance.
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

        ax = Plot.axes()

        plt = Plot.figure('Coefficients - V')
        self.plt2 = plt
        
        CT = Plot.plot(speed, CT, r'$CT$')
        CT.line.set_linestyle('-')
        CT.line.set_linewidth(2.0)
        CT.line.set_color((0.0, 0.0, 0.0))
        self.CT = CT
        Plot.xlabel(r'$Speed \; \mathrm{m/s}$')
        Plot.ylabel(r'$CT$ (Total resistance coefficient)')
        ax.xaxis.label.set_fontsize(15)
        ax.yaxis.label.set_fontsize(15)
        
        CF = Plot.plot(speed, CF, r'$CF$')
        CF.line.set_linestyle('-')
        CF.line.set_linewidth(2.0)
        CF.line.set_color((0.0, 1.0, 0.0))
        self.CF = CF
        Plot.xlabel(r'$Speed \; \mathrm{m/s}$')
        Plot.ylabel(r'$CF$ (Friction coefficient)')
        ax.xaxis.label.set_fontsize(15)
        ax.yaxis.label.set_fontsize(15)
        
        CAPP = Plot.plot(speed, CAPP, r'$CAPP$')
        CAPP.line.set_linestyle('-')
        CAPP.line.set_linewidth(2.0)
        CAPP.line.set_color((1.0, 0.0, 0.0))
        self.CAPP = CAPP
        Plot.xlabel(r'$Speed \; \mathrm{m/s}$')
        Plot.ylabel(r'$CAPP$ (Appendage resistance coefficient)')
        ax.xaxis.label.set_fontsize(15)
        ax.yaxis.label.set_fontsize(15)
        
        Cw = Plot.plot(speed, Cw, r'$Cw$')
        Cw.line.set_linestyle('-')
        Cw.line.set_linewidth(2.0)
        Cw.line.set_color((0.0, 0.0, 1.0))
        self.Cw = Cw
        Plot.xlabel(r'$Speed \; \mathrm{m/s}$')
        Plot.ylabel(r'$Cw$ (Wave resistance coefficient)')
        ax.xaxis.label.set_fontsize(15)
        ax.yaxis.label.set_fontsize(15)
        
        CB = Plot.plot(speed, CB, r'$CB$')
        CB.line.set_linestyle('-')
        CB.line.set_linewidth(2.0)
        CB.line.set_color((0.8, 0.2, 0.8))
        self.CB = CB
        Plot.xlabel(r'$Speed \; \mathrm{m/s}$')
        Plot.ylabel(r'$CB$ (Bulbous additional resistance coefficient )')
        ax.xaxis.label.set_fontsize(15)
        ax.yaxis.label.set_fontsize(15)
        
        CTR = Plot.plot(speed, CTR, r'$CTR$')
        CTR.line.set_linestyle('-')
        CTR.line.set_linewidth(2.0)
        CTR.line.set_color((0.5, 0.5, 0.5))
        self.CTR = CTR
        Plot.xlabel(r'$Speed \; \mathrm{m/s}$')
        Plot.ylabel(r'$CTR$ (Imnserd transom additional resistance coefficient)')
        ax.xaxis.label.set_fontsize(15)
        ax.yaxis.label.set_fontsize(15)
        
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

    def spreadSheet(self, speed, Rtotal, CT, CF, CAPP, Cw, CB, CTR, CA, ship):
        """ Write the output data file.
        @param speed, Ship speed.
        @param CT, Total resistance coefficient
        @param CF, Frictional resistance coefficient.
        @param CAPP, Appendage resistance coefficient.
        @param Cw, Wave resistance coefficient.
        @param CB, Additional resistance coefficient due to the presence of a 
                                                bulbous bow near the surface
        @param CTR, Additional resistance coefficient due to the inmersed.
                                                                    transom.
        @param CA, Model-ship correlation resistance coefficient.
        @param ship Active ship instance.
        """
        s = FreeCAD.activeDocument().addObject('Spreadsheet::Sheet',
                                               'Resistance Holtrop method')

        # Print the header
        s.set("A1", "speed [m/s]")
        s.set("B1", "resistance [kN]")
        s.set("C1", "CT")
        s.set("D1", "CF")
        s.set("E1", "CAPP")
        s.set("F1", "Cw")
        s.set("G1", "CB")
        s.set("H1", "CTR")
        s.set("I1", "CA")
        

        # Print the data
        for i in range(len(Rtotal)):
            s.set("A{}".format(i + 2), str(speed[i]))
            s.set("B{}".format(i + 2), str(Rtotal[i]))
            s.set("C{}".format(i + 2), str(CT[i]))
            s.set("D{}".format(i + 2), str(CF[i]))
            s.set("E{}".format(i + 2), str(CAPP[i]))
            s.set("F{}".format(i + 2), str(Cw[i]))
            s.set("G{}".format(i + 2), str(CB[i]))
            s.set("H{}".format(i + 2), str(CTR[i]))
            s.set("I{}".format(i + 2), str(CA[i]))
            

        # Recompute
        FreeCAD.activeDocument().recompute()
