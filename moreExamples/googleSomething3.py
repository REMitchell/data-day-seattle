from selenium import webdriver
#Use this if you have PhantomJS installed (and you don't want a browser popping up)
#driver = webdriver.PhantomJS(executable_path='<Path to Phantom JS>')
driver = webdriver.Firefox()
driver.get("https://www.google.com/search?q=data%20day%20seattle&rct=j")
driver.implicitly_wait(1)
print(driver.get_cookies())