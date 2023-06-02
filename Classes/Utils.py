import config
import openai
from pydub import AudioSegment

def chatGpt(text):

   openai.api_key = config.API_GPT
   completion = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=[
         {"role": "user", "content": text}
      ]
   )
   if completion.choices[0].finish_reason == 'stop':
      message = completion.choices[0].message.content
      return message.strip()
   return None

def ogg_to_mp3(input_file, output_file):
   audio = AudioSegment.from_ogg(input_file)
   audio.export(output_file, format="mp3")

def transcription(audio_file):
   openai.api_key = config.API_GPT
   audio_file = open(audio_file, "rb")
   transcript = openai.Audio.transcribe("whisper-1", audio_file)
   return transcript