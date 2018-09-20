###############################################################################

# Author: Antony Hallam
# Company: HWU
# Date: 15-9-2018

# File Name: funcRP.py

# Synopsis:
# Functions for calculating interface reflectivity of rocks.

###############################################################################

from numpy import sin, arcsin, cos, arccos, tan, degrees, radians, \
                  array, matmul, linalg, vectorize

def snellrr(thetai, vp1, vs1, vp2, vs2, units='radians'):
    '''
    Returns the reflected and refracted angles of an incident P-wave ray.
    :param thetai: P-wave angle of incidence for wavefront
    :param vp1, vs1, vp2, vs2: velocities for 2 halfspaces
    :keyword units: radians or degrees or deg2rad or rad2deg
    :return: returns a list of calculated angles using Snell's Law
                    thetai = input angle of P-wave incidence and output angle P-wave reflection
                    thetat = output angle of P-wave transmission
                    phir   = output angle of S-wave reflection
                    phit   = output angle of S-wave transmission
    '''
    if units in ['degrees', 'deg2rad']:
        out = [radians(thetai),0,0,0]
    elif units in ['radians', 'rad2deg']:
        out = [thetai,0,0,0]
    else:
        raise KeyError
    out[1] = arcsin((vp2*sin(out[0]))/vp1)
    out[2] = arcsin((vs1*sin(out[0]))/vp1)
    out[3] = arcsin((vs2*sin(out[0]))/vp1)
    if units in ['degrees','rad2deg']:
        return degrees(out).tolist()
    else:
        return out

def zoeppritzfull(thetai,vp1,vs1,rho1,vp2,vs2,rho2):
    '''
    CURRENTLY DOES NOT PREDICT AMP CORRECTLY
    Calculates the solution to the full Zoeppritz Matrix
    :param thetai: P-wave angle of incidence for wavefront in radians
    :param vp1, vs1, vp2, vs2: velocities for 2 halfspaces
    :param rho1, rho2: densities for 2 halfspaces
    :return: list [Rp, Rs, Tp, Ts] of amplitudes for reflected and transmitted rays
    '''
    ang = snellrr(thetai, vp1, vs1, vp2, vs2)
    c1 = vp1/vs1
    c2 = (rho2*vs2*vs2*vp1)/(rho1*vs1*vs1*vp2)
    c3 = (rho2*vs2*vp1)/(rho1*vs1*vs1)
    c4 = 1/c1
    c5 = (rho2*vp2)/(rho1*vp1)
    c6 = -1*(rho2*vs2)/(rho1*vp1)
    B = array([sin(thetai), cos(thetai), sin(2*thetai), cos(2*ang[2])])
    A = array([[  -sin(thetai),     -cos(ang[2]),      sin(ang[1]),      cos(ang[3])],
               [   cos(thetai),     -sin(ang[2]),      cos(ang[1]),     -sin(ang[3])],
               [ sin(2*thetai), c1*cos(2*ang[2]), c2*cos(2*ang[2]), c3*cos(2*ang[3])],
               [-cos(2*ang[2]), c4*sin(2*ang[2]), c5*cos(2*ang[3]), c6*sin(2*ang[3])]])
    return matmul(linalg.inv(A),B).tolist()

def zoeppritzPray(thetai,vp1,vs1,rho1,vp2,vs2,rho2):
    '''
    Calculates the solution to an incident down-going P-wave ray.
    :param thetai: P-wave angle of incidence for wavefront in radians
    :param vp1, vs1, vp2, vs2: velocities for 2 halfspaces
    :param rho1, rho2: densities for 2 halfspaces
    :return: list [Rp, Rs, Tp, Ts] of amplitudes for reflected and transmitted rays
    '''
    ang = snellrr(thetai, vp1, vs1, vp2, vs2)

    p = sin(thetai)/vp1; p2 = p*p
    a = rho2*(1-2*vs2**2*p2) - rho1*(1-2*vs1**2*p2)
    b = rho2*(1-2*vs2**2*p2) + 2*rho1*vs1**2*p2
    c = rho1*(1-2*vs1**2*p2) + 2*rho2*vs2**2*p2
    d = 2*(rho2*vs2**2 - rho1*vs1**2)
    E = b*cos(ang[0])/vp1 + c*cos(ang[1])/vp2
    F = b*cos(ang[2])/vs1 + c*cos(ang[3])/vs2
    G = a - d*cos(ang[0])/vp1*cos(ang[3])/vs2
    H = a - d*cos(ang[1])/vp2*cos(ang[2])/vs1
    D = E*F+G*H*p2

    PdPu = 1/D * ((b*cos(ang[0])/vp1-c*cos(ang[1])/vp2)*F - (a+d*cos(ang[0])/vp1*cos(ang[3])/vs2)*H*p2)
    PdPd = 2*rho1*cos(ang[0])/vp1 * F * vp1/(vp2*D)
    PdSu = -2 * cos(ang[0])/vp1 * (a*b + c*d*cos(ang[1])/vp2*cos(ang[3])/vs2)*p*vp1 / (vs2*D)
    PdSd = 2*rho1*cos(ang[0])/vp1 * H*p*vp1/ (vs2*D)

    return [PdPu, PdPd, PdSu, PdSd]


def calcreflp(vp1,vs1,rho1,vp2,vs2,rho2):
    '''
    Calculates the reflectivity parameters of an interface.
    :param vp1, vs1, vp2, vs2: velocities for 2 halfspaces
    :param rho1, rho2: densities for 2 halfspaces
    :return: list [rVp, rVs, rrho, rVsVp, dVp, dVs, drho]
    '''
    rVp = 0.5 * (vp1+vp2); rVs = 0.5 * (vs1+vs2)
    rrho = 0.5 * (rho1+rho2); rVsVp = rVs/rVp
    dVp = vp2-vp1; dVs = vs2-vs1; drho = rho2-rho1
    return [rVp, rVs, rrho, rVsVp, dVp, dVs, drho]

def bortfeld(theta,vp1,vs1,rho1,vp2,vs2,rho2):
    '''
    Calculates the solution to the full Bortfeld equations (1961)
    These are approximations which work well when the interval velocity is well defined.
    :param theta: P-wave angle of incidence for wavefront in radians
    :param vp1, vs1, vp2, vs2: velocities for 2 halfspaces
    :param rho1, rho2: densities for 2 halfspaces
    :return: Rp(theta) P-wave reflectivity of angle theta.
    '''
    rVp, rVs, rrho, rVsVp, dVp, dVs, drho = calcreflp(vp1,vs1,rho1,vp2,vs2,rho2)
    Rp = dVp/(2*rVp); Rrho = drho/(2*rrho); k=(2*rVs/rVp)**2
    R0 = Rp+Rrho; Rsh = 0.5*(dVp/rVp - k*drho/(2*rrho)-2*k*dVs/rVs)
    return R0+Rsh*sin(theta)**2.0+Rp*(tan(theta)**2)*(sin(theta)**2)

def akirichards(theta,vp1,vs1,rho1,vp2,vs2,rho2,method='avseth'):
    '''
    Aki-Richards forumlation of reflectivity functions.
    :param theta: P-wave angle of incidence for wavefront in radians
    :param vp1, vs1, vp2, vs2: velocities for 2 halfspaces
    :param rho1, rho2: densities for 2 halfspaces
    :param method: 'avseth' - avseth formulation or 'ar' - original aki-richards
    :return: Rp(theta)
    '''
    rVp, rVs, rrho, rVsVp, dVp, dVs, drho = calcreflp(vp1, vs1, rho1, vp2, vs2, rho2)
    ang = snellrr(theta, vp1, vs1, vp2, vs2)
    ang_Pavg = (ang[0]+ang[1])/2
    if method == 'avseth':
        W = 0.5*drho/rrho
        X = 2*rVs*rVs*drho / (vp1*vp1*rrho)
        Y = 0.5 * dVp / (rVp)
        Z = 4 * rVs * rVs * dVs / (vp1*vp1*rVs)
        return W - X*sin(theta)*sin(theta)+Y/(cos(ang_Pavg)*cos(ang_Pavg))-Z*sin(theta)*sin(theta)
    elif method =='ar':
        return 0.5*(dVp/rVp+drho/rrho)+0.5*(dVp/rVp-4*rVsVp*rVsVp*(drho/rrho+2*dVs/rVs))*theta*theta

def shuey(theta,vp1,vs1,rho1,vp2,vs2,rho2,mode='rtheta'):
    '''
    Shuey approximation to the Aki-Richards equations.
    :param theta: P-wave angle of incidence for wavefront in radians
    :param vp1, vs1, vp2, vs2: velocities for 2 halfspaces
    :param rho1, rho2: densities for 2 halfspaces
    :param mode: what to return 'rtheta' returns Rp(theta)
                                'R0_G'   returns [R0,G] aka [A,B]
    :return: Rp(theta)
    '''
    rVp, rVs, rrho, rVsVp, dVp, dVs, drho = calcreflp(vp1, vs1, rho1, vp2, vs2, rho2)
    R0 = 0.5 *(dVp/rVp+drho/rrho)
    G = 0.5 * dVp/rVp - 2. * (rVs*rVs)/(rVp*rVp)*(drho/rrho + 2.* dVs/rVs)
    if mode == 'rtheta':
        return R0 + G*sin(theta)*sin(theta)
    elif mode == 'R0_G':
        return [R0,G]

if __name__ == "__main__":
    from numpy import round
    from tests import test_title_msg, test_msg

    # test setup
    thetaid = 20       #degrees
    thetair = 0.349066 #radians
    vp1 = 3000; vs1 = 1800; rho1=2.4
    vp2 = 3500; vs2 = 2200; rho2=2.55

    test_title_msg("funcZoep")
    qcr_snellr_rad = [0.349066, 0.410452,  0.206680, 0.253522]
    qcr_snellr_deg = [20, 23.517147, 11.841915, 14.525731]
    act_snellr1 = round(snellrr(thetair,vp1,vs1,vp2,vs2),6)
    act_snellr2 = round(snellrr(thetair,vp1,vs1,vp2,vs2,units='rad2deg'),6)
    act_snellr3 = round(snellrr(thetaid,vp1,vs1,vp2,vs2,units='degrees'),6)
    act_snellr4 = round(snellrr(thetaid,vp1,vs1,vp2,vs2,units='deg2rad'),6)

    test_msg('snellr',"radians : output='radians'",act_snellr1,qcr_snellr_rad)
    test_msg('snellr',"deg2rad : output='rad2deg'",act_snellr1,qcr_snellr_rad)
    test_msg('snellr',"degrees : output='degrees'",act_snellr1,qcr_snellr_rad)
    test_msg('snellr',"rad2deg : output='deg2rad'",act_snellr1,qcr_snellr_rad)

    test_title_msg("zoeppritzfull")
    qcr_zoeppritzfull = [0.065510, -0.152313, 0.884692, -0.142204]
    act_zoeppritzfull = round(zoeppritzfull(thetair,vp1,vs1,rho1,vp2,vs2,rho2),6)
    test_msg('zoeppritzfull','full zoeppritz equation',act_zoeppritzfull,qcr_zoeppritzfull)

    test_title_msg("zoeppritzPray")
    qcr_zoeppritzPray = [0.077261, 0.901362, -0.076451, -0.085402]
    act_zoeppritzPray = round(zoeppritzPray(thetair,vp1,vs1,rho1,vp2,vs2,rho2),6)
    test_msg('zoeppritzPray','all parameters',act_zoeppritzPray,qcr_zoeppritzPray)

    test_title_msg("calcreflp")
    qcr_calcreflp = [3250.000000, 2000.000000, 2.475000, 0.615385, 500.000000, 400.000000, 0.150000]
    act_calcreflp = round(calcreflp(vp1,vs1,rho1,vp2,vs2,rho2),6)
    test_msg('calcreflp','',act_calcreflp,qcr_calcreflp)

    test_title_msg("bortfeld")
    qcr_bortfeld = 0.07929219225650763
    act_bortfeld = bortfeld(thetair,vp1,vs1,rho1,vp2,vs2,rho2)
    test_msg("bortfeld","",act_bortfeld,qcr_bortfeld)

    test_title_msg("akirichards")
    qcr_akirichards_avseth = 0.07158654420684037
    qcr_akirichards_ar = 0.07409121930516233
    act_akirichards_avseth = akirichards(thetair,vp1,vs1,rho1,vp2,vs2,rho2)
    act_akirichards_ar = akirichards(thetair,vp1,vs1,rho1,vp2,vs2,rho2,method='ar')
    test_msg('akirichards','avseth method',act_akirichards_avseth,qcr_akirichards_avseth)
    test_msg('akirichards','ar method',act_akirichards_ar,qcr_akirichards_ar)

    test_title_msg('shuey')
    qcr_shuey_rtheta = 0.07541534075276615
    act_shuey_rtheta = shuey(thetair,vp1,vs1,rho1,vp2,vs2,rho2)
    qcr_shuey_r0_g = [0.10722610722610722, -0.27193831809216423]
    act_shuey_r0_g = shuey(thetair,vp1,vs1,rho1,vp2,vs2,rho2,mode='R0_G')
    test_msg('shuey','mode=rtheta',act_shuey_rtheta,qcr_shuey_rtheta)
    test_msg('shuey','mode=R0_G',act_shuey_r0_g,qcr_shuey_r0_g)