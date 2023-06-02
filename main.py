import os
import config
from Classes.Handler import Handler

from watchdog.observers import Observer

if __name__ == '__main__':
   stopped = False
   observer = Observer()
   event_handler = Handler()
   observer.schedule(event_handler, path=os.path.abspath(config.PATH_NILSA), recursive=False)
   observer.start()
   try:
      while True:
         pass
   except KeyboardInterrupt:
      observer.stop()
   observer.join()
