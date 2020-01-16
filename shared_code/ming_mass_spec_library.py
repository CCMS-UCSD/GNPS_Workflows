#!/usr/bin/python


"""
Mass Spec Utilties

These classes provide utilities for mass spec data

"""


#Assume exact_mass is a float
#Adduct is a string
def get_adduct_mass(exact_mass, adduct):
    M = exact_mass

    if adduct == 'M':
        return M, 1

    if adduct == ('M+3H'):
        return M/3 + 1.007276, 3

    if adduct == ('M+2H+Na'):
        return M/3 + 8.334590, 3

    if adduct == ('M+H+2Na'):
        return M/3 + 15.7661904, 3

    if adduct == ('M+3Na'):
        return M/3 + 22.989218, 3

    if adduct == ('M+2H'):
        return M/2 + 1.007276, 2

    if adduct == ('M+H+NH4'):
        return M/2 + 9.520550, 2

    if adduct == ('M+H+Na'):
        return M/2 + 11.998247, 2

    if adduct == ('M+H+K'):
        return M/2 + 19.985217, 2

    if adduct == ('M+ACN+2H'):
        return M/2 + 21.520550, 2

    if adduct == ('M+2Na'):
        return M/2 + 22.989218, 2

    if adduct == ('M+2ACN+2H'):
        return M/2 + 42.033823, 2

    if adduct == ('M+3ACN+2H'):
        return M/2 + 62.547097, 2

    if adduct == ('M+H'):
        return M + 1.007276, 1

    if adduct == ('M+H-H2O'):
        return M + 19.01839 + 1.007276 + 1.007276, 1

    if adduct == ('M+NH4'):
        return M + 18.033823, 1

    if adduct == ('M+Na'):
        return M + 22.989218, 1

    if adduct == ('M+CH3OH+H'):
        return M + 33.033489, 1

    if adduct == ('M+K'):
        return M + 38.963158, 1

    if adduct == ('M+ACN+H'):
        return M + 42.033823, 1

    if adduct == ('M+2Na-H'):
        return M + 44.971160, 1

    if adduct == ('M+IsoProp+H'):
        return M + 61.06534, 1

    if adduct == ('M+ACN+Na'):
        return M + 64.015765, 1

    if adduct == ('M+2K-H'):
        return M + 76.919040, 1

    if adduct == ('M+DMSO+H'):
        return M + 79.02122, 1

    if adduct == ('M+2ACN+H'):
        return M + 83.060370, 1

    if adduct == ('M+IsoProp+Na+H'):
        return M + 84.05511, 1

    if adduct == ('2M+H'):
        return 2*M + 1.007276, 1

    if adduct == ('2M+NH4'):
        return 2*M + 18.033823, 1

    if adduct == ('2M+Na'):
        return 2*M + 22.989218, 1

    if adduct == ('2M+K'):
        return 2*M + 38.963158, 1

    if adduct == ('2M+ACN+H'):
        return 2*M + 42.033823, 1

    if adduct == ('2M+ACN+Na'):
        return 2*M + 64.015765, 1

    if adduct == ('M-H2O+H'):
        return M - 17.00384, 1

    if adduct == ('M-3H'):
        return M/3 - 1.007276, -3

    if adduct == ('M-2H'):
        return M/2 - 1.007276, -2

    if adduct == ('M-H2O-H'):
        return M - 19.01839, -1

    if adduct == ('M-H'):
        return M - 1.007276, -1

    if adduct == ('M+Na-2H'):
        return M + 20.974666, -2

    if adduct == ('M+Cl'):
        return M + 34.969402, 1

    if adduct == ('M+K-2H'):
        return M + 36.948606, -2

    if adduct == ('M+FA-H'):
        return M + 44.998201, -1

    if adduct == ('M+Hac-H'):
        return M + 59.013851, -1

    if adduct == ('M+Br'):
        return M + 78.918885, 1

    if adduct == ('M+TFA-H'):
        return M + 112.985586, -1

    if adduct == ('2M-H'):
        return 2*M - 1.007276, -1

    if adduct == ('2M+FA-H'):
        return 2*M + 44.998201, -1

    if adduct == ('2M+Hac-H'):
        return 2*M + 59.013851, -1

    if adduct == ('3M-H'):
        return 3*M - 1.007276, -1

    if adduct == ('M-2H2O+H'):
        return M + 1.007276 - 2*18.01057, 1

    if adduct == ('2M-2H+Na'):
        return M*2 - 1.007276 *2 + 22.989218, -1
    if adduct == ('2M-2H+K'):
        return M*2 - 1.007276 *2 + 38.963158, -1

    print("something else! " + adduct)
    return exact_mass, 0
