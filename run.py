import os,sys
currentpath = os.path.dirname(os.path.abspath(__file__))
GALEpath   = currentpath+'/GALE/'
parserpath = currentpath+'/parser/'
datapath   = currentpath+'/feature_tree_data/'
for x in [currentpath,GALEpath,datapath]:
    if x not in sys.path: sys.path.insert(0,x)

from GALE import *
from BinGALE import *
from model import *
from problem import *
from Feature_tree import *
from parser import *

import pdb,traceback,random
import numpy as np

###############################################
# ENTRANCE OF TESTING AND RUNNING THE PROJECT #
# python run.py -***                          #
###############################################
eis = None
spldata = None

def main_gale_with_spl(model,modelName):
    bing = BinGALE(eis)
    b = bing.gale()

if __name__ == '__main__':
    rungale = True
    model, modelName = './feature_tree_data/cellphone.xml','cell phone'
    for i,arg in enumerate(sys.argv):
        if arg == '-cellphone' or arg == '-s':
            model, modelName = './feature_tree_data/cellphone.xml','cell phone'
        if arg == '-eshop' or arg == '-XL':
            model, modelName = './feature_tree_data/eshop.xml', 'eshop'
        if arg == '-webportal':
            model, modelName = './feature_tree_data/Web_portal_FM.xml', 'web portal'
        if arg == '-eis':
            model, modelName = './feature_tree_data/EIS.xml', 'eis'
        if arg == '-nogale':
            rungale = False
        if arg == '-data':
            spldata = './input/'+argv[i+1]
        if arg == '-clear':
            pattern = "*.pyc"
            for root, dirs, files in os.walk(GALEpath):
                for file in filter(lambda x: re.match(pattern, x), files):
                    os.remove(os.path.join(root, file))
            os._exit(0)
    try:
        eis = FTModel(model, modelName)
        if spldata == None: spldata = './input/modelName'
        
        if rungale: main_gale_with_spl()
        print 'end of running~~~~~'
        pdb.set_trace()
    except:
        type, value, tb = sys.exc_info()
        traceback.print_exc()
        pdb.post_mortem(tb)
