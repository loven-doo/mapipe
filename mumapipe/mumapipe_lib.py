import sys
import re
import multiprocessing as mp

from mapipe.tools._inner_tools import _config_parser, _parse_cmd_args, _define_gf_or_ind, _gff_to_gtf
from mapipe import get_counts, index_genome
from mapipe.constants import DEFAULT_CONFIG


def run_mapipe(srr_list, srr_downloads_dir, genome_fasta_or_indices, gff, config_path=DEFAULT_CONFIG, threads=4, *args):
    config = _config_parser(config_path)
    genome_or_ind = _define_gf_or_ind(genome_fasta_or_indices)
    try:
        genome_indices = genome_or_ind['genome_indices']
    except KeyError:
        try:
            genome_indices = index_genome(genome_fasta=genome_or_ind['genome_fasta'],
                                          config_path=config_path, conf=config)
        except KeyError:
            print "No genome or genome indices file were in input"
            raise KeyError
    if gff[-3:] != "gtf":
        gtf = _gff_to_gtf(gff, config.get('HTSeq', 'gffread_exec'))
        gff = None
        gff = gtf
    task_thr = max(int(config.get('Trimmomatic', 'threads')), int(config.get('STAR', 'threads')))
    args_list = []
    srr_list_read = _read_srr_list_file(srr_list)
    for srr in srr_list_read:
        args_dict = {
            'srr': srr,
            'srr_downloads_dir': srr_downloads_dir,
            'genome_fasta_or_indices': genome_indices,
            'gff': gff,
            'config_path': config_path
        }
        args_list.append(args_dict)
    n_workers = int(threads)/task_thr
    if n_workers < 1:
        n_workers = 1
    pool = mp.Pool(n_workers)
    result = pool.map(_worker, args_list)
    pool.close()
    pool.join()

def _read_srr_list_file(f):
    srr_list_r = []
    read = open(f)
    for lines in read:
        line = None
        line = lines.strip()
        if len(line) == 0:
            continue
        line_list = re.findall(r"[\w']+", line)
        srr_list_r = srr_list_r + _new_line(line_list)
    return srr_list_r

def _new_line(l):
    srr_l = []
    for elms in l:
        elm = None
        elm = elms.strip(" .,;:/|_-\t\\")
        if len(elm) == 0:
            continue
        srr_l.append(elm)
    return srr_l

def _worker(kwargs):
    get_counts(**kwargs)


def main():
    args = _parse_cmd_args(sys.argv[1:], 1)
    run_mapipe(*args)
