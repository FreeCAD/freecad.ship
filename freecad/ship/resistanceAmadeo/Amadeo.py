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

def Lw_auto(L,V,prot):
    
    assert prot >= 0
    Lw = 1.11* V**(1/3) + 0.874*L - 2.56
    
    if prot > 0:
        
        Lw = Lw + prot
    
    return Lw    

def Sw_auto(L,V,prot):
    
    assert prot >= 0
    if prot == 0:
        Sw = 3.019*V**(2/3) +  0.602*V**(1/3)*L -1.734
    
    elif prot > 0:
        Sw = 4.420*V**(2/3) +  0.378*V**(1/3)*L -26.5
        
    return Sw
        

def Amadeo(L,B, T,Cb,V,u,prot=0,Sw='auto',Lw='auto',d=None,l=None):

    """ 
    Amadeo resistance prediction method.
    Positional parameters:
        
    L  -- Length between perpendiculars.
    B  -- Beam.
    T  -- Draft.
    Cb -- Block coefficient.
    V -- Displaced volume.
    u -- Speed. 
    
    
    keyword arguments
    
    Prot -- bow bulb length.
    Sw -- Wet surface.
    Lw -- Waterline length.
    D -- Ducted propeller diameter
    l -- Ducted propeller length
         
                """
                
    assert u >=0
    
    if u == 0:
        Rt = 0
        return Rt
    
    rho = 1025 # kg/m3 
    g = 9.81 # m/s2
    nu = 1.1892*10**-6  # m2/s
    
    Lw = Lw or 'auto'
    Sw = Sw or 'auto'
    
    if Lw == 'auto':
        Lw = Lw_auto(L, V, prot)
    
    if Sw == 'auto':
        Sw = Sw_auto(L, V, prot)

    """ Calculation of total wetted surface"""
    
    STCC = 0.1*L*T
    
    if d is not None and l is not None:
        
        STB = 1.13*math.pi*d**2*(l/d)/0.5
    
    else: 
        STB = 0
    
    STW = STB + Sw + STCC

    """ Calculation of resistance coefficients. """

        
    CA = (69 + 200*Cb*B/L - 0.26*L + 1300/L - 29.5*math.log10(L) + 17*(B/T) -(B/T)**2) *10 **(-5)
    Fn = u/(math.sqrt(g*L))
    RR = 1.24*Cb*B/L + 0.265* Fn**2 + 2.151*Fn - 0.298
        
    if prot==0:
           
        Rn = Lw*u/nu
        CF = 0.075/(math.log10(Rn) -2)**2
        CT = (CF + CA)/(1-RR)
        Rt = 0.5* rho* CT* STW* (u) **2 #N
           
    else:
           
        Rn = Lw*u/nu
        CF = 0.075/(math.log10(Rn)-2)**2
        Fnbb = u/(math.sqrt(g*prot))
        a = -47.3* Fnbb**3 + 292.7* Fnbb**2 - 579.7*Fnbb + 351.7
        b = 166.7* Fnbb**3 - 1037.6* Fnbb**2 + 2062.8*Fnbb - 1244.8
        DES = a* L/B + b
        RRcb = RR/(1 + DES/100)
        CT = (CF + CA)/(1-RRcb)
        Rt = 0.5*rho*CT*STW* (u) **2 #N
        
    return CA, Fn, Rn, CF, CT, Rt


if __name__== '__main__':
    
    import numpy as np
    import matplotlib.pyplot as plt
    
    
    L = 21.45
    Lw = 23.911
    B = 6.340
    T = 2.4 
    u = 0
    Cb = 0.22
    prot = 1.66
    V = 103.94
    Sw = 163.072
    l = 3
    d = 2
    
    vel = np.linspace (0.5144, 6.9444, num = 30)
    
    res = [Amadeo(L, B, T, Cb, V, u, prot, l, d) for u in vel]
    plt.plot (vel, res)
    plt.show ()
    

