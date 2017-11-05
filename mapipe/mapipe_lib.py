import os
import subprocess
import sys

from mapipe.constants import DEFAULT_CONFIG
from mapipe.tools._inner_tools import _parse_cmd_args, _config_parser, _prepare_paths, _get_files_list, \
    _define_gf_or_ind


def get_counts(srr, srr_downloads_dir, genome_fasta_or_indices, gff, config_path=DEFAULT_CONFIG, *args):
    config = _config_parser(config_path)
    download_reads(srr=srr, srr_downloads_dir=srr_downloads_dir, config_path=config_path, conf=config)
    reads_directory = os.path.join(srr_downloads_dir, srr)
    print srr + " reads downloaded succsessfuly"
    filter_reads(reads_dir=reads_directory, config_path=config_path, conf=config)
    print srr + " reads filtered succesfully"
    map_reads(reads_dir=reads_directory, genome_fasta_or_indices=genome_fasta_or_indices,
              config_path=config_path, conf=config)
    print srr + " reads mapped successfully"
    calculate_counts(gff=gff, reads_dir=reads_directory, config_path=config_path, conf=config)
    print "counts for " + srr + " reads got successfully"


def download_reads(srr, srr_downloads_dir, config_path=DEFAULT_CONFIG, conf=None):
    if not conf:
        conf = _config_parser(config_path)
    cmd = conf.get('fastq-dump', 'exec_path') + " -I --split-files " + srr + " -O " + \
          os.path.join(srr_downloads_dir, srr) + "/"
    subprocess.call("mkdir " + srr_downloads_dir, shell=True)
    subprocess.call("mkdir " + os.path.join(srr_downloads_dir, srr), shell=True)
    subprocess.call(_prepare_paths(cmd.replace("//", "/")), shell=True)
    subprocess.call("rm -r " + os.path.join(conf.get('fastq-dump', 'cash_dir'), srr+".sra.cashe"), shell=True)


def filter_reads(reads_dir, config_path=DEFAULT_CONFIG, conf=None):
    if not conf:
        conf = _config_parser(config_path)
    srr_list = _get_files_list(reads_dir)
    if len(srr_list) == 1:
        cmd = "java -jar " + conf.get('Trimmomatic', 'exec_path') + " SE -threads " + \
            conf.get('Trimmomatic', 'threads') + " -phred33 " + srr_list[0] + " " + \
            srr_list[0].split(".")[0]+"_trimm.fastq" + " ILLUMINACLIP: " + conf.get('Trimmomatic', 'ILLUMINACLIP') + \
            " LEADING: " + conf.get('Trimmomatic', 'LEADING') + " TRAILING: " + conf.get('Trimmomatic', 'TRAILING') + \
            " MINLEN: " + conf.get('Trimmomatic', 'MINLEN')
    else:
        srr_list_trimm = _get_trimm_names(srr_list)
        cmd = "java -jar " + conf.get('Trimmomatic', 'exec_path') + " PE -threads " + \
            conf.get('Trimmomatic', 'threads') + " -phred33 " + " ".join(srr_list) + " " + " ".join(srr_list_trimm) + \
            " ILLUMINACLIP: " + conf.get('Trimmomatic', 'ILLUMINACLIP') + " LEADING: " + \
            conf.get('Trimmomatic', 'LEADING') + " TRAILING: " + conf.get('Trimmomatic', 'TRAILING') + \
            " MINLEN: " + conf.get('Trimmomatic', 'MINLEN')
    subprocess.call(_prepare_paths(cmd).replace(": ", ":"), shell=True)
    for srr in srr_list:
        subprocess.call("rm " + srr, shell=True)

def _get_trimm_names(srr_l):
    srr_l_trimm = []
    for srr_f in srr_l:
        srr = srr_f.split(".")[0]
        srr_l_trimm.append(srr+"paired_trimm.fastq")
        srr_l_trimm.append(srr+"unpaired_trimm.fastq")
    return srr_l_trimm


def map_reads(reads_dir, genome_fasta_or_indices, config_path=DEFAULT_CONFIG, conf=None):
    if not conf:
        conf = _config_parser(config_path)
    genome_or_ind = _define_gf_or_ind(genome_fasta_or_indices)
    try:
        g_ind = genome_or_ind['genome_indices']
    except KeyError:
        try:
            g_ind = index_genome(genome_fasta=genome_or_ind['genome_fasta'], config_path=config_path,
                                 genome_indices="Genome_indices", conf=conf)
        except KeyError:
            print "No genome or genome indices file were in input"
            raise KeyError
    reads_f_list = _get_files_list(reads_dir)
    cmd = conf.get('STAR', 'exec_path') + " --runThreadN " + conf.get('STAR', 'threads') + " --genomeDir " + \
        g_ind + " --readFilesIn " + ",".join(reads_f_list) + " --outFileNamePrefix " + os.path.join(reads_dir, "") + \
        " --outSAMtype " + conf.get('STAR', 'outSAMtype')
    subprocess.call(_prepare_paths(cmd), shell=True)


def index_genome(genome_fasta, config_path=DEFAULT_CONFIG, genome_indices="Genome_indices", conf=None):
    if not conf:
        conf = _config_parser(config_path)
    subprocess.call("mkdir " + genome_indices, shell=True)
    ind_cmd = conf.get('STAR', 'exec_path') + " --runThreadN " + conf.get('STAR', 'threads') + \
              " --runMode genomeGenerate --genomeDir " + genome_indices + " --genomeFastaFiles " + genome_fasta
    subprocess.call(_prepare_paths(ind_cmd), shell=True)
    return genome_indices


def calculate_counts(gff, reads_dir, config_path=DEFAULT_CONFIG, conf=None):
    if not conf:
        conf = _config_parser(config_path)
    srr_list = _get_files_list(reads_dir)
    for srr in srr_list:
        if srr[-4:] == '.bam':
            cmd = "python -m HTSeq.scripts.count -f " + conf.get('HTSeq', 'format') + " -r " + \
                  conf.get('HTSeq', 'order') + " -s " + conf.get('HTSeq', 'stranded') + " " + srr + \
                  " " + gff + " 1 > " + srr[:-4] + ".ct 2 >> htseq.log"
            subprocess.call(_prepare_paths(cmd), shell=True)


def main():
    args = _parse_cmd_args(sys.argv[1:])
    get_counts(*args)
