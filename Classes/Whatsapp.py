import os.path
import os
import glob
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
from pydub import AudioSegment
import Classes.Utils as Utils
import config
import time
import requests

class Whatsapp(Driver):

   data = dict()
   browser = None


   def __init__(self, data):
      self.data = data


   def run(self, browser):
      self.browser = browser
      if self.data.get('__command__').lower() == 'WHATSAPP_SELENIUM_AUTHORIZATION'.lower():
         response = self.CheckAuthorization()
      elif self.data.get('__command__').lower() == 'WHATSAPP_SELENIUM_SEND_MESSAGE'.lower():
         response = self.SendMessage()
      elif self.data.get('__command__').lower() == 'WHATSAPP_SELENIUM_SEND_MESSAGE_GPT'.lower():
         response = self.SendMessage(True)
      elif self.data.get('__command__').lower() == 'WHATSAPP_SELENIUM_NEW_MESSAGES'.lower():
         response = self.NewMessages()
      elif self.data.get('__command__').lower() == 'WHATSAPP_SELENIUM_CONTACTER_MESSAGE'.lower():
         response = self.NewMessages(True)
      elif self.data.get('__command__').lower() == 'WHATSAPP_SELENIUM_UNREAD_CONTACTER_MESSAGES'.lower():
         response = self.UnreadCidMessage()
      elif self.data.get('__command__').lower() == 'WHATSAPP_SELENIUM_GET_PHOTO_PERSONE'.lower():
         response = self.GetPhotoPersonage()
      elif self.data.get('__command__').lower() == 'WHATSAPP_SELENIUM_GET_PHOTO_CONTACTER'.lower():
         response = self.GetPhotoContacter()
      elif self.data.get('__command__').lower() == 'WHATSAPP_SELENIUM_GET_FIRST_NAME_PERSONE'.lower():
         response = self.GetPersonage(['FIRST_NAME'])
      elif self.data.get('__command__').lower() == 'WHATSAPP_SELENIUM_GET_LAST_NAME_PERSONE'.lower():
         response = self.GetPersonage(['LAST_NAME'])
      elif self.data.get('__command__').lower() == 'WHATSAPP_SELENIUM_GET_FIRST_NAME_CONTACTER'.lower():
         response = self.GetContacter(['FIRST_NAME'])
      elif self.data.get('__command__').lower() == 'WHATSAPP_SELENIUM_GET_LAST_NAME_CONTACTER'.lower():
         response = self.GetContacter(['LAST_NAME'])


      if 'response' in locals():
         if 'id' in self.data:
            response.update({'ID':self.data['id']})
         response['MESSAGE'] = response['MESSAGE'].upper()
         response['COMMAND'] = self.data.get('__command__').upper()
         return response
      return False


   # Проверка авторизован ли персонаж или нет
   def CheckAuthorization(self):
      try:
         current_url = self.browser.driver.current_url
         if current_url != 'https://web.whatsapp.com/':
            self.browser.driver.get("https://web.whatsapp.com/")
         WebDriverWait(self.browser.driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'header[data-testid=chatlist-header]')))
         return {'STATUS': 200, 'MESSAGE': 'PERSONEN AUTHORIZED'}
      except:
         return {'STATUS': 400, 'MESSAGE': 'PERSONEN NOT AUTHORIZED'}


   # Отправка сообщения
   def SendMessage(self, gpt = False):
      is_auth = self.CheckAuthorization();
      if is_auth['STATUS'] == 200:
         if 'cid' in self.data :
            if 'message' in self.data:
               self.browser.driver.get(f"https://web.whatsapp.com/send?phone={self.data['cid']}&app_absent=0")
               try:
                  WebDriverWait(self.browser.driver, 45).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-testid=conversation-compose-box-input]')))
               except:
                  self.esc(2)
                  return {'STATUS': 400, 'MESSAGE': 'FAILED TO OPEN DIALOG'}
               try:
                  compose_box =self.browser.driver.find_element(By.CSS_SELECTOR, 'div[data-testid=conversation-compose-box-input]')
                  compose_box.click()
                  compose_box.clear()
                  action = ActionChains(self.browser.driver)
                  action.move_to_element(compose_box).click()

                  if gpt == True:
                     self.data['message'] = Utils.chatGpt(self.data['message'])
                     if not self.data['message']:
                        return {'STATUS': 400, 'MESSAGE': 'FAILED TO GET RESPONSE FROM CHAT-GPT'}

                  self.data['message'] = self.data['message'].replace('\\n', '\n').replace('<br>', '\n')
                  for char in self.data['message']:
                     if char == '\n':
                        action.key_down(Keys.SHIFT).send_keys(Keys.RETURN).key_up(Keys.SHIFT)
                     else:
                        action.send_keys(char)
                     action.pause(0.03)
                  action.perform()
                  compose_box.send_keys(Keys.ENTER)
                  self.esc(3)
                  return {'STATUS': 200, 'MESSAGE': 'MESSAGE SENT SUCCESSFULLY', 'TEXT':self.data['message'], 'CONTACTER': self.data['cid']}
               except Exception as e:
                  self.esc(2)
                  return {'STATUS': 400, 'MESSAGE': f'FAILED TO SEND MESSAGE. [ ERROR: {e} ]','CONTACTER': self.data['cid']}
            else:
               return {'STATUS': 400, 'MESSAGE': 'NOT MESSAGES TO SEND', 'CONTACTER': self.data['cid']}
         else:
            return {'STATUS': 400, 'MESSAGE': 'NO CONTACTER PARAMETER, MESSAGE CANNOT BE SENT'}
      else:
         return  is_auth

   # Получить список новых сообщений
   def NewMessages(self, is_sid = False):
      is_auth = self.CheckAuthorization();
      if is_auth['STATUS'] == 200:
         try:
            self.browser.driver.get("https://web.whatsapp.com/")
            WebDriverWait(self.browser.driver, 80).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'span[data-testid=filter]')))
            self.browser.driver.find_element(By.CSS_SELECTOR, 'span[data-testid=filter]').click()

            time.sleep(3)

            New_messages = []
            try:
               rows = self.browser.driver.find_elements(By.CSS_SELECTOR, 'div[data-testid=cell-frame-container]')
            except:
               rows = []
            if len(rows) > 0:
               for row in rows:
                  data = dict()

                  try:
                     data['CONTACTER'] = row.find_element(By.CSS_SELECTOR, 'div[data-testid=cell-frame-title]').text
                  except:
                     continue

                  data['CONTACTER'] = data['CONTACTER'].lstrip('+')
                  if not (data['CONTACTER'].isalpha()):
                     data['CONTACTER'] = data['CONTACTER'].replace(' ', '').replace('-', '')

                  if is_sid == True:
                     if int(data['CONTACTER']) != int(self.data.get('cid', 0)):
                        continue

                  try:
                     data['UNREAD_COUNT'] = int(row.find_element(By.CSS_SELECTOR, 'span[data-testid=icon-unread-count]').text)
                  except:
                     data['UNREAD_COUNT'] = 0

                  row.click()
                  time.sleep(2)

                  unread_message = []
                  try:
                     rows_dialog = self.browser.driver.find_elements(By.CSS_SELECTOR, 'div[data-testid=conversation-panel-messages] div:has( > div.focusable-list-item )')
                     rows_dialog.reverse()
                     if len(rows_dialog) > 0:
                        for item in rows_dialog:
                           row_d = item.find_element(By.CSS_SELECTOR, 'div.focusable-list-item')
                           style = row_d.get_attribute('class')
                           if 'message-in' in style:
                              data_dialog = dict()
                              data_dialog['TYPE_STATUS'] = 'text'
                              try:
                                 data_dialog['TEXT'] = row_d.find_element(By.CSS_SELECTOR, 'span.selectable-text').text
                              except:
                                 pass

                              try:
                                 data_dialog['DATE_TIME'] = row_d.find_element(By.CSS_SELECTOR, 'div[data-testid=msg-meta]').text
                              except:
                                 pass

                              try:
                                 row_d.find_element(By.CSS_SELECTOR, 'span[data-testid=audio-play]')
                                 data_dialog['TYPE_STATUS'] = 'audio'
                                 try:
                                    data_id = item.get_attribute('data-id')
                                    self.browser.driver.execute_script(f'''
                                       var element = document.querySelector('[data-id="{data_id}"] div[data-testid="msg-container"]');
                                       var mouseoverEvent = new MouseEvent("mouseover", {{
                                         bubbles: true,
                                         cancelable: true,
                                         view: window
                                       }});
                                       element.dispatchEvent(mouseoverEvent);
                                       ''')
                                    time.sleep(2)
                                    btn_down = row_d.find_element(By.CSS_SELECTOR, 'div[data-testid=icon-down-context]')
                                    btn_down.click()
                                    time.sleep(2)
                                    btn_download = self.browser.driver.find_element(By.CSS_SELECTOR, 'li[data-testid=mi-msg-download]')
                                    btn_download.click()
                                    time.sleep(5)
                                    files = glob.glob(os.path.join(config.PATH_DOWNLOAD, '*'))
                                    latest_file = max(files, key=os.path.getctime)
                                    if '.ogg' in latest_file:
                                       file_name = os.path.splitext(os.path.basename(latest_file))[0]
                                       output_file = os.path.join(config.PATH_DOWNLOAD, file_name + '.mp3')
                                       try:
                                          Utils.ogg_to_mp3(latest_file, output_file)
                                       except:
                                          pass
                                       if os.path.isfile(output_file):
                                          try:
                                             message = Utils.transcription(output_file)
                                             data_dialog['TEXT'] = message['text']
                                          except: pass
                                          os.remove(output_file)
                                    os.remove(latest_file)
                                 except:
                                    pass
                              except:
                                 pass

                              try:
                                 row_d.find_element(By.CSS_SELECTOR, 'div[data-testid=image-thumb]')
                                 data_dialog['TYPE_STATUS'] = 'image'
                              except:
                                 pass

                              try:
                                 row_d.find_element(By.CSS_SELECTOR, 'button[data-testid=document-thumb]')
                                 data_dialog['TYPE_STATUS'] = 'document'
                              except:
                                 pass

                              try:
                                 row_d.find_element(By.CSS_SELECTOR, 'div[data-testid=vcard-msg]')
                                 data_dialog['TYPE_STATUS'] = 'contact'
                              except:
                                 pass

                              try:
                                 row_d.find_element(By.CSS_SELECTOR, 'div[data-testid=poll-bubble]')
                                 data_dialog['TYPE_STATUS'] = 'poll'
                              except:
                                 pass

                              unread_message.append(data_dialog)
                           else:
                              break
                  except:
                     pass

                  data['MESSAGES'] = unread_message
                  New_messages.append(data)

            self.esc(3)
            try:
               self.browser.driver.find_element(By.CSS_SELECTOR, 'span[data-testid=filter]').click()
            except: pass

            if len(New_messages) > 0:
               return {'STATUS': 200, 'MESSAGE': 'COMMAND COMPLETED SUCCESSFULLY', 'DATA': New_messages}
            else:
               return {'STATUS': 401, 'MESSAGE': 'NO NEW MESSAGES', }
         except:
            return {'STATUS': 400, 'MESSAGE': 'NO BUTTON TO FILTER NEW MESSAGES'}
      else:
         return is_auth

   # Получить непрочитанные сообщения по контактеру
   # todo: Получает сообщение по номеру телефона
   # todo: DEPRECATION
   def UnreadCidMessage(self):
      if 'cid' in self.data:
         self.browser.driver.get(f"https://web.whatsapp.com/send?phone={self.data['cid']}&app_absent=0")
         try:
            WebDriverWait(self.browser.driver, 80).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-testid=conversation-compose-box-input]')))
         except:
            return {'STATUS': 400, 'MESSAGE': 'FAILED TO OPEN DIALOG'}

         try:
            self.browser.driver.find_element(By.CSS_SELECTOR, 'div[data-testid=conversation-panel-messages] span[data-testid=refresh]').click()
            time.sleep(1)
         except: pass

         try:
            unread_message = []
            try:
               rows = self.browser.driver.find_elements(By.CSS_SELECTOR, 'div[data-testid=conversation-panel-messages] div:has( > div.focusable-list-item )')
               rows.reverse()
               if len(rows) > 0:
                  for item in rows:
                     row = item.find_element(By.CSS_SELECTOR, 'div.focusable-list-item')
                     style = row.get_attribute('class')
                     if 'message-in' in style:
                        data = dict()
                        data['TYPE_STATUS'] = 'text'
                        try:
                           data['TEXT'] = row.find_element(By.CSS_SELECTOR, 'span.selectable-text').text
                        except: pass

                        try:
                           data['DATE_TIME'] = row.find_element(By.CSS_SELECTOR, 'div[data-testid=msg-meta]').text
                        except: pass

                        try:
                           row.find_element(By.CSS_SELECTOR, 'span[data-testid=audio-play]')
                           data['TYPE_STATUS'] = 'audio'
                           try:
                              data_id = item.get_attribute('data-id')
                              self.browser.driver.execute_script(f'''
                                 var element = document.querySelector('[data-id="{data_id}"] div[data-testid="msg-container"]');
                                 var mouseoverEvent = new MouseEvent("mouseover", {{
                                   bubbles: true,
                                   cancelable: true,
                                   view: window
                                 }});
                                 element.dispatchEvent(mouseoverEvent);
                                 ''')
                              time.sleep(2)
                              btn_down = row.find_element(By.CSS_SELECTOR, 'div[data-testid=icon-down-context]')
                              btn_down.click()
                              time.sleep(2)
                              btn_download = self.browser.driver.find_element(By.CSS_SELECTOR, 'li[data-testid=mi-msg-download]')
                              btn_download.click()
                              time.sleep(5)
                              files = glob.glob(os.path.join(config.PATH_DOWNLOAD, '*'))
                              latest_file = max(files, key=os.path.getctime)
                              if '.ogg' in latest_file:
                                 file_name = os.path.splitext(os.path.basename(latest_file))[0]
                                 output_file = os.path.join(config.PATH_DOWNLOAD, file_name+'.mp3')
                                 try:
                                    Utils.ogg_to_mp3(latest_file, output_file)
                                 except: pass
                                 if os.path.isfile(output_file):
                                    message = Utils.transcription(output_file)
                                    data['TEXT'] = message['text']
                                    os.remove(output_file)

                              os.remove(latest_file)
                           except: pass

                        except Exception as e: pass

                        try:
                           row.find_element(By.CSS_SELECTOR, 'div[data-testid=image-thumb]')
                           data['TYPE_STATUS'] = 'image'
                        except: pass

                        try:
                           row.find_element(By.CSS_SELECTOR, 'button[data-testid=document-thumb]')
                           data['TYPE_STATUS'] = 'document'
                        except: pass

                        try:
                           row.find_element(By.CSS_SELECTOR, 'div[data-testid=vcard-msg]')
                           data['TYPE_STATUS'] = 'contact'
                        except: pass

                        try:
                           row.find_element(By.CSS_SELECTOR, 'div[data-testid=poll-bubble]')
                           data['TYPE_STATUS'] = 'poll'
                        except: pass


                        unread_message.append(data)
                     else:
                        break
            except Exception as e:
               pass

            self.esc()
            return {'STATUS': 200, 'MESSAGE': 'COMMAND COMPLETED SUCCESSFULLY', 'UNREAD_MESSAGES': unread_message, 'CONTACTER': self.data['cid']}

         except Exception as e:
            self.esc()
            return {'STATUS': 400, 'MESSAGE': f'ERROR RECEIVING NEW MESSAGES. [ ERROR: {e} ]'}
      else:
         self.esc()
         return {'STATUS': 400, 'MESSAGE': 'NO PARAMETER CONTACTER UNABLE TO OPEN DIALOG'}

   # Сохранить фото персонажа
   def GetPhotoPersonage(self):
      current_url = self.browser.driver.current_url
      if current_url != 'https://web.whatsapp.com/':
         self.browser.driver.get("https://web.whatsapp.com/")
      try:
         WebDriverWait(self.browser.driver, 45).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'header[data-testid=chatlist-header]')))
         url_ava = ''
         path_ava = ''
         try:
            ava = self.browser.driver.find_element(By.CSS_SELECTOR, 'header[data-testid=chatlist-header] img')
            url_ava = ava.get_attribute('src')
            response = requests.get(url_ava)
            path_ava = f"{config.PATH_ATTACHMENTS_AVATARS}WHATSAPP_{self.data['id']}.jpg"
            with open(path_ava, 'wb') as f:
               f.write(response.content)
            path_ava = os.path.abspath(path_ava)

         except:
            pass
         if path_ava:
            return {'STATUS': 200, 'MESSAGE': 'PERSON GET PHOTO SUCCESS', 'URL': url_ava, 'PATH': path_ava}
         else:
            return {'STATUS': 200, 'MESSAGE': 'COMMAND COMPLETED SUCCESSFULLY, PHOTO NOT INSTALLED', 'URL': url_ava, 'PATH': path_ava}

      except:
         return {'STATUS': 400, 'MESSAGE': 'LOADING ERROR WHATSAPP'}

   # Получить аватарку контактера
   def GetPhotoContacter(self):
      if 'cid' in self.data:
         current_url = self.browser.driver.current_url
         if current_url != 'https://web.whatsapp.com/':
            self.browser.driver.get("https://web.whatsapp.com/")

         try:
            WebDriverWait(self.browser.driver, 45).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'header[data-testid=chatlist-header]')))
            url_ava = ''
            path_ava = ''
            try:
               list_search = self.browser.driver.find_element(By.CSS_SELECTOR, 'div[data-testid=chat-list-search]')
               list_search.click()
               search = str(self.data['cid'])
               list_search.send_keys(f"{search}")
               time.sleep(2)


               rows = self.browser.driver.find_elements(By.CSS_SELECTOR, 'div[data-testid=cell-frame-container]')
               if len(rows) > 0:
                  for row in rows:

                     cid = row.find_element(By.CSS_SELECTOR, 'div[data-testid=cell-frame-title]').text
                     cid = cid.lstrip('+')
                     if not (cid.isalpha()):
                        cid = cid.replace(' ', '').replace('-', '')

                     if str(cid) == str(self.data['cid']):
                        try:
                           ava = row.find_element(By.CSS_SELECTOR, 'img')
                           url_ava = ava.get_attribute('src')
                           response = requests.get(url_ava)
                           path_ava = f"{config.PATH_ATTACHMENTS_AVATARS}WHATSAPP_{self.data['id']}_{cid}.jpg"
                           with open(path_ava, 'wb') as f:
                              f.write(response.content)
                           path_ava = os.path.abspath(path_ava)
                           break
                        except: pass

               try:
                  self.browser.driver.find_element(By.CSS_SELECTOR, 'button[data-testid=icon-search-morph]').click()
               except: pass

            except Exception as e:
               pass

            if path_ava:
               return {'STATUS': 200, 'MESSAGE': 'CONTACTER GET PHOTO SUCCESS', 'URL': url_ava, 'PATH': path_ava, 'CONTACTER': self.data['cid']}
            else:
               return {'STATUS': 200, 'MESSAGE': 'COMMAND COMPLETED SUCCESSFULLY, PHOTO NOT INSTALLED', 'URL': url_ava, 'PATH': path_ava, 'CONTACTER': self.data['cid']}

         except:
            return {'STATUS': 400, 'MESSAGE': 'LOADING ERROR WHATSAPP'}


      else:
         return {'STATUS': 400, 'MESSAGE': 'NO CONTACTER PARAMETER FOR GETTING A PHOTO'}

   # Получить данные по персонажу
   def GetPersonage(self, params = []):
      try:
         current_url = self.browser.driver.current_url
         if current_url != 'https://web.whatsapp.com/':
            self.browser.driver.get("https://web.whatsapp.com/")
         WebDriverWait(self.browser.driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'header[data-testid=chatlist-header]')))

         body = self.browser.driver.find_element(By.CSS_SELECTOR, 'body')
         body.send_keys(Keys.CONTROL + Keys.ALT + 'p')
         time.sleep(1)
         first_name = ''
         last_name = ''
         try:
            info = self.browser.driver.find_elements(By.CSS_SELECTOR, 'span[data-testid=col-main-profile-input-read-only]')
            profile = info[0].text
            profile = profile.split()
            try:
               first_name = profile[0]
            except IndexError:
               first_name = ''

            try:
               last_name = profile[1]
            except IndexError:
               last_name = ''
         except:
            pass
         body.send_keys(Keys.ESCAPE)
         response = {}
         if 'FIRST_NAME' in params:
            response['FIRST_NAME_PERSONE'] = first_name
         if 'LAST_NAME' in params:
            response['LAST_NAME_PERSONE'] = last_name

         result = {'STATUS': 200, 'MESSAGE': 'OK'}
         result.update(response)
         return result
      except:
         return {'STATUS': 400, 'MESSAGE': 'WHATSAPP NOT LOADING'}


   # Получить данные по контактеру
   def GetContacter(self, params=[]):
      if 'cid' in self.data:
         self.browser.driver.get(f"https://web.whatsapp.com/send?phone={self.data['cid']}&app_absent=0")
         try:
            WebDriverWait(self.browser.driver, 80).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-testid=conversation-compose-box-input]')))

            body = self.browser.driver.find_element(By.CSS_SELECTOR, 'body')
            first_name = ''
            last_name = ''

            try:
               self.browser.driver.find_element(By.CSS_SELECTOR, 'div[data-testid=conversation-info-header]').click()
               time.sleep(1)
               info = self.browser.driver.find_elements(By.CSS_SELECTOR, 'div[data-testid=chat-info-drawer] section > div:nth-of-type(1) .selectable-text.copyable-text')
               for row in info:
                  text_original = row.text.replace('~', '')
                  text = text_original.replace(' ', '').replace('-', '').replace('+', '')
                  if not text.isnumeric():
                     profile = text_original.split()
                     try:
                        first_name = profile[0]
                     except IndexError:
                        first_name = ''

                     try:
                        last_name = profile[1]
                     except IndexError:
                        last_name = ''
                     break
            except:
               pass


            body.send_keys(Keys.ESCAPE)
            time.sleep(1)
            body.send_keys(Keys.ESCAPE)
            response = {}
            if 'FIRST_NAME' in params:
               response['FIRST_NAME_CONTACTER'] = first_name
            if 'LAST_NAME' in params:
               response['LAST_NAME_CONTACTER'] = last_name

            result = {'STATUS': 200, 'MESSAGE': 'OK', 'CONTACTER': self.data['cid']}
            result.update(response)
            return result
         except:
            return {'STATUS': 400, 'MESSAGE': 'FAILED TO OPEN DIALOG'}

      else:
         return {'STATUS': 400, 'MESSAGE': 'NO CONTACTER PARAMETER, IT IS NOT POSSIBLE TO GET DATA'}

   # Нажимаем esc
   def esc(self, count=1):
      try:
         body = self.browser.driver.find_element(By.CSS_SELECTOR, 'body')
         if count > 1:
            for _ in range(count):
               body.send_keys(Keys.ESCAPE)
               time.sleep(1)
         else:
            body.send_keys(Keys.ESCAPE)
      except:
         pass