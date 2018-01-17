import requests
import subprocess
import os
import string
import json

settings = json.load(open('pvgnaloader.ini'))

MAIL = settings['email']
PASS = settings['password']
RES = settings['resolution']
links = settings['links']

PVGNALOGIN = 'https://pvgna.com/login'
FINDTOKENL = 'name="authenticity_token" value="'
FINDTOKENR = '"'
FINDVLINKL = ';'
FINDVLINKR = '.m3u8'
FINDVNAMEL = '<h1 class="ui header">'
FINDVNAMER = '</h1>'

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
    
def print_progressbar(iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
    if iteration == total: 
        print()
    
print("Loading pvgna...")
s = requests.Session()
r = s.get(PVGNALOGIN)

token = find_between(r.text, FINDTOKENL, FINDTOKENR)

payload = {
    'utf8': '&#x2713;',
    'authenticity_token': token,
    'user[email]': MAIL,
    'user[password]': PASS,
    'commit': 'Log In'
}
print("Logging in...")
s.post(PVGNALOGIN, data=payload)

vlinks = []
vnames = []

print("Fetching video links...")
for link in links:
    r = s.get(link)
    vlink = find_between_r(r.text, RES + FINDVLINKR, FINDVLINKL)
    vname = find_between(r.text, FINDVNAMEL, FINDVNAMER)
    vname = sanitize_filename(vname)
    vlinks.append(vlink)
    vnames.append(vname)

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
    print("Nothing to download")
    exit()
    
print("Downloading videos...")
for idx,link in enumerate(vlinks):
    r = s.get(link + RES + '.m3u8')
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
            
print("Converting videos...")
for vname in vnames:
    ts_name = 'videos/' + vname + '.ts'
    mp4_name = 'videos/' + vname + '.mp4'
    with open(os.devnull, 'w') as f:
        subprocess.call('ffmpeg -y -i "' + ts_name + '" -acodec copy -vcodec copy "' + mp4_name + '"', shell=True, stdout=f, stderr=subprocess.STDOUT)
    os.remove(ts_name)

print("Done")