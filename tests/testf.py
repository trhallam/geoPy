###############################################################################

# Author: Antony Hallam
# Company: HWU
# Date: 16-9-2018

# File Name: testf.py

# Synopsis:
# Contains default functions for testing data.

###############################################################################

from numpy import array_equal

def test_func(act, qcr):
    if array_equal(act, qcr):
        print('passed')
    else:
        print('failed')
        print('Expected:');
        print(qcr)
        print('Output:');
        print(act)


def test_msg(fname, test_description, act, qcr):
    msg = 'test: ' + fname + ' - ' + test_description + " "
    dots = (74 - len(msg) % 80) * "."
    print(msg, dots, end=" ")
    test_func(act, qcr)


def test_title_msg(fname):
    print("##### unittest " + fname)