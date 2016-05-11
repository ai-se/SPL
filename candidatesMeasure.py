from tools.pareto import eps_sort
from tools.hv import HyperVolume

__author__ = "Jianfeng Chen"
__copyright__ = "Copyright (C) 2016 Jianfeng Chen"
__license__ = "MIT"
__version__ = "1.0"
__email__ = "jchen37@ncsu.edu"


hyper_volume = None  # hyper-volume object


def analysis_cans(candidate_lst, all_non_dominated=True):
    """
    all candidates must be evaluated
    :param candidate_lst:
    :param all_non_dominated:
    :returns candidate_hyper_volume
    """

    def _safety_check(i):
        assert hasattr(i, 'fitness'), "ERROR! Candidates must be evaluated"
    map(_safety_check, candidate_lst)

    objs = [tuple(c.fitness) for c in candidate_lst]
    if not all_non_dominated:
        front = eps_sort(objs)
    else:
        front = objs

    n = len(objs[0])
    global hyper_volume
    if not hyper_volume or len(hyper_volume.referencePoint) != n:
        hyper_volume = HyperVolume([1] * n)

    cans_hv = hyper_volume.compute(front)

    return cans_hv
