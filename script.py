#northwind
from bs4 import BeautifulSoup
import datetime
from random import randint
from random import shuffle
from time import sleep
from urllib.request import Request
from urllib.request import urlopen

def get_html(url):
    
    html_content = ''
    try:
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'}) #hdr)
        html_page = urlopen(req).read()
        html_content = BeautifulSoup(html_page, "html.parser")
    except: 
        pass
        
    return html_content

def get_details(url):
    
    stamp = {}
    
    try:
        html = get_html(url)
    except:
        return stamp

    try:
        price = html.select('.product-price')[0].get_text().strip()
        stamp['price'] = price.replace('$', '').replace(',', '').replace('CAD', '').strip()
    except: 
        stamp['price'] = None
        
    try:
        title = html.select('.product-single__title')[0].get_text().strip()
        stamp['title'] = title
    except:
        stamp['title'] = None    
        
    try:
        sold_out_href = html.find('link', {'itemprop':'availability'}).get('href')
        if 'OutOfStock' in sold_out_href:
            stamp['sold'] = 1
        else:
            stamp['sold'] = 0
    except:
        stamp['sold'] = 0

    try:
        collection_title = html.select('.collection-title')[0].get_text()
        categories = collection_title.split(':')
        category = categories[0].strip()
        sub_category = categories[1].strip()
        stamp['country'] = category
        stamp['sub_category'] = sub_category
    except:
        stamp['country'] = None        
        stamp['sub_category'] = None        

    stamp['currency'] = "CAD"

    # image_urls should be a list
    images = []                    
    try:
        image_items = html.select('.product-single__thumb')
        if image_items:
            for image_item in image_items:
                img_temp = image_item.get('href').replace('//', '')
                if img_temp:
                    img_parts = img_temp.split('?v=') 
                    img = img_parts[0]
                    if img not in images:
                        img = 'https://' + img
                        images.append(img)
        else:     
            img = get_value('data-zoom="//', '?v=', html)
            if img:
                img = 'https://' + img
                images.append(img)
    except:
        pass
    
    stamp['image_urls'] = images 
    
    try:
        raw_text = html.select('.product-single__desc')[0].get_text().strip()
        stamp['raw_text'] = raw_text.replace('\xa0',' ')
    except:
        stamp['raw_text'] = None
        
    if stamp['raw_text'] == None and stamp['title'] != None:
        stamp['raw_text'] = stamp['title']

    # scrape date in format YYYY-MM-DD
    scrape_date = datetime.date.today().strftime('%Y-%m-%d')
    stamp['scrape_date'] = scrape_date

    stamp['url'] = url
    print(stamp)
    print('+++++++++++++')
    sleep(randint(25, 65))
           
    return stamp

def get_page_items(url):

    items = []
    next_url = ''

    try:
        html = get_html(url)
    except:
        return items, next_url

    try:
        for item in html.select('a.product'):
            item_link = 'https://northwindstamps.com' + item.get('href').replace('&amp;', '&').strip()
            if item_link not in items:
                items.append(item_link)
    except:
        pass

    try:
        next_item = html.find("link", {"rel":"next"})
        next_url = 'https://northwindstamps.com' + next_item.get('href') 
    except:
        pass
    
    shuffle(list(set(items)))
    
    return items, next_url

def get_country_names():
    
    url = 'https://northwindstamps.com'
    
    items = []

    try:
        html = get_html(url)
    except:
        return items

    try:
        for item in html.select('#accessibleNav .site-nav__linkdrop'):
            item_text = item.get_text().strip()
            if item_text not in items:
                items.append(item_text)
    except: 
        pass

    return items

def get_subcategories(category):
    
    url = 'https://northwindstamps.com'
    
    items = []

    try:
        html = get_html(url)
    except:
        return items

    try:
        for item_cont in html.select('#accessibleNav .site-nav__dropdown'):
            item_cont_heading = item_cont.parent.select('a.site-nav__linkdrop')[0].get_text().strip()
            if category in item_cont_heading:
                for item in item_cont.select('li a'):
                    item_link = 'https://northwindstamps.com' + item.get('href')
                    if item_link not in items:
                        items.append(item_link)
    except: 
        pass
    
    shuffle(items)
    
    return items

def get_value(sep1,sep2, string):
    string = str(string)
    parts1 = string.split(sep1)
    parts2 = parts1[1].split(sep2)
    return parts2[0]

countries = get_country_names()
for country in countries:
    print(country)

selection = input('Choose category: ')
            
subcategories = get_subcategories(selection)
for subcategory in subcategories:
    page_url = subcategory
    while(page_url):
        page_items, page_url = get_page_items(page_url)
        for page_item in page_items:
            stamp = get_details(page_item)
    
 