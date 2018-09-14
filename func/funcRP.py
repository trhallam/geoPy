###############################################################################

# Author: Antony Hallam
# Company: HWU
# Date: 13-9-2018

# File Name: funcRP.py

# Synopsis:
# Functions for calculating rock physics properties and transforms.

###############################################################################

import numpy as np

def calcModVRH(fshale, shalemod, fnonshale, nonshalemod):
    '''
    This function calculates the voigh-reuss and vrh mix for a simple other/shale mix.
    :param fshale: fraction of material that is shale (0-1)
    :param shalemod: shale modulus (bulk or shear [K,mu])
    :param fnonshale: fraction of material that is not shale (0-1) (fshale+fnonshale <= 1)
    :param nonshalemod: non-shale modulus (bulk or shear [K,mu] to match shale mod.
    :return: mod_voigt, mod_reuss, mod_vrh
    '''
    mod_voigt = (fshale * shalemod) + (fnonshale * nonshalemod)
    mod_reuss = 1 / ((fshale / shalemod) + (fnonshale / nonshalemod))
    mod_vrh = 0.5 * (mod_voigt + mod_reuss)
    return mod_voigt, mod_reuss, mod_vrh

def calcDryFrame_dPres(erp_init,erp,mod_vrh,mod_E,mod_P,phi,c=[40,0,40,0,15]):
    """
    Calculates the dry rock frame for a given stress regieme and depth.
    :param erp_init: Effective Initial Reservoir Pressure (MPa) = Overburden Pressure - Initial Reservoir Pressure
    :param erp: Effective Current Reservoir Pressure (MPa) = Overburden Pressure - Current Reservoir Pressure
    :param mod_vrh: Voigt-Reuss mix for modulus (check this).
    :param mod_E: modulus stress sensitivity metric *2
    :param mod_P: modulus characteristic pressure constant *2
    :param phi: rock porosity
    :param c: critical porosity vector *1
    :return moddry: the dry-frame modulus for inputs

    References:
    [1] Amini and Alvarez (2014)
    [2] MacBeth (2004)
    """
    critphi = (c[0] + c[2]*phi) if phi <= c[4] else (c[2] + c[3]*phi)     #check critial porosity
    #Calcuate Bulk Modulus for Dry Frame
    dry1 = mod_vrh * (1 - phi / critphi)
    moddry = dry1 * (1 + (mod_E * np.exp(-erp_init / mod_P))) / (1 + (mod_E * np.exp(-erp / mod_P)))
    return moddry

def gassmann_dry2fluid(Kdry, K_vrh, Kfluid, phi):
    '''
    :param Kdry: Bulk modulus of the dry-frame.
    :param K_vrh: Modulus of voigt-reuss model.
    :param Kfluid: Bulk modulus of the fluid being placed in the dry frame.
    :param phi: Porosity of the material.
    :return: Kwet: Bulk modulus of the dry-frame saturated by fluid.
    '''
    return Kdry + ((1 - Kdry / K_vrh) ** 2) / ((phi / Kfluid) + ((1 - phi) / K_vrh) - (Kdry / (K_vrh ** 2)))

def mixfluid(water,oil,gas):
    '''
    Mixes three phase in the reservoir to calculate bulk modulus & density.
    :param water: list of length 3 bulkModulus, density, saturation
    :param oil: list of length 3 bulkModulus, density, saturation
    :param gas: list of length 3 bulkModulus, density, saturation
    :return:
    '''
    group = np.array([water,oil,gas])
    K =  1 / sum(group[:,2]/group[:,0]) #  k = 1 / (sum ( sat_i/k_i ))
    rho = sum(group[:,2]*group[:,1]) # rho = sum (sat_i*rho_i)
    #print('krho',K,rho)
    return K, rho

def calcVels(mu,rho):
    '''
    Calculates the S-wave velocity #TODO add units
    :param mu: The shear modulus
    :param rho: The material density
    :return: The shear wave velocity
    '''
    return np.sqrt(mu/rho)

def calcVelp(K,mu,rho):
    '''
    Calculates the P-wave velocity #TODO add units
    :param K: The saturated bulk modulus of the rock
    :param mu: The shear modulus
    :param rho: The material density
    :return: The pressure wave velocity
    '''
    return np.sqrt((K + (4 / 3) * mu) / rho)