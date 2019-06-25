#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Written as part of https://www.scrapehero.com/how-to-scrape-amazon-product-reviews-using-python/
# edited: agalan2021
from lxml import html
import requests
import xlsxwriter
from dateutil import parser as dateparser
from time import sleep
from random import randint

# https://udger.com/resources/ua-list/browser-detail?browser=Chrome
users = [
			'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/532.2 (KHTML, like Gecko) Chrome/4.0.223.3 Safari/532.2',
			'Mozilla/5.0 (X11; U; Linux x86_64; en-US) AppleWebKit/540.0 (KHTML,like Gecko) Chrome/9.1.0.0 Safari/540.0',
			'Mozilla/5.0 (X11; U; Windows NT 6; en-US) AppleWebKit/534.12 (KHTML, like Gecko) Chrome/9.0.587.0 Safari/534.12',
			'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.45 Safari/535.19',
			'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/530.5 (KHTML, like Gecko) Chrome/2.0.173.1 Safari/530.5',
			'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.36 Safari/535.7',
			'Mozilla/5.0 (Windows NT 6.0; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.66 Safari/535.11',
			'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.71 Safari/537.36',
			'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/534.14 (KHTML, like Gecko) Chrome/9.0.600.0 Safari/534.14',
			'Mozilla/5.0 (X11; U; Linux x86_64; en-US) AppleWebKit/540.0 (KHTML,like Gecko) Chrome/9.1.0.0 Safari/540.0'
		]

def ParseReviews(asin):
	for i in range(5):
		try:
			amazon_url  = 'https://www.amazon.com/dp/'+asin
			header = {'User-Agent' : users[randint(0,len(users)-1)]}

			page = requests.get(amazon_url,headers = header)
			page_response = page.text
			parser = html.fromstring(page_response)

			XPATH_NO_REVIEWS = '//*[@id="acrCustomerWriteReviewText"]//text()'
			XPATH_TOTAL_REVIEWS = '//*[@id="acrCustomerReviewText"]//text()'
			XPATH_RATING = '//*[@id="acrPopover"]/span[1]/a/i[1]/span//text()'

			raw_no_reviews = parser.xpath(XPATH_NO_REVIEWS)
			noReviews = ''.join(raw_no_reviews)

			if noReviews:
				totalReviews = '0'
				rating = '0'
			else:
				raw_total_reviews = parser.xpath(XPATH_TOTAL_REVIEWS)
				raw_rating = parser.xpath(XPATH_RATING)
				totalReviews = ''.join(raw_total_reviews).partition(' ')[0]
				rating = ''.join(raw_rating).partition(' ')[0]

			try:
				totalReviews[0]
			except IndexError:
				raise ValueError

			return totalReviews, rating
		except ValueError:
			print "Retrying to get the correct response"
	print "Error: Failed to process page"
	return 'Error','Error'

def ReadAsin():
	# Read Asins from input.txt file
	# Workbook references the xlsxwriter / sheet is the actual excel worksheet that data is being printed on
	AsinList = []
	with open('asins.txt','r') as fi:
		AsinList = fi.read().splitlines()
	workbook = xlsxwriter.Workbook('output.xlsx')
	sheet = workbook.add_worksheet()
	bold = workbook.add_format({'bold': True})
	sheet.set_column(1, 1, 12)
	sheet.write('A1', 'ASIN', bold)
	sheet.write('B1', 'Reviews', bold)
	sheet.write('C1', 'Stars', bold)
	# set to width 10
	row, col = 1, 0
	for asin in AsinList:
		print "Downloading and processing page https://www.amazon.com/dp/"+asin
		print '...'+str(row)
		data = ParseReviews(asin) # [0] : total reviews, [1] : rating
		sheet.write(row, col, asin)
		sheet.set_column(row, col, 12)
		sheet.write(row, col + 1, data[0])
		sheet.set_column(row, col, 12)
		sheet.write(row, col + 2, data[1])
		sheet.set_column(row, col, 12)
		row += 1
		sleep(5)
	print 'Asin List Complete'
	workbook.close()

if __name__ == '__main__':
	ReadAsin()
