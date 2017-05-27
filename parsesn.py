#!/usr/bin/env python3

import re, io, sys, traceback, requests, time
from collections import defaultdict


class Spotter:
    def __init__(self):
        self.location = (0, 0)
        self.arrow = None
        self.icon = None
        self.text = None
        self.mwid = None
        self.crew = None

#snfile = open("gr.txt")
snurl = "http://www.spotternetwork.org/feeds/gr.txt"
snreq = requests.get(snurl)
sntxt = snreq.text
#sntxt = snfile.read()
loopcount = 0
while sntxt.endswith("  \n") is False:
    time.sleep(5)
    snreq = requests.get(snurl)
    sntxt = snreq.text
    loopcount = loopcount + 1
    if loopcount > 5:
        exit(1)
        
sninput = io.StringIO(sntxt)

# spotterre = re.compile("Object: (-?\d+\.\d+),(-?\d+\.\d+)(?:.|\n)*?(?:Icon:) (0,0,[0-9]{3},2,.*)?(?:.|\n)*?Icon: ([^\"]*),\"([^\"]*)\"(?:.|\n)*?Text: (.*)(?:.|\n)*?End:")
objectre = re.compile("Object: (-?\d+\.\d+),(-?\d+\.\d+)(?:.|\n)*?")
headingre = re.compile("Icon: (0,0,[0-9]+,2,.*)(?:.|\n)*?")
# iconre = re.compile("Icon: ([^\"]*),\"([^\"]*)\"(?:.|\n)*?")
iconre = re.compile("Icon: 0,0,000,[61],([0-9]+),\"(.*)\"(?:.|\n)*?")
textre = re.compile("Text: (.*)(?:.|\n)*?")
crewre = re.compile(
    "(John Bowles)|(Dan Starker)|(Taylor DeWinter)|(Rob Morris)|(Josh Ringelstetter)|(Jacob Ela)|(Michael Birch)|(Brent Cook)")
mwre = re.compile("(MW[0-9]{3})")


#snfile = open("gr.txt")
#sninput = io.StringIO(snfile.read())

mwoutput = io.StringIO()
crewoutput = io.StringIO()

mwoutput.write("""Refresh: 1
Threshold: 999
Title: Midwest SSTRC SpotterNetwork Positions
Font: 1, 11, 1, "Courier New"
IconFile: 1, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/spotternet.png"
IconFile: 2, 15, 25, 8, 25, "http://www.spotternetwork.org/icon/arrows.png"
IconFile: 6, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/spotternet_new.png"
IconFile: 3, 22, 22, 11, 11, "http://grx.wockets.org/mwicons.png"\n\n""")

crewoutput.write("""Refresh: 1
Threshold: 999
Title: CREW SpotterNetwork Positions
Font: 1, 11, 1, "Courier New"
IconFile: 1, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/spotternet.png"
IconFile: 2, 15, 25, 8, 25, "http://www.spotternetwork.org/icon/arrows.png"
IconFile: 6, 22, 22, 11, 11, "http://www.spotternetwork.org/icon/spotternet_new.png"
IconFile: 3, 22, 22, 11, 11, "http://grx.wockets.org/crewicons.png"\n\n""")

spotters = []

line = sninput.readline()

icondict = defaultdict(lambda: '1')

icondict.update({'2': '1', '10': '2', '6': '3', '19': '1'})

try:
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
        if mwid is not None:
            spotter.mwid = mwid.group(1)
        crewid = crewre.search(line)
        if crewid:
            spotter.crew = True
        if (mwid is None) and (crewid is None):
            continue
        line = sninput.readline()
        text = textre.search(line)
        spotter.text = text.group(1)
        spotters.append(spotter)
        line = sninput.readline()
except Exception:
    # traceback.print_exc(file=sys.stdout)
    sys.exit(1)

for spotter in spotters:
    if spotter.mwid is not None:
        mwoutput.write('Object: {},{}\n'.format(spotter.location[0], spotter.location[1]))
        if spotter.arrow is not None:
            mwoutput.write('Icon: {}\n'.format(spotter.arrow))
        mwoutput.write('Icon: 0,0,000,3,{},\"{}\"\nText: {}\nText: 15, 20, 1, \"{}\"\nEnd:\n'.format(spotter.icon[0],
                                                                                                     spotter.icon[1],
                                                                                                     spotter.text,
                                                                                                     spotter.mwid))
    if spotter.crew is not None:
        crewoutput.write('Object: {},{}\n'.format(spotter.location[0], spotter.location[1]))
        if spotter.arrow is not None:
            crewoutput.write('Icon: {}\n'.format(spotter.arrow))
        crewoutput.write(
            'Icon: 0,0,000,3,{},\"{}\"\nText: {}\nEnd:\n'.format(spotter.icon[0], spotter.icon[1], spotter.text))

mwoutput.write('\n')
crewoutput.write('\n')

mwfile = open("mw.txt", "w")
crewfile = open("crew.txt", "w")
mwoutput.seek(0)
crewoutput.seek(0)
mwfile.write(mwoutput.read())
mwfile.close()
crewfile.write(crewoutput.read())
crewfile.close()
mwoutput.close()
crewoutput.close()
