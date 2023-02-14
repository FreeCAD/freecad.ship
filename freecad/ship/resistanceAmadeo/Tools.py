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
import random
from FreeCAD import Vector, Rotation, Matrix, Placement
import Part
from FreeCAD import Units
import FreeCAD as App
try:
    import FreeCADGui as Gui
except ImportError:
    pass
from .. import Instance
from ..shipUtils import Math
import numpy as np


DENS = Units.parseQuantity("1025 kg/m^3")  # Salt water
GRA = Units.parqueQuantity("9.81 m/s^2")
COMMON_BOOLEAN_ITERATIONS = 10

def Lw_auto(L,Vdespl,prot):
    
    Lw = 1.11* Vdespl**(1/3) + 0.874*L - 2.56
    
    if prot > 0:
        
        Lw = Lw + prot
    
    return Lw    

def Sw_auto(L,Vdespl,prot):
    
    if prot == 0:
        Sw = 3.019*Vdespl**(2/3) +  0.602*Vdespl**(1/3)*L -1.734
    
    elif prot > 0:
        Sw = 4.420*Vdespl**(2/3) +  0.378*Vdespl**(1/3)*L -26.5
        

def Amadeo(L,Lw,B,T,Cb,prot,Vdespl,maxs,mins,n,Sw,D,l):

    """ 
    Amadeo resistance prediction method.
    Amadeo arguments: 
    
    L  -- Length between perpendiculars.
    Lw -- Waterline length.
    B  -- Beam.
    T  -- draft.
    Cb -- Block coefficient.
    Prot -- bow bulb length.
    Vdespl -- Displaced volume.
    Smax -- Maximum speed. 
    Smin -- Minimum speed.   
    n -- number of speeds. 
    Sw -- Wet surface.
    D -- Ducted propeller diameter
    l -- Ducted propeller length """
    
    Lw = Lw or 'auto'
    Sw = Sw or 'auto'
    
    if Lw == 'auto':
        Lw = Lw_auto(L, Vdespl, prot)
    
    if Sw == 'auto':
        Sw = Sw_auto(L, Vdespl, prot)

    rho = 1025 # t/m3 
    g = 9.81 # m/s2
    nu = 1.1892*10**-6  # m2/s
    
    CAA = []
    CFF = []
    
    """ Calculation of total wetted surface"""
    STCC = 0.1*L*T
    
    STB = 1.13*math.pi*D**2*(l/D)/0.5
    
    STW = STB + Sw + STCC

    """ Make a list of speeds in knot"""
    
    vel = np.linspace (mins, maxs, (n-1))
         
    """ Calculation of resistance coefficients. """
    
    RT = []    
    RN = []
    FNB = []
    A = []
    BB = []
    des = []

    for v in vel:
        
        CA = (69 + 200*Cb*B/L - 0.26*L + 1300/L - 29.5*math.log10(L) + 17*(B/T) -(B/T)**2) *10 **(-5)
        CAA.append(CA)
        Fn = v*0.5144/(math.sqrt(g*L))
        RR = 1.24*Cb*B/L + 0.265* Fn**2 + 2.151*Fn - 0.298
        
        if prot==0:
           
           Rn = Lw*v*0.5144/nu
           RN.append (Rn)
           CF = 0.075/(math.log10(Rn) -2) **2
           CFF.append(CF)
           CT = (CF + CA)/(1-RR)
           Rt = 0.5* rho* CT* STW* (v*0.5144) **2
           RT.append(Rt)
           
        else:
           
           Rn = (Lw)*v*0.5144/nu
           RN.append (Rn)
           CF = 0.075/(math.log10(Rn)-2)**2
           CFF.append(CF)
           Fnbb = v*0.5144/(math.sqrt(g*prot))
           FNB.append (Fnbb)
           a = -47.3* Fnbb**3 + 292.7* Fnbb**2 - 579.7*Fnbb + 351.7
           A.append(a)
           b = 166.7* Fnbb**3 - 1037.6* Fnbb**2 + 2062.8*Fnbb - 1244.8
           BB.append(b)
           DES = a* L/B + b
           des.append(DES)
           RRcb = RR/(1 + DES/100)
           CT = (CF + CA)/(1-RRcb)
           Rt = 0.5*rho*CT*STW* (v*0.5144) **2
           RT.append(Rt)


    return RT


if __name__== '__main__':
    
    import matplotlib.pyplot as plt
    
    
    L = 21.45
    Lw = 23.911
    B = 6.340
    T = 2.4 
    Cb = 0.22
    prot = 1.66
    Vdespl = 103.94
    maxs = 13.5
    mins = 3
    n = 21
    Sw = 163.072
    l = 0
    D = 1
    
    vel = np.linspace (mins, maxs, (n-1))
    
    res = Amadeo(L, Lw, B, T, Cb, prot, Vdespl, maxs, mins, n, Sw, D, l)
    plt.plot (vel, res)
    plt.show ()
    

