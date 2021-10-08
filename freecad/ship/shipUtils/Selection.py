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
