#A program that scans RSS feeds and downloads podcasts
#Created by R. Adler

import feedparser
import urllib.request
import linecache
import sys
import time
import threading
import os
import validators


class Spinner(): #Borrowed from stackoverflow
    busy = False
    delay = 0.1
    
    @staticmethod
    def spinning_cursor():
        while 1:
            for cursor in '|/—\\':
                yield cursor
    
    def __init__(self, delay=None):
        self.spinner_generator = self.spinning_cursor()
        if delay and float(delay): self.delay = delay

    def spinner_task(self):
        while self.busy:
            sys.stdout.write(next(self.spinner_generator))
            sys.stdout.flush()
            time.sleep(self.delay)
            sys.stdout.write('\b')
            sys.stdout.flush()
            
    def __enter__(self):
        self.busy = True
        threading.Thread(target=self.spinner_task).start()
        
    def __exit__(self, exception, value, tb):
        self.busy = False
        time.sleep(self.delay)
        if exception is not None:
            return False


def showfeeds():
    def_feed = open('def-feed.txt', 'a+')
    print('Here are your RSS Feeds:') #Show Feeds
    def_feed.seek(0)
    nlines = sum(1 for line in open('def-feed.txt'))
    for i in range(1, nlines+1): #Formats Feeds to be readable
        with open('def-feed.txt') as f:
            linep = f.readlines()
            linepr = linep[i-1]
        print(str(i) + '. ' + linepr)
    def_feed.close()


OutOfRange = False
def parsefeed(parsed_feed, entrynum):
    try:
        entry = parsed_feed.entries[entrynum]
        entry_dict = {'title' : entry.title, 'published' : entry.published, 'link' : entry.link, 
                'itunes_duration' : entry.itunes_duration, 'itunes_explicit' : entry.itunes_explicit, 
                'url' : entry.enclosures[0].url}
        return entry_dict
    except IndexError:
        global OutOfRange
        OutOfRange = True


def downloadcast(url, path, entry_title):
    dpath = path + entry_title.replace('/', u'\u2044') + '.mp3'
    print('Downloading...')
    with Spinner():
        urllib.request.urlretrieve(url, dpath)
    print('Download Completed.')



def setfeed():
    def_feed = open('def-feed.txt', 'a+')
    other = u'\u0332'.join('other.')
    showfeeds()
    feed_option = None
    while not feed_option:
        feed_option = input('\nWhat RSS Feed would you like to access?(Use line number or type a valid RSS Feed Address): ')
        if validators.url(feed_option) == True:
            addfeed = input('\nWould you like to add this RSS Feed to you default list? (Y/N): ')
            if addfeed == "Y": #Adds new feed to def-feed.txt, gets proper line to write to.
                dfeed = linecache.getline('def-feed.txt', 1)
                if dfeed:
                    def_feed.write('\n' + feed_option)
                else:
                    def_feed.write(feed_option)
            feed = feed_option
        elif feed_option.isnumeric() == True:
            feed_opt = int(feed_option)
            feed_address = linecache.getline('def-feed.txt', feed_opt)
            feed = feed_address
        else:
            print('Improper Input.\n')
            feed_option = None
            continue
    def_feed.close()
    return feed


def is_connected():
    try:
        urllib.request.urlopen('https://google.com')
        return True
    except:
        False


print('Welcome to Podcast Downloader by R. Adler\n')


#This chunk sets file path for downloads
def_path = open('def-path.txt', 'a+')
pth = linecache.getline('def-path.txt', 1).split('\n')
dpath = r'{}'.format(pth[0])
if not dpath:
    newpth = input('Where would you like to save your files? (Make sure to include closing slash.)')
    def_path.write(newpth)
    dpath = r'{}'.format(newpth)
print('All files will download to: ', dpath,'\n')
def_path.close()


if is_connected() != True:
    print('You must be connected to the internet.')
    os._exit(1)


feed = "feed"
while feed:
    feed = setfeed() #Ignore this warning.
    pfeed = feedparser.parse(feed)
    entry = parsefeed(pfeed, 0)
    
    feed_length = len(pfeed.entries)


    print('\nMost Recent:')
    print(f"{entry['title']}\n{entry['link']}\nDuration: {entry['itunes_duration']}\nTime Published: {entry['published']}\nExplicit: {entry['itunes_explicit']}")


    alt = None
    txt = None
    while not alt:
        alt = input('Is this the episode you want?\n(Y/N): ')
        if alt == 'Y':
            while not txt:
                txt = input('Would you like to download this podcast?\n(Y/N): ')
                if txt == 'Y':
                    downloadcast(entry['url'], dpath, entry['title'])
                elif txt == 'N':
                    pass
                else:
                    print('Improper Input.\n')
                    txt = None
                    continue
        elif alt == 'N':
            pass
        else:
            print('Improper Input.\n')
            alt = None
            continue


    _min = 1
    _max = 6
    c = 0
    qmore = None
    while not qmore:
        qmore = input('Would you like to view more episodes?\n(Y/N): ')
        if qmore == 'Y':
            while qmore == 'Y':
                if OutOfRange == False:
                    print('Here are five more entries:\n')
                    _min = _min + c
                    _max = _max + c
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
                entnum = input('Which would you like view? (Type line number or type More to show more. Type Show All to show all entries. Type Change Feed to switch feeds. Else, type End):\n')
                if entnum == 'End':
                    print('Ok, Goodbye.\n')
                    os._exit(0)
                elif entnum == 'More':
                    if OutOfRange == True:
                        print('There are no more entries.\n')
                    else:    
                        c = c + 1
                    continue
                elif entnum.isnumeric():
                    entnum = int(entnum)
                    if entnum > (feed_length-1):
                        print('Invalid Entry.\n')
                        entnum = None
                        continue
                    entry = parsefeed(pfeed, entnum)
                    print(f"{entry['title']}\n{entry['link']}\nDuration: {entry['itunes_duration']}\nTime Published: {entry['published']}\nExplicit: {entry['itunes_explicit']}")
                    entnum_dl_txt = None
                    entnum_dl_txt = input('Would you like to download this podcast? (Y/N): ')
                    if entnum_dl_txt == 'Y':
                        downloadcast(entry['url'], dpath, entry['title'])
                        entnum_dl_ano = None
                        entnum_dl_ano = input('Would you like to view another? (Y/N): ')
                        if entnum_dl_ano == 'Y':
                            pass
                        elif entnum_dl_ano == 'N':
                            print('Ok, Goodbye.\n')
                            os._exit(0) 
                    elif entnum_dl_txt == 'N':
                        entnum_dl_ano = None
                        entnum_dl_ano = input('Would you like to view another? (Y/N): ')
                        if entnum_dl_ano == 'Y':
                            pass
                        elif entnum_dl_ano == 'N':
                            print('Ok, Goodbye.\n')
                            os._exit(0)
                    else:
                        print('Invalid Input.\n')
                        qmore = None
                        continue
                elif entnum == 'Show All':
                    for i in range(0, feed_length):
                        entry = pfeed.entries[i]
                        entrytitle = entry.title
                        print(str(i) + '. ' + entrytitle + '\n')
                        OutOfRange = True
                        continue
                elif entnum == 'Change Feed':
                    OutOfRange = False
                    break
                else:
                    print('Invalid Input.\n')
                    qmore = 'Y'
                    continue
        elif qmore == 'N':
            print('Ok, Goodbye.\n')
            os._exit(0)
        else:
            print('Invalid Input.\n')
            qmore = None
            continue
#Stuff seems fine now, hopefully.
