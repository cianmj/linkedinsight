from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pickle as pickle
import time
import os.path
import random

from BeautifulSoup import BeautifulSoup

import linkedin_parse as lparse

'''
Here we login to LinkedIn with the user's account from the homepage
Sleeps are required for page to completely load
'''

def check_exists(var):
	return var in locals() or var in globals()


class LinkedInBrowz(object):

	def __init__(self,username,password):
		driver = webdriver.Chrome('./chromedriver')
		driver.get("http://www.linkedin.com")
		time.sleep(1)
		elem = driver.find_element_by_id("session_key-login")
		elem.send_keys(username)
		elem = driver.find_element_by_id("session_password-login")
		elem.send_keys(password)
		elem = driver.find_element_by_id("signin")
		elem.click()
		time.sleep(2)
		self._driver = driver
		#html= driver.find_element_by_xpath(".//html") 
		#print html; raw_input()

	def get_user_profile(self,url):
		self._driver.get(url)
		#driver.get("https://www.linkedin.com/profile/view?id=21713660&authType=name&authToken=PULK&trk=prof-connections-name")
		time.sleep(5)
		#elem = driver.find_element_by_xpath('//*[@id="following-container"]/div/div/div[2]/ul/li[15]/a[2]')
		#elem = driver.find_element_by_class_name("see-action")
		for i in range(6):
			self._driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
			time.sleep(1)
		#elem = driver.find_element_by_id("profile_v2_follow")
		#driver.execute_script(elem)
		#webdriver.ActionChains(driver).move_to_element(elem).click(elem).perform()
		#elem.click()

	def get_connections(self):
		self._driver.get("https://www.linkedin.com/contacts/?filter=recent&trk=nav_responsive_tab_network#?sortOrder=recent&fromFilter=true&connections=disabled&")
		time.sleep(5)
		for i in range(10):
			self._driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
			time.sleep(1)
		source = self.download_html()
		self.save_html(source,"connections")

	def download_html(self):
		elem = self._driver.find_element_by_xpath("//*")
		#elem = driver.find_element_by_xpath('//*[@id="pagekey-contacts-contacts"]/script[9]')
		#source_code = elem.get_attribute()
		source_code = elem.get_attribute("outerHTML")
		return source_code

	def save_html(self,html_source,file_name):
		#content = elem.page_source
		f = open(file_name+'.html', 'wb')
		f.write(html_source.encode('utf-8'))
		f.close()

	def get_groups(self):
		self._driver.get("https://www.linkedin.com/myGroups?trk=nav_responsive_sub_nav_groups")
		time.sleep(5)
		for i in range(5):
			self._driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
			time.sleep(1)
		source = self.download_html()
		self.save_html(source,"groups")


	def all_contacts(self):
		url = "https://www.linkedin.com/vsearch/p?type=people&keywords=&orig=GLHD&rsid=&pageKey=contacts-manage-sources&search=Search&page_num="
		for i in range(1,1000):
			print i
			html = self.get_page(url+str(i),2)
			lparse.parse_all_contacts(html)
			time.sleep(random.uniform(5.,30.))

	### running this still...   *** changed ***
	def get_group_members(self,group_data):
		#group_list = [4543555,152247,2326082,2206132,89680,42370,2067005]
		#group_list = [87348,3744988,122866,2025093,1815840]
		group_list = [2212712,3427378,2154029]
		for gid in group_data:
			if gid in group_list:
				print gid,group_data[gid]
				group_site = "https://www.linkedin.com/groups?viewMembers=&gid="+str(gid)
				html = self.get_page(str(group_site))
				self.save_html(html,"group_page")
				number_pages=lparse.parse_group_members(html,gid)
				print number_pages
				group_site += "&split_page="
				for i in range(2,min(26,number_pages-1)):
					print i
					html = self.get_page(group_site+str(i))
					np=lparse.parse_group_members(html,gid)
					time.sleep(random.uniform(10.,30.))
			else:
				continue


	def get_page(self,group_url,scroll=5):
		self._driver.get(group_url)
		time.sleep(2)
		for i in range(scroll):
			self._driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
			time.sleep(1)
		return self.download_html()
		#self.save_html(source,"groups")		


	def get_companies(self):
		url = "https://www.linkedin.com/companies?dspFllwed=&split_page=1"
		self._driver.get(url)
		time.sleep(5)
		#for i in range(5):
		#	self._driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
		#	time.sleep(1)
		source = self.download_html()
		time.sleep(5)
		url = "https://www.linkedin.com/companies?dspFllwed=&split_page=2"
		self._driver.get(url)
		time.sleep(5)
		source += self.download_html()
		self.save_html(source,"companies")


	def get_company_members(self,data):
		id_list = [10667,2633739,260901]
		for gid in data:
			if gid in id_list:
				print gid,data[gid]
				site = "https://www.linkedin.com/vsearch/p?f_CC="+str(gid)+"&pt=people"
				#site = "https://www.linkedin.com/company/"+str(gid)
				html = self.get_page(str(site))
				self.save_html(html,"company_page")
				number_pages=lparse.parse_company_members(html,gid)
				site += "&page_num="
				for i in range(2,min(25,number_pages)):
					print i
					html = self.get_page(site+str(i))
					np=lparse.parse_company_members(html,gid)
					time.sleep(random.uniform(5.,30.))
			else:
				continue

	def _dump_user(self,uid):#add_data,db):
		url = "https://www.linkedin.com/profile/view?id=" + str(uid)
		html = self.get_page(url)
		soup = BeautifulSoup(html)

		file_name = str(uid)+'.html'
		outfile = open('html_data/'+file_name,'wb')
		outfile.write(str(soup))
		outfile.close()



	def extractSkills(self):
		html = self.get_page("https://www.linkedin.com/profile/view?id=38480")
		soup = BeautifulSoup(html)
		print soup


if __name__ == '__main__':

	[username,password] = pickle.load(open('linkedin_user.p','rb'))

	#if True:
	#	browz = LinkedInBrowz(username,password)
	#	browz.all_contacts()
	#	exit()

# Get users connections
	if not os.path.isfile('member_data_c.p'):
		print 'My Connections...'
		fname = "connections.html"
		if not os.path.isfile(fname):
			print "Downloading connections, press enter"; raw_input()
			if not check_exists("browz"):
				print 'Loading browz'
				browz = LinkedInBrowz(username,password)
			browz.get_connections()
		f = open(fname,"rb")
		connections_html = f.read()
		f.close()
		print "Parsing connections, press return"
		raw_input()
		lparse.parse_connections(connections_html)


# Get users groups
	if not os.path.isfile('group_data.p'):
		print 'My Groups...'
		fname = "groups.html"
		if True or not os.path.isfile(fname):
			print "Downloading groups, press enter"; raw_input()
			if not check_exists("browz"):
				print 'Loading browz'
				browz = LinkedInBrowz(username,password)
			browz.get_groups()
		f = open(fname,"rb")
		groups_html = f.read()
		f.close()
		print "Parsing groups"
		lparse.parse_groups(groups_html)


# Get members of groups
	if not os.path.isfile('member_data_cg.p'):
		print 'Getting members of groups, press enter'; raw_input()
		try:
			group_data = pickle.load(open('group_data.p','rb'))
		except:
			print "No group_data.p file"
			exit()

		if not check_exists("browz"):
			print 'Loading browz'
			browz = LinkedInBrowz(username,password)
			time.sleep(5)
		browz.get_group_members(group_data)


# Get users companies
	if not os.path.isfile('company_data.p'):
		print 'My companies...'
		fname = "companies.html"
		if not os.path.isfile(fname):
			print "Downloading companies, press enter"; raw_input()
			if not check_exists("browz"):
				print 'Loading browz'
				browz = LinkedInBrowz(username,password)
			browz.get_companies()
		f = open(fname,"rb")
		groups_html = f.read()
		f.close()
		print "Parsing companies"
		lparse.parse_companies(companies_html)	


# Get members of companies
	if not os.path.isfile('member_data_cgm.p'):
		print 'Getting members of companies, press enter'; raw_input()
		try:
			company_data = pickle.load(open('company_data.p','rb'))
		except:
			print "No company_data.p file"
			exit()
		if not check_exists("browz"):
			print 'Loading browz'
			browz = LinkedInBrowz(username,password)
			time.sleep(10)
		browz.get_company_members(company_data)


	print 'EXIT'




