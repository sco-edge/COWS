### Implementing to make traffics
### Making traffics on 'productpage' site(ISTIO's sample webpage)
from selenium import webdriver
from time import sleep

driver = webdriver.Chrome() # after selenium4 no need to select path

try:
        while True:
                driver.get("192.168.49.2:31880/productpage")
                sleep(3) # Every 3seconds
finally:
        driver.quit()