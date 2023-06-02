import os, json, time
import config

class Report:

   def write(self, data):
      file_data = os.path.join(os.path.abspath(config.PATH_WEB_DRIVER), config.FILE_DATA)
      flag = os.path.join(os.path.abspath(config.PATH_WEB_DRIVER), config.FILE_FLAG)

      data  = json.dumps(data)

      while True:
         if os.path.isfile(flag):
            time.sleep(5)
         else:
            f = open(file_data, 'w')
            f.write(data)
            f.close()
            f = open(flag, 'w')
            f.write('OK')
            f.close()
            break
