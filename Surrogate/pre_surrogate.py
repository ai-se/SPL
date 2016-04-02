import pdb
from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from FeatureModel.ftmodel import FTModel

__author__ = "Jianfeng Chen"
__copyright__ = "Copyright (C) 2016 Jianfeng Chen"
__license__ = "MIT"
__version__ = "1.0"
__email__ = "jchen37@ncsu.edu"


def write_random_individuals(name, num_of_individuals=100, contain_non_leaf=False):
    ft_model = FTModel(name, num_of_attached_objs=2, setConVioAsObj=True)
    cans = [ft_model.genRandomCan('v2') for _ in range(num_of_individuals)]
    map(ft_model.eval, cans)
    # write the candidates to folder surrogate_testing
    spl_addr = [i for i in sys.path if i.endswith('SPL')][0]
    with open(spl_addr+'/surrogate_data/' + name + '.raw', 'w+') as f:
        if contain_non_leaf:
            dec_head = ['>' + i.id for i in ft_model.ft.features]
        else:
            dec_head = ['>' + i.name for i in ft_model.dec]
        obj_head = ['$' + i.name for i in ft_model.obj]
        head = ','.join(dec_head) + ',' + ','.join(obj_head)
        f.write(head)
        f.write('\n')
        for can in cans:
            if contain_non_leaf:
                f.write(','.join(map(str, can.fulfill)))
            else:
                f.write(','.join(map(str, can.decs)))
            f.write(',')
            f.write(','.join(map(str, can.scores)))
            f.write('\n')

if __name__ == '__main__':
    try:
        write_random_individuals('eis', 100, contain_non_leaf=True)
    except:
        type, value, tb = sys.exc_info()
        # traceback.print_exc()
        # pdb.post_mortem(tb)
