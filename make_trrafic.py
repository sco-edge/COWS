### Implementing to make traffics
from selenium import webdriver
from time import sleep

driver = webdriver.Chrome()

try:
        while True:
                driver.get("192.168.49.2:31880/productpage")
                sleep(3) # Every 3seconds
finally:
        driver.quit()