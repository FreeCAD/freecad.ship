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
from FreeCAD import Units
from .. import WeightInstance as Instance


def matrix(size, val=0):
    return [[val for j in range(size)] for i in range(size)]


def createWeight(shapes, ship, density, inertia):
    """Create a new weight instance

    Position arguments:
    shapes -- List of shapes of the weight
    ship -- Ship owner
    density -- Density of the object. 4 possibilities are considered here:
        * Density as Mass/Volume: then the weight will be considered as a
        volumetric object. Used for blocks or similar.
        * Density as Mass/Area: then the weight will be considered as an area
        element. Used for structural shells.
        * Density as Mass/Length: then the weight will be cosidered as a linear
        element. Used for linear structural reinforcements.
        * Mass: Then a punctual mass will be considered. Used for complex
        weights, like engines or other machines.
    inertia -- Inertia matrix (3x3)

    Returned value:
    The new weight object

    It is strongly recommended to pass just shapes matching with the provided
    density, e.g. don't use volumetric shapes with a linear density value (kg/m)

    The tool will claim the new weight as a child of the ship object. Please do
    not remove the partner ship object before removing this new weight before.
    """
    # Create the object
    obj = App.ActiveDocument.addObject("Part::FeaturePython", "Weight")
    weight = Instance.Weight(obj, shapes, ship)
    Instance.ViewProviderWeight(obj.ViewObject)

    # Setup the mass/density value
    m_unit = "kg"
    l_unit = "m"
    m_qty = Units.Quantity(1, Units.Mass)
    l_qty = Units.Quantity(1, Units.Length)
    a_qty = Units.Quantity(1, Units.Area)
    v_qty = Units.Quantity(1, Units.Volume)
    if density.Unit == m_qty.Unit:
        w_unit = m_unit
        obj.Mass = density.getValueAs(w_unit).Value
    elif density.Unit == (m_qty / l_qty).Unit:
        w_unit = m_unit + '/' + l_unit
        obj.LineDens = density.getValueAs(w_unit).Value
    elif density.Unit == (m_qty / a_qty).Unit:
        w_unit = m_unit + '/' + l_unit + '^2'
        obj.AreaDens = density.getValueAs(w_unit).Value
    elif density.Unit == (m_qty / v_qty).Unit:
        w_unit = m_unit + '/' + l_unit + '^3'
        obj.Dens = density.getValueAs(w_unit).Value

    # Install the inertia
    i_unit = "kg*m^2"
    I = matrix(4, 0.0)
    I[3][3] = 1.0
    for i,row in enumerate(inertia):
        for j,val in enumerate(row):
            I[i][j] = val.getValueAs(i_unit).Value
    I_flat = []
    for i in range(4):
        for j in range(4):
            I_flat.append(I[j][i])
    obj.Inertia = tuple(I_flat)

    # Set it as a child of the ship
    weights = ship.Weights[:]
    weights.append(obj.Name)
    ship.Weights = weights
    ship.Proxy.cleanWeights(ship)
    ship.Proxy.cleanTanks(ship)
    ship.Proxy.cleanLoadConditions(ship)

    App.ActiveDocument.recompute()

    return obj


def __compute_cog(shapes, elem_type):
    """Compute the center of gravity a set of shapes

    Position arguments:
    shapes -- List of shapes of the same type (see elem_type)
    elem_type -- 1 = vertex, 2 = line, 3 = face, 4 = solids

    Returned value:
    The center of gravity
    """
    l_qty = Units.Quantity(1, Units.Length)
    cog = [Units.Quantity(0, Units.Length) for i in range(3)]
        
    if elem_type == 1:
        mass = len(shapes)
        for shape in shapes:
            cog[0] = cog[0] + shape.X * l_qty
            cog[1] = cog[1] + shape.Y * l_qty
            cog[2] = cog[2] + shape.Z * l_qty
    else:
        mass = 0.0
        for shape in shapes:
            mass += shape.Mass
            cog[0] = cog[0] + shape.Mass * shape.CenterOfMass.x * l_qty
            cog[1] = cog[1] + shape.Mass * shape.CenterOfMass.y * l_qty
            cog[2] = cog[2] + shape.Mass * shape.CenterOfMass.z * l_qty

    for i in range(3):
        cog[i] = cog[i] / mass
    return cog


def __steiner(shape, point, elem_type):
    """Compute the inertia matrix of a shape respect to a different point

    Position arguments:
    shape -- The shape to analyze
    point -- The reference point
    elem_type -- 1 = vertex, 2 = line, 3 = face, 4 = solids

    Returned value:
    The inertia matrix
    """
    l_qty = Units.Quantity(1, Units.Length)
    i_qty = l_qty
    for i in range(elem_type):
        i_qty = i_qty * l_qty
    I = matrix(4, 0.0 * i_qty)
    I[3][3] = 1.0 * i_qty

    r = [point[0] - Units.Quantity(shape.CenterOfMass.x, Units.Length),
         point[1] - Units.Quantity(shape.CenterOfMass.y, Units.Length),
         point[2] - Units.Quantity(shape.CenterOfMass.z, Units.Length)]
    r2 = r[0] * r[0] + r[1] * r[1] + r[2] * r[2]

    if elem_type != 1:
        for i in range(3):
            for j in range(3):
                I[i][j] = Units.Quantity(shape.MatrixOfInertia.A[i + j * 4],
                                         i_qty.Unit)

    for i in range(3):
        I[i][i] += r2 * (i_qty / l_qty**2)
        for j in range(3):
            I[i][j] -= r[i] * r[j] * (i_qty / l_qty**2)
    return I


def compute_inertia(shapes, elem_type):
    """Compute the inertia matrix for a set of shapes

    Position arguments:
    shapes -- List of shapes that compounds the weight (just the ones matching
              elem_type will be taken into account)
    elem_type -- 1 = vertex, 2 = line, 3 = face, 4 = solids

    Returned value:
    The inertia matrix
    """
    s = []
    for shape in shapes:
        if elem_type == 1:
            s = s + shape.Vertexes
        if elem_type == 2:
            s = s + shape.Edges
        if elem_type == 3:
            s = s + shape.Faces
        if elem_type == 4:
            s = s + shape.Solids

    cog = __compute_cog(s, elem_type)
    I = __steiner(s[0], cog, elem_type)
    if len(s) > 1:
        for shape in s[1:]:
            I_shape = __steiner(shape, cog, elem_type)
            for i in range(3):
                for j in range(3):
                    I[i][j] += I_shape[i][j]
    return I
