###############################################################################

# Author: Antony Hallam
# Company: HWU
# Date: 11-9-2018

# File Name: dataTests.py

# Synopsis:
# Runs tests on classes and functions from data.

###############################################################################

from data import structLith

nonshale = structLith.structMineral('nonshale',70,35,2.74)
shale = structLith.structMineral('shale',15,5,2.68)
#oil, water, gas
fluid = structLith.structFluid('fluid',[0.636,2.96,0.017],[0.686,1.056,0.145],[0.54,0.09,0.37])
fluid.mixfluids()

dryrock = structLith.structDryFrame('rock',nonshale,shale,0.05,0.2)
dryrock.calcRockMatrix()
dryrock.calcDryFrame(1*3.281*6.89476/1000,3180,12,12,0.45,15,0.75,16)

rock = structLith.structRock(dryrock,fluid)
rock.calcGassmann()
rock.calcDensity()
rock.calcElastic()