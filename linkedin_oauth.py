'''
Created on Nov 12, 2013

@author: work
'''

from linkedin import linkedin
from oauthlib import *

import csv

# Define CONSUMER_KEY, CONSUMER_SECRET,
# USER_TOKEN, and USER_SECRET from the credentials
# provided in your LinkedIn application

print 'Reading keys + secrets'
csv_file = csv.reader(open('auth2.0.txt','rb'), dialect=csv.excel_tab)
keys_secrets = []
for row in csv_file:
    keys_secrets.append(str(row[1]))
    #print str(row[1])

RETURN_URL = 'http://localhost:8000'

# Instantiate the developer authentication class
authentication = linkedin.LinkedInDeveloperAuthentication(keys_secrets[0], keys_secrets[1], keys_secrets[2], keys_secrets[3],RETURN_URL, linkedin.PERMISSIONS.enums.values())

# Pass it in to the app...
print 'Loading application.'
application = linkedin.LinkedInApplication(authentication)


# Use the app....
#NOTES:
# api member id is different than web member id !!!
# member url may have to be public 'http' not private 'https' !!!
print 'Getting profiles...'
#g = application.get_profile(member_url="http://www.linkedin.com/in/cianmenzeljones")
#g = application.get_profile(member_url="https://www.linkedin.com/profile/view?id=104100816")
#g = application.get_profile(member_id="104100816",selectors=['id', 'first-name', 'last-name','skills', 'educations'])

#g = application.get_profile(selectors=['id', 'first-name', 'last-name','skills', 'educations','group_memberships','summary','courses'])
#print g

h = application.get_connections(selectors=['id'])
print h['values']

for val in h['values']:
	mem = val['id']
	hi = application.get_profile(member_id=mem,selectors=['id', 'first-name', 'last-name','skills', 'educations','group_memberships','summary','courses'])
	print hi
	raw_input()


