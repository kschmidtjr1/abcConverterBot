#built-in
import time
#downloaded
import mechanize
from bs4 import BeautifulSoup
#local
import keys

def convert_from_abc(notation):
    global browser
    print("enter convert_notation")
    #get page
    url = 'http://www.mandolintab.net/abcconverter.php'
    browser.open(url)
    #use forms 
    browser.form = list(browser.forms())[2]
    browser['abc'] = notation
    response = browser.submit('submit')
    soup = BeautifulSoup(response.read(),"html.parser")
    #check and extract
    resources = []
    songs = soup.find_all(id="converter_display")
    if len(songs)>0:
        for i in range(len(songs)):
            a = list(songs[i].children)[1] #first entry '\n'
            alink = a.attrs['href']
            imglink = alink[:-5]+"-"+"%03d"%i+".png"
            resources.append((imglink,alink))
        return resources
    else:
        return None

    # useful for host sites requiring mp3 format (not in use)
def convert_from_midi(midi_url):
    global browser
    print("converting to mp3")
    #get page
    url = 'http://conversion-tool.com/midi'
    browser.open(url)
    #use forms
    browser.form = list(browser.forms())[0]
    browser['remotefile'] = midi_url
    browser.submit('calcbutton')
    return check_response(browser.geturl())

    # helper for mp3 conversion
def check_response(url):
    response = browser.open(url)
    start = time.clock()
    #refresh and recheck until success/failure/2 min
    while time.clock()-start < 2*60:
        response = browser.reload()
        soup = BeautifulSoup(response.read(),"html.parser")
        link = soup.find('a',class_="alert-link").attrs['href']
        if link == 'contact':
            return False,None
        elif link[-4:] == '.mp3':
            return True,link
        else:
            time.sleep(5)
    return False,link
    
        
browser_user_agent = "MusicalText abc music notation converter"
browser = mechanize.Browser()
browser.set_handle_robots(False)
browser.set_handle_refresh(False)
browser.addheaders = [(browser_user_agent, 'Firefox')]
