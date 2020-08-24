#A program that scans RSS feeds and downloads podcasts
#Created by R. Adler

import feedparser
import urllib.request
import linecache
import sys
import time
import threading
import os

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


def NextEntries(a, b, c): #Gets next entries in a feed and formats them then prints
    c = c * 5
    a = a + c
    b = b + c
    EntryRange = range(a, b)
    for i in EntryRange:
        try:
            NextEntries.ntry = parsefeed.feed.entries[i]
        except IndexError:  
            NextEntries.OutOfRange = True
            print('There are no more entries.\n')
            return False
        else:
            NextEntries.titles = NextEntries.ntry.title
            print(str(i) + '. ' + NextEntries.titles + '\n')
            NextEntries.OutOfRange = False


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


def parsefeed(rssfeed, entryinfeed):
    parsefeed.feed = feedparser.parse(rssfeed)
    parsefeed.entry = parsefeed.feed.entries[entryinfeed]
    parsefeed.title = parsefeed.entry.title
    parsefeed.published = parsefeed.entry.published
    parsefeed.link = parsefeed.entry.link
    parsefeed.itunes_duration = parsefeed.entry.itunes_duration
    parsefeed.itunes_explicit = parsefeed.entry.itunes_explicit
    parsefeed.url = parsefeed.entry.enclosures[0].url
    parsefeed.path = dpath + parsefeed.title + '.mp3'


def downloadcast():
    print('Preparing Download...')
    url = parsefeed.url
    path = parsefeed.path
    print('Downloading...')
    with Spinner():
        urllib.request.urlretrieve(url, path)
    print('Download Completed.')


def setfeed():
    def_feed = open('def-feed.txt', 'a+')
    other = '\u0332'.join('other.')
    showfeeds()
    feed_option = None
    while not feed_option:
        feed_option = input('\nWhat RSS Feed would you like to access?(Use line number or type ' + other + ')'+'\n')
        if feed_option == 'other':
            nfeed = input('What RSS Feed would you like to access?:\n')
            addfeed = input('Would you like to add this RSS Feed to you default list?\n(Y or N): ')
            if addfeed == "Y": #Adds new feed to def-feed.txt, gets proper line to write to.
                dfeed = linecache.getline('def-feed.txt', 1)
                if dfeed:
                    def_feed.write('\n' + nfeed)
                else:
                    def_feed.write(nfeed)
            feed = nfeed
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


print('Welcome to Podcast Downloader by R. Adler\n')


#This chunk sets file path for downloads
def_path = open('def-path.txt', 'a+')
pth = linecache.getline('def-path.txt', 1).split('\n')
dpath = pth[0]
if not dpath:
    newpth = input('Where would you like to save your files? (Make sure to include closing slash.)')
    def_path.write(newpth)
print('All files will download to: ', dpath,'\n')
def_path.close()


feed = "feed"
while feed:
    feed = setfeed() #Ignore this warning.
    parsefeed(feed, 0) #Something is NOT RIGHT!
    pfeed = parsefeed.feed
    feed_length = len(pfeed.entries)


    print('\nMost Recent:')
    print(parsefeed.title, '\n', parsefeed.link, '\n', 'Duration: ', parsefeed.itunes_duration, '\n','Time Published:', parsefeed.published, '\n', 'Explicit: ', parsefeed.itunes_explicit, '\n')


    alt = None
    txt = None
    while not alt:
        alt = input('Is this the episode you want?\n(Y or N): ')
        if alt == 'Y':
            while not txt:
                txt = input('Would you like to download this podcast?\n(Y or N): ')
                if txt == 'Y':
                    downloadcast()
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

    try:  #Gets Attribute or sets Attribute
        getattr(NextEntries, 'OutOfRange')
    except AttributeError:
        setattr(NextEntries, 'OutOfRange', False)


    c = 0
    qmore = None
    while not qmore:
        qmore = input('Would you like to view more episodes?\n(Y or N): ')
        if qmore == 'Y':
            while qmore == 'Y':
                if NextEntries.OutOfRange == False:
                    print('Here are five more entries:\n')
                    NextEntries(1, 6, c)
                entnum = None
                entnum = input('Which would you like view? (Type line number or type More to show more. Type Show All to show all entries. Type Change Feed to switch feeds. Else, type End):\n')
                if entnum == 'End':
                    print('Ok, Goodbye.\n')
                    os._exit(0)
                elif entnum == 'More':
                    if NextEntries.OutOfRange == True:
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
                    else:
                        pass
                    parsefeed(pfeed, entnum)
                    print(parsefeed.title, '\n', parsefeed.link, '\n', 'Duration: ', parsefeed.itunes_duration, '\n','Time Published:', parsefeed.published, '\n', 'Explicit: ', parsefeed.itunes_explicit, '\n')
                    entnum_dl_txt = None
                    entnum_dl_txt = input('Would you like to download this podcast?\n(Y or N): ')
                    if entnum_dl_txt == 'Y':
                        downloadcast()
                        entnum_dl_ano = None
                        entnum_dl_ano = input('Would you like to view another?\n(Y or N): ')
                        if entnum_dl_ano == 'Y':
                            pass
                        elif entnum_dl_ano == 'N':
                            print('Ok, Goodbye.\n')
                            os._exit(0) 
                    elif entnum_dl_txt == 'N':
                        entnum_dl_ano = None
                        entnum_dl_ano = input('Would you like to view another?\n(Y or N): ')
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
                    for i in range(0, (feed_length)):
                        entrytitle = parsefeed.title
                        print(str(i+1) + '. ' + entrytitle + '\n')
                        NextEntries.OutOfRange = True
                        continue
                elif entnum == 'Change Feed':
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
