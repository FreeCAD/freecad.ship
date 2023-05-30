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
    def __init__(self, speed, Rtotal, CT, CF, CAPP, Cw, CB, CTR, CA, EKW, BKW, ship):
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
        @param EKW, Efficient power.
        @param BKW, Break power.
        @param ship Active ship instance.
        """
        self.plot(speed, Rtotal, ship)
        self.plotPower(speed, EKW, BKW, ship)
        self.plotCoeff(speed, CT, CF, CAPP, Cw, CB, CTR, CA, ship)
        self.spreadSheet(speed, Rtotal, CT, CF, CAPP, Cw, CB, CTR, CA, EKW, BKW, ship)

    def plot(self, speed, Rtotal, ship):
        """ Perform HOltrop resistance plot.
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
            
        plt = Plot.figure('Resistance - V')
        self.plt = plt
        
        ax = Plot.axes()
        Plot.xlabel(r'$Speed \; \mathrm{m/s}$')
        Plot.ylabel(r'$Resistance \; \mathrm{kN}$')
        ax.spines['right'].set_color((0.0, 0.0, 0.0))
        ax.spines['top'].set_color((0.0, 0.0, 0.0))
        ax.xaxis.label.set_fontsize(15)
        ax.yaxis.label.set_fontsize(15)
        ax.set_title('Holtrop Resistance vs Speed', fontweight='bold')
        
        areas = Plot.plot(speed, Rtotal, 'Resistance Holtrop method')
        areas.line.set_linestyle('-')
        areas.line.set_linewidth(2.0)
        areas.line.set_color((0.0, 0.0, 0.0))

        # Show grid
        Plot.grid(True)
        # End
        return False

    def plotPower(self, speed, EKW, BKW, ship):
        """ Perform Holtrop power plot.
        @param Speed, Ship speed.
        @param EKW, Efficient power.
        @param BKW, Break power.
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
    
        plt = Plot.figure('Power - V')
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
        ax.set_title('Holtrop Power vs Speed', fontweight='bold')
        
        EKW = Plot.plot(speed, EKW, r'$EKW, \; Efficient \; power$')
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
    
    
    def plotCoeff(self, speed, CT, CF, CAPP, Cw, CB, CTR, CA, ship):
        """ Perform Holtrop coefficients plot.
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

        plt = Plot.figure('Coefficients')
        self.plt2 = plt
        
        plt.axes.ticklabel_format(axis = 'y', scilimits = (0,0))
        
        ax = Plot.axes()
        ax.set_position([0.05, 0.1,  0.62,  0.8])
        Plot.xlabel(r'$Speed \; \mathrm{m/s}$')
        Plot.ylabel(r'$Resistance \; coefficients$')
        ax.spines['right'].set_color((0.0, 0.0, 0.0))
        ax.spines['top'].set_color((0.0, 0.0, 0.0))
        ax.xaxis.label.set_fontsize(15)
        ax.yaxis.label.set_fontsize(15)
        ax.set_title('Holtrop Resistance Coefficients vs Speed', fontweight='bold')
        
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
        
        Cw = Plot.plot(speed, Cw, r'$CW$, Wave resistance coefficient')
        Cw.line.set_linestyle('-')
        Cw.line.set_linewidth(2.0)
        Cw.line.set_color((1.0, 0.0, 0.0))
        self.Cw = Cw
        
        CA = Plot.plot(speed, CA, r'$CA$, Model-ship correlation coefficient')
        CA.line.set_linestyle('-')
        CA.line.set_linewidth(2.0)
        CA.line.set_color((0.2, 0.8, 0.2))
        self.CA = CA

        CAPP = Plot.plot(speed, CAPP, r'$CAPP$, Appendage resistance coefficient')
        CAPP.line.set_linestyle('-')
        CAPP.line.set_linewidth(2.0)
        CAPP.line.set_color((1.0, 1.0, 0.0))
        self.CAPP = CAPP
        
        CB = Plot.plot(speed, CB, r'$CB$, Bulbous resistance coefficient')
        CB.line.set_linestyle('-')
        CB.line.set_linewidth(2.0)
        CB.line.set_color((0.8, 0.2, 0.8))
        

        CTR = Plot.plot(speed, CTR, r'$CTR$, Transom resistant coefficient')
        CTR.line.set_linestyle('-')
        CTR.line.set_linewidth(2.0)
        CTR.line.set_color((0.5, 0.5, 0.5))
        self.CTR = CTR
        
        # Show grid
        Plot.grid(True)
        Plot.legend(True, pos =(1.05,0.72))
        # End
        return False

    def spreadSheet(self, speed, Rtotal, CT, CF, CAPP, Cw, CB, CTR, CA, EKW, BKW, ship):
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
        @param EKW, Efficient power.
        @param BKW, Break power.
        @param ship Active ship instance.
        """
        s = FreeCAD.activeDocument().addObject('Spreadsheet::Sheet',
                                               'Resistance Holtrop method')

        # Print the header
        s.set("A1", "Speed [m/s]")
        s.set("B1", "Resistance [kN]")
        s.set("C1", "CT * 10^3")
        s.set("D1", "CF * 10^3")
        s.set("E1", "CAPP")
        s.set("F1", "CW * 10^4")
        s.set("G1", "CB * 10^3")
        s.set("H1", "CTR * 10^3")
        s.set("I1", "CA * 10^3")
        s.set("J1", "EKW [kW]")
        s.set("K1", "BKW [kW]")
        

        # Print the data
        for i in range(len(Rtotal)):
            s.set("A{}".format(i + 2), str(speed[i]))
            s.set("B{}".format(i + 2), str(Rtotal[i]))
            s.set("C{}".format(i + 2), str(CT[i] * 1000))
            s.set("D{}".format(i + 2), str(CF[i] * 1000))
            s.set("E{}".format(i + 2), str(CAPP[i] * 1000))
            s.set("F{}".format(i + 2), str(Cw[i] * 10000))
            s.set("G{}".format(i + 2), str(CB[i] * 1000))
            s.set("H{}".format(i + 2), str(CTR[i]  * 1000))
            s.set("I{}".format(i + 2), str(CA[i]  * 1000))
            s.set("J{}".format(i + 2), str(EKW[i]))
            s.set("K{}".format(i + 2), str(BKW[i]))
        
        # Recompute
        FreeCAD.activeDocument().recompute()
