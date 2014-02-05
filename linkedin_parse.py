import re
import string
from BeautifulSoup import BeautifulSoup
#import cPickle as pickle
import pickle as pickle
from nltk import clean_html
import TextItem
import unicodedata

def stripHtmlTags(self, htmlTxt):
	if htmlTxt is None:
		return None
	else:
		return ''.join(BeautifulSoup(htmlTxt).findAll(text=True))

def removeTags(html, *tags):
	soup = BeautifulSoup(html)
	for tag in tags:
		for tag in soup.findAll(tag):
			tag.replaceWith("")
	return soup


def unorm(source):
	return str(unicodedata.normalize('NFKD', source).encode('ascii', 'ignore'))

def parse_connections(html):
	soup = BeautifulSoup(html)
	#soup_members = soup.findAll('li',{'class':'member'}) # for member IDs
	soup_name = soup.findAll('h3',{'class':'name'})
	soup_desc = soup.findAll('a',{'class':'title'})
	#print soup_name
	#print 
	#print soup_desc
	try:
		infile = open('member_data.p','rb')
		member_data = pickle.load(infile)
		infile.close()
	except:
		member_data = {}
	loop=0
	for row,row2 in zip(soup_name,soup_desc):
		loop+=1
		#group_members.append(str(re.findall('\d+',row['id'])[0]))
		try:
			temp = re.findall(r'\>(.*?)\<\/',str(row))[0]
			name = temp.split('>')[1]
			url = temp.split('\"')[1]
			member_id = re.findall(r'li_(.*?)&amp',str(url))[0]
			desc = re.findall(r'>(.*?)<',str(row2))[0]
			member_data[int(member_id)]=(str(name),str(desc),True,list(),list(),str(url))
			#print name,member_id
		except:
			print "Skipping connections... ?"
			exit()
			continue
	''' How to append values to list within a tuple in a dictionary
	mid = 230033220
	if mid in member_data:
		print member_data[mid]
		member_data[mid][3].append("name")
		print member_data[mid]
	'''
	pickle.dump(member_data,open('member_data.p','wb'))

def parse_all_contacts(html):

	infile = open('member_data.p','rb')
	member_data = pickle.load(infile)
	infile.close()

	soup = BeautifulSoup(html)
	temp = soup.findAll('a',{'class':'title'})
	temp2 = soup.findAll('p',{'class':'description'})
	temp3 = re.findall(r'"degree-icon ">(.*?)<',str(soup))
	for row,row2,row3 in zip(temp,temp2,temp3):
		mid = int(re.findall(r'id\=(.*?)&amp',str(row))[0])
		name = re.findall(r'">(.*?)</a>',str(row))[0]
		desc = str(re.findall(r'>(.*?)</',str(row2))[0]).replace("&amp;", "&")
		url = "/profile/view?id="+str(mid)
		if row3 == '1':
			conn = True
		else:
			conn = False
		#print mid,name,desc,url,conn
		#raw_input()

		if mid not in member_data:
			member_data[mid]=(str(name),str(desc),conn,list(),list(),str(url))
			print 'New member added:', mid,str(name),conn
		else:
			tmp = member_data[mid]
			member_data[mid]=(tmp[0],tmp[1],conn,tmp[3],tmp[4],tmp[5])
			continue

	outfile = open('member_data.p','wb')
	pickle.dump(member_data,outfile)
	outfile.close()


def parse_groups(html):
	soup = BeautifulSoup(html)
	soup_name = soup.findAll('a',{'class':'public'})
	soup_name2 = soup.findAll('a',{'class':'private'})

	group_data = {}
	for row in soup_name:
		try:
			name = re.findall(r'>(.*?)<',str(row))[0]
			url = row['href']
			temp = re.findall(r'-(.*?)\?trk',str(url))
			group_id = str(temp[0]).split("-")[-1]
			group_data[int(group_id)] = [name,url]
		except:
			print "Skipping groups... ?"
			exit()

	for row in soup_name2:
		try:
			name = (re.findall(r'>(.*?)<',str(row))[0]).replace("&amp;", "&")
			url = row['href']
			group_id = re.findall(r'gid=(.*?)\&trk',str(url))[0]
			group_data[int(group_id)] = [name,url]
		except:
			print "Skipping groups... ?"
			exit()

	pickle.dump(group_data,open('group_data.p','wb'))


def parse_group_members(html,gid):
	soup = BeautifulSoup(html)
	try:
		numberMembers = soup.findAll('h3',{'class':'page-title'})
		numberMembers = re.findall(r'\((.*?)\)',str(numberMembers[0]))
		numberMembers = int(re.sub(',','',numberMembers[0]))
		numberpages = int(numberMembers/20.)
	except:
		numberpages = 25
	infile = open('member_data.p','rb')
	member_data = pickle.load(infile)
	infile.close()

	soup_id = soup.findAll('li',{'class':'member'})
	soup_name = soup.findAll('img',{'class':'photo'})
	soup_desc = soup.findAll('p',{'class':'member-headline'})
	loop = 0

	for row,row2,row3 in zip(soup_name,soup_desc,soup_id):
		try:
			mid = int(row3['id'].split("-")[1])
			name = unorm(row['alt'])
			desc = re.findall(r'\>(.*?)\<\/',str(row2))[0]
			url = "profile/view?id="+str(mid)
			loop += 1
			if mid in member_data:
				if gid not in member_data[mid][3]:
					member_data[mid][3].append(gid)
					continue
			else:
				member_data[int(mid)]=(str(name),str(desc),False,[gid],list(),str(url))
		except:
			print 'Skipping group members'
			continue

	outfile = open('member_data.p','wb')
	pickle.dump(member_data,outfile)
	outfile.close()
	return numberpages


def parse_companies(html):
	soup = BeautifulSoup(html)
	soup_name = soup.findAll('div',{'class':'logo'})
	soup_id = soup.findAll('div',{'class':"following stop-following"})
	company_data = {}
	loop = 0
	for row,row2 in zip(soup_name,soup_id):
		loop += 1
		try:
			name = re.findall(r'alt\="(.*?)"',str(row))[0]
			url = re.findall(r'href\="(.*?)"',str(row))[0]
			cid = re.findall(r'/companies/(.*?)\?stp',str(row2))[0]
			company_data[int(cid)] = [name,url]
		except:
			print "Skipping groups... ?"
			exit()
			continue
	pickle.dump(company_data,open('company_data.p','wb'))


def parse_company_members(html,gid):
	soup = BeautifulSoup(html)
	try:
		numberMembers = soup.findAll('div',{'id':'results_count'})
		numberMembers = float(re.findall(r'strong>(.*?)<',str(numberMembers[0]))[0])
		numberpages = int(numberMembers/10.)+2
	except:
		numberpages = 50
	infile = open('member_data.p','rb')
	member_data = pickle.load(infile)
	infile.close()

	soup_name = soup.findAll('a',{'class':'title'})
	soup_desc = soup.findAll('p',{'class':'description'})
	loop = 0
	for row,row2 in zip(soup_name,soup_desc):
		try:
			mid = re.findall(r'id\=(.*?)\&amp',str(row))[0]
			name = re.findall(r'>(.*?)</a>',str(row))[0]
			desc = clean_html(str(row2))
			url = "profile/view?id="+str(mid)
			loop += 1
			if mid in member_data:
				if gid not in member_data[mid][4]:
					member_data[mid][4].append(gid)
					continue
			else:
				member_data[int(mid)]=(str(name),str(desc),False,list(),[gid],str(url))
		except:
			print 'Skipping group members'
			continue
	outfile = open('member_data.p','wb')
	pickle.dump(member_data,outfile)
	outfile.close()
	return numberpages



if __name__=="__main__":

	#f = open('groups.html','rb')
	f = open('temp.txt','rb')
	html = f.read()
	f.close()
	parse_all_contacts(html)
	#parse_groups(html)

	#infile = open('member_data.p','rb')
	#member_data = pickle.load(infile)
	#infile.close()
	#mid = 104100816
	#print member_data[mid]

	print 'linedin_parse EXIT'
	exit()

