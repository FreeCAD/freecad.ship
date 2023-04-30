# ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2011, 2016 Jose Luis Cercos Pita <jlcercos@gmail.com>   *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)    *
# *   as published by the Free Software Foundation; either version 2 of     *
# *   the License, or (at your option) any later version.                   *
# *   for detail see the LICENCE text file.                                 *
# *                                                                         *
# *   This program is distributed in the hope that it will be useful,       *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU Library General Public License for more details.                  *
# *                                                                         *
# *   You should have received a copy of the GNU Library General Public     *
# *   License along with this program; if not, write to the Free Software   *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *   USA                                                                   *
# *                                                                         *
# ***************************************************************************

import numpy as np

def Lw_auto(L ,V ,prot):
    
    assert prot >= 0
    Lw = 1.11* V ** (1/3) + 0.874 * L - 2.56
    
    if prot > 0:
        
        Lw = Lw + prot
        
    return Lw

def Sw_auto(L ,V ,prot):
    
    assert prot >= 0
    if prot == 0:
        Sw = 3.019*V**(2/3) +  0.602*V**(1/3)*L -1.734
    
    elif prot > 0:
        Sw = 4.420*V**(2/3) +  0.378*V**(1/3)*L -26.5
        
    return Sw
        
def Amadeo(L,B, T,Cb,V,u, prot=0,Sw='auto',Lw='auto',d=None,
           l=None, has_rudder = False):

    """ 
    Amadeo resistance prediction method.
    Positional parameters:
        
    L  -- Length between perpendiculars.
    B  -- Beam.
    T  -- draft.
    Cb -- Block coefficient.
    V -- Displaced volume.
    u -- speed. 
    
    keyword arguments:
    
    Prot -- bow bulb length.
    Sw -- Wet surface
    Lw -- Waterline length.
    D -- Ducted propeller diameter
    l -- Ducted propeller length
    
    Returns: 
    
    Rt -- total resistance in kN
    uu -- speeds higher than 0 m/s
    CF -- Friction coefficient
    CA -- Roughness coefficient
    CR -- residual resistance coefficient
    CT -- Total resistance coefficient
                """
    rho = 1025 # kg/m3 
    g = 9.81 # m/s2
    nu = 1.1892*10**-6  # m2/s
    
    assert np.all (u >= 0)
    valid_u_mask = u > 0
    uu = u[valid_u_mask]
    Rt = np.zeros(len(uu), dtype= float)
    CF = np.zeros(len(uu), dtype= float)
    CA = np.zeros(len(uu), dtype= float)
    CR = np.zeros(len(uu), dtype= float)
    CT = np.zeros(len(uu), dtype= float)
    

    Lw = Lw or 'auto'
    Sw = Sw or 'auto'
    
    if Lw == 'auto':
        Lw = Lw_auto(L, V, prot)

    if Sw == 'auto':
        Sw = Sw_auto(L, V, prot)

    """ Calculation of total wetted surface"""
    
    STCC = 0.1*L*T if has_rudder else 0.0
    
    if d is not None and l is not None:
        
        STB = 1.13*np.pi*d**2*(l/d)/0.5
    
    else: 
        STB = 0

    STW = STB + Sw + STCC

    """ Calculation of resistance coefficients. """

    Ca = (69 + 200 * Cb * B / L - 0.26 * L + 1300 / L - 29.5 * np.log10(L) 
          + 17 * B / T - (B / T)**2) * 10 ** -5
    Fn = uu / (np.sqrt(g * L))
    RR = 1.24 * Cb * B / L + 0.265 * Fn**2 + 2.151 * Fn - 0.298
    CA = np.linspace(Ca, Ca, len(uu))
    
    if prot==0:
           
        Rn = Lw * uu / nu
        CF = 0.075 / (np.log10(Rn) - 2) **2
        CT = (CF + Ca) / (1 - RR)
        CR = CT * RR
        Rt = 0.5 * rho * CT * STW * uu ** 2 / 1000 #kN

    else:
           
        Rn = Lw * uu / nu
        CF = 0.075 / (np.log10(Rn) - 2) ** 2
        Fnbb = uu / (np.sqrt( g * prot))
        a = -47.3 * Fnbb**3 + 292.7 * Fnbb**2 - 579.7 * Fnbb + 351.7
        b = 166.7 * Fnbb**3 - 1037.6 * Fnbb**2 + 2062.8 * Fnbb - 1244.8
        DES = a * L / B + b
        RRcb = RR /(1 + DES / 100)
        CT = (CF + Ca)/(1 - RRcb)
        CR = CT * RRcb
        Rt = 0.5 * rho * CT * STW * uu ** 2 / 1000 #kN

    return Rt, uu, CF, CA, CR, CT

if __name__== '__main__':

    import matplotlib.pyplot as plt
    
    L = 21.42
    Lw = 22.498
    B = 6.34
    T = 2.52
    Cb = 0.233
    prot = 0.98
    V = 103.369
    Sw = ()

    vel = np.linspace (0, 6.1728, num = 13)

    Resistencia, velocidades, Cfric, Crug ,Cresidual ,CTotal = Amadeo(L, B,
                                                    T, Cb, V, vel, prot,Sw,Lw)
    print(Resistencia, velocidades, Cfric, Crug ,Cresidual ,CTotal)
    
    plt.plot (velocidades , Resistencia)
    plt.xlabel("V [m/s]")
    plt.ylabel("Resistencia total [kN]")
    plt.show ()