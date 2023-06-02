import os.path
import traceback
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

class Telegram(Driver):

   data = dict()
   browser = None


   def __init__(self, data):
      self.data = data


   def run(self, browser):
      self.browser = browser
      if self.data.get('__command__').lower() == 'TELEGRAM_SELENIUM_AUTHORIZATION'.lower():
         response = self.CheckAuthorization()
      elif self.data.get('__command__').lower() == 'TELEGRAM_SELENIUM_SEND_MESSAGE'.lower():
         response = self.SendMessage()
      elif self.data.get('__command__').lower() == 'TELEGRAM_SELENIUM_SEND_MESSAGE_GPT'.lower():
         response = self.SendMessage(True)
      elif self.data.get('__command__').lower() == 'TELEGRAM_SELENIUM_NEW_MESSAGES'.lower():
         response = self.NewMessages()
      elif self.data.get('__command__').lower() == 'TELEGRAM_SELENIUM_CONTACTER_MESSAGE'.lower():
         response = self.NewMessagesContacter()
      elif self.data.get('__command__').lower() == 'TELEGRAM_SELENIUM_GET_PHOTO_PERSONE'.lower():
         response = self.GetPersonage(['PHOTO'])
      elif self.data.get('__command__').lower() == 'TELEGRAM_SELENIUM_GET_FIRST_NAME_PERSONE'.lower():
         response = self.GetPersonage(['FIRST_NAME'])
      elif self.data.get('__command__').lower() == 'TELEGRAM_SELENIUM_GET_LAST_NAME_PERSONE'.lower():
         response = self.GetPersonage(['LAST_NAME'])
      elif self.data.get('__command__').lower() == 'TELEGRAM_SELENIUM_GET_PHONE_PERSONE'.lower():
         response = self.GetPersonage(['PHONE'])
      elif self.data.get('__command__').lower() == 'TELEGRAM_SELENIUM_GET_PEER_ID_PERSONE'.lower():
         response = self.GetPersonage(['PEER_ID'])
      elif self.data.get('__command__').lower() == 'TELEGRAM_SELENIUM_GET_USERNAME_PERSONE'.lower():
         response = self.GetPersonage(['USERNAME'])
      elif self.data.get('__command__').lower() == 'TELEGRAM_SELENIUM_GET_INFO_PERSONE'.lower():
         response = self.GetPersonage(['INFO'])
      elif self.data.get('__command__').lower() == 'TELEGRAM_SELENIUM_GET_LINK_PERSONE'.lower():
         response = self.GetPersonage(['LINK'])
      elif self.data.get('__command__').lower() == 'TELEGRAM_SELENIUM_GET_PHOTO_CONTACTER'.lower():
         response = self.GetContacter(['PHOTO'])
      elif self.data.get('__command__').lower() == 'TELEGRAM_SELENIUM_GET_FIRST_NAME_CONTACTER'.lower():
         response = self.GetContacter(['FIRST_NAME'])
      elif self.data.get('__command__').lower() == 'TELEGRAM_SELENIUM_GET_LAST_NAME_CONTACTER'.lower():
         response = self.GetContacter(['LAST_NAME'])
      elif self.data.get('__command__').lower() == 'TELEGRAM_SELENIUM_GET_PHONE_CONTACTER'.lower():
         response = self.GetContacter(['PHONE'])
      elif self.data.get('__command__').lower() == 'TELEGRAM_SELENIUM_GET_PEER_ID_CONTACTER'.lower():
         response = self.GetContacter(['PEER_ID'])
      elif self.data.get('__command__').lower() == 'TELEGRAM_SELENIUM_GET_USERNAME_CONTACTER'.lower():
         response = self.GetContacter(['USERNAME'])
      elif self.data.get('__command__').lower() == 'TELEGRAM_SELENIUM_GET_INFO_CONTACTER'.lower():
         response = self.GetContacter(['INFO'])
      elif self.data.get('__command__').lower() == 'TELEGRAM_SELENIUM_GET_LINK_CONTACTER'.lower():
         response = self.GetContacter(['LINK'])
      if 'response' in locals():
         if 'id' in self.data:
            response.update({'ID': self.data['id']})
         response['MESSAGE'] = response['MESSAGE'].upper()
         response['COMMAND'] = self.data.get('__command__').upper()
         return response
      return False



   def CheckAuthorization(self):
      try:
         self.browser.driver.get('https://web.telegram.org/k/')
         WebDriverWait(self.browser.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.input-search')))
         return {'STATUS': 200, 'MESSAGE': 'PERSONEN AUTHORIZED'}
      except:
         return {'STATUS': 400, 'MESSAGE': 'PERSONEN NOT AUTHORIZED'}

   # Отправка сообщения
   def SendMessage(self, gpt=False):
      is_auth = self.CheckAuthorization()
      if  is_auth['STATUS'] == 200:
         if 'cid' in self.data or 'peer_id' in self.data:
            if 'cid' in self.data:
               if type(self.data['cid']) == int:
                  url = f"https://web.telegram.org/k/#?tgaddr=tg%3A%2F%2Fresolve%3Fphone%3D{self.data['cid']}"
               else:
                  if self.data['cid'][0] == '@':
                     url = f"https://web.telegram.org/k/#{self.data['cid']}"
                  else:
                     url = f"https://web.telegram.org/k/#@{self.data['cid']}"
               cid = self.data['cid']
            elif 'peer_id' in self.data:
               url = f"https://web.telegram.org/k/#{self.data['peer_id']}"
               cid = self.data['peer_id']
            if 'message' in self.data:
               self.browser.driver.get(url)
               try:
                  WebDriverWait(self.browser.driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.input-message-container')))
               except:
                  return {'STATUS': 400, 'MESSAGE': 'FAILED TO OPEN DIALOG'}
               try:
                  compose_box = self.browser.driver.find_element(By.CSS_SELECTOR, '.input-message-container .input-message-input:nth-of-type(1)')
                  compose_box.click()
                  compose_box.clear()
                  action = ActionChains(self.browser.driver)
                  action.move_to_element(compose_box).click()

                  if gpt == True:
                     self.data['message'] = Utils.chatGpt(self.data['message'])
                     if not self.data['message']:
                        return {'Status': 400, 'Message': 'Failed to get response from ChatGPT'}

                  self.data['message'] = self.data['message'].replace('\\n', '\n').replace('<br>', '\n')
                  for char in self.data['message']:
                     if char == '\n':
                        action.key_down(Keys.SHIFT).send_keys(Keys.RETURN).key_up(Keys.SHIFT)
                     else:
                        action.send_keys(char)
                     action.pause(0.05)
                  action.perform()
                  compose_box.send_keys(Keys.ENTER)
                  return {'STATUS': 200, 'MESSAGE': 'Message sent successfully', 'TEXT': self.data['message'], 'CONTACTER': cid}
               except Exception as e:
                  return {'STATUS': 400, 'MESSAGE': f'Failed to send message. [ Error: {e} ]', 'CONTACTER': cid}
            else:
               return {'STATUS': 400, 'MESSAGE': 'NOT MESSAGES TO SEND', 'CONTACTER': cid}
         else:
            return {'STATUS': 400, 'MESSAGE': 'NO CONTACTER PARAMETER, MESSAGE CANNOT BE SENT'}
      else:
         return is_auth

   # Получить список новых сообщений
   def NewMessages(self):
      is_auth = self.CheckAuthorization()
      if is_auth['STATUS'] == 200:

         try:
            WebDriverWait(self.browser.driver, 40).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.input-search')))

            New_messages = []
            temps_peer = []
            time.sleep(5)
            actions = ActionChains(self.browser.driver)
            is_next = True
            while is_next:
               try:
                  rows = self.browser.driver.find_elements(By.CSS_SELECTOR, 'div.chatlist-parts[data-filter-id="0"] .chatlist .chatlist-chat')
               except:
                  rows = []
               if len(rows) > 0:

                  is_unread = False
                  for index, row in enumerate(rows):
                     try:
                        peer_id = int(row.get_attribute('data-peer-id'))
                     except:
                        peer_id=0
                     if (peer_id not in temps_peer) and (peer_id > 0):
                        data = dict()
                        temps_peer.append(peer_id)
                        is_unread = True
                        data['PEER_ID'] = peer_id
                        try:
                           data['UNREAD_COUNT'] = int(row.find_element(By.CSS_SELECTOR, 'div.unread').text)
                        except:
                           data['UNREAD_COUNT'] = 0

                        if data['UNREAD_COUNT'] > 0:
                           row.click()
                           time.sleep(4)
                           unread_message = []
                           unread_message = self.getUnreadMessagesOfDialog()[0]

                           try:
                              body = self.browser.driver.find_element(By.CSS_SELECTOR, 'body')
                              body.send_keys(Keys.ESCAPE)
                           except:
                              pass

                           data['MESSAGES'] = unread_message
                           New_messages.append(data)
                     if index == len(rows) - 1:
                        try:
                           actions.move_to_element(row).perform()
                        except: pass
               else:
                  is_next = False

               if is_unread == False:
                  is_next = False

            return {'STATUS': 200, 'MESSAGE': 'COMMAND COMPLETED SUCCESSFULLY', 'DATA': New_messages}

         except Exception as e:
            # traceback.print_exc()
            return {'STATUS': 400, 'MESSAGE': f"ERROR: {e}"}
      else:
         return is_auth

   # Получить новые сообщения по контактеру
   def NewMessagesContacter(self):
      is_auth = self.CheckAuthorization()
      if is_auth['STATUS'] == 200:
         if 'cid' in self.data or 'peer_id' in self.data:
            if 'cid' in self.data:
               if type(self.data['cid']) == int:
                  url = f"https://web.telegram.org/k/#?tgaddr=tg%3A%2F%2Fresolve%3Fphone%3D{self.data['cid']}"
               else:
                  if self.data['cid'][0] == '@':
                     url = f"https://web.telegram.org/k/#{self.data['cid']}"
                  else:
                     url = f"https://web.telegram.org/k/#@{self.data['cid']}"
            elif 'peer_id' in self.data:
               url = f"https://web.telegram.org/k/#{self.data['peer_id']}"

            self.browser.driver.get(url)
            try:
               WebDriverWait(self.browser.driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.input-message-container')))
            except:
               return {'STATUS': 400, 'MESSAGE': 'FAILED TO OPEN DIALOG'}
            New_messages = []
            time.sleep(5)
            actions = ActionChains(self.browser.driver)
            compose_box = self.browser.driver.find_element(By.CSS_SELECTOR, '.input-message-container .input-message-input:nth-of-type(1)')
            peer_id = int(compose_box.get_attribute('data-peer-id'))
            data = dict()
            data['PEER_ID'] = peer_id
            unread_message, data['UNREAD_COUNT'] = self.getUnreadMessagesOfDialog()

            self.esc()

            data['MESSAGES'] = unread_message
            New_messages.append(data)

            return {'STATUS': 200, 'MESSAGE': 'COMMAND COMPLETED SUCCESSFULLY', 'DATA': New_messages}

         else:
            return {'STATUS': 400, 'MESSAGE': 'NO CONTACTER PARAMETER, MESSAGE CANNOT BE SENT'}
      else:
         return is_auth


   #  пробегает по диалогу с человек и вытаскивает входящие сообщения
   def getUnreadMessagesOfDialog(self):
      while True:
         try:
            btn = self.browser.driver.find_element(By.CSS_SELECTOR, '.bubbles-go-down')
            btn.click()
         except:
            break

      unread_message = []
      unread_count = 0
      actions = ActionChains(self.browser.driver)
      try:
         rows_dialog = self.browser.driver.find_elements(By.CSS_SELECTOR, '.bubbles-inner .bubble')
         rows_dialog.reverse()
         if len(rows_dialog) > 0:
            for row_d in rows_dialog:
               try:
                  actions.move_to_element(row_d).perform()
               except:
                  pass
               style = row_d.get_attribute('class')
               if 'is-in' in style:
                  data_dialog = dict()
                  data_dialog['TYPE_STATUS'] = 'text'

                  try:
                     data_dialog['TEXT'] = row_d.find_element(By.CSS_SELECTOR, '.message').text
                  except:
                     pass

                  try:
                     data_dialog['DATE_TIME'] = int(row_d.get_attribute('data-timestamp'))
                  except:
                     pass

                  try:
                     voice_box = row_d.find_element(By.CSS_SELECTOR, '.message.voice-message')
                     data_dialog['TYPE_STATUS'] = 'audio'
                     action = ActionChains(self.browser.driver)
                     actions.context_click(voice_box).perform()
                     btn_down = self.browser.driver.find_element(By.CSS_SELECTOR, 'div.tgico-download')
                     time.sleep(2)
                     btn_down.click()
                     time.sleep(5)
                     files = glob.glob(os.path.join(config.PATH_DOWNLOAD, '*'))
                     latest_file = max(files, key=os.path.getctime)
                     if 'voice' in latest_file:
                        file_name = os.path.splitext(os.path.basename(latest_file))[0]
                        output_file = os.path.join(config.PATH_DOWNLOAD, file_name + '.mp3')
                        try:
                           Utils.ogg_to_mp3(latest_file, output_file)
                        except:
                           pass
                        if os.path.isfile(output_file):
                           message = Utils.transcription(output_file)
                           data_dialog['TEXT'] = message['text']
                           os.remove(output_file)

                     os.remove(latest_file)

                  except:
                     pass

                  if 'photo' in style:
                     data_dialog['TYPE_STATUS'] = 'image'

                  try:
                     row_d.find_element(By.CSS_SELECTOR, '.message.document-message')
                     data_dialog['TYPE_STATUS'] = 'document'
                  except:
                     pass

                  unread_message.append(data_dialog)

                  if 'is-first-unread' in style:
                     unread_count = len(unread_message)
                     break
               else:
                  break
      except:
         pass

      return (unread_message, unread_count)

   # Получить данные персонажа
   def GetPersonage(self, params = []):
      self.browser.driver.get("https://web.telegram.org/k/")
      time.sleep(1)
      try:
         WebDriverWait(self.browser.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.input-search')))
         path_ava = ''
         first_name = ''
         last_name = ''
         phone = ''
         username=''
         info=''
         link=''
         peer_id=''
         try:
            self.browser.driver.find_element(By.CSS_SELECTOR, '.sidebar-tools-button').click()
            time.sleep(1)
            self.browser.driver.find_element(By.CSS_SELECTOR, '.tgico-settings').click()
            time.sleep(1)

            try:
               phone = self.browser.driver.find_element(By.CSS_SELECTOR, '.tgico-phone .row-title').text
               phone = phone.lstrip('+').replace(' ', '').replace('-', '')
            except: pass
            try:
               username = self.browser.driver.find_element(By.CSS_SELECTOR, '.tgico-username .row-title').text
            except: pass
            try:
               info = self.browser.driver.find_element(By.CSS_SELECTOR, '.tgico-info .row-title').text
            except: pass
            try:
               link = self.browser.driver.find_element(By.CSS_SELECTOR, '.tgico-link .row-title').text
            except: pass
            try:
               profile = self.browser.driver.find_element(By.CSS_SELECTOR, '.profile-name .peer-title')
               peer_id = int(profile.get_attribute('data-peer-id'))
               profile = profile.text
               profile = profile.split()
               try:
                  first_name = profile[0]
               except IndexError:
                  first_name = ''
               try:
                  last_name = profile[1]
               except IndexError:
                  last_name = ''
            except: pass

            if 'PHOTO' in params:
               try:
                  ava = self.browser.driver.find_element(By.CSS_SELECTOR, '.profile-content .profile-avatars-avatar:nth-of-type(1)')
                  ava.click()
                  WebDriverWait(self.browser.driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.media-viewer-aspecter img')))
                  image_element = self.browser.driver.find_element(By.CSS_SELECTOR, '.media-viewer-aspecter img')
                  filename = f"{config.PATH_ATTACHMENTS_AVATARS}TELEGRAM_{self.data['id']}.jpg"
                  image_element.screenshot(filename)
                  path_ava = os.path.abspath(filename)
                  self.esc()
                  time.sleep(1)
               except Exception as e:
                  pass
         except:
            pass

         self.esc()

         response = {}
         if 'FIRST_NAME' in params:
            response['FIRST_NAME_PERSONE'] = first_name
         if 'LAST_NAME' in params:
            response['LAST_NAME_PERSONE'] = last_name
         if 'PHONE' in params:
            response['PHONE'] = phone
         if 'USERNAME' in params:
            response['USERNAME'] = username
         if 'INFO' in params:
            response['INFO'] = info
         if 'LINK' in params:
            response['LINK'] = link
         if 'PEER_ID' in params:
            response['PEER_ID'] = peer_id
         if 'PHOTO' in params:
            response['PATH'] = path_ava
            response['MESSAGE'] = 'PERSON GET PHOTO SUCCESS'

         result = {'STATUS': 200, 'MESSAGE': 'OK'}
         result.update(response)
         return result

      except:
         return {'STATUS': 400, 'MESSAGE': 'LOADING ERROR TELEGRAM'}

   # Получить данные Контактера
   def GetContacter(self, params=[]):
      if 'cid' in self.data or 'peer_id' in self.data:
         response = {}
         if 'cid' in self.data:
            cid = self.data['cid']
            response['CONTACTER'] = self.data['cid']
            if type(self.data['cid']) == int:
               url = f"https://web.telegram.org/k/#?tgaddr=tg%3A%2F%2Fresolve%3Fphone%3D{self.data['cid']}"
            else:
               if self.data['cid'][0] == '@':
                  url = f"https://web.telegram.org/k/#{self.data['cid']}"
               else:
                  url = f"https://web.telegram.org/k/#@{self.data['cid']}"
         elif 'peer_id' in self.data:
            cid = self.data['peer_id']
            response['PEER_ID'] = self.data['peer_id']
            url = f"https://web.telegram.org/k/#{self.data['peer_id']}"

         self.browser.driver.get(url)
         try:
            WebDriverWait(self.browser.driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.input-message-container')))
         except:
            return {'STATUS': 400, 'MESSAGE': 'FAILED TO OPEN DIALOG'}

         path_ava = ''
         first_name = ''
         last_name = ''
         phone = ''
         username = ''
         info = ''
         link = ''
         peer_id = ''
         try:
            self.browser.driver.find_element(By.CSS_SELECTOR, '.chat-info').click()
            time.sleep(1)

            try:
               phone = self.browser.driver.find_element(By.CSS_SELECTOR, '.sidebar-left-section-content .tgico-phone .row-title').text
               phone = phone.lstrip('+').replace(' ', '').replace('-', '')
            except:
               pass
            try:
               username = self.browser.driver.find_element(By.CSS_SELECTOR, '.sidebar-left-section-content .tgico-username .row-title').text
            except:
               pass
            try:
               info = self.browser.driver.find_element(By.CSS_SELECTOR, '.sidebar-left-section-content .tgico-info .row-title').text
            except:
               pass
            try:
               link = self.browser.driver.find_element(By.CSS_SELECTOR, '.sidebar-left-section-content .tgico-link .row-title').text
            except:
               pass
            try:
               profile = self.browser.driver.find_element(By.CSS_SELECTOR, '.profile-content .profile-name .peer-title')
               peer_id = int(profile.get_attribute('data-peer-id'))
               profile = profile.text
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

            if 'PHOTO' in params:
               try:
                  ava = self.browser.driver.find_element(By.CSS_SELECTOR, '.profile-content .profile-avatars-avatar:nth-of-type(1)')
                  ava.click()
                  WebDriverWait(self.browser.driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.media-viewer-aspecter img')))
                  image_element = self.browser.driver.find_element(By.CSS_SELECTOR, '.media-viewer-aspecter img')
                  filename = f"{config.PATH_ATTACHMENTS_AVATARS}TELEGRAM_{self.data['id']}_{cid}.jpg"
                  image_element.screenshot(filename)
                  path_ava = os.path.abspath(filename)
                  self.esc()
                  time.sleep(1)
               except Exception as e:
                  pass
         except:
            pass

         self.esc(2)


         if 'FIRST_NAME' in params:
            response['FIRST_NAME_PERSONE'] = first_name
         if 'LAST_NAME' in params:
            response['LAST_NAME_PERSONE'] = last_name
         if 'PHONE' in params:
            response['PHONE'] = phone
         if 'USERNAME' in params:
            response['USERNAME'] = username
         if 'INFO' in params:
            response['INFO'] = info
         if 'LINK' in params:
            response['LINK'] = link
         if 'PEER_ID' in params:
            response['PEER_ID'] = peer_id
         if 'PHOTO' in params:
            response['PATH'] = path_ava
            response['MESSAGE'] = 'CONTACTER GET PHOTO SUCCESS'

         result = {'STATUS': 200, 'MESSAGE': 'OK'}
         result.update(response)
         return result

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