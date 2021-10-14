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
try:
    import FreeCADGui as Gui
except ImportError:
    Gui = None
from FreeCAD import Vector, Matrix, Placement
import Part
from FreeCAD import Units
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


def __vol_cog(shape):
    vol = 0.0
    cog = Vector()
    for solid in shape.Solids:
        vol += solid.Volume
        sCoG = solid.CenterOfMass
        cog.x = cog.x + sCoG.x * solid.Volume
        cog.y = cog.y + sCoG.y * solid.Volume
        cog.z = cog.z + sCoG.z * solid.Volume
    cog.x = cog.x / vol
    cog.y = cog.y / vol
    cog.z = cog.z / vol
    return cog, vol


def compute(lc, fs_ref=True, doc=App.ActiveDocument):
    points, ship, weights, tanks = GZ.gz(
        lc, [Units.parseQuantity("0 deg")], True)
    if points == []:
        return None, 0, 0, 0
    gz, draft, trim = points[0]
    group_objs = []
    # Create a free surface
    L = ship.Length
    B = ship.Breadth
    name = __make_name('SinkAndTrim_FS', doc)
    shape = Part.makePlane(2.0 * L, 2.0 * B, App.Vector(-L, -B, 0))
    if not fs_ref:
        shape = __place_shape(shape, -draft, -trim)
    Part.show(shape, name)
    doc.recompute()
    if Gui:
        fs = Gui.getDocument(doc.Name).getObject(name)
        fs.LineColor = (0.0, 0.0, 0.5)
        fs.ShapeColor = (0.0, 0.7, 1.0)
    group_objs.append(doc.getObject(name))

    # Copy and place the ship
    name = __make_name('SinkAndTrim_{}'.format(ship.Name), doc)
    shape = ship.Shape.copy()
    if fs_ref:
        shape = __place_shape(ship.Shape.copy(), draft, trim)
    Part.show(shape, name)
    doc.recompute()
    if Gui:
        plot_ship = Gui.getDocument(doc.Name).getObject(name)
        plot_ship.Transparency = 50
    group_objs.append(doc.getObject(name))
    doc.getObject(name).Label = 'SinkAndTrim_' + ship.Label
    # Copy and place the tanks
    tank_shapes = []  # Untransformed
    for tank, dens, level in tanks:
        name = __make_name('SinkAndTrim_{}'.format(tank.Name), doc)
        vol = tank.Proxy.getVolume(tank, level)
        shape = tank.Proxy.getFluidShape(tank, vol, trim=trim)
        tank_shapes.append(shape)
        if shape is None:
            continue
        if fs_ref:
            shape = __place_shape(shape.copy(), draft, trim)
        Part.show(shape, name)
        doc.recompute()
        group_objs.append(doc.getObject(name))
        doc.getObject(name).Label = 'SinkAndTrim_' + tank.Label
    # Place the bouyancy center
    disp, B, _ = Hydrostatics.displacement(ship, draft, trim=trim)
    disp *= GZ.G
    name = __make_name('SinkAndTrim_B', doc)
    shape = Part.Vertex(B)
    if fs_ref:
        shape = __place_shape(shape, draft, trim)
    Part.show(shape, name)
    doc.recompute()
    if Gui:
        b = Gui.getDocument(doc.Name).getObject(name)
        b.PointSize = 10.00
    group_objs.append(doc.getObject(name))
    # Place the COG
    COG, W = GZ.weights_cog(weights)
    mom_x = Units.Quantity(COG.x, Units.Length) * W
    mom_y = Units.Quantity(COG.y, Units.Length) * W
    mom_z = Units.Quantity(COG.z, Units.Length) * W
    for i, tank_data in enumerate(tanks):
        dens = tank_data[1]
        shape = tank_shapes[i]
        if shape is None:
            continue
        tank_cog, tank_vol = __vol_cog(shape)
        tank_weight = Units.Quantity(tank_vol, Units.Volume) * dens * GZ.G
        mom_x += Units.Quantity(tank_cog.x, Units.Length) * tank_weight
        mom_y += Units.Quantity(tank_cog.y, Units.Length) * tank_weight
        mom_z += Units.Quantity(tank_cog.z, Units.Length) * tank_weight
        W += tank_weight
    COG = Vector(mom_x / W, mom_y / W, mom_z / W)
    name = __make_name('SinkAndTrim_COG', doc)
    shape = Part.Vertex(COG)
    if fs_ref:
        shape = __place_shape(shape, draft, trim)
    Part.show(shape, name)
    doc.recompute()
    if Gui:
        cog = Gui.getDocument(doc.Name).getObject(name)
        cog.PointSize = 10.00
    group_objs.append(doc.getObject(name))

    # Create a group where the results will be placed
    name = __make_name('SinkAndTrim_results', doc)
    group = doc.addObject('App::DocumentObjectGroup', name)
    for obj in group_objs:
        group.addObject(obj)
    doc.recompute()

    return group, draft, trim, disp / GZ.G
