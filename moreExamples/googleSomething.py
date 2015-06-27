from urllib.request import urlopen
html = urlopen("https://www.google.com/search?q=data%20day%20seattle&rct=j")
print(html.read())
