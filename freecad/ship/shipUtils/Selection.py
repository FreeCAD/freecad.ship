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
import FreeCADGui as Gui
from FreeCAD import Units
import sys


def __get_shape_solids(obj):
    try:
        return obj.Solids
    except AttributeError:
        try:
            return __get_shape_solids(obj.Shape)
        except AttributeError:
            return []
    return []


def __get_shape_surfaces(obj):
    try:
        return obj.Faces
    except AttributeError:
        try:
            return __get_shape_surfaces(obj.Shape)
        except AttributeError:
            return []
    return []


def __get_shape_lines(obj):
    try:
        return obj.Edges
    except AttributeError:
        try:
            return __get_shape_lines(obj.Shape)
        except AttributeError:
            return []
    return []


def __get_shape_points(obj):
    try:
        return obj.Vertexes
    except AttributeError:
        try:
            return __get_shape_points(obj.Shape)
        except AttributeError:
            return []
    return []


def get_solids():
    """Returns the selected solids
    """
    shapes = []
    for obj in Gui.Selection.getSelection():
        shapes += __get_shape_solids(obj)
    return shapes


def get_surfaces():
    """Returns the selected faces
    """
    shapes = []
    for obj in Gui.Selection.getSelection():
        shapes += __get_shape_surfaces(obj)
    return shapes


def get_lines():
    """Returns the selected edges
    """
    shapes = []
    for obj in Gui.Selection.getSelection():
        shapes += __get_shape_lines(obj)
    return shapes


def get_points():
    """Returns the selected vertices
    """
    shapes = []
    for obj in Gui.Selection.getSelection():
        shapes += __get_shape_points(obj)
    return shapes


def get_shapes():
    return get_points() + get_lines() + get_surfaces() + get_solids()


def get_ships():
    objs = []
    for obj in Gui.Selection.getSelection():
        try:
            if obj.IsShip:
                objs.append(obj)
        except AttributeError:
            continue
    return objs


def get_tanks():
    objs = []
    for obj in Gui.Selection.getSelection():
        try:
            if obj.IsTank:
                objs.append(obj)
        except AttributeError:
            continue
    return objs


def get_lc_ship(lc):
    try:
        if lc not in lc.Document.getObjectsByLabel(lc.get('B2')):
            return None
        ships = lc.Document.getObjectsByLabel(lc.get('B1'))
    except ValueError:
        None
    if len(ships) != 1:
        return None
    ship = ships[0]
    try:
        if not ship.IsShip:
            return None
    except AttributeError:
        return None
    return ship


def get_lc_weights(lc):
    objs = []
    i = 6
    while True:
        try:
            label = lc.get('A{}'.format(i))
        except ValueError:
            break
        i += 1
        weights = lc.Document.getObjectsByLabel(label)
        if len(weights) != 1:
            msg = QtGui.QApplication.translate(
                "ship_console",
                "Several weights are labelled '{}'!".format(label),
                None)
            App.Console.PrintError(msg + '\n')
            continue
        weight = weights[0]
        try:
            if not weight.IsWeight:
                continue
        except AttributeError:
            continue
        objs.append(weight)
    return objs


def get_lc_tanks(lc):
    objs = []
    i = 6
    while True:
        cells = ['{}{}'.format(c, i) for c in ('C', 'D', 'E')]
        try:
            label = lc.get('C{}'.format(i))
            dens = lc.get('D{}'.format(i))
            level = lc.get('E{}'.format(i))
        except ValueError:
            break
        i += 1
        tanks = lc.Document.getObjectsByLabel(label)
        if len(tanks) != 1:
            msg = QtGui.QApplication.translate(
                "ship_console",
                "Several tanks are labelled '{}'!".format(label),
                None)
            App.Console.PrintError(msg + '\n')
            continue
        tank = tanks[0]
        try:
            if not tank.IsTank:
                continue
        except AttributeError:
            continue
        try:
            dens = float(dens)
            level = float(level)
        except ValueError:
            continue
        dens = Units.parseQuantity('{} kg / m^3'.format(dens))
        objs.append((tank, dens, level))
    return objs


def get_lcs():
    objs = []
    for obj in Gui.Selection.getSelection():
        try:
            if obj.TypeId != 'Spreadsheet::Sheet':
                continue
        except ValueError:
            continue
        # Check if it is a Loading condition:
        if get_lc_ship(obj) is None:
            continue
        objs.append(obj)
    return objs


def get_meshes():
    objs = []
    for obj in Gui.Selection.getSelection():
        try:
            if obj.Module != 'Mesh':
                continue
        except AttributeError:
            continue
        objs.append(obj)
    return objs    


def get_doc_ships(doc=None):
    doc = doc or App.ActiveDocument
    objs = []
    for obj in doc.Objects:
        try:
            if obj.IsShip:
                objs.append(obj)
        except AttributeError:
            continue
    return objs

# Some shortcuts for Seakeeping
# =============================

def get_lc_mesh(lc):
    """Get the mesh associated to the ship associated to the load condition
    """
    ship = get_lc_ship(lc)
    if ship is None:
        return None
    try:
        if len(ship.Mesh) != 1:
            return None
    except AttributeError:
        return None
    return lc.Document.getObject(ship.Mesh[0])


def get_lcs_with_mesh():
    """Get the selected load conditions which has a ship with an associated
    mesh
    """
    lcs = get_lcs()
    objs = []
    for lc in lcs:
        ship = get_lc_ship(lc)
        try:
            if len(ship.Mesh) != 1:
                continue
        except AttributeError:
            continue
        if App.ActiveDocument.getObject(ship.Mesh[0]) is None:
            continue
        objs.append(lc)
    return objs
