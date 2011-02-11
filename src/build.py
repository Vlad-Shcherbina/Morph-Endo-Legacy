from time import clock
import sys
from collections import namedtuple

import Image
import numpy

size = 600

commands = {
    'PIPIIIC': 'black',
    'PIPIIIP': 'red',
    'PIPIICC': 'green',
    'PIPIICF': 'yellow',
    'PIPIICP': 'blue',
    'PIPIIFC': 'magenta',
    'PIPIIFF': 'cyan',
    'PIPIIPC': 'white',
    'PIPIIPF': 'transparent',
    'PIPIIPP': 'opaque',
    'PIIPICP': 'clear',
    'PIIIIIP': 'move',
    'PCCCCCP': 'counter clockwise',
    'PFFFFFP': 'clockwise',
    'PCCIFFP': 'mark',
    'PFFICCP': 'line',
    'PIIPIIP': 'fill',
    'PCCPFFP': 'add bitmap',
    'PFFPCCP': 'compose',
    'PFFICCF': 'clip',
    }


class Bucket(object):
    def __init__(self):
        self.clear()
        
    def get_color(self):
        if self.cached_color is not None:
            return self.cached_color
        if self.num_colors == 0:
            r = g = b = 0
        else:
            r = self.r//self.num_colors
            g = self.g//self.num_colors
            b = self.b//self.num_colors
        if self.num_alphas == 0:
            a = 255
        else:
            a = self.a//self.num_alphas
        self.cached_color = result = a*r//255, a*g//255, a*b//255, a
        return result
    
    def add_color(self, r, g, b):
        self.num_colors += 1
        self.r += r
        self.g += g
        self.b += b
        self.cached_color = None
        
    def add_alpha(self, a):
        self.num_alphas += 1
        self.a += a
        self.cached_color = None
        
    def clear(self):
        self.num_colors = 0
        self.r = self.g = self.b = 0
        self.num_alphas = 0
        self.a = 0
        self.cached_color = None
        
        
class Builder(object):
    def __init__(self):
        rgb = numpy.zeros((3, size, size), dtype=int)
        a = 255*numpy.ones((1, size, size), dtype=int)
        self.bitmaps = [numpy.concatenate((rgb, a))]
        self.bucket = Bucket()
        
        self.x = self.y = 0
        self.markX = self.markY = 0
        self.dirX, self.dirY = 1, 0
        
        self.cost = 0
        
    @staticmethod
    def bitmap_to_image(bitmap):
        img = bitmap[:3]
        img = numpy.swapaxes(img, 0, 1)
        img = numpy.swapaxes(img, 1, 2)
        img = numpy.asarray(img, dtype=numpy.ubyte)
        img = Image.fromarray(img, mode='RGB')
        return img
        
    def get_state_image(self):
        img = Image.new('RGB', (size*2, size))
        img.paste(self.bitmap_to_image(self.bitmaps[0]), (0, 0))
        for i, bmp in enumerate(self.bitmaps[1:]):
            t = self.bitmap_to_image(bmp)
            t = t.resize((size//3, size//3), Image.ANTIALIAS)
            img.paste(t, (size+i%3*size//3, i//3*size//3))
        return img
         
    def get_result_image(self):
        return self.bitmap_to_image(self.bitmaps[0])
    
    def run_command(self, cmd):
        cmd = commands.get(cmd)
        
        if cmd == 'black':
            self.bucket.add_color(0, 0, 0)
        elif cmd == 'red':
            self.bucket.add_color(255, 0, 0)
        elif cmd == 'green':
            self.bucket.add_color(0, 255, 0)
        elif cmd == 'yellow':
            self.bucket.add_color(255, 255, 0)
        elif cmd == 'blue':
            self.bucket.add_color(0, 0, 255)
        elif cmd == 'magenta':
            self.bucket.add_color(255, 0, 255)
        elif cmd == 'cyan':
            self.bucket.add_color(0, 255, 255)
        elif cmd == 'white':
            self.bucket.add_color(255, 255, 255)
        elif cmd == 'transparent':
            self.bucket.add_alpha(0)
        elif cmd == 'opaque':
            self.bucket.add_alpha(255)
            
        elif cmd == 'clear':
            self.bucket.clear()
            
        elif cmd == 'move':
            self.move()
        elif cmd == 'counter clockwise':
            self.turn_counter_clockwise()
        elif cmd == 'clockwise':
            self.turn_clockwise()
            
        elif cmd == 'mark':
            self.markX, self.markY = self.x, self.y
        
        elif cmd == 'line':
            self.line(self.x, self.y, self.markX, self.markY)
        elif cmd == 'fill':
            self.tryfill()
            
        elif cmd == 'add bitmap':
            if len(self.bitmaps) < 10:
                self.bitmaps.insert(0, numpy.zeros((4, size, size), dtype=int))
        elif cmd == 'compose':
            self.compose()
        elif cmd == 'clip':
            self.clip()
        
    def turn_clockwise(self):
        self.dirX, self.dirY = -self.dirY, self.dirX
        
    def turn_counter_clockwise(self):
        self.dirX, self.dirY = self.dirY, -self.dirX
        
    def move(self):
        self.x += self.dirX
        self.x %= size
        self.y += self.dirY
        self.y %= size
        
    def get_pixel(self, x, y):
        #return tuple(self.bitmaps[0][:, y, x])
        bitmap = self.bitmaps[0]
        return (bitmap[0, y, x], 
                bitmap[1, y, x], 
                bitmap[2, y, x], 
                bitmap[3, y, x])
        
    def set_pixel(self, x, y):
        #self.bitmaps[0][:, y, x] = self.bucket.get_color()
        bitmap = self.bitmaps[0]
        r, g, b, a = self.bucket.get_color()
        bitmap[0, y, x] = r
        bitmap[1, y, x] = g
        bitmap[2, y, x] = b
        bitmap[3, y, x] = a
        
        self.cost += 1
        
    def line(self, x0, y0, x1, y1):
        dx = x1-x0
        dy = y1-y0
        d = max(abs(dx), abs(dy))
        if dx*dy <= 0:
            c = 1
        else:
            c = 0
        x = x0*d+(d-c)//2
        y = y0*d+(d-c)//2
        for i in range(d):
            self.set_pixel(x//d, y//d)
            x += dx
            y += dy
        self.set_pixel(x1, y1)
        
    def tryfill(self):
        new = self.bucket.get_color()
        old = self.get_pixel(self.x, self.y)
         
        if new == old:
            return

        fill_tasks = set([(self.x, self.y)])
        visited = set()
        
        def add_task(x, y):
            xy = x, y
            if xy in visited or xy in fill_tasks:
                return
            fill_tasks.add(xy)
        
        while fill_tasks:
            x, y = fill_tasks.pop()
            visited.add((x, y))
            if self.get_pixel(x, y) != old:
                continue
            self.set_pixel(x, y)
            if x > 0:
                add_task(x-1, y)
            if x < size-1:
                add_task(x+1, y)
            if y > 0:
                add_task(x, y-1)
            if y < size-1:
                add_task(x, y+1)           

        
    def compose(self):
        if len(self.bitmaps) < 2:
            return
        self.bitmaps[1] *= 255-self.bitmaps[0][3,:,:]
        self.bitmaps[1] //= 255
        self.bitmaps[1] += self.bitmaps[0]
        del self.bitmaps[0]
        self.cost += size*size
        
    def clip(self):
        if len(self.bitmaps) < 2:
            return
        self.bitmaps[1] *= self.bitmaps[0][3,:,:]
        self.bitmaps[1] //= 255
        del self.bitmaps[0]
        self.cost += size*size


def main():
    b = Builder()
    
    _, filename = sys.argv 
        
    fin = open(filename+'.rna')
    start = clock()
    
    frame = 0
    
    for rna in fin:
        rna = rna.strip()
        cmd = commands.get(rna)
        #print cmd
        #if cmd == "add bitmap":
        #    img = b.get_state_image()
        #    img.save("precheck_prefix.png") # to extract prefix that is removed afterwards
        #    raw_input()
            
        b.run_command(rna)
        #if b.cost > 1000:
        #    print 'saving frame', frame
        #    b.get_state_image().save('f:/temp/frames/frame{:04}.png'.format(frame))
        #    b.cost = 0
        #    frame += 1

    print 'it took', clock()-start
    b.get_result_image().save(filename+'.png')
    
    
if __name__ == '__main__':
    main()    