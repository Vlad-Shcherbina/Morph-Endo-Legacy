from dna_code import endo



def main():
    text = endo()[0x3e78:0x6848]
    with open('achtung.txt', 'w') as fout:
        for i in range(0, len(text), 16):
            print text[i:i+16]
    
    png = endo()[0x6c58:]
    i = png.find('PP', )
    png, audio = png[:i], png[i+2:]
    
    assert len(png)%8 == 0
    with open('achtung.png', 'wb') as fout:
        for i in range(0, len(png), 8):
            t = png[i:i+8].replace('I', '0').replace('C', '1')
            t = t[::-1]
            fout.write(chr(int(t, 2)))
            
    audio = audio[:audio.find('P')] 
    
    assert len(audio)%8 == 0
    with open('achtung.hz', 'wb') as fout:
        for i in range(0, len(audio), 8):
            t = audio[i:i+8].replace('I', '0').replace('C', '1')
            t = t[::-1]
            fout.write(chr(int(t, 2)))

if __name__ == '__main__':
    main()