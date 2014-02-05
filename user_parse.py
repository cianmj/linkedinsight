import mechanize

import re
import string
from BeautifulSoup import BeautifulSoup
import cPickle as pickle

import TextItem as TextItem

from nltk import clean_html
import unicodedata

import os.path

chars = {
    '\xc2\x82' : ',',        # High code comma
    '\xc2\x84' : ',,',       # High code double comma
    '\xc2\x85' : '...',      # Tripple dot
    '\xc2\x88' : '^',        # High carat
    '\xc2\x91' : '\x27',     # Forward single quote
    '\xc2\x92' : '\x27',     # Reverse single quote
    '\xc2\x93' : '\x22',     # Forward double quote
    '\xc2\x94' : '\x22',     # Reverse double quote
    '\xc2\x95' : ' ',
    '\xc2\x96' : '-',        # High hyphen
    '\xc2\x97' : '--',       # Double hyphen
    '\xc2\x99' : ' ',
    '\xc2\xa0' : ' ',
    '\xc2\xa6' : '|',        # Split vertical bar
    '\xc2\xab' : '<<',       # Double less than
    '\xc2\xbb' : '>>',       # Double greater than
    '\xc2\xbc' : '1/4',      # one quarter
    '\xc2\xbd' : '1/2',      # one half
    '\xc2\xbe' : '3/4',      # three quarters
    '\xca\xbf' : '\x27',     # c-single quote
    '\xcc\xa8' : '',         # modifier - under curve
    '\xcc\xb1' : ''          # modifier - under line
}

def replace_chars(match):
    char = match.group(0)
    return chars[char]


def unorm(source):
    return str(unicodedata.normalize('NFKD', source).encode('ascii', 'ignore'))

def single_space_alph_num(mystring):
    reexp = r':(?=..(?<!\d:\d\d))|[^a-zA-Z0-9 ](?<!:)'
    temp = re.sub(reexp,"",str(mystring))
    return ' '.join(temp.split())   


def user_parse(uid,html):
    soup = BeautifulSoup(html.decode('utf8','ignore'))
    #soup = BeautifulSoup(html.decode('utf-8', 'ignore'))
    # Get background information in singlet spaced text form
    temp = soup.find('div',{'id':'background-experience'})
    temp2 = clean_html(str(temp))
    background = single_space_alph_num(temp2)
    # Get education information
    temp = soup.find('div',{'id':'background-education'})
    temp2 = clean_html(str(temp))
    education = single_space_alph_num(temp2)
    # Get number of connections
    temp = soup.find('div',{'class':'member-connections'})
    #try:
    if temp == None:
        n_connec = 0
    else:
        n_connec = re.findall(r'strong>(.*?)<',str(temp))[0].replace('+','')

    soup_skill = soup.find('ul',{'class':'skills-section'})
    skill_list = re.findall(r'data-endorsed-item-name\="(.*?)"',str(soup_skill))
    val_list = re.findall(r'data-count\="(.*?)">',str(soup_skill))
    skills = {}
    for skill,val in zip(skill_list,val_list):
        skills[skill] = val

    temp = soup.find('div',{'class':'profile-groups'})
    #print temp
    #gnames = re.findall(r'strong>(.*?)<',str(temp))
    gids2 = re.findall(r'groups\?gid\=(.*?)\&amp',str(temp))
    gnames = re.findall(r'alt\="(.*?)"',str(temp))
    #gids = set(gids)
    groups = {}

    gids = []
    for i in range(0,len(gids2),2):  # remove duplicate groupids
        gids.append(gids2[i])

    for row,row2 in zip(gids,gnames):
        gurl = "/groups?gid="+str(row)+"&trk=my_groups-b-grp-v"
        groups[row] = [row2.replace('&amp;','&'),gurl]


    user_tuple = (uid,n_connec,skills,background,education,groups)

    file_name = str(uid)+".p"
    outfile = open('user_data/'+file_name,'wb')
    pickle.dump(user_tuple,outfile)
    outfile.close()



def get_user_pictures(uid,html):
    browser = mechanize.Browser()
    browser.set_handle_robots(False)

    try:
    #soup = BeautifulSoup(html.decode('utf8','ignore'))
    #temp = re.findall(r"imgSrc(.*?)',img",str(soup))
    #url = str(temp[0].replace('\\','')[3:])
    #img = browser.open(url).read()
        soup = BeautifulSoup(html)
        tmp = soup.findAll('div',{'class':'profile-picture'})[0]
        url = re.findall(r'src\="(.*?)"',str(tmp))[0]
        img = browser.open(url).read()
    except:
        print "Skipped"
        load = open('static/pictures/blank.jpg', 'rb')
        img = load.read()
        load.close()

    filename = 'static/pictures/'+str(uid)+'.jpg'
    save = open(filename, 'wb')
    save.write(img)
    save.close()


if __name__=='__main__':

    #infile = open('html_data/id_list.p','rb')
    #id_list = pickle.load(infile)
    #infile.close()

    #infile = open("html_data/360806.html",'rb')
    #html = infile.read()
    #infile.close()
    #get_user_pictures(360806,html)
    #exit()
    infile = open('member_data.p','rb')
    member_data = pickle.load(infile)
    infile.close()

    filename="blacklist.dat"
    with open(filename) as f:
        blist = f.readlines()

    blacklist = []
    for row in blist:
        blacklist.append(int(row))

    path, dirs, files = os.walk("html_data").next()
    number_users = len(files)
    loop = 0; skip = 0;
    for filename in os.listdir('html_data'):
        filename = filename.replace('#','')
        location = str('html_data/'+filename)
        #for uid in id_list:
        uid = int(filename[0:-5])

        #uid = int(176210095)
        #location = 'html_data/'+str(uid)+'.html'

        try:
            #file_name = str(uid)+'.html'
            infile = open(location,'rb')
            html = infile.read()
            infile.close()
            loop += 1
        except:
            skip += 1
            continue

        if not os.path.isfile('user_data/'+str(uid)+'.p') and uid not in blacklist:
        #if member_data[uid][2]:
            print "Parsing: ",uid
            user_parse(uid,html)

        if not os.path.isfile('static/pictures/'+str(uid)+'.jpg'):
            print "Getting picture: ",uid
            get_user_pictures(uid,html)



    print 'Files processed:',loop
    print 'Files skipped:',skip

    print "user_parse. DONE."

