import mechanize
import re
import string
from BeautifulSoup import BeautifulSoup
import pickle
import os.path

import time
import random

import DbAccess as dba
import MySQLdb

from scraper import LinkedInBrowz


class LinkedInParser(object):

    def __init__(self, login, password):
        # Simulate browser with cookies enabled
        browser = mechanize.Browser()
        browser.set_handle_robots(False)
        browser.open("https://www.linkedin.com/")
        browser.select_form(name="login")
        browser["session_key"] = login
        browser["session_password"] = password
        self.br = browser
        response = browser.submit()
        title = self.loadTitle()
        print title

    def loadPage(self, url):
        return self.br.open(url)


    def loadTitle(self):
        html = self.loadPage("http://www.linkedin.com/nhome")
        soup = BeautifulSoup(html)
        return soup.find("title")

    def _dump_user(self,uid): #add_data,db):
        url = "https://www.linkedin.com/profile/view?id=" + str(uid)
        html = self.loadPage(url)
        soup = BeautifulSoup(html)
        #db.cursor.execute(add_data, (uid,"lkajsdlkfj"))
        #c=db.cursor()
        #c.execute(add_data, (uid,"lkajsdlkfj"))
        #db.cursor.execute('SHOW TABLES')
        #data = db.cursor.fetchall()
        #for row in data:
        #    print row
        file_name = str(uid)+'.html'
        outfile = open('html_data/'+file_name,'wb')
        outfile.write(str(soup))
        outfile.close()



if __name__ == '__main__':
    [username,password] = pickle.load(open('linkedin_user.p','rb'))
    #parser = LinkedInParser(username, password)

    browz = LinkedInBrowz(username,password)

    infile = open('member_data.p','rb')
    member_data = pickle.load(infile)
    infile.close()
    #db = dba.DbAccess('user_html',usr='root')
    #add_data = ("INSERT INTO raw_data VALUES (%s, %s)")
    #group_list = [152247,4332669]

    try:
        infile = open('html_data/id_list.p','rb')
        id_list = pickle.load(infile)
        infile.close()
    except:
        id_list = []

    for mid in member_data:
        #if group_list[0] in member_data[mid][3] or group_list[1] in member_data[mid][3]:
        if True or not member_data[mid][2]:
            #if mid not in id_list:
            if not os.path.isfile('html_data/'+str(mid)+'.html'):
                print mid
                browz._dump_user(mid)
                #parser._dump_user(mid)#,add_data,db)
                id_list.append(mid)
                time.sleep(random.uniform(9.,31.))


    outfile = open('html_data/id_list.p','wb')
    id_list = pickle.dump(id_list,outfile)
    outfile.close()

    #db.connect(usr='root')
    #db.cnx.commit()
    #db.close()
