import json
import os, hashlib, config, re
import chardet

from Classes.Tinder import Tinder
from Classes.Whatsapp import Whatsapp
from Classes.Telegram import Telegram
from Classes.Driver import Driver
from Classes.Report import Report

class CommandHandler:

   drivers = dict()

   # Чтение коммандного файла
   def reed_data(self):
      file_data = os.path.join(os.path.abspath(config.PATH_NILSA), config.FILE_DATA)
      rows = []
      with open(file_data, 'rb') as f:
         data = f.read()
         result = chardet.detect(data)

      with open(file_data, 'r', encoding=result['encoding']) as file:
         last_param = dict()
         last_line = file.readlines()[-1]
         if ':' in last_line:
            last_param = self.pars_line(last_line)

         file.seek(0)
         for line in file.readlines():
            if line != '':
               if ':' not in line:
                  command = line.strip()
                  rows.append({'command': command, 'params': last_param})
                  index_row = len(rows) - 1
               else:
                  param = self.pars_line(line)
                  if param:
                     rows[index_row]['params'].update(param)
      return rows

   # парсинг строки файла
   def pars_line(self, line):
      param = line.split(":", maxsplit=1)
      if len(param) == 2:
         key = param[0].strip().lower()
         val = param[1].strip()

         if val:
            if key == 'id':
               return {'id': int(val)}
            elif key == 'cookies':
               return {'cookies': val}
            elif key == 'proxy':
               proxy = self.pars_proxy(val)
               return {'proxy': proxy}
            elif key == 'contacter':
               if val.isnumeric():
                  return {'cid': int(val)}
               else:
                  return {'cid': str(val)}
            elif key == 'peer_id':
               return {'peer_id': int(val)}
            elif key == 'message':
               return {'message': val}

      return None

   # парсинг строки прокси
   def pars_proxy(self, url):
      pattern = r'^(?P<protocol>http|sock5)://(?P<username>[^:]+):(?P<password>[^@]+)@(?P<ip>[^:]+):(?P<port>\d+)$'
      match = re.match(pattern, url)
      if match:
         protocol = match.group('protocol')
         username = match.group('username')
         password = match.group('password')
         ip = match.group('ip')
         port = match.group('port')
         return {"protocol": protocol, 'username': username, 'password': password, 'ip': ip, 'port': port}
      else:
         return None

   # по комманде опередяем сеть
   def get_network(self, command):
      if command.lower() in [x.lower() for x in config.TINDER]:
         return 'Tinder'
      elif command.lower() in [x.lower() for x in config.WHATSAPP]:
         return 'Whatsapp'
      elif command.lower() in [x.lower() for x in config.TELEGRAM]:
         return 'Telegram'

      return None

   def reed_command(self, data):
      if isinstance(data, dict):
         if data.get('__network__') == 'Tinder':
            driver = Tinder(data)
         elif data.get('__network__') == 'Whatsapp':
            driver = Whatsapp(data)
         elif data.get('__network__') == 'Telegram':
            driver = Telegram(data)

         browser = self.get_browser(data)
         return driver.run(browser)

   def get_browser(self, data):
      hash_cookie = hashlib.md5(data.get('cookies').encode()).hexdigest()
      if hash_cookie not in self.drivers:
         browser = Driver(data)
         self.drivers[hash_cookie] = browser
      else:
         try:
            self.drivers[hash_cookie].driver.title
         except:
            browser = Driver(data)
            self.drivers[hash_cookie] = browser
      return self.drivers[hash_cookie]

   def updatePersonage(self, network, params):
      id = params.get('id', 0)
      update_data = dict()
      if id > 0:
         person_path = os.path.abspath(f"Personages/personag_{id}")
         if os.path.isfile(person_path):
            with open(person_path, "r", encoding='utf-8') as file:
               person_data = json.loads(file.read())
         else:
            person_data = dict()

         update_data = person_data.get(network, dict())
         update_data.update(params)
         person_data[network] = update_data

         f = open(person_path, 'w', encoding='utf-8')
         f.write(json.dumps(person_data))
         f.close()
      else:
         raise Exception('No id parameter')

      return  update_data