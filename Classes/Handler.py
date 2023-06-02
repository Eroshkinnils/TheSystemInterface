from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from Classes.Report import Report
from Classes.CommandHandler import CommandHandler

import os
import config
import json


class Handler(FileSystemEventHandler):
   cmdHadler = CommandHandler()


   def on_created(self, event):
      if event.is_directory == False:
         name = os.path.basename(event.src_path)
         if name == config.FILE_FLAG:
            self.reed_data()

   def reed_data(self):
      file_data = os.path.join(os.path.abspath(config.PATH_NILSA), config.FILE_DATA)
      flag = os.path.join(os.path.abspath(config.PATH_NILSA), config.FILE_FLAG)
      if os.path.isfile(file_data):
         try:
            commands = self.cmdHadler.reed_data()
            params = []
            for key, val in enumerate(commands):
               network = self.cmdHadler.get_network(val['command'])
               param = self.cmdHadler.updatePersonage(network, val['params'])
               param.update({"__network__": network})
               param.update({"__command__": val['command']})
               params.append(param)

            results = []
            for param in params:
               response = self.cmdHadler.reed_command(param)
               if response:
                  results.append(response)
            Report().write(results)

         except Exception as e:
            Report().write([{"STATUS": 401, "MESSAGE": f"ERROR: {e}"}])

      if os.path.isfile(flag):
         os.remove(flag)
