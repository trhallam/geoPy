# -*- coding: utf-8 -*-
'''
###############################################################################

# Author: Antony Hallam
# Company: Origin Energy
# Date: 4-8-2016

# File Name: setup.py

# Synopsis:
# Installion and stand alone Orange App for owprobability.

# Calling:
# 

###############################################################################
'''

from setuptools import setup

setup(name="Probability",
      packages=["owprobability"],
      package_data={"owprobability": ["icons/*.svg"]},
      classifiers=["Example :: Invalid"],
      # Declare owprobability package to contain widgets for the "Probability" category
      entry_points={"orange.widgets": "Probability = owprobability"},
      )