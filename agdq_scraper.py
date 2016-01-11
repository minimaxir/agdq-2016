import requests
import json
import csv
import time
import re
import os
import datetime
from random import shuffle
from bs4 import BeautifulSoup, Comment

def request_until_succeed(url, if_404_exit = False, seconds_sleep_after_request = 0):
	
	success = False
	while success is False:
		try: 	
			req = requests.get(url)
			time.sleep(seconds_sleep_after_request)
			if req.status_code == 200:
				success = True
		except Exception, e:
			print e
			time.sleep(1)
			
			print "Error for URL %s: %s" % (url, datetime.datetime.now())
			
			is_404 = '404' in str(e)
			if if_404_exit & is_404:
				return '';
			
	return req.text
	
def unicode_normalize(text):
	return text.translate(dict.fromkeys([0x201c, 0x201d, 0x2011, 0x2013, 0x2014, 0x2018, 0x2019, 0x2026, 0x2032])).encode('utf-8')
	
urls = []
count = 0
	
with open('agdq_urls.csv') as data:
	reader = csv.DictReader(data)
	for line in reader:
		urls.append(line['amount.href'])

shuffle(urls)
print len(urls)


with open('agdq_comments.csv', 'wb') as file:
	writer = csv.writer(file)
	writer.writerow(["comment","bid_category", "bid_choice", "url"])

	for url in urls:
		if url is not None:
			soup = BeautifulSoup(request_until_succeed(url), "lxml")
			if soup is None:
				continue;

			try:
				comment = '' if soup.find(attrs={"class": "Invalid Variable: commentstate"}) is None else soup.find(attrs={"class": "Invalid Variable: commentstate"}).text.strip()
				
				if comment is not '':
					comment = unicode_normalize(comment)
			except Exception, e:
				comment = ''
				
			bid_category = '' if soup.find('a', href=re.compile(r'/tracker/run/')) is None else soup.find('a', href=re.compile(r'/tracker/run/')).text
			
			if bid_category is not '':
				bid_category = unicode_normalize(bid_category)
			
			bid_choice = '' if soup.find('a', href=re.compile(r'/tracker/bid/')) is None else soup.find('a', href=re.compile(r'/tracker/bid/')).text
			
			if bid_choice is not '':
				bid_choice = unicode_normalize(bid_choice)
			
			#print [comment, bid_category, bid_choice, url]
			
			if not (comment == '' and bid_category == '' and bid_choice == ''):
				writer.writerow([comment, bid_category, bid_choice, url])
			
			count = count + 1
			if count % 1000 == 0:
				print "%s: %s" % (count, datetime.datetime.now())
			