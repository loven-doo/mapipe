mapipe -r SRR3200454 -d SRRs -i ../Felis_catus/Genome_indices -a ../Felis_catus/GFF/ref_Felis_catus_8.0_top_level.gtf -c config_example.ini

mumapipe -l srr_list_example.txt -d SRRs -i ../Felis_catus/Genome_indices -a ../Felis_catus/GFF/ref_Felis_catus_8.0_top_level.gtf -c mapipe/configs/config_example.ini -t 32  

mapipe.gff_tools.gff3_to_gtf -i ref_Felis_catus_8.0_top_level.gff3
