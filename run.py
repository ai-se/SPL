import os
import sys
import glob
import pdb
import traceback
from GALE.BinGALE import BinGALE
from FeatureModel.ftmodel import FTModel


current_path = os.path.dirname(os.path.abspath(__file__))

###############################################
# ENTRANCE TO TESTING AND RUNNING THE PROJECT #
# python run.py -***                          #
###############################################
ftm = None
spl_data = None


def clear():
    junk_type = ['pyc', 'cost', 'raw', 'dot', 'time', 'png']
    for x in os.walk(current_path):
        path = x[0]
        if '.' in path:
            continue
        for type in junk_type:
            for junk in glob.glob(path+'/*.'+type):
                if 'surrogate_data' not in junk and 'png' in junk:
                    continue  # avoid deleting the pictures in report
                print junk + ' moved'
                os.remove(junk)


def main_gale_with_spl(ftm, np):
    if np:
        bing = BinGALE(ftm, np)
    else:
        bing = BinGALE(ftm)
    b = bing.gale()


if __name__ == '__main__':
    rungale = True
    model, modelName = './feature_tree_data/cellphone.xml','cell phone'
    np = None
    for i, arg in enumerate(sys.argv):
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
            spl_data = current_path + '/input/' + sys.argv[i + 1] + '.cost'
        if arg == '-np':
            np = int(sys.argv[i+1])
        if arg in ['-clear', '-clean', '-cls']:
            clear()
            os._exit(0)
        if arg == '-nodebug':
            pdb.set_trace = pdb.set_trace = lambda: None
    try:
        if spl_data == None: spl_data = current_path + '/input/' + modelName.replace(" ", "") + '.cost'
        ftm = FTModel(model, modelName, spl_data)
        ftm.printModelInfo()
        if rungale: main_gale_with_spl(ftm, np)
        print 'end of running~~~~~'
        pdb.set_trace()
    except:
        type, value, tb = sys.exc_info()
        traceback.print_exc()
        pdb.post_mortem(tb)
