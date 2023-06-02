from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.proxy import Proxy, ProxyType
from Classes.Driver import Driver
from Classes.Report import Report

class Tinder(Driver):

   data = dict()
   browser = None


   def __init__(self, data):
      self.data = data


   def run(self, browser):
      self.browser = browser
      if self.data.get('__command__').lower() == 'TinderSeleniumAuthorization'.lower():
         response = self.CheckAuthorization()


      if 'response' in locals():
         Report().write(response)



   def CheckAuthorization(self):
      try:
         self.browser.driver.get('https://tinder.com/')
         WebDriverWait(self.browser.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'nav')))
         return {'Status': 200, 'Message': 'Character is authorized'}
      except:
         return {'Status': 400, 'Message': 'Character not authorized'}