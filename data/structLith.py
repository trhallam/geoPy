###############################################################################

# Author: Antony Hallam
# Company: HWU
# Date: 11-9-2018

# File Name: structLith.py

# Synopsis:
# RPT for 1D modelling.

###############################################################################

from func.funcAVOModels import calcRandNorm, calcAVO
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

    def __init__(self, name, bulkmod, rho, sat):
        """
        :param name: string to use for the name of the fluid.
        :param bulkmod: bulkModulus of the fluid/s (GPa)
        :param rho: density of the fluid/s (g/cc)
        :param sat: saturations of the fluid/s (should add to 1).
        """
        self.name = name
        self.Ks = bulkmod
        self.rhos = rho
        self.sats = sat
        self.mixfluids()

    def mixfluids(self):
        self.K = 0;
        self.rho = 0;  # reset bulk and density of mixed fluid
        for (flK, fld, fsat) in zip(self.Ks, self.rhos, self.sats):
            self.K = fsat / flK + self.K
            self.rho = self.rho + fsat * fld
        self.K = 1.0 / self.K

    def updateSat(self, sat):
        self.sats = sat; self.mixfluids()


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
        self.c1 = 0.3521;
        self.c2 = 0;
        self.c3 = 0.3521;
        self.c4 = 0;
        self.c5 = 0.1499;
        self.fracshale = self.vshale / (1. - self.phi)  # fraction rock shale
        self.fracnonshale = (1. - self.vshale - self.phi) / (1. - self.phi)  # fraction rock not shale
        self.rho = self.fracshale*self.shale.den + self.fracnonshale*self.nonshale.den

    def calcRockMatrix(self):
        self.Km_voigt = (self.fracshale * self.shale.K) + (self.fracnonshale * self.nonshale.K);
        self.Km_reuss = 1 / ((self.fracshale / self.shale.K) + (self.fracnonshale / self.nonshale.K));
        self.Km_vrh = 0.5 * (self.Km_voigt + self.Km_reuss);

        self.Gm_voigt = self.fracshale * self.shale.Mu + self.fracnonshale * self.nonshale.Mu;
        self.Gm_reuss = 1 / (self.fracshale / self.shale.Mu + self.fracnonshale / self.nonshale.Mu);
        self.Gm_vrh = 0.5 * (self.Gm_voigt + self.Gm_reuss);

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

        #check critial porosity
        if self.phi <= self.c5:
            self.critphi = self.c1 + self.c2*self.phi
        else:
            self.critphi = self.c3 + self.c4*self.phi

        #Calcuate Bulk Modulus for Dry Frame
        Kdry1 = self.Km_vrh * (1 - self.phi / self.critphi)
        self.Kdry = Kdry1 * (1 + (Ek * np.exp(-self.peffi / Pk))) / (1 + (Ek * np.exp(-self.peff / Pk)))

        Gdry1 = self.Gm_vrh * (1 - self.phi / self.critphi)
        self.Gdry = Gdry1 * (1 + (Eg * np.exp(-self.peffi / Pg))) / (1 + (Eg * np.exp(-self.peff / Pg)))

    def calcKSat(self,fluidK):
        return self.Kdry + ((1 - self.Kdry / self.Km_vrh) ** 2) / (
                    (self.phi / fluidK) + ((1 - self.phi) / self.Km_vrh) - (self.Kdry / (self.Km_vrh ** 2)))

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
        self.vels = np.sqrt(self.dryFrame.Gdry / self.den);
        self.velp = np.sqrt((self.Ksat + (4 / 3) * self.dryFrame.Gdry) / self.den);
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
