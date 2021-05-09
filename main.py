#A program that scans RSS feeds and downloads podcasts
#Created by R. Adler

#notes
#for py 3.10 when it enters production: encorperate switch statements
#for better inputs, ln.246, rework it, consider working it into a function and add a sort of "aliasing" system, possible user keybinds, etc. as well as just a general settings menu to configure saved feeds
#add search feature
#to make case-sensitivity not an issue, make all inputs lowercase by default
#"options": {"m": "more", "more": "more", "sa": "show all", "show all": "show all", "cf": "change feed", "change feed": "change feed", "s": "search", "search": "search", "e": "end", "end": "end"}
#eventually add the above line to program

import feedparser
import requests
import sys
import os
import validators
import socket
from funcs import *
import json

OutOfRange = False


print('Welcome to Podcast Downloader by R. Adler\n')


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
        newpth = input('Where would you like to save your files?: ')
        if os.path.exists(newpth) == False: #valid path?
            dpath = None
            continue
        if newpth[0] == 'c' or newpth[0] == 'C': #windows path
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

    alt = None
    txt = None
    while not alt:
        alt = input('Is this the episode you want? (y/n): ')
        if alt.lower() == 'y':
            while not txt:
                txt = input('Would you like to download this podcast? (y/n): ')
                if txt.lower() == 'y':
                    downloadpath = dpath + entry['title'].replace('/', u'\u2044') + '.mp3'
                    print(f'Downloading {entry["title"]}')
                    downloadcast(entry['url'], downloadpath) 
                elif txt.lower() == 'n':
                    pass
                else:
                    print('Improper Input.\n')
                    txt = None
                    continue
        elif alt.lower() == 'n':
            pass
        else:
            print('Improper Input.\n')
            alt = None
            continue


    _min = 1
    _max = 6
    c = 0
    qmore = None
    DisplayMore = True
    while not qmore:
        qmore = input('Would you like to view more episodes? (y/n): ')
        if qmore.lower() == 'y':
            while True:
                if OutOfRange == False and DisplayMore == True: #doesn't work as expected
                    DisplayMore = False
                    print('Here are five more entries:\n')
                    if c != 0:
                        _min = _max
                        _max = _min + 5
                    if _max >= feed_length:
                        _max = feed_length
                        _min = feed_length - 5
                    for x in range(_min, _max):
                        x_entry = pfeed.entries[x]
                        entry_title = x_entry.title
                        print(str(x) + '. ' + entry_title + '\n')
                        if x >= feed_length:
                            OutOfRange = True
                            print('Out of entries.')
                            break
                entnum = None
                entnum = input('Which would you like view? (Type line number or for more options type "o" or "options"):\n')
                if entnum.lower() == 'end' or entnum.lower() == 'e':
                    print('Ok, Goodbye.')
                    feed = False
                    break
                elif entnum.lower() == 'options' or entnum.lower() == 'o':
                    print("Current options include:\n|letter|name       |meaning (Note: you can use either the letter or name)|\n|     o|options    |displays this                                        |\n|     m|more       |show more episodes                                   |\n|    sa|show all   |show all episodes                                    |\n|    cf|change feed|change to another feed                               |\n|     e|end        |end program                                          |\n|     s|search     |search for a string in an episode title              |")
                elif entnum.lower() == 'more' or entnum.lower() == 'm':
                    if OutOfRange == True:
                        print('There are no more entries.\n')
                    else:
                        DisplayMore = True
                        if c == 0:
                            c += 1
                    continue
                elif entnum.isnumeric():
                    entnum = int(entnum)
                    if entnum > (feed_length-1):
                        print('Invalid Entry.\n')
                        entnum = None
                        continue
                    entry = parsefeed(pfeed, entnum)
                    pinfo(entry)
                    entnum_dl_txt = None
                    entnum_dl_txt = input('Would you like to download this podcast? (Y/N): ')
                    if entnum_dl_txt.lower() == 'y':
                        downloadpath = dpath + entry['title'].replace('/', u'\u2044') + '.mp3'
                        downloadcast(entry['url'], downloadpath)
                        entnum_dl_ano = None
                        entnum_dl_ano = input('Would you like to view another? (Y/N): ')
                        if entnum_dl_ano.lower() == 'y':
                            pass
                        elif entnum_dl_ano.lower() == 'n':
                            print('Ok, Goodbye.')
                            os._exit(0)
                            break
                    elif entnum_dl_txt.lower() == 'n':
                        entnum_dl_ano = None
                        entnum_dl_ano = input('Would you like to view another? (Y/N): ')
                        if entnum_dl_ano.lower() == 'y':
                            pass
                        elif entnum_dl_ano.lower() == 'n':
                            print('Ok, Goodbye.')
                            feed = False
                            break
                    else:
                        print('Invalid Input.\n')
                        qmore = None
                        continue
                elif entnum.lower() == 'show all' or entnum.lower() == 'sa':
                    for i in range(0, feed_length):
                        entry = pfeed.entries[i]
                        entrytitle = entry.title
                        print(str(i) + '. ' + entrytitle + '\n')
                        OutOfRange = True
                        continue
                elif entnum.lower() == 'change feed' or entnum.lower() == 'cf':
                    OutOfRange = False
                    DisplayMore = True
                    break
                elif entnum.lower() == 'search' or entnum.lower() == 's':
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
                else:
                    print('Invalid Input.\n')
                    qmore = 'Y'
                    continue
        elif qmore.lower() == 'n':
            print('Ok, Goodbye.')
            feed = False
            break
        else:
            print('Invalid Input.\n')
            qmore = None
os._exit(0)
#Stuff seems fine now, hopefully.
