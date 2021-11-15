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


def isAprox(a,b,tol=0.000001):
    """returns if a value is into (b-tol,b+tol)
    @param a Value to compare.
    @param b Center of valid interval
    @param tol Radius of valid interval
    @return True if a is into (b-tol,b+tol), False otherwise
    """
    if (a < b+abs(tol)) and (a > b-abs(tol)):
        return True
    return False


def isSamePoint(a,b,tol=0.000001):
    """returns if two points are the same with a provided tolerance
    @param a Point to compare.
    @param b Reference point.
    @param tol Radius of valid interval
    @return True if twice point are the same, False otherwise
    @note FreeCAD::Base::Vector types must be provided
    """
    if isAprox(a.x,b.x,tol) and isAprox(a.y,b.y,tol) and isAprox(a.z,b.z,tol):
        return True
    return False


def isSameVertex(a,b,tol=0.0001):
    """returns if two points are the same with a provided tolerance
    @param a Point to compare.
    @param b Reference point.
    @param tol Radius of valid interval
    @return True if twice point are the same, False otherwise
    @note FreeCAD::Part::Vertex types must be provided
    """
    if isAprox(a.X,b.X,tol) and isAprox(a.Y,b.Y,tol) and isAprox(a.Z,b.Z,tol):
        return True
    return False


def matrix(size, val=0):
    return [[val for j in range(size)] for i in range(size)]


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
