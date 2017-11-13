import os
import subprocess
import sys
import logging

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
    subprocess.call("rm -r " + os.path.join(conf.get('fastq-dump', 'cache_dir'), srr+".sra.cache"), shell=True)


#TODO: not only illumina support should be implemented till 2.0 version
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


def map_reads(reads_dir, genome_fasta_or_indices, gff, config_path=DEFAULT_CONFIG, conf=None):
    if not conf:
        conf = _config_parser(config_path)
    genome_or_ind = _define_gf_or_ind(genome_fasta_or_indices)
    try:
        g_ind = genome_or_ind['genome_indices']
        if _check_sjdb(g_ind):
            gff = None
    except KeyError:
        try:
            g_ind = index_genome(genome_fasta=genome_or_ind['genome_fasta'], gff=gff, config_path=config_path, 
                                 genome_indices="Genome_indices", conf=conf)
            gff = None
        except KeyError:
            print "No genome or genome indices file were in input"
            raise KeyError
    reads_f_list = _get_files_list(reads_dir)
    if not gff:
        sjdb_option = ""
    elif gff[-5:] != ".gff3":
        sjdb_option = " --sjdbGTFfile " + gff + " --sjdbGTFtagExonParentTranscript Parent"
    else:
        sjdb_option = " --sjdbGTFfile " + gff
    cmd = conf.get('STAR', 'exec_path') + " --runThreadN " + conf.get('STAR', 'threads') + " --genomeDir " + \
        g_ind + sjdb_option + " --readFilesIn " + ",".join(reads_f_list) + \
        " --outFileNamePrefix " + os.path.join(reads_dir, "") + " --quantMode GeneCounts --outSAMtype " + \
        conf.get('STAR', 'outSAMtype')
    subprocess.call(_prepare_paths(cmd), shell=True)


def _check_sjdb(g_ind):
    ind_fs_list = _get_files_list(g_ind)
    for f in ind_fs_list:
        os.path.split()
        

def index_genome(genome_fasta, gff=None, config_path=DEFAULT_CONFIG, genome_indices="Genome_indices", conf=None):
    if not conf:
        conf = _config_parser(config_path)
    if not gff:
        sjdb_option = ""
    elif gff[-5:] == ".gff3":
        sjdb_option = " --sjdbGTFfile " + gff + " --sjdbGTFtagExonParentTranscript Parent"
    else:
        sjdb_option = " --sjdbGTFfile " + gff
    subprocess.call("mkdir " + genome_indices, shell=True)
    ind_cmd = conf.get('STAR', 'exec_path') + " --runThreadN " + conf.get('STAR', 'threads') + \
              " --runMode genomeGenerate --genomeDir " + genome_indices + " --genomeFastaFiles " + \
              genome_fasta + sjdb_option 
    subprocess.call(_prepare_paths(ind_cmd), shell=True)
    return genome_indices


def calculate_counts(gff, reads_dir, config_path=DEFAULT_CONFIG, conf=None):
    if not conf:
        conf = _config_parser(config_path)
    #gtf = annotation_to_ensemble_gtf(gff, config_path=config_path, conf=conf)
    #gff = None
    #gff = gtf
    srr_list = _get_files_list(reads_dir)
    for srr in srr_list:
        if srr[-4:] == '.bam':
            cmd = "python -m HTSeq.scripts.count -f " + conf.get('HTSeq', 'format') + " -r " + \
                  conf.get('HTSeq', 'order') + " -s " + conf.get('HTSeq', 'stranded') + " -t " + \
                  conf.get('HTSeq', 'type') + " -i " + conf.get('HTSeq', 'idattr') + " " + srr + \
                  " " + gff + " 1> " + os.path.join(reads_dir, os.path.split(reads_dir)[1]) + ".csv 2>> htseq.log"
            subprocess.call(_prepare_paths(cmd), shell=True)


def annotation_to_ensemble_gtf(gff, config_path=DEFAULT_CONFIG, conf=None):
    to_gtf_conv = False
    to_ensemble_conv = False
    if not conf:
        conf = _config_parser(config_path)
    if gff[-3:] != "gtf":
        gtf = gff_to_gtf(gff, config_path=config_path, conf=conf)
        gff = None
        gff = gtf
        to_gtf_conv = True
    gtf, to_ensemble_conv = _check_gtf(gff)
    gff = None
    gff = gtf
    if to_gtf_conv or to_ensemble_conv:
        logging.info("Convertion to ensemble fromate is done")
    else:
        logging.info("Your file is just in ensemble gtf format")
    return gff

#TODO: Write this method properly during 1.x versions
def _check_gtf(gtf):
    conv = False
    gtf_read = open(gtf)
    for lines in gtf:
        line = None
        line = lines.strip()
        if len(line) == 0:
            continue
        if line[0] == "#":
            continue

    if not conv:  #
        conv = True
    if conv:
        new_gtf = _annot_to_ensemble(gtf)  #will be implemented during next versions
        gtf = None
        gtf = new_gtf
    return gtf, conv


def gff_to_gtf(gff, config_path=DEFAULT_CONFIG, conf=None):
    if not conf:
        conf = _config_parser(config_path)
    gff_no_ext = gff.split(".")[:-1]
    gff_no_ext.append("gtf")
    gtf = ".".join(gff_no_ext)
    convert_cmd = conf.get('HTSeq', 'gffread_exec') + " " + gff + " -T -o " + gtf
    subprocess.call(_prepare_paths(convert_cmd), shell=True)
    return gtf


def main():
    args = _parse_cmd_args(sys.argv[1:])
    get_counts(*args)
