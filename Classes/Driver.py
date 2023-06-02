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

import zipfile
import os

class Driver:
   data = dict()
   driver = None

   def __init__(self, data):
      self.data = data

      screen_width = 800
      screen_height = 500
      scale = 100

      absolute_path = os.path.abspath("Webdriver")
      service = Service(ChromeDriverManager(path=absolute_path).install())

      options = webdriver.ChromeOptions()
      absolute_path = data.get('cookies')
      options.add_argument(f'user-data-dir={absolute_path}')
      options.add_argument('--allow-profiles-outside-user-dir')
      options.add_argument('--profiling-flush=10')
      options.add_argument('--enable-aggressive-domstorage-flushing')
      options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")
      options.add_argument("--disable-blink-features=AutomationControlled")
      options.add_argument(f"--window-size={screen_width},{screen_height}")
      options.add_argument("--disable-fullscreen")
      options.add_experimental_option("detach", True)
      options.add_experimental_option("excludeSwitches", ['enable-automation'])

      if  'proxy' in data:
         if data['proxy']:
            manifest_json = """
            {
               "version": "1.0.0",
               "manifest_version": 2,
               "name": "Chrome Proxy",
               "permissions": [
                   "proxy",
                   "tabs",
                   "unlimitedStorage",
                   "storage",
                   "<all_urls>",
                   "webRequest",
                   "webRequestBlocking"
               ],
               "background": {
                   "scripts": ["background.js"]
               },
               "minimum_chrome_version":"76.0.0"
            }
            """

            background_js = """
            let config = {
                    mode: "fixed_servers",
                    rules: {
                    singleProxy: {
                        scheme: "%s",
                        host: "%s",
                        port: parseInt(%s)
                    },
                    bypassList: ["localhost"]
                    }
                };
            chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});
            function callbackFn(details) {
                return {
                    authCredentials: {
                        username: "%s",
                        password: "%s"
                    }
                };
            }
            chrome.webRequest.onAuthRequired.addListener(
                        callbackFn,
                        {urls: ["<all_urls>"]},
                        ['blocking']
            );
            """ % (data['proxy']['protocol'],data['proxy']['ip'], data['proxy']['port'], data['proxy']['username'], data['proxy']['password'])

            plugin_file =os.path.abspath(f"Proxy/{data['proxy']['ip']}.zip")
            with zipfile.ZipFile(plugin_file, 'w') as zp:
               zp.writestr('manifest.json', manifest_json)
               zp.writestr('background.js', background_js)
            options.add_extension(plugin_file)

      self.driver = webdriver.Chrome(service=service, options=options)
      self.driver.execute_script(f"document.body.style.zoom='{scale}%'")
