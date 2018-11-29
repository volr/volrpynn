"""
A module for error functions and their derivatives
"""
import abc
import numpy
import volrpynn.activation

def sum_squared_error(output, labels):
    return ((output.T - labels) ** 2).T