'''
Created on Nov 13, 2013

@author: work
'''
from LinkedInParser import LinkedInParser
import pickle

[username,password] = pickle.load(open('linkedin_user.p','rb'))

parser = LinkedInParser(username, password)

#skills = parser.extractSkills()
#print skills
#exit()

group_ids = parser.extractGroups()

try:
    groups = pickle.load( open("groups_name.p", "rb") )
except:
    groups = {}

for gid in group_ids: #gid = '1990010'
    if gid not in groups:
        print gid
        groups[gid] = parser.extractMembers(gid)
        pickle.dump(groups, open("groups_name.p", "wb"))

pickle.dump(groups, open("groups_name.p", "wb"))
print "\nEND\n"
