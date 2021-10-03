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

import math
import FreeCAD as App
import FreeCADGui as Gui
from FreeCAD import Vector, Matrix, Placement
import Part
from FreeCAD import Units
from PySide import QtGui
from .. import Instance as ShipInstance
from .. import WeightInstance
from .. import TankInstance
from ..shipGZ import Tools as GZ
from ..shipHydrostatics import Tools as Hydrostatics


def __make_name(name, doc=App.ActiveDocument):
    i = 0
    out = name
    while doc.getObject(out) != None:
        out = name + "{:03d}".format(i)
    return out


def __place_shape(shape, draft, trim):
    return shape.translate(
        (0, 0, -draft)).rotate((0, 0, 0), (0, 1, 0), -trim)


def compute(lc, doc=App.ActiveDocument):
    points, ship, weights, tanks = GZ.gz(
        lc, [Units.parseQuantity("0 deg")], True)
    if points == []:
        return None
    gz, draft, trim = points[0]
    # Create a free surface
    L = ship.Length
    B = ship.Breadth
    name = __make_name('SinkAndTrim_FS', doc)
    Part.show(Part.makePlane(2.0 * L, 2.0 * B,
                             App.Vector(-L, -B, 0)),
                             name)
    doc.recompute()
    fs = Gui.getDocument(doc.Name).getObject(name)
    fs.LineColor = (0.0, 0.0, 0.5)
    fs.ShapeColor = (0.0, 0.7, 1.0)
    fs.Transparency = 75
    # Copy and place the ship
    name = __make_name('SinkAndTrim_{}'.format(ship.Name), doc)
    Part.show(__place_shape(ship.Shape.copy(), draft, trim), name)
    doc.recompute()
    plot_ship = Gui.getDocument(doc.Name).getObject(name)
    plot_ship.Transparency = 50
    # Copy and place the tanks
    for tank, dens, level in tanks:
        name = __make_name('SinkAndTrim {}'.format(tank.Name), doc)
        vol = tank.Proxy.getVolume(tank, level)
        shape = tank.Proxy.getFluidShape(tank, vol, trim=trim)
        Part.show(__place_shape(shape, draft, trim), name)
        doc.recompute()
    # Place the bouyancy center
    disp, B, _ = Hydrostatics.displacement(ship, draft, trim=trim)
    
    
    
    
