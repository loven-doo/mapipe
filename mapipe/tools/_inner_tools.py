import argparse
import ConfigParser

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
        required=False,
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
            params_list.append({'genome_fasta': input_args.genome_fasta})
    else:
        params_list.append({'genome_indices': input_args.genome_indices})
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
