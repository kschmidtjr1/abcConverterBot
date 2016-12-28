#downloaded
import pyimgur
import datetime
import requests
try:#issue with __init__.py file not loading properly on first try
    import mixcloud
except:
    import mixcloud
#local
import keys
import form_handler

def upload_image(image_url,title='',description=''):
    global picClient
    print 'Uploding image'
    if title == '':
        title = 'Converted score from abc notation'
    if description == '':
        description = 'Converted score from abc notation'
        
    res = picClient.upload_image(url=image_url,title=title,description=description)

    if res is None:
        print 'didn\'t manage to uplaod the to imgur'
        return image_url
    else:
        print 'Your photo is here : ' ,res.link
        return res.link

def upload_music(midi_url,comment, title='',description=''):
    global musicClient, res
    success,mp3_url = form_handler.convert_from_midi(midi_url)
    if success:
        print 'Uploading music from:',mp3_url
        if title == '':
            title = 'Converted score from abc notation'
        if description == '':
            description = 'Converted score from abc notation'
        # mixcloud
        cc = get_cloudcast(comment,title,description)
        res = mixcloud_upload(cc,mp3_url)
        
        if res.status_code == 200:
            print 'Your music is here : ','https://www.mixcloud.com/developrK/%s'%mixcloud.slugify(comment.id)
            return 'https://www.mixcloud.com/developrK/%s'%mixcloud.slugify(comment.id)
        else:
            print 'didn\'t manage to upload to hostsite'
            return mp3_url
    elif mp3_url is None:
        print 'didn\'t manage to convert to mp3'
        return mp3_url
    else:
        #TODO:Use threading/queue to re-check response and resubmit
        print 'convertion to mp3 taking too long, revisit later'
        return mp3_url

def get_cloudcast(comment, title, description):
    key = mixcloud.slugify(comment.id)
    name = comment.id
    slug = mixcloud.slugify(comment.author.name)
    artist = mixcloud.Artist(slug, comment.author.name)
    track = mixcloud.Track(title, artist)
    #TODO: take in multiple sections
    sec = mixcloud.Section(0, track)
    tags = ['generated']
    user = mixcloud.User('developrk','developrK')
    create_time = datetime.datetime.fromtimestamp(comment.created)
    
    return mixcloud.Cloudcast(key,name,sec,tags,description,user,create_time)

def mixcloud_upload(cloudcast, mp3file):
    url = 'https://api.mixcloud.com/upload/'
    payload = {'name': cloudcast.name,
               'percentage_music': 100,
               'description': cloudcast.description(),
               }
    sec = cloudcast.sections()
    payload['sections-0-artist'] = sec.track.artist.name
    payload['sections-0-song'] = sec.track.name
    payload['sections-0-start_time'] = sec.start_time

    for num, tag in enumerate(cloudcast.tags):
        payload['tags-%s-tag' % num] = tag

    files = {'mp3': mp3file}

    r = requests.post(url,
                      data=payload,
                      params={'access_token': keys.mixcloud_token},
                      files=files,
                      )
    return r

picClient = pyimgur.Imgur(keys.imgur_client_id)

