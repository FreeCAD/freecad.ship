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


def Sw_auto(B, T, Lw, Cb, Cw, Cm, ABT):
    Sw = (Lw * (2 * T + B) * np.sqrt(Cm) * (0.453 + 0.4425 * Cb
                - 0.2862 * Cm - 0.003467 * (B / T) + 0.3696 * Cw)
                                            + 2.38 * (ABT / Cb))
    return Sw
        

def Holtrop(B, T, Lw, V, Cb, Cm, Cw, cstern, iE, xcb, u, hb, etap, 
            seamargin, Sapplist, ABT, AT, Sw='auto'):

    """
    Holtrop resistance prediction method.
    Positional parameters:
        
    B  -- Beam.
    T  -- draft.
    Lw -- Waterline length.
    V -- Displaced volume.
    Cb -- Block coefficient.
    Cm -- Midship-section coefficient.
    Cw -- Waterplane coefficient.
    Cstern -- Coefficient related to the specic shape of the afterbody.
    iE -- Half angle of entrance.
    xcb -- Longitudinal position of the center of buoyancy.
    u -- speed.
    hb -- position of the center of the transverse area ABT above the keel line
    etap -- Propulsive coefficient.
    seamargin -- sea margin to calculate EKW and BKW
    Sapplist -- List of appendage' areas.
    ABT -- Transverlse bulb area.
    AT -- Inmersed part of the transverse area of the transom.
    
    keyword arguments:

    Sw -- Wet surface

    Returns:
    
    Rt -- Total resistance in kN.
    uu -- Speeds higher than 0 m/s.
    CT -- Total resistance coefficient.
    CF -- Frictional resistance coefficient.
    CAPP -- Appendage resistance coefficient.
    CW -- Wave resistance coefficient.
    CB -- Additional resistance coefficient due to the presence of a bulbous
                                                        bow near the surface.
    CTR -- Additional resistance coefficient due to the inmersed transom.
    CA -- Model-ship correlation resistance coefficient.
                """
    rho = 1025 # kg/m3 
    g = 9.81 # m/s2
    nu = 1.1892*10**-6  # m2/s
    Cp = Cb / Cm
    
    assert T > 0
    assert Lw > 0
    assert Cm > 0
    assert B > 0
    assert V > 0
    assert np.all(u >= 0)
    valid_u_mask = u > 0
    uu = u[valid_u_mask]
    
    Rt = np.zeros(len(uu), dtype=float)
    RF = np.zeros(len(uu), dtype=float)
    RAPP = np.zeros(len(uu), dtype=float)
    RW = np.zeros(len(uu), dtype=float)
    RB = np.zeros(len(uu), dtype=float)
    RTR = np.zeros(len(uu), dtype=float)
    RA = np.zeros(len(uu), dtype=float)
    CT = np.zeros(len(uu), dtype=float)
    CAPP = np.zeros(len(uu), dtype=float)
    CB = np.zeros(len(uu), dtype=float)
    CTR = np.zeros(len(uu), dtype=float)
    
    Sw = Sw or 'auto'

    if Sw == 'auto':
        Sw = Sw_auto(B, T, Lw, Cb, Cw, Cm, ABT)
        
    """Frictional resistance"""

    Rn = Lw * uu / nu
    CF = 0.075 / (np.log10(Rn) - 2) ** 2
    RF = 1 / 2 * rho * uu ** 2 * CF * Sw / 1000 #kN

    """Form factor"""
    
    Lr = Lw * (1 - Cp + (0.06 * Cp * xcb) / (4 * Cp - 1))
    
    if cstern == 0: c13 = 0.89
    elif cstern == 1: c13 = 1
    elif cstern == 2: c13 = 1.11
    
    k1_1 = (0.93 + 0.487118 * c13 * (B / Lw) ** 1.06806 * (T / Lw) ** 0.46106 *
    (Lw / Lr) ** 0.121563 * (Lw ** 3 / V) ** 0.36486 * (1 - Cp) ** (-0.604247))
    
    """Appendance resistance"""
    
    k2values = [1.7, 1.5, 2.8, 3.0, 1.7, 3.0, 2.0, 3.0, 2.8, 2.7, 1.4]
    sumk2 = 0
    sumsapp = 0
    for i in range(0, 10):
        
        k2 = 0 if Sapplist[i] == 0 else k2values[i] * Sapplist[i]
        sumk2 = sumk2 + k2
        sumsapp = sumsapp + Sapplist[i]
    try:
        k2eq = sumk2 / sumsapp
        
    except ZeroDivisionError:
        k2eq = 0.0

    RAPP = 1 / 2 * rho * uu ** 2 * k2eq * sumsapp * CF / 1000 #kN
    
    if k2eq != 0:
        
        CAPP = RAPP * 1000 / (1 / 2 * rho * sumsapp * uu ** 2)
        
    """Wave resistance"""
    
    Fn = uu / (np.sqrt(g * Lw))
    
    ratioB = B / Lw
    
    if ratioB <= 0.11: c7 = 0.229577 * ratioB ** 0.33333
    elif ratioB >= 0.25: c7 = 0.5 - 0.0625 * (1 / ratioB)
    elif 0.11 < ratioB < 0.25: c7 = ratioB
    
    c1 = 2223105 * c7 ** 3.78613 * (T / B) ** 1.07961 * (90 - iE) ** (-1.37565)
    
    c3 = 0.56 * ABT ** 1.5 / (B * T * (0.31 * np.sqrt(ABT) + T - hb))
    
    c2 = np.exp(-1.89 * np.sqrt(c3))
    
    c5 = 1 - (0.8 * AT) / (B * T * Cm)
   
    c17 = (6919.3 * Cm ** (- 1.3346) * (V / Lw ** 3) ** 2.00977 *
                                           ((Lw / B) - 2) ** 1.40692)
    
    c16 = 1.73014 - 0.7067 * Cp if Cp >= 0.8 else (8.07981 * Cp - 13.8673 *
                                                 Cp ** 2 + 6.984388 * Cp ** 3)
    
    ratioLw = Lw ** 3 / V
    if ratioLw <= 512: c15 = -1.69385
    elif ratioLw >= 1727: c15 = 0.0
    elif 512 < ratioLw < 1727: c15 = (-1.69385 + ((Lw / (V ** (1 / 3))) - 8.0) 
                                                                      / 2.36)
    
    m1 = (0.0140407 * (Lw / T) - (1.75254 * V ** (1 / 3)) / Lw - 4.79323 *
                                                              (B / Lw) - c16)
    
    m3 = -7.2035 * (B / Lw) ** 0.326869 * (T / B) ** 0.605375
    
    m4 = c15 * 0.4 * np.exp(- 0.034 * Fn ** (- 3.29))
    
    if (1 / ratioB) >= 12: lamda = 1.446 * Cp - 0.36
    if (1 / ratioB) < 12: lamda = 1.446 * Cp - 0.03 * (Lw / B)
        
    l = len(Fn) - 1
    for i in (0, l):
        
        if Fn[i] <= 0.4:
            RW = (c1 * c2 * c5 * V * rho * g * np.exp(m1 *
                    Fn ** (- 0.9) + m4 * np.cos(lamda * Fn ** (- 2)))) / 1000
            
        if Fn[i] >= 0.5: RW = (c17 * c2 * c5 * V * rho * g * np.exp(m3 * 
                    Fn ** (- 0.9)  + m4 * np.cos(lamda * Fn ** (- 2)))) / 1000
    
        if 0.4 < Fn[i] < 0.55: 
            Rwa = (c1 * c2 * c5 * V * rho * g * np.exp(m1 * 0.4 ** (-0.9)
                                        + m4 * np.cos(lamda * 6.25))) / 1000
                         
            Rwb = (c17 * c2 * c5 * V * rho * g * np.exp(m3 * 0.55 ** (- 0.9)
                                 + m4 * np.cos(lamda * 0.55 ** (- 2)))) / 1000       
        
            RW = Rwa + (10 * Fn - 4) * ((Rwb - Rwa) / 1.5) #kN
        
    Cw = RW * 1000 / (1 / 2 * rho * Sw * uu ** 2)
    """Aditional resistance due to the presence of a bulbous"""

    if ABT != 0:
    
         Pb = 0.56 * np.sqrt(ABT) / (T - 1.5 * hb)
         
         Fni = (uu / (np.sqrt(g * (T - hb - 0.25 * np.sqrt(ABT))) + 0.15 *
                                                                      uu ** 2))
         
         RB = ((0.11 * np.exp(-3 * Pb ** (-2)) * Fni ** 3 * ABT ** 1.5 * g *
                                    rho) / (1 + Fni ** 2)) * 1 / 1000 #kN

         CB = RB * 1000 / (1 / 2 * rho * ABT * uu ** 2)
    
    """Aditional resistance due to the inmnersed transom"""
    
    if AT != 0:

        Fnt = uu / (np.sqrt((2 * g * AT) / (B + B * Cw)))
        l2 = len(Fnt) - 1
        for i in (0,l2):
            
            c6 = 0 if Fnt[i] >= 5  else 0.2 * (1 - 0.2 * Fnt[i])

        RTR = 1 / 2 * rho * uu ** 2 * AT * c6 / 1000 #kN 
        CTR = RTR * 1000 / (1 / 2 * rho * AT * uu ** 2)
    
    """Correlation resistance"""
    
    ratioT = T / Lw
    c4 = 0.04 if ratioT >= 0.04 else ratioT
    
    Ca = (0.006 * (Lw + 100) ** (-0.16) - 0.00205 + 0.003 * np.sqrt(Lw / 7.5)
                                              * Cb ** 4 * c2 * (0.04 - c4))
    
    RA = 1 / 2 * rho * uu ** 2 * Sw * Ca / 1000 #kN
    CA = np.linspace(Ca, Ca, len(uu))
    """Total resistance."""

    CT = CF + CAPP + Cw + CB + CTR + CA
    Rt = RF * k1_1 + RAPP + RW + RB + RTR + RA

    EKW = Rt * uu * (1 + seamargin)
    BKW = EKW / etap
    
    return Rt, uu, CT, CF, CAPP, Cw, CB, CTR, CA, EKW, BKW, Sw

    
if __name__ == '__main__':

    import matplotlib.pyplot as plt

    Lw = 44.879
    B = 10
    T = 4
    V = 1007.8
    Cb = 0.566
    Cm = 0.9345
    Cw = 0.6733
    cstern = 1
    iE = 28
    xcb = -0.7645
    hb = 2.127
    etap = 0.6
    seamargin = 0.15
    Sapplist = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    ABT = 2.372
    AT = 0
    Sw = 572.547

    speeds = np.linspace(1.5432, 5.6584, num=9)

    Rtotal, uu, CT, CF, CAPP, Cw, CB, CTR, CA, EKW, BKW, Sw = Holtrop(B,
        T, Lw, V, Cb, Cm, Cw, cstern, iE, xcb, speeds, hb, etap, seamargin,
        Sapplist, ABT, AT, Sw)
    
    plt.plot(uu, Rtotal)
    plt.xlabel("Speeds [m/s]")
    plt.ylabel("Total resistance [kN]")
    plt.show()
    
    plt.plot(uu, EKW)
    plt.xlabel("Speeds [m/s]")
    plt.ylabel("Efective power [kW]")
    plt.show()