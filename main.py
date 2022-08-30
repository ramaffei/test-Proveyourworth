from datetime import datetime
import json
from requests import Session, Request
from PIL import Image, ImageDraw, ImageFont
from bs4 import BeautifulSoup

class ProveYourWorth():
   """
   Desarrollado por Rodrigo Maffei.
   Github: https://github.com/ramaffei
   Linkedin: https://www.linkedin.com/in/ramaffei/
   Mail: rodrigoa.maffei@gmail.com

   python-version: 3.10.4
   """

   HEAD_PAYLOAD = 'X-Payload-URL'
   HEAD_POST = 'X-Post-Back-To'

   def __init__(self, star_url: str, nombre_imagen: str = 'image', carpeta: str = '/', cv: str = '') -> None:
      self.start_url = star_url
      self.session = Session()
      self.__startSession__()
      self.url_payload = ''
      self.image = nombre_imagen
      self.carpeta = carpeta
      self.resume = cv

   def __startSession__(self) -> None:
      print(self.start_url)
      with self.session.get(self.start_url) as s:
         self.start_html = BeautifulSoup(s.text, 'html.parser')

   def getPhpCookie(self) -> str:
      with self.session as s:
         return s.cookies.get('PHPSESSID')

   def login(self) -> str:
      params = self.__getParamsFromForm__()
      if params is not None:
         method = params['method']
         url = params['url']
         del params['method'], params['url']
         self.__params__ = params
         with self.session as s:
            req = Request(method, url=url, params=params)
            prepped = s.prepare_request(req)
            print('Iniciando Login en: {}'.format(url))
            resp = s.send(prepped)
            if resp.headers.get(self.HEAD_PAYLOAD, False):
               print('Login Exitoso')
               self.url_payload = resp.headers[self.HEAD_PAYLOAD]
               return self.url_payload
      else:
         print('No se pudo iniciar sesion')
         return ''

   def getHash(self) -> str:
      return self.__params__.get('statefulhash', None)

   def downloadImagePayload(self) -> int:
      try:
         print('Descargando payload de {}'.format(self.url_payload))
         with self.session.get(self.url_payload) as s:
            with open(f'{self.carpeta}{self.image}.jpg','wb') as f:
               f.write(s.content)
               f.close()
            print('Imagen descargada con exito')
            if s.headers.get(self.HEAD_POST) is not None:
               self.__url_post__ = s.headers[self.HEAD_POST]
            return s.status_code
      except Exception as e:
         print('Ocurrio un error, no se pudo descargar la imagen: {}'.format(e))
         return None

   def __drawImage__(self, **kwargs) -> None:
      print('Modificando Imagen')
      with Image.open(f'{self.carpeta}{self.image}.jpg') as im:
         draw = ImageDraw.Draw(im)
         text = ''
         for k,v in kwargs.items():
            text += f'{k} = {v}\n'
         font = ImageFont.truetype("arial.ttf", 28)
         draw.multiline_text((10,10), text, font=font, fill=(228,48,9))
         self.image = self.image+'_mod'
         im.save(f'{self.carpeta}{self.image}.jpg',"JPEG")
         print('Imagen Modificada')
   
   def sendBackTo(self, **kwargs) -> None:
      self.__drawImage__(**kwargs)

      files = {
        "code": open("main.py","rb"),
        "image": open(self.carpeta+self.image+'.jpg',"rb"),
        "requirements": open("requirements.txt")
      }

      if self.resume is not None:
         files['resume'] = open(self.carpeta+self.resume, "rb")
      
      with open(self.carpeta+'aboutme.txt', "r") as aboutme:
         aboutme = aboutme.read()
         if aboutme != '':
            print('pasando')
            kwargs['aboutme'] = aboutme
      
      #kwargs['python-version'] = '3.10.4'
      
      print('Enviando datos a {}'.format(self.__url_post__))
      r = self.session.post(self.__url_post__, data=kwargs, files=files)
      print(r.text)
      print(r.headers)
      print(r.status_code)


   def __getParamsFromForm__(self):
      soup = self.start_html
      form = soup.find('form')
      if form is None:
         return
      params = {}
      params['url'] = '{0}/{1}'.format(self.start_url, form['action'])
      params['method'] = form['method']

      inputs = form.find_all('input')
      for i in inputs:
         if i.get('name') is not None:
            params[i['name']] = i['value'] if i.get('value', None) is not None else input('Por favor, ingrese un valor para {}: '.format(i['name']))

      return params


if __name__ == '__main__':
   print('Comenzado prueba:')
   test = ProveYourWorth(
      'https://www.proveyourworth.net/level3', 
      'payload', 
      'files/', 
      cv = 'CV_Maffei Rodrigo_2022.pdf')

   test.login()
   test.downloadImagePayload()

   data = {
      'name': 
      'Rodrigo Maffei', 
      'email': 
      'rodrigoa.maffei@gmail.com', 
      'Hash': test.getHash()
      }

   test.sendBackTo(**data)
   print("Prueba finalizada")


