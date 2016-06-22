#!/usr/bin/env python3

import string, re, io

class Spotter:
    def __init__(self):
        self.location = (0,0)
        self.arrow = None
        self.icon = None
        self.text = None
        self.mwid = None

spotterre = re.compile("Object: (-?\d+\.\d+),(-?\d+\.\d+)(?:.|\n)*?(?:Icon:) (0,0,[0-9]{3},2,.*)?(?:.|\n)*?Icon: ([^\"]*),\"([^\"]*)\"(?:.|\n)*?Text: (.*)(?:.|\n)*?End:")
objectre = re.compile("Object: (-?\d+\.\d+),(-?\d+\.\d+)(?:.|\n)*?")
headingre = re.compile("Icon: (0,0,[0-9]+,2,.*)(?:.|\n)*?")
#iconre = re.compile("Icon: ([^\"]*),\"([^\"]*)\"(?:.|\n)*?")
iconre = re.compile("Icon: 0,0,000,6,([0-9]+),\"(.*)\"(?:.|\n)*?")
textre = re.compile("Text: (.*)(?:.|\n)*?")
mwre = re.compile("(MW[0-9]{3})")

snfile = open("gr.txt")
sninput = io.StringIO(snfile.read())

mwoutput = io.StringIO()

mwoutput.write ("""Refresh: 1
Threshold: 999
Title: Midwest SSTRC SpotterNetwork Positions
Font: 1, 11, 1, "Courier New"
IconFile: 1, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/spotternet.png"
IconFile: 2, 15, 25, 8, 25, "http://www.spotternetwork.org/icon/arrows.png"
IconFile: 6, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/spotternet_new.png"\n\n""")

spotters = []

line = sninput.readline()

icondict = {'2':'13', '10':'15', '6':'14'}

while line is not '':
    loc = objectre.search(line)
    if loc is None:
        line = sninput.readline()
        continue
    spotter = Spotter()
    spotter.location = loc.groups()
    line = sninput.readline()
    heading = headingre.search(line)
    if heading is not None:
        spotter.arrow = heading.group(1)
        line = sninput.readline()
    icon = iconre.search(line)
    spotter.icon = (icondict[icon.group(1)], icon.group(2))
    mwid = mwre.search(line)
    if mwid is None:
        continue
    spotter.mwid = mwid.group(1)
    line = sninput.readline()
    text = textre.search(line)
    spotter.text = text.group(1)
    spotters.append(spotter)
    line = sninput.readline()

for spotter in spotters:
    mwoutput.write('Object: {},{}\n'.format(spotter.location[0], spotter.location[1]))
    if spotter.arrow is not None:
        mwoutput.write('Icon: {}\n'.format(spotter.arrow))
    mwoutput.write('Icon: 0,0,000,1,{},\"{}\"\nText: {}\nText: 15, 20, 1, \"{}\"\nEnd:\n'.format(spotter.icon[0], spotter.icon[1], spotter.text, spotter.mwid))

mwoutput.write('\n')

mwfile = open("mw.txt", "w")
mwoutput.seek(0)
mwfile.write(mwoutput.read())
mwfile.close()
mwoutput.close()