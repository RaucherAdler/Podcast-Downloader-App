#A program that scans RSS feeds and downloads podcasts
#Created by R. Adler

#notes
#for better inputs, ln.246, rework it, consider working it into a function and add a sort of "aliasing" system, possible user keybinds, etc. as well as just a general settings menu to configure saved feeds
#improve search syntax
#eventually add the above line to program
#rework path handling

import os
from funcs import *
import json

OutOfRange = False

helptext = "Current options include:\n\
        |letter|name       |meaning (Note: you can use either the letter or name)|\n\
        |     o|options    |displays this                                        |\n\
        |     m|more       |show more episodes                                   |\n\
        |    sa|show all   |show all episodes                                    |\n\
        |    cf|change feed|change to another feed                               |\n\
        |     e|end        |end program                                          |\n\
        |     s|search     |search for a string in an episode title              |"
options = ["o", "m", "sa", "cf", "e", "s", "options", "more", "show all", "change feed", "end", "search"]


#Set download path
with open('config.json', 'a+') as f:
    try:
        f.seek(0)
        config = json.load(f)
    except:
        config = {
                'dir': '',
                "feeds": []
                }
        json.dump(config, f, indent=4)

pth = config['dir']
dpath = r'{}'.format(pth)
if not dpath:
    while not dpath:
        newpth = input('Where would you like to save your files?: ').strip()
        if os.path.exists(newpth) == False: #valid path?
            dpath = None
            continue
        if newpth[0].lower() == 'c': #windows path
            if newpth[-1] != '\\':
                newpth = newpth + '\\'
        else: #non-windows path
            if newpth[-1] != '/':
                newpth = newpth + '/'
        with open('config.json', 'w+') as f:
            config['dir'] = newpth
            f.seek(0)
            json.dump(config, f, indent=4)
        dpath = r'{}'.format(newpth)
print('All files will download to: ', dpath,'\n')


if is_connected() != True:
    print('You must be connected to the internet.')
    os._exit(1)


feed = "feed"
while feed:
    pfeed = setfeed()
    entry = parsefeed(pfeed, 0)
    feed_length = len(pfeed.entries)


    print('\nMost Recent:')
    pinfo(entry)

    _min = 0
    _max = 5
    c = 0
    DisplayMore = True
    while True:
        if OutOfRange == False and DisplayMore == True:
            DisplayMore = False
            print('\nHere are five more entries:\n')
            if c != 0:
                _min = _max
                _max = _min + 5
            if _max >= feed_length:
                _max = feed_length
                _min = feed_length - 5
            for x in range(_min, _max):
                x_entry = pfeed.entries[x]
                entry_title = x_entry.title
                print(str(x+1) + '. ' + entry_title + '\n')
                if x >= feed_length:
                    OutOfRange = True
                    print('Out of entries.')
                    break
        entstr = None
        entstr = input('Which would you like view? (Type line number or for more options type "o" or "options"):\n').strip().lower()
        try:
            optnum = options.index(entstr) % len(options)
            match(optnum):
                case 0: #options
                    print(helptext)
                case 1: #more
                    if OutOfRange == True:
                        print("There are no more entries.\n")
                    else:
                        DisplayMore = True
                        if c == 0: c = 1
                    continue
                case 2: #show all
                    for i in range(0, feed_length):
                        entry = pfeed.entries[i]
                        entrytitle = entry.title
                        print(str(i+1) + '. ' + entrytitle + '\n')
                        OutOfRange = True
                case 3: #change feed
                    OutOfRange = False
                    DisplayMore = True
                    break
                case 4: #end
                    print("Goodbye.")
                    feed = False
                    break
                case 5: #search
                    searchstr = input('Search for: ').lower()
                    ineps = []
                    for ind, fd in enumerate(pfeed.entries):
                        if searchstr in fd['title'].lower():
                            ineps.append(ind)
                    if len(ineps) == 0:
                        print('No Episodes Found')
                    else:
                        print('String found in:\n')
                        for x in ineps:
                            print(f'{str(x+1)}. {pfeed.entries[x]["title"]}')
        except ValueError:
            if entstr.isnumeric():
                entnum = int(entstr)
                if entnum > feed_length:
                    print('Invalid Entry.\n')
                    entstr = None
                    continue
                entry = parsefeed(pfeed, entnum - 1)
                pinfo(entry)
                downloadq = None
                downloadq = input('Would you like to download this episode? (Y/N): ').strip().lower()
                if downloadq == 'y':
                    downloadpath = dpath + entry['title'].replace('/', u'\u2044') + '.mp3'
                    downloadcast(entry['url'], downloadpath)
                elif downloadq != 'n':
                    print('Invalid Input.\n')
            else:
                print('Invalid Input.\n')
                continue
os._exit(0)
#Stuff seems fine now, hopefully.
