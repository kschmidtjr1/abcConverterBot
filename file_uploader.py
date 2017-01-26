#downloaded
import pyimgur
import datetime
import requests
#local
import keys
import form_handler

picClient = pyimgur.Imgur(keys.imgur_client_id)

def upload_image(image_url,title='',description=''):
    global picClient
    print('Uploding image')
    if title == '':
        title = 'Converted score from abc notation'
    if description == '':
        description = 'Converted score from abc notation'
        
    res = picClient.upload_image(url=image_url,title=title,description=description)

    if res is None:
        print('didn\'t manage to uplaod the to imgur')
        return image_url
    else:
        print('Your photo is here : ' ,res.link)
        return res.link

def upload_music(midi_url,comment, title='',description=''):
##    global musicClient, res
##    success,mp3_url = form_handler.convert_from_midi(midi_url)
##    if success:
##        print 'Uploading music from:',mp3_url
##        return mp3_url
##    else: # mp3_url is None
##        print 'didn\'t manage to convert to mp3'
          return midi_url
##    else:
##        #TODO:Use threading/queue to re-check response and resubmit
##        print 'convertion to mp3 taking too long, revisit later'
##        return mp3_url

picClient = pyimgur.Imgur(keys.imgur_client_id)

