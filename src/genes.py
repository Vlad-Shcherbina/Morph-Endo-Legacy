

from dna_code import *



Gene = namedtuple('Gene', 'offset size')
class Gene(Gene):
    def content(self):
        green_start = endo().find(green_zone_marker)
        return endo()[green_start+self.offset:green_start+self.offset+self.size]
    
    def patch_prefix(self, new_content):
        assert len(new_content) == self.size
        pattern = [
            open_paren,
            Search(green_zone_marker),
            Skip(self.offset-len(green_zone_marker)),
            close_paren,
            Skip(self.size),
            ]
        template = \
            [Reference(0, 0)]+\
            map(Base, new_content)
            
        items = pattern+[close_paren]+template+[close_paren]
        return ''.join(i.to_dna() for i in items)
    
    def dump(self, fname):
        f = open(fname, 'w')
        f.write(self.content())
        f.close() 

apple = Gene(0x65F785, 0x0003FB)
mlephant = Gene(0x5B427d, 0x002811)
do_self_check = Gene(0x000058, 1) # that self check from the beginning
gene_table_page_nr = Gene(0x00510, 0x00018)
font_table_dots = Gene(0x0A1AC3, 0x002400)
font_table_cyperus = Gene(0x033965, 0x002400)
font_table_bird_ring = Gene(0x0aa059, 0x002400)
vmu_code_purchase_code = Gene(0x03391B, 24)

# control
init = Gene(0x23ca0e, 0xa0e)
terminate = Gene(0x224e0f, 0x18a)

# help pages
help_activating_genes = Gene(0x2bc2cb, 0xc0eb)
help_adaptive_genes = Gene(0x197686, 0xd7d4)
help_background = Gene(0x590ba8, 0x122b)
help_background_1 = Gene(0x44e2fa, 0x1e83)
help_beautiful_numbers = Gene(0xe5d10, 0x7e2d)
help_catalog_page = Gene(0x533c16, 0x8e94)
help_compression_rna = Gene(0x572530, 0x79e5)
help_encodings = Gene(0x5a97d8, 0xaa8d)
help_error_correcting_codes = Gene(0x42ccf3, 0x6ed8)
help_fuun_security = Gene(0x6db2e0, 0x0126c8)
help_fuun_structure = Gene(0x401f1c, 0x720e)
help_initial_cond = Gene(0x4abbf1, 0x0097f2)
help_integer_encoding = Gene(0x43f9ce, 0x4aac)
help_intro = Gene(0x361701, 0x648f7) # too large to patch into security
help_lsystems = Gene(0x5ca81e, 0x6ffd)
help_patching_dna = Gene(0x579f2d, 0xe2e7)
help_undocumented_rna = Gene(0x2b681d, 0x56d7)
help_virus = Gene(0x613180, 0x78e9)
help_vmu = Gene(0x594930, 0x6b41)

# help _purchase_code pages
help_beautiful_numbers_purchase_code = Gene(0x33933, 0x18)
help_error_correcting_codes_purchase_code = Gene(0x33903, 0x18)

#impdoc pages
impdoc_background = Gene(0x6d690c, 0x9e9)
impdoc1 = Gene(0x1f9e38, 0xcee7)
impdoc10 = Gene(0x4ded48, 0x173b)
impdoc2 = Gene(0x4f2c6f, 0xeb39)
impdoc3 = Gene(0x61ba6c, 0x181e9)
impdoc4 = Gene(0x4b53fb, 0x178eb)
impdoc5 = Gene(0x50b88b, 0xe60c)
impdoc6 = Gene(0x4e345c, 0xf7fb)
impdoc7 = Gene(0x41e665, 0xe676)
impdoc8 = Gene(0x33ddf5, 0xfc05)
impdoc9 = Gene(0x268981, 0xefdf)

#fuundoc
fuundoc1 = Gene(0x3d67ae, 0x129b8)
fuundoc2 = Gene(0x2279f2, 0x12063)
fuundoc3 = Gene(0x40ee09, 0xbccc)

#contests
contest_1998 = Gene(0x1A5B73, 0x007D96)
contest_1999 = Gene(0x34da12, 0xd1d3)
contest_2000 = Gene(0x5655d7, 0x9e94)
contest_2001 = Gene(0x54ecfa, 0x93b2)
contest_2002 = Gene(0x24748b, 0x9bc7)
contest_2003 = Gene(0x23eb4e, 0x8925)
contest_2004 = Gene(0x2ad4aa, 0x935b)
contest_2005 = Gene(0xcc21e, 0xae91)
contest_2006 = Gene(0x435804, 0x95f5)
contest_2007 = Gene(0x2084f9, 0xb052)

most_wanted = Gene(0x5d1833, 0x3e659)
printgenetable = Gene(0x284bc3, 0x272c1)

# big data chunks
hitWithTheClueStick = Gene(0x528, 0x32f3c)
vmuRegCode = Gene(0x33483, 0x480)   #
giveMeAPresent = Gene(0x5d, 0x480)  # equal size wtf?

goodVibrations = Gene(0x501, 0x9)

crack_chars = Gene(0x0c0f1d, 0x0006c0)
crack_key = Gene(0x5c6673, 0x002a14)
crack_key_and_print = Gene(0x6C9469, 0x001616)
crack_test_value = Gene(0x0c0f05, 0x000018)


help_error_correcting_codes_purchase_code = Gene(0x033903, 0x000018)

help_beautiful_numbers = Gene(0x0e5d10, 0x007e2d)

