#built-in
import time
#downloaded
import praw
#local
import keys
import file_uploader
import form_handler

##imgur_id = config.get('imgurBot','client_id')
##imgur_secret = config.get('imgurBot','client_secret')
##client = pyimgur.Imgur(client_id)

##CLIENT_ID = 'Od88G943zMR4UQ'
##CLIENT_SECRET = '1Y8qqD4DFpmR6Xfr9FXpfxDSTXQ'
##REDIRECT_URL = 'http://127.0.0.1:65010/authorize_callback'
##REFRESH_TOKEN = '62167096-lev3INJkTFPKO69ug0fhq3BAqbg'

def main():
    print "entered main"
    subreddit = r.get_subreddit('test')
    #iterate through all comments in given subreddit
    for c in praw.helpers.comment_stream(r,subreddit):
        if check_condition(c):
            #check if bot response recorded
            if not keys.comment_replied(c.id):
                already_commented = False
                #get context of comment (to get replies)
                submission = r.get_submission(submission_id=c.permalink)
                try: #reveal all hiding comments
                    submission.replace_more_comments(limit=None, threshold=0)
                except:
                    pass
                comment = submission.comments[0]
                for reply in comment.replies:
                    print "entered reply loop" 
                    #check if bot commented
                    if str(reply.author) == keys.reddit_user:
                        print "already commented"
                        keys.add_comment(c.id)
                        already_commented = True
                        break
                #last check if reply found before activating bot
                if not already_commented:
                    bot_action(c)

def check_condition(comment):
    text = comment.body
    called = '{' in text and '}' in text
    if called:
        start = text.index('{')
        end = text.index('}')
    return called and '|' in text[start+1:end]

#TODO:threading or queued tasks for mp3 needing to be re-submitted or re-check_response
#TODO:if don't have mp3 after first pass, edit post later
def bot_action(comment):
    print "enter bot_action"
    keys.add_comment(comment.id)
    text = comment.body
    print "Text:\n" + text
    start = text.index('{')
    end = text.index('}')
    notation,title,description = parse_notation(text[start+1:end])
    print "parsed notation:\n" + notation
    temp_res = form_handler.convert_from_abc(notation)
    if temp_res is None:
        return
    hosted_res = list()
    i = 0
    for r_img,r_mus in temp_res:
        print r_img
        print r_mus
        imglink = file_uploader.upload_image(r_img,title[i],description[i])
        muslink = file_uploader.upload_music(r_mus,comment,title[i],description[i])
        hosted_res.append((imglink,muslink))
        i += 1
    msg = "Hi, I\'m musicaltextbot.\n\nI converted your abc notation to"
    for img,mus in hosted_res:
        msg = msg+"\n\n[score](%s) and [performed](%s)"%(img,mus)
    #TODO: set up queue to get other info while waiting
    passed = False
    while not passed:
        try:
            comment.reply(msg)
            passed = True
        except:
            print 'commented too much, waiting...'
            time.sleep(60*10)            
    print msg

def parse_notation(notation):
    tokens = notation.split('\n')
    prefix = []
    titles = []
    alternate = False
    descriptions = []
    songs = []
    new_tags = True
    new_music = True
    new_songs = []
    return_count = -1 #first song => new song
    song_num = -1 #nothing allocated
    output = ''
    
    while tokens[0] == '': #remove excess leading newlines
        tokens.remove('')
        
    for token in tokens:
        if token == '' and return_count > -1: #check number of 
            return_count += 1
            if(return_count > 1):
                return_count = -1
        elif ':' == token[1]:
            if new_tags or token[0] == 'X':
                song_num += 1
                if return_count == -1 or token[0] == 'X': #set new song
                    new_songs.append(song_num)
                    titles.append('')
                    descriptions.append('')
                    alternate = False
                new_tags = False
                prefix.append('') #allocate new position in list
            return_count = 0
            new_music = True
            if 'T:' in token: #start letter parsing
                if not alternate:
                    titles[len(new_songs)-1] = token[2:]
                    alternate = True
                else:
                    descriptions[len(new_songs)-1] += token[2:]+'\n'
            if 'N:' in token:
                descriptions[len(new_songs)-1] += token[2:]+'\n'
            if 'X:' in token: #don't trust user's numbering
                prefix[song_num] += token[0:2]+'%d\n'%song_num
            elif 'K:' in token and token.endswith(':'): #scale can't be missing
                prefix[song_num] += token+'C\n'
            else:
                prefix[song_num] += token+'\n'
        else:
            if return_count == -1 and new_tags: #set new song, empty tags
                song_num += 1
                new_songs.append(song_num)
                prefix.append('')
                titles.append('')
                descriptions.append('')
                songs.append('')
            if new_music: #following creation of tags
                new_music = False
                songs.append('') #allocate new position in list
            new_tags = True
            return_count = 0
            songs[song_num] += token
    for i in range(song_num+1):
        if 'X:' not in prefix[i] and i in new_songs: #starting tag
            prefix[i] = 'X:%d\n'%i + prefix[i]
        if 'K:' not in prefix[i] and i in new_songs: #ending tag
            prefix[i] += 'K:C\n'
        if len(songs[i]) > 0: #need music, can't process only tags
            output += prefix[i] + songs[i] + '\n'
    return output,titles,descriptions


reddit_user_agent = "MusicalText abc music notation converter by /u/lurker3710"
comment_ids = list()

r = praw.Reddit(user_agent=reddit_user_agent, site_name='redditBot')
r.refresh_access_information(refresh_token=r.refresh_token)
main()
##while True:
##    #try:
##    print "call main"
##    main()
##    except:
##        print "assign r"
##        r = praw.Reddit(user_agent=USER_AGENT, site_name='redditBot')
##        r.refresh_access_information(refresh_token=r.refresh_token)
