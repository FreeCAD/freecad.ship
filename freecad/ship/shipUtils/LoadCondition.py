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

import FreeCAD as App
from FreeCAD import Vector, Units
from .Selection import get_lc_weights, get_lc_tanks
from ..shipGZ import Tools as GZ


def cog(lc, roll=Units.parseQuantity("0 deg"),
            trim=Units.parseQuantity("0 deg")):
    """Compute the center of gravity in the upright ship reference system

    Position arguments:
    lc -- The load condition

    Keyword arguments:
    roll -- The roll angle
    trim -- The trim angle

    Returns:
    The center of gravity and the total weight (In Newtons)
    """
    cog, w = GZ.weights_cog(get_lc_weights(lc))
    # Add the tanks effect
    tw = Units.parseQuantity("0 kg")
    mom_x = Units.Quantity(cog.x, Units.Length) * w
    mom_y = Units.Quantity(cog.y, Units.Length) * w
    mom_z = Units.Quantity(cog.z, Units.Length) * w
    for t, dens, level in get_lc_tanks(lc):        
        vol = t.Proxy.getVolume(t, level)
        t_weight = vol * dens * GZ.G
        t_cog = t.Proxy.getCoG(t, vol, roll, trim)
        mom_x += Units.Quantity(t_cog.x, Units.Length) * t_weight
        mom_y += Units.Quantity(t_cog.y, Units.Length) * t_weight
        mom_z += Units.Quantity(t_cog.z, Units.Length) * t_weight
        tw += vol * dens
    w += tw * GZ.G

    return Vector(mom_x / w, mom_y / w, mom_z / w), w


def weights_inertia(lc, c=None):
    """Compute the inertia matrix of the ship, without considering the tanks

    Position arguments:
    lc -- The load condition

    Keyword arguments:
    c -- The reference point. If None, the center of gravity from cog() will be
         considered

    Returns:
    The Inertia matrix
    """
    c = c or cog(lc)[0]
    I = [[0 for i in range(3) ] for j in range(3)]
    for w in get_lc_weights(lc):
        I_w = w.Proxy.getInertia(w, center=c)
        for i in range(3):
            for j in range(3):
                I[i][j] += I_w[i][j]
    return I
