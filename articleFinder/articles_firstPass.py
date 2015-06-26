from topic import Topic
from content import Content
import pymysql
import requests
from bs4 import BeautifulSoup
import sys

class Scraper:
	conn = None
	cur = None

	def __init__(self):
		global conn
		global curcomp
		


	def openCon(self):
		global conn
		global cur
		#Use this line connecting to MySQL on Linux/Unix/MacOSX
		conn = pymysql.connect(host='127.0.0.1', unix_socket='/tmp/mysql.sock', user='root', passwd=None, db='mysql', charset='utf8')
		#Use this line connecting to MySQL on Windows
		#conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd=None, db='mysql' charset='utf8')

		cur = conn.cursor(pymysql.cursors.DictCursor)
		cur.execute("USE press")

	def closeCon(self):
		global conn
		global cur
		conn.close()

	#Stores content if content does not already exist for that URL and topic
	def storeContent(self, topic, title, body, url):
		global conn
		global cur
		if(len(body) > 9999):
			body = body[:9999]
		if(len(title) > 999):
			title = title[:999]
		cur.execute("SELECT * FROM content WHERE url = %s AND topicId = %s", (url, int(topic.id)))
		if cur.rowcount == 0:
			try:
				cur.execute("INSERT INTO content (topicId, title, body, url) VALUES(%s, %s, %s, %s)", (int(topic.id), title, body, url))
			except:
				print("Could not store article")
			try:
				conn.commit()
			except:
				conn.rollback()

	#Creates a new topic in the database, if one does not exist. Returns a topic object
	def getTopicFromName(self, topicName):
		global conn
		global cur
		if topicName is None:
			return None
		print("SELECT * FROM topics WHERE name = %s", (topicName))
		cur.execute("SELECT * FROM topics WHERE name = %s", (topicName))
		if cur.rowcount == 0:
			print("INSERT INTO topics (name) VALUES(%s)", (topicName))
			cur.execute("INSERT INTO topics (name) VALUES(%s)", (topicName))
			conn.commit()
			topicId = cur.lastrowid
		else:
			topicId = cur.fetchone()['id']

		print("Creating topic with id "+str(topicId)+" and name "+str(topicName))
		topic = topic(topicId, topicName)
		return topic


	def getPage(self, url):
		session = requests.Session()
		headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36", "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"}
		req = session.get(url, headers=headers)
		bsObj = BeautifulSoup(req.text)
		return bsObj

	def getReuters(self, topic):
		bsObj = self.getPage("http://www.reuters.com/search/news?blob="+topic.name)
		searchResults = bsObj.findAll("span",{"class":"searchResult"})
		print("Search results are size: "+str(len(searchResults)))
		for result in searchResults:
			url = result.find("li",{"class":"searchHeadline"}).find("a").attrs["href"]
			print(url)
			#Reuters uses absolute URLs rather than relative ones
			pageObj = self.getPage(url)
			title = pageObj.find("h1")
			body = pageObj.find("span",{"id":"articleText"})
			if title != None and body != None:
				self.storeContent(topic, title.get_text(), body.get_text(), url)


	def getBloomberg(self, topic):
		#http://www.bloomberg.com/search?query=hubspot
		bsObj = self.getPage("http://www.bloomberg.com/search?query="+topic.name)
		searchResults = bsObj.findAll("div", {"class":"search-result"})
		print("Search results size: "+str(len(searchResults)))
		for result in searchResults:
			url = result.find("h1", {"class","search-result-story__headline"}).find("a").attrs["href"]
			url = "http://www.bloomberg.com/"+url
			print(url)
			pageObj = self.getPage(url)
			title = pageObj.find("h1", {"class":"lede-headline"})
			body = pageObj.find("section",{"class":"article-body"})
			if title != None and body != None:
				self.storeContent(topic, title.get_text(), body.get_text(), url)

	def getIReachContent(self, topic):
		bsObj = self.getPage("http://www.ireachcontent.com/search/?keywords="+topic.name)
		searchResults = bsObj.findAll("h3", {"class":"media-heading"})
		print("Search results size: "+str(len(searchResults)))
		for result in searchResults:
			#URLs are absolute
			url = result.find("a").attrs["href"]
			print(url)
			pageObj = self.getPage(url)
			title = pageObj.find("h1")
			body = pageObj.find("div", {"class":"release-text"})

			if title != None and body != None:
				self.storeContent(topic, title.get_text(), body.get_text(), url)

	def getPehub(self, topic):
		bsObj = self.getPage("https://www.pehub.com/?s="+topic.name)
		searchResults = bsObj.findAll("h2")
		print("Search results size: "+str(len(searchResults)))
		for result in searchResults:
			#URLs are absolute
			url = result.find("a").attrs["href"]
			print(url)
			pageObj = self.getPage(url)
			title = pageObj.find("h1")
			body = pageObj.find("div", {"class":"entry-content"})
			if title != None and body != None:
				self.storeContent(topic, title.get_text(), body.get_text(), url)


	def scrape(self, topicStr):
		global conn
		global cur
		topic = self.getTopicFromName(topicStr)
		self.getPehub(topic)
		self.getReuters(topic)
		self.getBloomberg(topic)
		self.getIReachContent(topic)

if len(sys.argv) < 2:
	sys.exit("Must provide a filename to read from")

f = open(sys.argv[1], 'r')
topicName = f.readline().strip()
scraper = Scraper()
scraper.openCon()

while(topicName):
	print("GETTING INFO ABOUT: "+topicName);
	scraper.scrape(topicName)
	topicName = f.readline().strip()


scraper.closeCon()



