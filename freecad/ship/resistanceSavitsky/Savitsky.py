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
from scipy.optimize import fsolve
import matplotlib.pyplot as plt
import warnings

# Avoid printing warnings type RuntimeWarning
warnings.filterwarnings("ignore", category=RuntimeWarning)

# Constants
rho = 1025  # Salt water density [kg/m3]
g = 9.81  # Gravity acceleration in Earth [m/s2]
nu = 1.1892 * 10 ** -6  # Salt water dynamic viscosity [m2/s]
kn_to_ms = 0.5144  # Conversion factor from knots to meters per second


def calculate_n(disp, trim_angle):
    return disp * g * np.cos(trim_angle)


def calculate_cv(v, g, b):
    return v/np.sqrt(g * b)


def calculate_cl_b(v, b, disp):
    return disp * g / (0.5 * rho * v**2 * b**2)


def equation_01(cl_0, deadrise_angle, cl_b):
    result = cl_b - cl_0 + 0.0065 * deadrise_angle * cl_0**0.6
    return result


def equation_02(lb_lambda, trim_angle, cv, cl_0):
    result = cl_0 - (np.degrees(trim_angle)**1.1) * (0.012 * lb_lambda**0.5 + 0.0055 * lb_lambda**2.5 / cv**2)
    return result


def calculate_cl_0d(lb_lambda, trim_angle):
    return 0.0120 * lb_lambda**0.5 * trim_angle**1.1


def calculate_cl_bd(cl_0d, deadrise_angle):
    return cl_0d - cl_0d**0.6 * deadrise_angle * 0.0065


def calculate_disp_d(rho, v, b, cl_bd):
    return 0.5 * rho * v**2 * b**2 * cl_bd / g


def calculate_pd(disp_d, lb_lambda, b, trim_angle):
    return disp_d * g / (lb_lambda * b**2 * np.cos(trim_angle))


def calculate_v_1(v, pd, rho):
    return v * (1 - 2 * pd / (rho * v**2))**0.5


def calculate_re_lambda(v_1, lb_lambda, b, nu):
    return v_1 * lb_lambda * b / nu


def calculate_cf_schoenherr(cf, re_lambda):
    result = 0.242 / np.sqrt(cf) - np.log10(cf * re_lambda)
    return result


def calculate_dfriction(cf, rho, v_1, lb_lambda, b, deadrise_angle):
    return cf * rho * v_1**2 * lb_lambda * b**2 * 0.5 / np.cos(np.radians(deadrise_angle))


def calculate_cpressure(dpressure, rho, v_1, lb_lambda, b):
    return dpressure / (rho * v_1**2 * lb_lambda * b**2 * 0.5)


def calculate_ctotal(drag, rho, v_1, lb_lambda, b):
    return drag / (rho * v_1**2 * lb_lambda * b**2 * 0.5)


def calculate_cp(cv, lb_lambda):
    return 0.75 - 1 / (5.21 * cv**2 / lb_lambda**2 + 2.39)


def equation_03(disp, lcg, n, cp, lb_lambda, b):
    return disp * g * lcg - n * cp * lb_lambda * b


def calculate_drag(disp, trim_angle, dfric):
    return disp * g * np.tan(trim_angle) + dfric / np.cos(trim_angle)


def savitsky(b, vmin, vmax, nspeeds, disp, deadrise_angle, lcg, trim_step, Sea_Margin, efficiency):
    tol = trim_step / 2.5
    trim_step = np.radians(trim_step)

    assert b > 0
    assert vmin > 0
    assert vmax > vmin
    assert nspeeds > 1
    assert disp > 0
    assert deadrise_angle > 0
    assert lcg > 0

    if trim_step < 0:
        trim_step = np.radians(0.01)

    # Units conversions
    vmin = vmin * kn_to_ms
    vmax = vmax * kn_to_ms
    disp = disp * 1e3

    speeds = np.linspace(vmin, vmax, nspeeds)
    drag = np.zeros(nspeeds, dtype=float)
    trims = np.zeros(nspeeds, dtype=float)
    lift = np.zeros(nspeeds, dtype=float)
    dfriction = np.zeros(nspeeds, dtype=float)
    dpressure = np.zeros(nspeeds, dtype=float)
    lam = np.zeros(nspeeds, dtype=float)
    reynolds = np.zeros(nspeeds, dtype=float)
    cfric = np.zeros(nspeeds, dtype=float)
    cpres = np.zeros(nspeeds, dtype=float)
    ctotal = np.zeros(nspeeds, dtype=float)
    speed = np.zeros(nspeeds, dtype=float)

    # Initialize variables to zero
    dfric, trim_angle, cl_b, cl_0, n, lb_lambda, lp, re_lambda, trim, cf \
        = None, None, None, None, None, None, None, None, None, None

    j = 0
    out_of_limits = False

    for i in range(nspeeds):
        v = speeds[i]

        trim_min = np.radians(2.0)
        trim_max = np.radians(15.0)
        trim_angles = np.arange(trim_min, trim_max, trim_step)

        for trim_angle in trim_angles:
            trim = np.rad2deg(trim_angle)  # Just convert the trim into degrees to plot it later
            n = calculate_n(disp, trim_angle)
            cv = calculate_cv(v, g, b)
            cl_b = calculate_cl_b(v, b, disp)

            cl_0 = fsolve(equation_01, np.array([0.1]), args=(deadrise_angle, cl_b))
            cl_0 = cl_0[0]
            lb_lambda = fsolve(equation_02, np.array([3]), args=(trim_angle, cv, cl_0))
            lb_lambda = lb_lambda[0]

            cl_0d = calculate_cl_0d(lb_lambda, trim_angle)
            cl_bd = calculate_cl_bd(cl_0d, deadrise_angle)
            disp_d = calculate_disp_d(rho, v, b, cl_bd)
            pd = calculate_pd(disp_d, lb_lambda, b, trim_angle)
            v_1 = calculate_v_1(v, pd, rho) * 0.99
            re_lambda = calculate_re_lambda(v_1, lb_lambda, b, nu)
            cf = fsolve(calculate_cf_schoenherr, np.array([0.001]), args=re_lambda)
            cf = cf[0] + 0.0004
            dfric = calculate_dfriction(cf, rho, v_1, lb_lambda, b, deadrise_angle)
            cp = calculate_cp(cv, lb_lambda)

            B = disp * g * lcg
            equilibrium = equation_03(disp, lcg, n, cp, lb_lambda, b)

            if np.rad2deg(trim_angle) > 14.980:
                out_of_limits = True
                print('WARNING: Could not get a solution for the maximum velocity introduced, it is out of limits!')
                break

            # Stop the iteration if the equilibrium is less than the set tolerance
            if abs(equilibrium) < tol * B:
                break

        if out_of_limits:
            break

        if cv >= 1:
            # Start saving results once inside equations application range
            drag[j] = calculate_drag(disp, trim_angle, dfric)
            dfriction[j] = dfric
            trims[j] = trim
            lift[j] = n
            dpressure[j] = disp * g * np.tan(trim_angle)
            lam[j] = lb_lambda
            reynolds[j] = re_lambda / 1000
            cfric[j] = cf
            cpres[j] = calculate_cpressure(dpressure[j], rho, v_1, lb_lambda, b)
            ctotal[j] = calculate_ctotal(drag[j], rho, v_1, lb_lambda, b)
            speed[j] = v

            j += 1

    # Trim vectors, deleting zeros
    drag = drag[:j]
    speed = speed[:j]
    trims = trims[:j]
    lift = lift[:j]
    dfriction = dfriction[:j]
    dpressure = dpressure[:j]
    lam = lam[:j]
    reynolds = reynolds[:j]
    cfric = cfric[:j]
    cpres = cpres[:j]
    ctotal = ctotal[:j]

    EKW = drag * speed * (1 + Sea_Margin)
    BKW = EKW / efficiency

    return drag, speed/kn_to_ms, trims, lift, dfriction, dpressure, lam, reynolds, cfric, cpres, ctotal, EKW, BKW


if __name__ == '__main__':

    # Example to test the code
    Vmin = 10                           # Min velocity [m/s]
    Vmax = 60                           # Max velocity [m/s]
    Nspeeds = 100                       # Number of speeds [-]
    B = 6.5                             # Beam [m]
    disp = 70                           # Displacement [kg]
    LCG = 10                            # Longitudinal center of gravity [m]
    Deadrise_angle = 20                 # Deadrise angle []

    trim_step = 0.01
    Sea_Margin = 0.15
    efficiency = 0.6

    drag, speeds, trims, lift, dfriction, dpressure, lam, rein, cfri, cpres, ctotal, EKW, BKW \
        = savitsky(B, Vmin, Vmax, Nspeeds, disp, Deadrise_angle, LCG, trim_step, Sea_Margin, efficiency)

    plt.plot(speeds, drag, label="Resistance", color="red")
    plt.xlim(left=0)
    plt.ylim(bottom=0)
    plt.xlabel("Speeds [kn]")
    plt.ylabel("Total resistance [kN]")
    plt.title("Savitsky Resistance")
    plt.legend()
    plt.grid()
    plt.show()
