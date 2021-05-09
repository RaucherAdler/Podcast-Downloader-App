import feedparser
import requests
import sys
import os
import validators
import socket
import json

OutOfRange = False


def showfeeds(): #isn't working right yet
    with open('config.json', 'r+') as f:
        config = json.load(f)
    feeds = config['feeds']
    nfeeds = len(feeds)
    if nfeeds != 0:
        print('Here are your RSS Feeds:\n') #Show Feeds
        if nfeeds > 1:
            for i in range(0, nfeeds-1): #Formats Feeds to be readable    
                feed = feeds[i]
                print(str(i+1) + '. ' + feed)
        else:
            print("1. " + feeds[0])



def format_bytes(size): #from stackoverflow
    power = 2**10
    n = 0
    power_labels = {0 : '', 1: 'K', 2: 'M', 3: 'G', 4: 'Y'}
    while size > power:
        size /= power
        n += 1
    return size, power_labels[n]+'B'



def parsefeed(parsed_feed, entrynum):
    try:
        entry = parsed_feed.entries[entrynum]
        try:
            entry_dict = {'title' : entry.title, 'published' : entry.published, 'link' : entry.link, 
                'duration' : entry.itunes_duration, 'explicit' : entry.itunes_explicit, 
                'file_length' : int(entry.enclosures[0].length), 'url' : entry.enclosures[0].url}
        except:
            entry_dict = {'title' : entry.title, 'published' : entry.published, 'link' : entry.link,
                'file_length' : int(entry.enclosures[0].length), 'url' : entry.enclosures[0].url}
        return entry_dict
    except IndexError:
        global OutOfRange
        OutOfRange = True



def setfeed():
    with open('config.json', 'r+') as f:
        config = json.load(f)
    showfeeds()
    feed = True
    while feed:
        feed_option = input('\nWhat RSS Feed would you like to access? (Use line number or type a valid RSS Feed Address): ')
        if validators.url(feed_option) == True:
            addfeed = input('\nWould you like to add this RSS Feed to your default feed list? (Y/N): ')
            if addfeed == 'Y':
                config['feeds'].append(feed_option)
                with open('config.json', 'w+') as f:
                    f.seek(0)
                    json.dump(config, f, indent=4)
            feed = feed_option
            parsed_feed = feedparser.parse(feed)
            if parsed_feed is not None:
                break
            else:
                print('Invalid Feed\n')
                continue
        elif feed_option.isnumeric():
            feed_opt = int(feed_option)
            feed = config['feeds'][feed_opt-1]
            parsed_feed = feedparser.parse(feed)
            if parsed_feed is not None:
                break
            else:
                print('Invalid Feed\n')
                continue
        else:
            print('Invalid Input.\n')
            feed = True
            continue
    return parsed_feed



def is_connected(host="8.8.8.8", port=53, timeout=3): #from stackoverflow
    try:
        socket.setdefaulttimeout(timeout)
        s = socket.socket()
        s.connect((host, port))
        s.close()
        return True
    except socket.error:
        return False



def pinfo(entry):
    title = entry['title']
    link = entry['link']
    published = entry['published']
    try:
        pubtime = entry['duration']
    except:
        pubtime = None
    try:
        explicit = entry['explicit']
    except:
        explicit = None

    filelenbyte = entry['file_length']
    byte, frmt = format_bytes(filelenbyte)
    formatted_bytes = str(round(byte, 2)) + frmt

    print(f'Title: {title}')
    print(f'{link} | {formatted_bytes}')
    print(f'Duration: {pubtime}')
    print(f'Time Published: {published}')
    print(f'Explicit: {explicit}')
    


def downloadcast(url, path): #from stackoverflow (partially)
    with open(path, 'wb') as f:
        response = requests.get(url, stream=True)
        tlength = response.headers.get('content-length')
    
        if tlength is None:
            f.write(response)
        else:
            dld = 0
            tlength = int(tlength)
            for data in response.iter_content(chunk_size=round(tlength/1000)):
                dld += len(data)
                f.write(data)
                done = int(50*dld/tlength)
                sys.stdout.write('\r[{}{}]'.format('/' * done, '·' * (50-done)))
                sys.stdout.flush()
            sys.stdout.write('\n')
