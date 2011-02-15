

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


apple = Gene(0x65F785, 0x0003FB)
mlephant = Gene(0x5B427d, 0x002811)
do_self_check = Gene(0x000058, 1) # that self check from the beginning
gene_table_page_nr = Gene(0x00510, 0x00018)
font_table_dots = Gene(0x0A1AC3, 0x002400)
font_table_cyperus = Gene(0x033965, 0x002400)
font_table_bird_ring = Gene(0x0aa059, 0x002400)
vmu_code_purchase_code = Gene(0x03391B, 24)

help_fuun_security = Gene(0x6db2e0, 0x0126c8)
help_initial_cond = Gene(0x4abbf1, 0x0097f2)

crack_chars = Gene(0x0c0f1d, 0x0006c0)
crack_key = Gene(0x5c6673, 0x002a14)
crack_key_and_print = Gene(0x6C9469, 0x001616)
crack_test_value = Gene(0x0c0f05, 0x000018)

contest1998 = Gene(0x1A5B73, 0x007D96)

help_beautiful_numbers = Gene(0x0e5d10, 0x007e2d)