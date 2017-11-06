# Pipeline for mapping RNA-seq reads

It consists of four steps:
1. Downloading reads from ncbi SRA database by SRR id using fastq-dump program
2. Filtering reads using Trimmomatic program
3. Mapping procedure conducted with STAR
4. Get genes counts using HTSeq library

### Requirements:
- Python 2.7
- fastq-dump
- Trimmomatic
- STAR
- HTSeq
- gffread


### How to use

Install it:
```
pip install git+https://github.com/loven-doo/mapipe.git
```

Have a look at mapipe/configs/config_example.ini to understand how to set fastq-dump,
Trimmomatic, STAR and HTSeq in your config.ini file.
Look at other example files to know more about mapipe usage

1. If you want prepare only one SRR  
Excute 'mapipe' or 'python -m mapipe' with folowing options:  
-r [--srr] <The SRR id for the reads>  
-d [--srr_downloads_dir] <Name/of/directory/where/reads/should/be/downloaded>  
-g [--genome_fasta] <Fasta/file/with/chromosomes> (only if indices are not exists)  
-i [--genome_indices] <File/with/genome/indices>  
-a [--gff] <gff/file/with/annotation>  
-c [--config_path] <Your/config.ini/file>  

Also you can use import in python:
```
from mapipe import get_counts

get_counts(srr, srr_downloads_dir, genome_fasta_or_indices, gff, config_path)
```
2. If you want prepare a list of SRRs  
Excute 'mumapipe' or 'python -m mumapipe' with folowing options:  
-l [--srr_list] <Text/file/with/srr/list>  
-d [--srr_downloads_dir] <Name/of/directory/where/reads/should/be/downloaded>  
-g [--genome_fasta] <Fasta/file/with/chromosomes> (only if indices are not exists)  
-i [--genome_indices] <File/with/genome/indices>  
-a [--gff] <gff/file/with/annotation>  
-c [--config_path] <Your/config.ini/file>  
-t [--threads] <Number of threads>  

Also you can use import in python:
```
from mumapipe import run_mapipe

run_mapipe(srr_list, srr_downloads_dir, genome_fasta_or_indices, gff, config_path, threads)
```
3. If you want conduct only one step
Use import in python:  
```
import mapipe  

mapipe.download_reads(srr, srr_downloads_dir, config_path) # downloads reads from SRA database using fastq-dump

reads_dir = os.path.join(srr_downloads_dir, srr) # joins the path to fastq files
mapipe.filter_reads(reads_dir, config_path) # filters reads using Trimmomatic

mapipe.map_reads(reads_dir, genome_fasta_or_indices, config_path) # runs STAR (it can automatically index input genome)

mapipe.index_genome(genome_fasta, config_path, genome_indices)
# Indexes input fasta file with chromosomes, genome_indices = "Genome_indices" by default
# so you can change destination folder name

mapipe.calculate_counts(gff, reads_dir, config_path) # Calculates read counts using HTSeq
```
