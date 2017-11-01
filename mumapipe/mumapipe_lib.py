import sys
import multiprocessing as mp

from mapipe.tools._inner_tools import _config_parser, _parse_cmd_args
from mapipe import get_counts, index_genome
from mapipe.constants import DEFAULT_CONFIG


def run_mapipe(srr_list, srr_downloads_dir, genome_or_ind, gff, config_path=DEFAULT_CONFIG, threads=4, *args):
    config = _config_parser(config_path)
    try:
        genome_or_ind['genome_indices']
    except KeyError:
        try:
            g_ind = index_genome(genome=genome_or_ind['genome_fasta'], conf_path=config_path, conf=config)
            genome_or_ind = {'genome_indices': g_ind}
        except KeyError:
            print "No genome or genome indices file were in input"
            raise KeyError
    task_thr = max(int(config['Trimmomatic']['threads']), int(config['STAR']['threads']))
    args_list = []
    srr_list_read = open(srr_list)
    for srr in srr_list_read:
        args_dict = {
            'srr': srr,
            'srr_downloads_dir': srr_downloads_dir,
            'genome_or_ind': genome_or_ind,
            'gff': gff,
            'config_path': config_path
        }
        args_list.append(args_dict)
    pool = mp.Pool(int(threads)/task_thr)
    result = pool.map(_worker, args_list)
    pool.close()
    pool.join()


def _worker(kwargs):
    run_mapipe(**kwargs)


def main():
    args = _parse_cmd_args(sys.argv[-1:], 1)
    run_mapipe(*args)
