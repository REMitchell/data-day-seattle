import requests

session = requests.Session()
headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5)AppleWebKit 537.36 (KHTML, like Gecko) Chrome","Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"}
url = "https://www.google.com/search?q=data%20day%20seattle&rct=j"
req = session.get(url, headers=headers)

f = open('searchResults.html', 'w')
f.write(req.text)