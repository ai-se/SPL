import os,sys
import glob
currentpath= os.path.dirname(os.path.abspath(__file__))
GALEpath   = currentpath+'/GALE/'
parserpath = currentpath+'/parser/'
datapath   = currentpath+'/feature_tree_data/'
inputpath  = currentpath+'/input/'
toolspath  = currentpath+'/tools/'
for x in [currentpath, GALEpath, datapath, toolspath]:
    if x not in sys.path: sys.path.insert(0,x)

from GALE import *
from BinGALE import *
from model import *
from problem import *
from Feature_tree import *
from result_stat import *
from parser import *

import pdb,traceback,random
import numpy as np

###############################################
# ENTRANCE TO TESTING AND RUNNING THE PROJECT #
# python run.py -***                          #
###############################################
ftm = None
spldata = None

def clear():
   junkType = ['pyc','cost']
   for x in os.walk(currentpath):
       path = x[0]
       if '.' in path: continue
       for type in junkType:
           for junk in glob.glob(path+'/*.'+type):
               print junk +' moved'
               os.remove(junk)

def main_gale_with_spl(ftm,np):
    if np:
        bing = BinGALE(ftm,np)
    else:
        bing = BinGALE(ftm)
    b = bing.gale()

if __name__ == '__main__':
    rungale = True
    model, modelName = './feature_tree_data/cellphone.xml','cell phone'
    np = None
    for i,arg in enumerate(sys.argv):
        if arg in ['-cellphone', '-S']:
            model, modelName = './feature_tree_data/cellphone.xml','cell phone'
        if arg in ['-webportal', '-M']:
            model, modelName = './feature_tree_data/Web_portal_FM.xml', 'web portal'
        if arg in ['-eis', '-L']:
            model, modelName = './feature_tree_data/EIS.xml', 'eis'
        if arg in ['-eshop', '-XL']:
            model, modelName = './feature_tree_data/eshop.xml', 'eshop'
        if arg in ['-nogale', '-ng']:
            rungale = False
        if arg == '-data':
            spldata = currentpath+'/input/'+sys.argv[i+1]+'.cost'
        if arg == '-np':
            np = int(sys.argv[i+1])
        if arg in ['-clear','-clean']:
            clear()
            os._exit(0)
    try:
        if spldata == None: spldata = currentpath+'/input/'+modelName.replace(" ","")+'.cost'
        ftm = FTModel(model, modelName,spldata)
        ftm.printModelInfo()
        if rungale: main_gale_with_spl(ftm, np)
        print 'end of running~~~~~'
        pdb.set_trace()
    except:
        type, value, tb = sys.exc_info()
        traceback.print_exc()
        pdb.post_mortem(tb)
