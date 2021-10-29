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
import Spreadsheet
import numpy as np
from .Tools import DIRS


class Plot(object):
    def __init__(self, title, periods):
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

        self.is_angle = title.lower() in ['roll', 'pitch', 'yaw']

        dirs = list(DIRS)
        dirs.append(2.0 * np.pi)
        periods = [0] + [t.getValueAs('s').Value for t in periods]

        self.plt = Plot.figure(title)
        self.plt.axes.remove()
        fig = self.plt.fig
        ax = fig.subplots(subplot_kw=dict(projection='polar'))
        self.plt.axesList = [ax]
        self.plt.setActiveAxes(-1)
        self.r, self.theta = np.meshgrid(periods, dirs)
        self.rao = np.zeros((len(dirs), len(periods)))
        cs = ax.contourf(self.theta, self.r, self.rao, cmap='jet')
        self.label = 'm / m' if not self.is_angle else 'deg / m'
        self.cb = fig.colorbar(cs, label=self.label)
        self.plt.update()

    def update(self, rao=None):
        if rao:
            self.rao[:rao.shape[0], :rao.shape[1]] = rao
        # Copy the 360deg dir data from the 0deg one
        self.rao[-1, :] = self.rao[0,:]
        # Contour cannot be updated, so we must replot
        self.plt.axes.remove()
        fig = self.plt.fig
        ax = fig.subplots(subplot_kw=dict(projection='polar'))
        self.plt.axesList = [ax]
        self.plt.setActiveAxes(-1)
        rao = self.rao if not self.is_angle else np.degrees(self.rao)
        cs = ax.contourf(self.theta, self.r, rao, cmap='jet', levels=100)
        self.cb.remove()
        self.cb = fig.colorbar(cs, label=self.label)
        self.plt.update()
