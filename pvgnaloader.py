import requests
import subprocess
import os
import string
import json
import math

settings = json.load(open('pvgnaloader.ini'))

res = settings['resolution']
links = settings['links']

PVGNALOGIN = 'https://pvgna.com/login'
FINDTOKENL = 'name="authenticity_token" value="'
FINDTOKENR = '"'
FINDVLINKL = ';'
FINDVLINKR = res + '.m3u8'
FINDVNAMEL = '<h1 class="ui header">'
FINDVNAMER = '</h1>'
FINDCHPTRL = '<a class="link step" href="'
FINDCHPTRR = '"'

def find_between(s, left, right):
    start = s.find(left) + len(left)
    end = s.find(right, start)
    return s[start:end]

def find_between_r(s, right, left):
    end = s.rindex(right)
    start = s.rindex(left, 0, end) + len(left)
    return s[start:end]
    
def sanitize_filename(s):
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    return ''.join(c for c in s if c in valid_chars)
    
def print_progressbar(iteration, total, prefix = '', suffix = '', decimals = 1, length = 50):
    blocks = ["", "▌"]
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    blockindex = math.floor(((length * iteration / total) - filledLength) * len(blocks))
    bar = '█' * filledLength + blocks[blockindex] + '-' * (length - filledLength - len(blocks[blockindex]))
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
    if iteration == total: 
        print()
    
print("Loading pvgna...")
s = requests.Session()
adapter = requests.adapters.HTTPAdapter(max_retries=10)
s.mount('https://', adapter)
s.mount('http://', adapter)
r = s.get(PVGNALOGIN)

token = find_between(r.text, FINDTOKENL, FINDTOKENR)

payload = {
    'utf8': '&#x2713;',
    'authenticity_token': token,
    'user[email]': settings['email'],
    'user[password]': settings['password'],
    'commit': 'Log In'
}
print("Logging in...")
r = s.post(PVGNALOGIN, data=payload)

if r.text.find('Invalid email or password.') != -1:
    print('Login incorrect')
    exit()

vlinks = []
vnames = []
chapterlinks = links[:]
    
if settings['crawlchapters']:
    print('\rFetching chapters...', end='\r')
    for idx,link in enumerate(links):
        r = s.get(link)
        restsrc = r.text
        while restsrc.find(FINDCHPTRL) != -1:
            chapterlink = 'https://pvgna.com' + find_between(restsrc, FINDCHPTRL, FINDCHPTRR)
            restsrc = restsrc[restsrc.find(FINDCHPTRL) + len(FINDCHPTRL):]
            if chapterlink not in chapterlinks:
                chapterlinks.append(chapterlink)
    print('\rFetching chapters... [%s]' % (str(idx+1)+'/'+str(len(links))), end='\r')
print()

links = chapterlinks

print('\rFetching video links...', end='\r')
for idx,link in enumerate(links):
    r = s.get(link)
    vlink = find_between_r(r.text, FINDVLINKR, FINDVLINKL)
    vname = find_between(r.text, FINDVNAMEL, FINDVNAMER)
    vname = sanitize_filename(vname)
    vlinks.append(vlink)
    vnames.append(vname)
    print('\rFetching video links... [%s]' % (str(idx+1)+'/'+str(len(links))), end='\r')
print()
    
idx = 0
while(idx < len(vnames)):
    mp4_name = 'videos/' + vnames[idx] + '.mp4'
    if os.path.isfile(mp4_name):
        print('"' + vnames[idx] + '" already exists!')
        del vlinks[idx]
        del vnames[idx]
    else:
        idx = idx + 1

if len(vnames) == 0:
    print('Nothing to download')
    exit()
    
print('Downloading videos...')
for idx,link in enumerate(vlinks):
    r = s.get(link + res + '.m3u8')
    lines = r.text.splitlines()
    ts_name = 'videos/' + vnames[idx] + '.ts'
    with open(ts_name, 'wb') as outfile:
        for idx2,ts_link in enumerate(lines):
            if (ts_link.endswith('.ts')):
                r = s.get(link + ts_link, stream=True)
                for chunk in r:
                    outfile.write(chunk)
            print_progressbar(idx*100+100/len(lines)*(idx2), len(vlinks)*100, str(idx+1)+'/'+str(len(vlinks)))

print_progressbar(100, 100, str(len(vlinks))+'/'+str(len(vlinks)))
            
print('\rConverting videos...', end='\r')
for idx,vname in enumerate(vnames):
    ts_name = 'videos/' + vname + '.ts'
    mp4_name = 'videos/' + vname + '.mp4'
    with open(os.devnull, 'w') as f:
        subprocess.call('ffmpeg -y -i "' + ts_name + '" -acodec copy -vcodec copy "' + mp4_name + '"', shell=True, stdout=f, stderr=subprocess.STDOUT)
    os.remove(ts_name)
    print('\rConverting videos... [%s]' % str(idx+1)+'/'+str(len(vnames)), end='\r')
print()

print("Done")