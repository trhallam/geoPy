###############################################################################

# Author: Antony Hallam
# Company: HWU
# Date: 15-9-2018

# File Name: funcRP.py

# Synopsis:
# Functions for calculating interface reflectivity of rocks.

###############################################################################

from numpy import sin, arcsin, cos, arccos, tan, \
                  array, degrees, radians, matmul,linalg

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

def bortfeld(thetai,vp1,vs1,rho1,vp2,vs2,rho2):
    '''
    Calculates the solution to the full Bortfeld equations (1961)
    These are approximations which work well when the interval velocity is well defined.
    :param thetai: P-wave angle of incidence for wavefront in radians
    :param vp1, vs1, vp2, vs2: velocities for 2 halfspaces
    :param rho1, rho2: densities for 2 halfspaces
    :return: list [Rp, Rs, Tp, Ts] of amplitudes for reflected and transmitted rays
    '''
    rVp, rVs, rrho, rVsVp, dVp, dVs, drho = calcreflp(vp1,vs1,rho1,vp2,vs2,rho2)
    Rp = dVp/(2*rVp); Rrho = drho/(2*rrho); k=(2*rVs/rVp)**2
    R0 = Rp+Rrho; Rsh = 0.5*(dVp/rVp - k*drho/(2*rrho)-2*k*dVs/rVs)
    return R0+Rsh*sin(thetai)**2.0+Rp*(tan(thetai)**2)*(sin(thetai)**2)

if __name__ == "__main__":
    from numpy import round, array_equal

    def test_func(act,qcr):
        if array_equal(act,qcr):
            print('passed')
        else:
            print('failed')
            print('Expected:'); print(qcr)
            print('Output:'); print(act)

    def test_msg(fname, test_description, act, qcr):
        msg = 'test: '+fname+' - '+test_description+" "
        dots = (74-len(msg)%80)*"."
        print(msg,dots,end=" ")
        test_func(act, qcr)

    def test_title_msg(fname):
        print("##### unittest "+fname)

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

    test_title_msg("calcreflp")
    qcr_calcreflp = [3250.000000, 2000.000000, 2.475000, 0.615385, 500.000000, 400.000000, 0.150000]
    act_calcreflp = round(calcreflp(vp1,vs1,rho1,vp2,vs2,rho2),6)
    test_msg('calcreflp','',act_calcreflp,qcr_calcreflp)

    test_title_msg("bortfeld")
    qcr_bortfeld = 0.07929219225650763
    act_bortfeld = bortfeld(thetair,vp1,vs1,rho1,vp2,vs2,rho2)
    test_msg("bortfeld","",act_bortfeld,qcr_bortfeld)