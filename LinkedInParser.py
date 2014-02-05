'''
Created on Nov 12, 2013

@author: work
'''

#import cookielib
#import os
#import urllib
#import urllib2
import mechanize
import re
import string
from BeautifulSoup import BeautifulSoup
import pickle

import time
import random


#[username,password] = pickle.load(open('linkedin_user.p','rb'))


def verify_access(soup):
    temp = soup.find("title")
    for row in temp:
        try:
            desc = str(re.findall(r'\>(.*?)\<\/',str(row))[0]).split(' ') # <title>Restricted Action | LinkedIn</title>
        except:
            return True

        if desc[0] == "Restricted":
            return False
        else:
            return True
    

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

    def extractContacts(self):
    	html = self.loadPage("https://www.linkedin.com/contacts/?filter=recent&trk=nav_responsive_tab_network#?sortOrder=recent&fromFilter=true&connections=disabled&")
    	soup = BeautifulSoup(html)
    	print soup

    def extractGroups(self):
        html = self.loadPage("https://www.linkedin.com/myGroups?trk=nav_responsive_sub_nav_groups")
        soup = BeautifulSoup(html)
        soup_groups = soup.findAll('a',{'class':'media-asset'})
        groups = []
        for row in soup_groups:
            #site = re.sub('.trk=my_groups-b-grp-v','',row['href'])
            site =  str(re.findall('\d+',row['href'])[0])
            #site = str(site[0])
            groups.append(site)
        return groups

    def extractMembers(self,group_site):
        group_site = "https://www.linkedin.com/groups?viewMembers=&gid="+group_site
        html = self.loadPage(group_site)
        soup = BeautifulSoup(html)
        if verify_access(soup) == False:
            print 'Pausing - access restricted'; raw_input()
            print 'continue?'; raw_input
        numberMembers = soup.findAll('h3',{'class':'page-title'})
        numberMembers = re.findall(r'\((.*?)\)',str(numberMembers[0]))
        numberMembers = int(re.sub(',','',numberMembers[0]))
        group_site += "&split_page="
        group_members = {}
        numberpages = int(numberMembers/20.)
        #for i in range(1,2):
        for i in range(2,min(50,numberpages)):
            if (i%10==1):
                print i
            html = self.loadPage(group_site+str(i))
            time.sleep(random.uniform(10.,40.))
            soup = BeautifulSoup(html)
            #soup_members = soup.findAll('li',{'class':'member'}) # for member IDs
            soup_name = soup.findAll('img',{'class':'photo'})
            soup_desc = soup.findAll('p',{'class':'member-headline'})
            for row,row2 in zip(soup_name,soup_desc):
                #group_members.append(str(re.findall('\d+',row['id'])[0]))
                try:
                    name = str(row['alt'])
                    desc = re.findall(r'\>(.*?)\<\/',str(row2))[0]
                    group_members[name] = desc
                except:
                    continue
        return group_members

    def extractSkills(self):
        html = self.loadPage("https://www.linkedin.com/profile/view?id=38480")
        soup = BeautifulSoup(html)
        print soup
        #soup_skills = soup.find("")



if __name__ == '__main__':

	[username,password] = pickle.load(open('linkedin_user.p','rb'))
	parser = LinkedInParser(username, password)

	parser.extractSkills()
	#parser.extractContacts()



