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
import FreeCAD
from FreeCAD import Base
import Spreadsheet

class Plot(object):
    def __init__(self, speed, resis, ship):
        """ Constructor. performs the plot and shows it.
        @param Speed, Ship speed.
        @param Resis, Resistance computed.
        @param ship Active ship instance.
        """
        self.plot(speed, resis, ship)
        self.spreadSheet(speed, resis, ship)

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

        areas = Plot.plot( speed, resis, 'Resistance Amadeo method')
        areas.line.set_linestyle('-')
        areas.line.set_linewidth(2.0)
        areas.line.set_color((0.0, 0.0, 0.0))
       
        # Write axes titles
        Plot.xlabel(r'$x \; \mathrm{m/s}$')
        Plot.ylabel(r'$Resistance \; \mathrm{kN}$')
        # Show grid
        Plot.grid(True)
        # End
        return False

    def spreadSheet(self, speed, resis, ship):
        """ Write the output data file.
        @param Speed, Ship speed.
        @param Resis, Resistance computed.
        @param ship Active ship instance.
        """
        s = FreeCAD.activeDocument().addObject('Spreadsheet::Sheet',
                                               'Resistance Amadeo method')

        # Print the header
        s.set("A1", "speed [m/s]")
        s.set("B1", "resistance [kN]")

        # Print the data
        for i in range(len(resis)):
            s.set("A{}".format(i + 2), str(speed[i]))
            s.set("B{}".format(i + 2), str(resis[i]))

        # Recompute
        FreeCAD.activeDocument().recompute()
