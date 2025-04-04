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
import time
from math import *
import FreeCAD
from FreeCAD import Base, Vector, Units
import Part
from .shipUtils import Paths, Math
from .shipUtils.Math import compute_inertia

QT_TRANSLATE_NOOP = FreeCAD.Qt.QT_TRANSLATE_NOOP


def add_weight_props(obj):
    """This function adds the properties to a weight instance, in case they are
    not already created

    Position arguments:
    obj -- Part::FeaturePython object

    Returns:
    The same input object, that now has the properties added
    """
    try:
        obj.getPropertyByName('IsWeight')
    except AttributeError:
        tooltip = QT_TRANSLATE_NOOP(
            "App::Property",
            "True if it is a valid weight instance, False otherwise")
        obj.addProperty("App::PropertyBool",
                        "IsWeight",
                        "Weight",
                        tooltip).IsWeight = True
    try:
        obj.getPropertyByName('Mass')
    except AttributeError:
        tooltip = QT_TRANSLATE_NOOP(
            "App::Property",
            "Mass [kg]")
        obj.addProperty("App::PropertyFloat",
                        "Mass",
                        "Weight",
                        tooltip).Mass = 0.0
    try:
        obj.getPropertyByName('LineDens')
    except AttributeError:
        tooltip = QT_TRANSLATE_NOOP(
            "App::Property",
            "Linear density [kg / m]")
        obj.addProperty("App::PropertyFloat",
                        "LineDens",
                        "Weight",
                        tooltip).LineDens = 0.0
    try:
        obj.getPropertyByName('AreaDens')
    except AttributeError:
        tooltip = QT_TRANSLATE_NOOP(
            "App::Property",
            "Area density [kg / m^2]")
        obj.addProperty("App::PropertyFloat",
                        "AreaDens",
                        "Weight",
                        tooltip).AreaDens = 0.0
    try:
        obj.getPropertyByName('Dens')
    except AttributeError:
        tooltip = QT_TRANSLATE_NOOP(
            "App::Property",
            "Density [kg / m^3]")
        obj.addProperty("App::PropertyFloat",
                        "Dens",
                        "Weight",
                        tooltip).Dens = 0.0
    try:
        obj.getPropertyByName('Inertia')
    except AttributeError:
        tooltip = QT_TRANSLATE_NOOP(
            "App::Property",
            "Inertia [kg * m^2]")
        obj.addProperty("App::PropertyMatrix",
                        "Inertia",
                        "Weight",
                        tooltip).Inertia = (0, 0, 0, 0,
                                            0, 0, 0, 0,
                                            0, 0, 0, 0,
                                            0, 0, 0, 1)
    return obj


class Weight:
    def __init__(self, obj, shapes, ship):
        """ Transform a generic object to a ship instance.

        Position arguments:
        obj -- Part::FeaturePython created object which should be transformed
        in a weight instance.
        shapes -- Set of shapes which will compound the weight element.
        ship -- Ship where the weight is allocated.
        """
        add_weight_props(obj)
        obj.Shape = Part.makeCompound(shapes)
        obj.Proxy = self

    def onChanged(self, fp, prop):
        """Detects the ship data changes.

        Position arguments:
        fp -- Part::FeaturePython object affected.
        prop -- Modified property name.
        """
        if prop == "Mass":
            pass

    def execute(self, fp):
        """Detects the entity recomputations.

        Position arguments:
        fp -- Part::FeaturePython object affected.
        """
        pass

    def _getPuntualMass(self, fp, shape):
        """Compute the mass of a puntual element.

        Position arguments:
        fp -- Part::FeaturePython object affected.
        shape -- Vertex shape object.
        """
        return Units.parseQuantity('{0} kg'.format(fp.Mass))

    def _getLinearMass(self, fp, shape):
        """Compute the mass of a linear element.

        Position arguments:
        fp -- Part::FeaturePython object affected.
        shape -- Edge shape object.
        """
        rho = Units.parseQuantity('{0} kg/m'.format(fp.LineDens))
        l = Units.Quantity(shape.Length, Units.Length)
        return rho * l

    def _getAreaMass(self, fp, shape):
        """Compute the mass of an area element.

        Position arguments:
        fp -- Part::FeaturePython object affected.
        shape -- Face shape object.
        """
        rho = Units.parseQuantity('{0} kg/m^2'.format(fp.AreaDens))
        a = Units.Quantity(shape.Area, Units.Area)
        return rho * a

    def _getVolumetricMass(self, fp, shape):
        """Compute the mass of a volumetric element.

        Position arguments:
        fp -- Part::FeaturePython object affected.
        shape -- Solid shape object.
        """
        rho = Units.parseQuantity('{0} kg/m^3'.format(fp.Dens))
        v = Units.Quantity(shape.Volume, Units.Volume)
        return rho * v

    def getMass(self, fp):
        """Compute the mass of the object, already taking into account the
        type of subentities.

        Position arguments:
        fp -- Part::FeaturePython object affected.

        Returned value:
        Object mass
        """
        m = Units.parseQuantity('0 kg')
        for s in fp.Shape.Solids:
            m += self._getVolumetricMass(fp, s)
        for f in fp.Shape.Faces:
            m += self._getAreaMass(fp, f)
        for e in fp.Shape.Edges:
            m += self._getLinearMass(fp, e)
        for v in fp.Shape.Vertexes:
            m += self._getPuntualMass(fp, v)
        return m

    def _getPuntualMoment(self, fp, shape):
        """Compute the moment of a puntual element (respect to 0, 0, 0).

        Position arguments:
        fp -- Part::FeaturePython object affected.
        shape -- Vertex shape object.
        """
        m = self._getPuntualMass(fp, shape)
        x = Units.Quantity(shape.X, Units.Length)
        y = Units.Quantity(shape.Y, Units.Length)
        z = Units.Quantity(shape.Z, Units.Length)
        return (m * x, m * y, m * z)

    def _getLinearMoment(self, fp, shape):
        """Compute the mass of a linear element (respect to 0, 0, 0).

        Position arguments:
        fp -- Part::FeaturePython object affected.
        shape -- Edge shape object.
        """
        m = self._getLinearMass(fp, shape)
        cog = shape.CenterOfMass
        x = Units.Quantity(cog.x, Units.Length)
        y = Units.Quantity(cog.y, Units.Length)
        z = Units.Quantity(cog.z, Units.Length)
        return (m * x, m * y, m * z)

    def _getAreaMoment(self, fp, shape):
        """Compute the mass of an area element (respect to 0, 0, 0).

        Position arguments:
        fp -- Part::FeaturePython object affected.
        shape -- Face shape object.
        """
        m = self._getAreaMass(fp, shape)
        cog = shape.CenterOfMass
        x = Units.Quantity(cog.x, Units.Length)
        y = Units.Quantity(cog.y, Units.Length)
        z = Units.Quantity(cog.z, Units.Length)
        return (m * x, m * y, m * z)

    def _getVolumetricMoment(self, fp, shape):
        """Compute the mass of a volumetric element (respect to 0, 0, 0).

        Position arguments:
        fp -- Part::FeaturePython object affected.
        shape -- Solid shape object.
        """
        m = self._getVolumetricMass(fp, shape)
        cog = shape.CenterOfMass
        x = Units.Quantity(cog.x, Units.Length)
        y = Units.Quantity(cog.y, Units.Length)
        z = Units.Quantity(cog.z, Units.Length)
        return (m * x, m * y, m * z)

    def getMoment(self, fp):
        """Compute the mass of the object, already taking into account the
        type of subentities.

        Position arguments:
        fp -- Part::FeaturePython object affected.

        Returned value:
        List of moments toward x, y and z
        """
        m = [Units.parseQuantity('0 kg*m'),
             Units.parseQuantity('0 kg*m'),
             Units.parseQuantity('0 kg*m')]
        for s in fp.Shape.Solids:
            mom = self._getVolumetricMoment(fp, s)
            for i in range(len(m)):
                m[i] = m[i] + mom[i]
        for f in fp.Shape.Faces:
            mom = self._getAreaMoment(fp, f)
            for i in range(len(m)):
                m[i] = m[i] + mom[i]
        for e in fp.Shape.Edges:
            mom = self._getLinearMoment(fp, e)
            for i in range(len(m)):
                m[i] = m[i] + mom[i]
        for v in fp.Shape.Vertexes:
            mom = self._getPuntualMoment(fp, v)
            for i in range(len(m)):
                m[i] = m[i] + mom[i]
        return m

    def getCenterOfMass(self, fp):
        """Compute the mass of the object, already taking into account the
        type of subentities.

        Position arguments:
        fp -- Part::FeaturePython object affected.

        Returned value:
        Center of Mass vector
        """
        mass = self.getMass(fp)
        moment = self.getMoment(fp)
        cog = []
        for i in range(len(moment)):
            cog.append(moment[i] / mass)
        return Vector(cog[0].Value, cog[1].Value, cog[2].Value)

    def getInertia(self, fp, center=None):
        """Get the inertia with respect a point.

        Position arguments:
        fp -- Part::FeaturePython object affected.
    
        Keyword arguments:
        center -- FreeCAD.Vector The reference point. If None the center of
                  gravity is considered

        Returned value:
        Inertia matrix [kg * m^2]
        """
        mass = self.getMass(fp)
        if fp.Mass != 0.0:
            add_weight_props(fp)  # For backward compatibility
            I = [[fp.Inertia.A[i + j*4] for j in range(3)] for i in range(3)]
        else:
            if fp.LineDens != 0.0:
                dens = fp.LineDens
                I = compute_inertia(fp.Shape.Edges, 2)
            if fp.AreaDens != 0.0:
                dens = fp.AreaDens
                I = compute_inertia(fp.Shape.Faces, 3)
            if fp.Dens != 0.0:
                dens = fp.Dens
                I = compute_inertia(fp.Shape.Solids, 3)
            for i, row in range(I):
                for j, value in range(row):
                    I[i][j] = (dens * value).getValueAs('kg*m^2').Value
        return I

class ViewProviderWeight:
    def __init__(self, obj):
        """Add this view provider to the selected object.

        Keyword arguments:
        obj -- Object which must be modified.
        """
        obj.Proxy = self

    def attach(self, obj):
        """Setup the scene sub-graph of the view provider, this method is
        mandatory.
        """
        return

    def updateData(self, fp, prop):
        """If a property of the handled feature has changed we have the chance
        to handle this here.

        Keyword arguments:
        fp -- Part::FeaturePython object affected.
        prop -- Modified property name.
        """
        return

    def getDisplayModes(self, obj):
        """Return a list of display modes.

        Keyword arguments:
        obj -- Object associated with the view provider.
        """
        modes = []
        return modes

    def getDefaultDisplayMode(self):
        """Return the name of the default display mode. It must be defined in
        getDisplayModes."""
        return "Flat Lines"

    def setDisplayMode(self, mode):
        """Map the display mode defined in attach with those defined in
        getDisplayModes. Since they have the same names nothing needs to be
        done. This method is optional.

        Keyword arguments:
        mode -- Mode to be activated.
        """
        return mode

    def onChanged(self, vp, prop):
        """Detects the ship view provider data changes.

        Keyword arguments:
        vp -- View provider object affected.
        prop -- Modified property name.
        """
        pass

    def __getstate__(self):
        """When saving the document this object gets stored using Python's
        cPickle module. Since we have some un-pickable here (the Coin stuff)
        we must define this method to return a tuple of all pickable objects
        or None.
        """
        return None

    def __setstate__(self, state):
        """When restoring the pickled object from document we have the chance
        to set some internals here. Since no data were pickled nothing needs
        to be done here.
        """
        return None

    def getIcon(self):
        """Returns the icon for this kind of objects."""
        return os.path.join(os.path.dirname(__file__),
                            "resources/icons/",
                            "Ship_Weight.svg")
