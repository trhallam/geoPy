###############################################################################

# Author: Antony Hallam
# Company: HWU
# Date: 11-9-2018

# File Name: structLith.py

# Synopsis:
# RPT for 1D modelling.

###############################################################################

from func.funcAVOModels import calcRandNorm, calcAVO
from func.funcRP import calcModVRH, calcDryFrame_dPres, gassmann_dry2fluid, mixfluid, calcVelp, calcVels
import numpy as np
import copy


class structMineral(object):
    """
    This class is used to represent and model mineral properties.
    """

    def __init__(self, name, bulkmod, shearMod, rho):
        """
        Initiate bulk mineral properties.
        bulkmod - bulk Modulus K (GPa)
        shearMod - shear Modulus Mu (GPa)
        rho - mineral density (g/cc)
        """
        self.name = name
        self.K = bulkmod
        self.Mu = shearMod
        self.den = rho


class structFluid(object):
    """
    This class is used to represent and model fluid properties.
    """

    def __init__(self, name, water=[2.96,1.056,0.5], oil=[0.636,0.686,0.25], gas=[0.017,0.145,0.25]):
        """
        :param name: string to use for the name of the fluid.
        :keyword water: list of bulkModulus, density, saturation
        :keyword oil: list of bulkModulus, density, saturation
        :keyword gas: list of bulkModulus, density, saturation
        Units: bulkModulus in GPa, density in (g/cc), saturation in frac where the sum of 3 phases should add to 1).
        """
        self.name = name     #fluid name
        self.water = water; self.oil = oil; self.gas = gas
        self.K = 0           #mixed fluid bulk modulus
        self.rho = 0         #mixed fluid density
        self.mixfluids()     #calcuate mixed fluid properties

    def getKs(self):
        return [self.water[0],self.oil[0],self.gas[0]]

    def getRhos(self):
        return [self.water[1],self.oil[1],self.gas[1]]

    def getSats(self):
        return [self.water[2],self.oil[2],self.gas[2]]

    def mixfluids(self):
        self.K, self.rho = mixfluid(self.water,self.oil,self.gas)

    def updateSat(self, sat):
        self.water[2] = sat[0]; self.oil[2] = sat[1]; self.gas[2] = sat[2]
        self.mixfluids()


class structDryFrame(object):
    """
    This class is used to represent dry frames of mixed structMinerals.
    """

    def __init__(self, name, nonshale, shale, vshale, phi):
        """
        :param name: Name of the rock
        :param nonshale: takes arguments of type structMineral
        :param shale: takes arguments of type structMineral
        :param vshale: the fraction of volume shale
        :param phi: porosity of the rock
        """
        self.name = name
        self.nonshale = nonshale;
        self.shale = shale;
        self.vshale = vshale
        self.phi = phi
        # define critical porosity values in fractions.
        self.c = [0.3521, 0, 0.3521, 0, 0.1499]
        self.fracshale = self.vshale / (1. - self.phi)  # fraction rock shale
        self.fracnonshale = (1. - self.vshale - self.phi) / (1. - self.phi)  # fraction rock not shale
        self.rho = self.fracshale*self.shale.den + self.fracnonshale*self.nonshale.den

    def calcRockMatrix(self): #calculate the voigt-reuss bounds
        self.Km_voigt, self.Km_reuss, self.Km_vrh = calcModVRH(self.fracshale, self.shale.K,
                                                               self.fracnonshale, self.nonshale.K)
        self.Gm_voigt, self.Gm_reuss, self.Gm_vrh = calcModVRH(self.fracshale, self.shale.Mu,
                                                               self.fracnonshale, self.nonshale.Mu)

    def calcDryFrame(self,vsgrad,depth,initp,resp,Ek,Pk,Eg,Pg):
        """
        Calculates the dry rock frame for a given stress regieme and depth.
        :param vsgrad: vertical stress gradient in MPa/m
        :param depth: Depth for calculation (meters TVDSS) be careful for deep water.
        :param initp: Initial Reservoir Pressure (MPa)
        :param resp: Current Reservoir Pressure (MPa)
        """
        self.vsgrad = vsgrad; self.depth = depth;
        self.initp = initp; self.resp=resp
        self.vstress = vsgrad*depth
        self.peffi = self.vstress - initp #effective initial pressure
        self.peff = self.vstress - resp   #effective current pressure
        self.mod = [Ek,Pk,Eg,Pg]

        self.Kdry = calcDryFrame_dPres(self.peffi,self.peff,self.Km_vrh,Ek,Pk,self.phi,c=self.c)
        self.Gdry = calcDryFrame_dPres(self.peffi,self.peff,self.Gm_vrh,Eg,Pg,self.phi,c=self.c)

    def calcKSat(self,fluidK):
        return gassmann_dry2fluid(self.Kdry,self.Km_vrh,fluidK,self.phi)

    def updatePres(self,newresp):
        self.calcDryFrame(self.vsgrad,self.depth,self.initp,newresp,*self.mod)

class structRock(object):
    """
    This class combines the fundamentals to build rocks.
    """
    def __init__(self,dryFrame,fluid):
        """
        Input a populated structDryFrame and structFluid
        :param dryFrame:
        :param fluid:
        """
        self.dryFrame = dryFrame; self.fluid=fluid

    def calcGassmann(self):
        self.Ksat = self.dryFrame.calcKSat(self.fluid.K)

    def calcDensity(self):
        self.den = self.dryFrame.rho + self.fluid.rho*self.dryFrame.phi

    def calcElastic(self):
        self.vels = calcVels(self.dryFrame.Gdry, self.den)
        self.velp = calcVelp(self.Ksat, self.dryFrame.Gdry, self.den);
        self.pimp = self.velp * self.den;
        self.simp = self.vels * self.den;
        self.vpvs = self.velp / self.vels;

class structLith(object):
    """ 
    This class is used to represent and deal with tops/interval logs.
    """

    def __init__(self, name, colour, Vp, Vs, Rho, VpStd, VsStd, RhoStd):
        "Initiate lithology properties."
        self.name = name
        self.colour = colour
        self.Vp = Vp  # P-wave velocity
        self.Vs = Vs  # S-wave velocity
        self.Rho = Rho  # Density
        self.AI = Vp * Rho  # Acoustic Impedance
        self.SI = Vs * Rho  # Shear Impedance
        self.VPVS = Vp / Vs  # VpVs Ratio

        self.VpStd = VpStd
        self.VsStd = VsStd
        self.RhoStd = RhoStd

    def calcModel(self, nsims, std, var):
        self.nsims = nsims
        self.var = var
        self.mSdt = std

        self.seed = np.random.rand(nsims)
        self.VpMod = calcRandNorm(self.Vp, self.VpStd * std, self.seed, var)
        self.VsMod = calcRandNorm(self.Vs, self.VsStd * std, self.seed, var)
        self.RhoMod = calcRandNorm(self.Rho, self.RhoStd * std, self.seed, var)
        self.AIMod = self.VpMod * self.RhoMod
        self.SIMod = self.VsMod * self.RhoMod
        self.VPVSMod = self.VpMod / self.VsMod
        self.lmrMod = self.AIMod * self.AIMod - 2 * self.SIMod * self.SIMod
        self.murMod = self.SIMod * self.SIMod


class structAVOMod(object):

    def __init__(self, lith1, lith2, nsims, std, var, colour):
        self.topName = lith1.name
        self.botName = lith2.name
        self.name = self.topName + " on " + self.botName
        self.colour = colour
        self.topMod = copy.deepcopy(lith1)
        self.botMod = copy.deepcopy(lith2)

        self.topMod.calcModel(nsims, std, var)
        self.botMod.calcModel(nsims, std, var)

        self.AVOMod = calcAVO(self.topMod.VpMod, self.botMod.VpMod,
                              self.topMod.VsMod, self.botMod.VsMod,
                              self.topMod.RhoMod, self.botMod.RhoMod)

        # others to follow as required
