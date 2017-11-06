import argparse
import ConfigParser
import os
import subprocess

from mapipe.constants import DEFAULT_CONFIG


def _parse_cmd_args(args, multi=None):
    parser = argparse.ArgumentParser()
    if not multi:
        parser.add_argument(
            '-r',
            '--srr',
            help="The SRR id for the reads",
            required=True,
            action='store'
    )
    parser.add_argument(
        '-d',
        '--srr_downloads_dir',
        default='srr_downloads',
        help="The name of directory where reads should be downloaded",
        required=True,
        action='store'
    )
    parser.add_argument(
        '-g',
        '--genome_fasta',
        help="Fasta file with chromosomes if indices are not exists",
        default=None,
        required=False,
        action='store'
    )
    parser.add_argument(
        '-i',
        '--genome_indices',
        default=None,
        help="The file with genome indices if it exists",
        required=False,
        action='store'
    )
    parser.add_argument(
        '-a',
        '--gff',
        help="gff file with annotation",
        default=None,
        required=True,
        action='store'
    )
    parser.add_argument(
        '-c',
        '--config_path',
        default=None,
        help="Manual config file",
        required=False,
        action='store'
    )
    if multi:
        parser.add_argument(
            '-l',
            '--srr_list',
            help="File with srr list",
            default=None,
            required=True,
            action='store'
        )
        parser.add_argument(
            '-t',
            '--threads',
            help="Number of threads",
            default=4,
            required=False,
            action='store'
        )


    cmd_args = parser.parse_args(args)
    return _prepare_args(cmd_args, multi)

def _prepare_args(input_args, multi=None):
    if multi:
        params_list=[input_args.srr_list]
    else:
        params_list = [input_args.srr]
    params_list.append(input_args.srr_downloads_dir)
    if not input_args.genome_indices:
        if not input_args.genome_fasta:
            print "No genome or genome indices file were in input"
            ind = raw_input("Enter path to the directory with indices for genome (if you \
                        have only genome fasta file miss it): ")
            if not ind:
                g = raw_input("Enter path to the fasta file with chromosomes sequences: ")
                if not g:
                    print "No genome or genome indices file were in input"
                    raise IOError
        else:
            params_list.append(input_args.genome_fasta)
    else:
        params_list.append(input_args.genome_indices)
    params_list.append(input_args.gff)
    if input_args.config_path:
        params_list.append(input_args.config_path)
    if multi:
        params_list.append(input_args.threads)
    return params_list


def _config_parser(config_path=DEFAULT_CONFIG):
    """ Function parses config file and puts the result into an object of ConfigParser class

      :param config_path: path to config file
      :return: a ConfigParser object
      """
    config = ConfigParser.ConfigParser()
    config.read(config_path)
    return config


def _prepare_paths(cmd):
    prepared_cmd_list = []
    parent_prefix = os.path.expanduser("~")
    cmd_list = cmd.split()
    for cmd_part in cmd_list:
        if cmd_part[0] == "~":
            prepared_cmd_list.append(parent_prefix + cmd_part[1:])
        else:
            prepared_cmd_list.append(cmd_part)
    return " ".join(prepared_cmd_list)


def _get_files_list(files_d):
    files_l = []
    f_list = os.listdir(files_d)
    for f in f_list:
        f_path = None
        f_path = os.path.join(files_d, f)
        if os.path.isfile(f_path):
            files_l.append(f_path)
    return files_l


#TODO: should be upgraded during 1.X versions
def _define_gf_or_ind(gf_or_ind):
    if not gf_or_ind:
        return {}
    elif gf_or_ind[-6:] == ".fasta":
        return {'genome_fasta': gf_or_ind}
    else:
        return {'genome_indices': gf_or_ind}


def _gff_to_gtf(gff, gffread_exec):
    gff_no_ext = gff.split(".")[:-1]
    gff_no_ext.append("gtf")
    gtf = ".".join(gff_no_ext)
    convert_cmd = gffread_exec + " " + gff + " -T -o " + gtf
    subprocess.call(_prepare_paths(convert_cmd), shell=True)
    return gtf