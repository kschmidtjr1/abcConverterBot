#built-in
import time
#downloaded
import praw
#local
import keys
import file_uploader
import form_handler

def main():
    global queue, timer, blocked
    subreddit = r.subreddit('test') 
    #iterate through all comments in given subreddit
    for comment in subreddit.stream.comments():
        if check_condition(comment):
            print('comment found!')
            #check if bot response recorded
            #need up update to use postgreSQL
            if not keys.comment_replied(comment.id):
                already_commented = False
                for reply in comment.replies:
                    print("checking replies")
                    #check if bot commented
                    if str(reply.author) == keys.reddit_user:
                        print("already commented")
                        keys.add_comment(comment.id)
                        already_commented = True
                        break
            else:
                already_commented = True
                print("already commented")
            #last check if reply found before activating bot
            if not already_commented:
                bot_action(comment)
        if len(queue) > 0 and (not blocked or time.time() > timer + 60 * 10):
            print("submitting %d comment(s)"%len(queue))
            blocked = False
            #submit_comments();

def check_condition(comment):
    text = comment.body
    called = '{' in text and '}' in text
    if called:
        start = text.index('{')
        end = text.index('}')
    return called and '|' in text[start+1:end]

def bot_action(comment):
    print("enter bot_action")
    keys.add_comment(comment.id)
    text = comment.body
    start = text.index('{')
    end = text.index('}')
    notation,title,description = parse_notation(text[start+1:end])
    temp_res = form_handler.convert_from_abc(notation)
    if temp_res is None:
        print('unable to convert from abc notation')
        return
    hosted_res = list()
    i = 0
    for r_img,r_mus in temp_res:
        imglink = file_uploader.upload_image(r_img,title[i],description[i])
        muslink = file_uploader.upload_music(r_mus,comment,title[i],description[i])
        hosted_res.append((imglink,muslink))
        i += 1
    msg = "Hi, I\'m MusicalTextBot.\n\nI converted your abc notation to"
    for img,mus in hosted_res:
        msg = msg+"\n\n[score](%s) and [performed](%s)"%(img,mus)
    msg = msg+"\n\n^^the ^^music ^^link ^^will ^^expire ^^in ^^roughly ^^1 ^^hour"
    reply = (comment,msg)
    queue.append(reply)
    
def submit_comments():
    response = queue[0]
    comment,msg = response
    try:
        comment.reply(msg)
        queue.pop(0)
        print(msg)
    except:
        print('blocked, looking for more comments')
        blocked = True
        timer = time.time;       

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


r = praw.Reddit('redditBot')
queue = list()
blocked = False
timer = time.time()
main()
