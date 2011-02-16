import genes
import dna_code as dna

# utilizing CODE INJECTION
# YEAAAAAAAAAAAAH

#unknown_impdocs = ["impdoc" + str(n) for n in xrange(1, 10 + 1)]
#unknown_help = ['help_adaptive_genes', 'help_initial_cond', 
#                'help_intro', 'help_virus', 'help_vmu']
#unknown_fuundocs =  ["fuundoc" + str(n) for n in xrange(1, 3 + 1)]

# still unknown but it's too long... :(
#unknown_help = ['help_intro']

encrypted_help = ['help_activating_genes', 'help_error_correcting_codes', \
                  'help_beautiful_numbers']

unknown_contests = ['contest_' + str(n) for n in xrange(1998, 2007 + 1)]

# fuun_security as host
#host_gene = genes.help_fuun_security
#host_activation_prefix = \
#    "IIPIFFCPICFPPICIICCCCCCCCCCCCCCCCCCCCCCCCIICIPPPFCFCCCFCCFCFFFCCFFCCCCFIIC"

# most_wanted as host
host_gene = genes.most_wanted
host_activation_prefix = \
    "IIPIFFCPICFPPICIICCCCCCCCIICIPPPCCCCFFFIIC"

def process_genes(names_list, prefix=""):
    for gene_name in names_list:
        gene = genes.__dict__[gene_name]
        # may still fail for some lengths due to minimum nop length
        if gene.size <= host_gene.size:
            dna.create_and_run_prefix(prefix + \
                            dna.replace_procedure_prefix(host_gene, gene) + \
                            host_activation_prefix,
                            "data\\ripped_pages\\" + gene_name)

if __name__ == "__main__":
#    prefix = dna.replace_procedure_prefix(genes.help_background, \
#                                          genes.impdoc_background)
#    process_genes(unknown_impdocs, prefix)
    
#    process_genes(unknown_help)
#    process_genes(unknown_fuundocs)
    process_genes(unknown_contests)
    
