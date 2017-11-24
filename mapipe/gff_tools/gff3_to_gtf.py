import io
import sys
import argparse
from collections import OrderedDict


class GTFWriteTools(object):

    def __init__(self, chr_name, source, start, end, score, strand, phase):
        self.chr_name = chr_name
        self.source = source
        self.start = start
        self.end = end
        self.score = score
        self.strand = strand
        self.phase = phase
        self.id = None
        self.parent = None
        self.gene_id = None
        self.gene_name = None
        self.transcript_id = None
        self.feature = None

    @staticmethod
    def gtf_writer(gtf, s, new=False):
        if new:
            gtf_f = io.open(gtf, 'w', newline="\n")
        else:
            gtf_f = io.open(gtf, 'a', newline="\n")
        gtf_f.write(unicode(s + "\n"))
        gtf_f.close()

    def create_line(self):
        line = self.chr_name+ "\t" + self.source + "\t" + self.feature + "\t" + self.start + "\t" + self.end + \
               "\t" + self.score + "\t" + self.strand + "\t" + self.phase + "\t" + "gene_id " + self.gene_id + \
               "; gene_name " + self.gene_name
        if not self.transcript_id:
            return line
        else:
            return line + "; transcript_id " + self.transcript_id


    def read_attr(self, col9, parent_dict, id, parent, gene_name):
        defined_attrs = {id: 'id', parent: 'parent', gene_name: 'gene_name'}
        attr_dict = {}
        col9_list = col9.split(";")
        for attr in col9_list:
            attr_list = attr.split("=")
            if attr_list[0] in defined_attrs.keys():
                attr_dict[defined_attrs[attr_list[0]]] = attr_list[1]
        self.id = attr_dict['id']
        try:
            self.parent = parent_dict[attr_dict['parent']]
        except (KeyError, TypeError):
            self.parent = None
        try:
            self.gene_name = attr_dict['gene_name']
        except KeyError:
            self.gene_name = "Undefined"


class Gene(GTFWriteTools):

    def __init__(self, chr_name, source, start, end, score, strand, phase):
        super(Gene, self).__init__(chr_name, source, start, end, score, strand, phase)
        self.feature = "gene"
        self.transcripts = []
        self.exons = []

    def write_to_gtf(self, gtf):
        gene_line = self.create_line()
        self.gtf_writer(gtf, gene_line)
        for transcript in self.transcripts:
            transcript.write_to_gtf(gtf)

    def read_attr(self, col9, id, parent, gene_name, parent_dict=None):
        super(Gene, self).read_attr(col9, parent_dict, id, parent, gene_name)
        self.gene_id = self.id


class Transcript(GTFWriteTools):

    def __init__(self, chr_name, source, start, end, score, strand, phase):
        super(Transcript, self).__init__(chr_name, source, start, end, score, strand, phase)
        self.feature = "transcript"
        self.exons = []

    def read_attr(self, col9, genes, id, parent, gene_name):
        super(Transcript, self).read_attr(col9, genes, id, parent, gene_name)
        if not self.parent:
            return False
        self.transcript_id = self.id
        self.gene_id = self.parent.gene_id
        self.gene_name = self.parent.gene_name
        return True

    def write_to_gtf(self, gtf):
        transcript_line = self.create_line()
        self.gtf_writer(gtf, transcript_line)
        for exon in self.exons:
            exon.write_to_gtf(gtf)


class Exon(GTFWriteTools):

    def __init__(self, chr_name, source, start, end, score, strand, phase):
        super(Exon, self).__init__(chr_name, source, start, end, score, strand, phase)
        self.feature = "exon"
        self.cds = None

    def read_attr(self, col9, transcripts, id, parent, gene_name):
        super(Exon, self).read_attr(col9, transcripts, id, parent, gene_name)
        if not self.parent:
            return False        
        self.gene_id = self.parent.gene_id
        self.gene_name = self.parent.gene_name
        self.transcript_id = self.parent.transcript_id
        return True

    def write_to_gtf(self, gtf):
        exon_line = self.create_line()
        self.gtf_writer(gtf, exon_line)
        if self.cds:
            self.cds.write_to_gtf(gtf)


class CDS(GTFWriteTools):

    def __init__(self, chr_name, source, start, end, score, strand, phase):
        super(CDS, self).__init__(chr_name, source, start, end, score, strand, phase)
        self.feature = "CDS"

    def read_attr(self, col9, transcripts, id, parent, gene_name):
        super(CDS, self).read_attr(col9, transcripts, id, parent, gene_name)
        if not self.parent:
            return False
        self.gene_id = self.parent.gene_id
        self.gene_name = self.parent.gene_name
        self.transcript_id = self.parent.transcript_id
        self._define_exon()
        return True

    def _define_exon(self):
        for exon in self.parent.exons:
            try:
                cds_start = int(self.start)
                cds_end = int(self.end)
                exon_start = int(exon.start)
                exon_end = int(exon.end)
            except ValueError:
                break
            if cds_start >= exon_start and cds_end <= exon_end and self.strand == exon.strand:
                exon.cds = self
                break

    def write_to_gtf(self, gtf):
        cds_line = self.create_line()
        self.gtf_writer(gtf, cds_line)


def gff3_converter(gff, id_attrt='ID', parent_attr='Parent', gene_name_attr='gene', gtf=None, **kwargs):
    genes = OrderedDict()
    transcripts = OrderedDict()
    header = True
    new_gtf = True
    if not gtf:
        gtf = ".".join(gff.split(".")[:-1]) + ".gtf"
    gff_f = open(gff)
    for lines in gff_f:
        line = None
        line = lines.strip()
        if len(line) == 0:
            continue
        if line[0] == "#":
            if header:
                GTFWriteTools.gtf_writer(gtf, line, new_gtf)
                new_gtf = False
            continue
        line_list = line.split("\t")
        try:
            feature = None
            feature = line_list[2].lower()
        except IndexError:
            continue
        if feature == "gene":
            header = False
            gene = Gene(
                chr_name=line_list[0],
                source=line_list[1],
                start=line_list[3],
                end=line_list[4],
                score=line_list[5],
                strand=line_list[6],
                phase=line_list[7]
            )
            gene.read_attr(line_list[8], id_attrt, parent_attr, gene_name_attr)
            genes[gene.gene_id] = gene
        elif "rna" in feature or "transcript" in feature:
            transcript = Transcript(
                chr_name=line_list[0],
                source=line_list[1],
                start=line_list[3],
                end=line_list[4],
                score=line_list[5],
                strand=line_list[6],
                phase=line_list[7]
            )
            attr_got = transcript.read_attr(line_list[8], genes, id_attrt, parent_attr, gene_name_attr)
            if not attr_got:
                continue
            transcript.parent.transcripts.append(transcript)
            transcripts[transcript.transcript_id] = transcript
        elif feature == "exon":
            exon = Exon(
                chr_name=line_list[0],
                source=line_list[1],
                start=line_list[3],
                end=line_list[4],
                score=line_list[5],
                strand=line_list[6],
                phase=line_list[7]
            )
            attr_got = exon.read_attr(line_list[8], transcripts, id_attrt, parent_attr, gene_name_attr)
            if not attr_got:
                attr_got = exon.read_attr(line_list[8], genes, id_attrt, parent_attr, gene_name_attr)            
                if not attr_got:
                    continue
            exon.parent.exons.append(exon)
        elif feature == "cds":
            cds = CDS(
                chr_name=line_list[0],
                source=line_list[1],
                start=line_list[3],
                end=line_list[4],
                score=line_list[5],
                strand=line_list[6],
                phase=line_list[7]
            )
            attr_got = cds.read_attr(line_list[8], transcripts, id_attrt, parent_attr, gene_name_attr)
            if not attr_got:
                attr_got = cds.read_attr(line_list[8], genes, id_attrt, parent_attr, gene_name_attr)
        else:
            continue
    _write_genes(genes, gtf)
    return gtf


def _write_genes(genes, gtf):
    for gene_id in genes.keys():
        genes[gene_id].write_to_gtf(gtf)


def _parse_cmd_args(cmd_args):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-i',
        '--gff3',
        required=True,
        help="The name of input gff3 file",
        action='store'
    )
    parser.add_argument(
        '-id',
        '--ID',
        default="ID",
        required=False,
        help="Equivalent to 'ID' attribute in your file",
        action='store'
    )
    parser.add_argument(
        '-p',
        '--Parent',
        default="Parent",
        required=False,
        help="Equivalent to 'Parent' attribute in your file",
        action='store'
    )
    parser.add_argument(
        '-n',
        '--GeneName',
        default="gene",
        required=False,
        help="Equivalent to 'gene' attribute in your file",
        action='store'
    )
    parser.add_argument(
        '-o',
        '--gtf',
        default=None,
        required=False,
        help="The name of output gtf file",
        action='store'
    )

    options = parser.parse_args(cmd_args)
    return _prepare_args(options)


def _prepare_args(opt):
    opt_dict = {}
    opt_dict['gff'] = opt.gff3
    opt_dict['id_attr'] = opt.ID
    opt_dict['parent_attr'] = opt.Parent
    opt_dict['gene_name_attr'] = opt.GeneName
    opt_dict['gtf'] = opt.gtf
    return opt_dict


def main():
    kwargs = _parse_cmd_args(sys.argv[1:])
    gff3_converter(**kwargs)


if __name__ == "__main__":
    kwargs = _parse_cmd_args(sys.argv[1:])
    gff3_converter(**kwargs)
