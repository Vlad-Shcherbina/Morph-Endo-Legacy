'''
Usage:
    img_diff.py <img1> <img2>
'''

import sys

import Image


def main():
    if len(sys.argv) != 3:
        print __doc__
        return
    
    _, src_filename, dst_filename = sys.argv
    
    src = Image.open(src_filename)
    dst = Image.open(dst_filename)
    
    assert src.size == dst.size
    
    width, height = src.size
    
    diff = Image.new("RGB", (width*3, height))
    diff.paste(src, (0, 0))
    diff.paste(dst, (width*2, 0))
    
    cnt = 0
    for y in range(height):
        for x in range(width):
            if src.getpixel((x, y)) == dst.getpixel((x, y)):
                color = (0, 255, 0)
            else:
                color = (255, 0, 0)
                cnt += 1
            diff.putpixel((x+width, y), color)
    
    diff.save('_diff.png')
    if cnt == 0:
        print 'images are equal'
    else:
        print 'images differ in', cnt, 'pixels'


if __name__ == '__main__':
    main()
    