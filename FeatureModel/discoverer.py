from abc import ABCMeta, abstractmethod

__author__ = "Jianfeng Chen"
__copyright__ = "Copyright (C) 2016 Jianfeng Chen"
__license__ = "MIT"
__version__ = "1.0"
__email__ = "jchen37@ncsu.edu"


"""
Abstract class to define the engine which is for feature model selection
"""


class Discoverer:
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self): pass

    @abstractmethod
    def gen_valid_one(self): pass
