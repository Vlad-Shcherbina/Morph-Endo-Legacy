'''
Usage:
    steganography.py <image>
    
It produces image_uncovered file.
'''

import sys
import os
import Image


def main(args=sys.argv):
    if len(args) != 2:
        print __doc__
        exit()
        
    _, filename = args
    base, ext = os.path.splitext(filename)
    if base.endswith('_uncovered'):
        print filename, 'already uncovered'
        exit()
    if not ext:
        ext = '.png'
    img = Image.open(base+ext)
    
    width, height = img.size
    for y in range(height):
        for x in range(width):
            r, g, b = img.getpixel((x, y))
            r = r%2*255
            g = g%2*255
            b = b%2*255
            img.putpixel((x, y), (r, g, b))
    img.save(base+'_uncovered'+ext)
    pass


if __name__ == '__main__':
    main(sys.argv)