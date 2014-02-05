
import os
from flask import Flask, render_template, request, jsonify
import MySQLdb
#from flask.ext.cache import Cache
import sys
import ast
import json
import re

import modelling as mod

app = Flask(__name__)
#db = MySQLdb.connect(user="root", host="localhost",db="world",unix_socket="/var/mysql/mysql.sock")
db = MySQLdb.connect(user="root", host="localhost", port=3306, db="linkedinsight",unix_socket="/var/mysql/mysql.sock")


@app.route("/")
def hello():
    #value = request.args.get('q',None)

    #cursor = db.cursor()
    #sql = "DROP TABLE IF EXISTS skill_user,user_details"
    #cursor.execute(sql)
    print "Entering index.html"
    list = ""
    return render_template('index.html',value=list)#,word=value)


# this will return the main search results
@app.route("/search.html")
def search():
    print "Entering search.html"

    email = request.args.get('email',None)
    passwd = request.args.get('passwd',None)
    fromindex = request.args.get('fromindex',None)
    print email, passwd, fromindex

    #if email != "cianmj@gmail.com" and passwd != "cianmj":
    #if fromindex == "index" and email != "" and passwd != "":
    if fromindex == "index" and email != "cianmj@gmail.com" and passwd != "cianmj":
        error = "User not in database - please contact administrator."
        return render_template('index.html',value=error)

    value = request.args.get('q',None)
    print value

    data = mod.find_skills(value,False)
    print data
    if data == 0:
        error = "Cannot find keyword(s)"
        return render_template('index.html',value=error)

    tmp = []
    for val in data:
        tmp.append(int(val[1]))
    minvalue = min(tmp)
    maxvalue = max(tmp)

    return render_template('search.html',results=data,keyword=value,maxval=maxvalue,minval=minvalue)


@app.route("/search_matter.html")
def search_matter():
    value = request.args.get('q',None)
    print "Entering search_matter.html"
    value = value.encode('ascii','ignore')

    #from code import interact; interact(local=locals())
    
    data = mod.find_skills(value,True)
    if data == 0:
        error = "Cannot find keyword(s)"
        return render_template('index.html',value=error)
        
    tmp = []
    for val in data:
        tmp.append(int(val[1]))
    minvalue = min(tmp)
    maxvalue = max(tmp)
    
    return render_template('search_matter.html',results=data,keyword=value,maxval=maxvalue,minval=minvalue)

# this will return results to jquery function (conn,people,groups)
@app.route("/search_get")
def search_get():

    skill_text = request.args.get('skills','')
    skill_text = skill_text.encode('ascii','ignore')
    skill_list = skill_text.split(',')

    keyword = request.args.get('keyword','')

    #print keyword
    #from code import interact; interact(local=locals())

    data = mod.find_people_groups(skill_list,keyword)

    #print data
    #from code import interact; interact(local=locals())
    # data output looks good here -- see what happens in javascript
    #return data
    return jsonify(data)



@app.route('/about.html')
def about():
    return render_template('about.html')

@app.route('/contact.html')
def contact():
    return render_template('contact.html')

@app.route('/presentation.html')
def presentation():
    return render_template('presentation.html')

@app.route("/db")
def cities_page():
    db.query("SELECT Name FROM city;")

    query_results = db.store_result().fetch_row(maxrows=0)
    cities = ""
    for result in query_results:
        cities += unicode(result[0], 'ISO-8859-1')
        cities += "<br>"
    return cities

@app.route("/db_fancy")
def cities_page_fancy():
    db.query("SELECT Name, CountryCode, Population FROM city;")

    query_results = db.store_result().fetch_row(maxrows=0)
    cities = []
    for result in query_results:
        cities.append(dict(name=unicode(result[0], 'ISO-8859-1'), country=result[1], population=result[2]))
    return render_template('cities.html', cities=cities)


@app.route('/<pagename>')
def regularpage(pagename=None):
    """
    Route not found by the other routes above. May point to a static template.
    """
    return "You've arrived at " + pagename
    #if pagename==None:
    #    raise Exception, 'page_not_found'
    #return render_template(pagename)

if __name__ == '__main__':
    print "Starting debugging server."
    try:
        pt = int(sys.argv[1])
    except:
        pt = 5000
    print "Port:",pt

    app.run(debug=True, host='localhost', port=pt)



