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
from FreeCAD import Vector, Matrix, Placement
import Part
from FreeCAD import Units
import numpy as np
import capytaine as cpt
from capytaine.meshes.meshes import Mesh as cptMesh
from scipy.linalg import block_diag
from ..shipGZ import Tools as GZ
from ..shipHydrostatics import Tools as Hydrostatics
from ..shipSinkAndTrim import Tools as Equilibrium
from ..shipUtils import LoadCondition


DIRS = np.linspace(0.0, 2.0 * np.pi, num=36, endpoint=False)
DOFS = ['Roll', 'Pitch', 'Yaw', 'Surge', 'Sway', 'Heave']


def freecad_mesh_to_captain(mesh,
                            draft=Units.Quantity(0, Units.Length),
                            trim=Units.Quantity(0, Units.Angle)):
    """Convert a FreeCAD mesh into a capytaine one"""
    verts = []
    a = trim.getValueAs('rad').Value
    R = np.array([[np.cos(a),  0, np.sin(a)],
                  [0,          1, 0        ],
                  [-np.sin(a), 0, np.cos(a)]])
    for p in mesh.Mesh.Points:
        vert = [Units.Quantity(p.x, Units.Length).getValueAs('m').Value,
                Units.Quantity(p.y, Units.Length).getValueAs('m').Value,
                Units.Quantity(p.z, Units.Length).getValueAs('m').Value]
        vert = np.dot(R, vert)
        vert[2] -= draft.getValueAs('m').Value
        verts.append(vert)
    faces = []
    for f in mesh.Mesh.Facets:
        face = list(f.PointIndices)
        if len(face) == 3:
            # Triangles are supported by means of repeating the first and last
            # points
            face.append(face[0]) 
        faces.append(face)
    return cptMesh(vertices=verts, faces=faces, name=mesh.Name)


def equilibrium_data(lc, ship, weights, tanks):
    """Compute the hydrostatic stiffnes matrix

    Position arguments
    lc -- Load condition
    ship -- The ship data
    """
    group, draft, trim, disp, objs = Equilibrium.compute(
        lc, fs_ref=False, doc=lc.Document)
    # Collect the COG and B
    COG = App.Vector(objs['COG'].Shape.X,
                     objs['COG'].Shape.Y,
                     objs['COG'].Shape.Z)
    B = App.Vector(objs['B'].Shape.X,
                   objs['B'].Shape.Y,
                   objs['B'].Shape.Z)
    xcb = Units.Quantity(B.x, Units.Length)
    ycb = Units.Quantity(B.y, Units.Length)
    zcb = Units.Quantity(B.z, Units.Length)
    zcg = Units.Quantity(COG.z, Units.Length)

    # Remove the temporal objects
    doc = group.Document
    group.removeObjectsFromDocument()
    doc.removeObject(group.Name)
    doc.recompute()

    # Compute the inertia (without tanks)
    I = LoadCondition.weights_inertia(lc)
    a = trim.getValueAs('rad').Value
    R = np.array([[np.cos(a),  0, np.sin(a)],
                  [0,          1, 0        ],
                  [-np.sin(a), 0, np.cos(a)]])
    RT = np.transpose(R)
    I = R @ I @ RT

    # Compute the hydrostatic stiffness matrix
    wpa, _, wp = Hydrostatics.floatingArea(ship, draft=draft, trim=trim)
    rhog = GZ.DENS * GZ.G
    k33 = (rhog * wpa).getValueAs('N/m').Value
    k34 = k43 = k33 * ycb.getValueAs('m').Value
    k35 = k53 = k33 * xcb.getValueAs('m').Value
    k45 = k54 = k33 * ycb.getValueAs('m').Value * xcb.getValueAs('m').Value
    i_unit = (Units.Quantity(1, Units.Length)**4).Unit
    Ixx = Units.Quantity(wp.MatrixOfInertia.A11, i_unit)
    Iyy = Units.Quantity(wp.MatrixOfInertia.A11, i_unit)
    kr = (rhog * Ixx).getValueAs('N*m').Value
    kp = (rhog * Iyy).getValueAs('N*m').Value
    kw = (disp * GZ.G * (zcb - zcg)).getValueAs('N*m').Value
    k44 = kw + kr + k33 * (ycb.getValueAs('m').Value**2)
    k55 = kw + kp + k33 * (xcb.getValueAs('m').Value**2)
    K = [[k33, k34, k35],
         [k43, k44, k45],
         [k53, k54, k55]]

    m = disp.getValueAs('kg').Value

    return block_diag(m, m, m, I), block_diag(0, 0, K, 0), draft, trim
    

def generate_boat(lc, ship, weights, tanks, mesh):
    M, kHS, draft, trim = equilibrium_data(lc, ship, weights, tanks)

    boat = cpt.FloatingBody(mesh=freecad_mesh_to_captain(mesh, draft, trim),
                            name=lc.Name)
    boat.add_all_rigid_body_dofs()
    boat.keep_immersed_part()
    boat.mass = boat.add_dofs_labels_to_matrix(M)
    boat.hydrostatic_stiffness = boat.add_dofs_labels_to_matrix(kHS)

    return boat


def simulation(lc, ship, weights, tanks, mesh, omegas):
    body = generate_boat(lc, ship, weights, tanks, mesh)

    problems = []
    for omega in omegas:
        for dof in body.dofs:
            problems.append(cpt.RadiationProblem(omega=omega,
                                                 body=body,
                                                 radiating_dof=dof))
        for d in DIRS:
            problems.append(cpt.DiffractionProblem(omega=omega,
                                                   body=body,
                                                   wave_direction=d))
    return problems


def solve_sim(sims, omegas):
    """Solve for all the directions of a single period
    """
    bem_solver = cpt.BEMSolver()
    i_sim = 0
    for j, omega in enumerate(omegas):
        radiation = [
            bem_solver.solve(sims[i_sim + i]) for i in range(len(DOFS))]
        i_sim += len(DOFS)
        for i, d in enumerate(DIRS):
            results = radiation[:]
            results.append(bem_solver.solve(sims[i_sim]))
            i_sim += 1
            dataset = cpt.assemble_dataset(results)
            yield i, j, cpt.post_pro.rao(dataset, wave_direction=d)
    """
    bem_solver = cpt.BEMSolver()
    results = [bem_solver.solve(problem) for problem in sims]
    dataset = cpt.assemble_dataset(results)
    for i,d in enumerate(DIRS):
        dataset['RAO_{}'.format(i)] = cpt.post_pro.rao(dataset,
                                                       wave_direction=d)
    return dataset
    """
