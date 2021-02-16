import re
import json
import time
import datetime


def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    print('cleanhtml done')
    return cleantext


def cleanjson(data):
    for i in data:
        # Remove url from image
        for j in range(len(i['images'])):
            url = i['images'][j]
            url = url.replace('https://images.craigslist.org/', '')
            url = url.replace('_50x50c.jpg', '')
            i['images'][j] = url

        # Remove symbols from price
        if i['price'] is not None:
            i['price'] = i['price'].replace('$', '')
            i['price'] = i['price'].replace(',', '')
            i['price'] = int(i['price'])
        if type(i['price']) is not int:
            i['price'] = int(0)

        # Split neighborhood into array
        split = []
        if i['result-hood'] != None:
            neighborhood = i['result-hood'].replace(' (', '')
            neighborhood = neighborhood.replace(')', '')
            neighborhood = neighborhood.replace(' / ', ',')
            split = neighborhood.split(',')
        i['neighborhood'] = split

        # Date to UNIX time
        date = i['result-date']
        element = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M")
        tuple = element.timetuple()
        i['date'] = time.mktime(tuple)

        # Split housing into array
        split = []
        if i['housing'] != None:
            rooms = i['housing'].replace('/ ', '')
            rooms = rooms.replace('ft', '')
            split = rooms.split('br - ')
            if len(split) == 1:
                tmp = split[0]
                split += [tmp]
                split[0] = ''
            if split[0] != '':
                i['bedrooms'] = int(split[0])
            else:
                i['bedrooms'] = int(0)
            if split[1] != '':
                i['area'] = int(split[1])
            else:
                i['area'] = int(0)
        else:
            i['bedrooms'] = int(0)
            i['area'] = int(0)

        # Remove qrcode text
        if i['postingbody'] != None:
            i['postingbody'] = cleanhtml(i['postingbody'])
            i['postingbody'] = i['postingbody'].replace(
                '\n        \n            QR Code Link to This Post\n            ',
                '')
            i['postingbody'] = i['postingbody'].replace('\n        ', '')
            i['postingbody'] = re.sub('\n', '<br/ >', i['postingbody'])
            # i['postingbody'] = i['postingbody'].replace('\n', '<br/>')
        # Delete unused
        unused = ['url', 'result-price', 'housing', 'result-hood', 'result-tags', 'result-date', 'postinginfo',
                  'titletextonly', 'attrgroup', 'hood']
        for j in unused:
            del i[j]
    print("cleanjson done")
    return data


if __name__ == '__main__':
    x = open("apts.json", "r+")
    data = json.load(x)
    x.close()

    data = cleanjson(data)

    with open("apts_clean.json", "w") as outfile:
        json.dump(data, outfile)
    with open("apts_clean.json", "r") as outfile:
        y = outfile.read()

    # y = cleanhtml(y)
    y = y.replace('"postingbody":', '"body":')
    y = y.replace('"result-title":', '"title":')
    y = y.replace('\n          ', '')

    with open("apts_clean_nohtml.json", "w") as outfile:
        outfile.write(y)
