import MySQLdb
import numpy as np
from os import sys
from sklearn.ensemble import RandomForestRegressor
#from collections import defaultdict
import cPickle as pickle
import collections
import forest as fr
import kmeans as km
import os
import re
import math as math
import random

import matplotlib.pyplot as plt

from collections import Counter

def alpha_num(mystring):
    reexp = r':(?=..(?<!\d:\d\d))|[^a-zA-Z0-9 ](?<!:)'
    temp = re.sub(reexp,"",str(mystring))
    return ' '.join(temp.split())  
    
def numb(mystring):
    reexp = r':(?=..(?<!\d:\d\d))|[^0-9 ](?<!:)'
    temp = re.sub(reexp,"",str(mystring))
    return int(' '.join(temp.split()))


def check_exists(var):
    return var in locals() or var in globals()


def map_feature(x):
    """ Add polynomial features to x in order to reduce high bias.
    """
    m, n = x.shape
    out = x

    # Add quodratic features.
    for i in range(n):
        for j in range(i, n):
            out = np.hstack((out, x[:, i].reshape(m, 1) * x[:, j].reshape(m, 1)))

    # Add cubic features.
    for i in range(n):
        for j in range(i, n):
            for k in range(j, n):
                out = np.hstack(
                    (out, x[:, i].reshape(m, 1) * x[:, j].reshape(m, 1) * x[:, k].reshape(m, 1)))
    return out


def scale_data(x):
    """ Scale data with zero mean and unit variance.
    """
    mu = x.mean(axis=0)
    sigma = x.std(axis=0)
    x = (x - mu) / sigma
    return (x, mu, sigma)


def logistic_regression(db,features_ll):

    if not check_exists('db'):
        db = MySQLdb.connect(user="root",host="localhost",port=3306,db="linkedinsight",unix_socket="/var/mysql/mysql.sock")
        cursor = db.cursor()

    sql = """SELECT su.userid,ud.num_connections,ud.job,su.skill,su.value,ud.phd
            from skill_user su join user_features ud on su.userid = ud.userid"""

    db.query(sql)

    query_results = db.store_result().fetch_row(maxrows=0)
    data = []
    for result in query_results:
        data.append(result)

    print features_ll
    scale_val = 100
    features = {}
    prev_id = 0
    for row in data:
        if int(row[0]) not in features:
            features[int(row[0])] = [int(row[2]),int(row[5])]
            features[int(row[0])] += [0] * len(features_ll)
        skill = row[3]
        if skill in features_ll:
            features[int(row[0])][features_ll.index(skill)+2] = row[4]


    data = []
    for key in features.keys():
        val = features[key][2:]
        if all(v == 0 for v in val):
            del features[key]

    for key in features.keys(): 
        data.append(features[key])

    print 'Entering learning algorithm...'
    nloops = 20
    feature_sum = np.array([0.]*(len(data[0])-1))
    for i in range(nloops):
        train_data = []
        test_data = []
        cut = 0.9
        for i in range(len(data)):
            if random.random() < cut:
                train_data.append(data[i])
            else:
                test_data.append(data[i])
        train_data = np.array(train_data)
        test_data = np.array(test_data)

        #print 'Include polynomial structure and scaled data:'
        #map_feature(train_data); map_feature(test_data)
        #train_data_scale,mu,sigma = scale_data(train_data[:,1:])
        #train_data = np.column_stack((train_data[:,0],train_data_scale))
        #test_data = np.column_stack((test_data[:,0],(test_data[:,1:]-mu)/sigma))

        feature_import = fr.forest_solver(train_data,test_data)

        for i in range(len(feature_import)):
            feature_sum[i] += feature_import[i]

    feature_sum /= float(nloops)
    feature_import = list(feature_sum)


    tmp = {}
    tmp['PhD'] = feature_import[0]
    for i in range(len(features_ll)):
        tmp[features_ll[i]] = feature_import[i+1]

    feature_sort = sorted(tmp.items(), key=lambda x: -x[1])


    # K-Means++ clustering of skills
    #skill_set = [0] * len(feature_import)
    #for i in range(0,5):
    #    skill_set[features_ll.index(feature_sort[i][0])] = 1
    #feature_data = data[:,1::]
    #cluster = km.kmeans(feature_data,skill_set)


    return feature_sort


def get_skill_list(db,sql,sql2):

    db.query(sql)

    query_results = db.store_result().fetch_row(maxrows=0)
    skill_list = {}
    for result in query_results:
        if result[0] in skill_list:
            #skill_list[result[0]] += 1 #result[1]
            # skill_list[result[0]] += float(result[1]/math.log(result[2]+10))
            skill_list[result[0]] += float(result[1])
        else:
            #skill_list[result[0]] = 1 #result[1]
            # skill_list[result[0]] = float(result[1]/math.log(result[2]+10))
            skill_list[result[0]] = float(result[1])

    db.query(sql2)
    query_results = db.store_result().fetch_row(maxrows=0)
    for result in query_results:
        jobtot = float(result[0])

    for skill in skill_list:
        skill_list[skill] /= jobtot


    skill_set = set(skill_list.keys())

    skill_dict = sorted(skill_list.items(), key=lambda x: -x[1])

    return skill_set,skill_dict



def get_skill_match(db,sql,skills):

    db.query(sql)

    query_results = db.store_result().fetch_row(maxrows=0)
    user_list = []
    skill_list = []
    endorse_list = []
    url_dict = {}
    id_dict = {}

    for result in query_results:
        user_list.append(result[0])
        skill_list.append(result[1])
        endorse_list.append(result[4])
        url_dict[result[0]] = result[2]
        id_dict[result[0]] = result[3]

    top_user = {}
    for i in range(len(user_list)):
        if skill_list[i] in skills:
            if len(skills) == 1:
                inc = endorse_list[i]
            else:
                inc = 1 + int(endorse_list[i]/10.)
            if user_list[i] in top_user:
                top_user[user_list[i]] += inc
            else:
                top_user[user_list[i]] = inc

    user_sort = sorted(top_user.items(), key=lambda x: -x[1])

    user_url = []
    for val in user_sort:
        user_url.append([val[0].split(',')[0].split('(')[0],url_dict[val[0]],id_dict[val[0]]])

    return user_url
    

def most_popular_groups(db,jobsid):

    jobsidstr = '","'.join([str(i) for i in jobsid])

    sql = 'select groupid from group_all_user where userid in ("' + jobsidstr + '")'
    db.query(sql)
    query_results = db.store_result().fetch_row(maxrows=0)
    groupsid = []
    for result in query_results:
        groupsid.append(int(result[0]))

    gtmp = set(groupsid)
    gcount = {}
    for item in gtmp:
        gcount[item] = groupsid.count(item)

    return sorted(gcount.items(), key=lambda x: -x[1])



def keyword_table(db,keyword):

    keyword = str(keyword.lower().replace(';',''))

    cursor = db.cursor()

    sql = """SELECT ud.userid,ud.background,u.title FROM user_details ud 
            JOIN user u on u.userid = ud.userid"""

    db.query(sql)
    query_results = db.store_result().fetch_row(maxrows=0)
    
    # Keyword search of profile tile and background...
    jobsid = []
    loop = 0
    print keyword
    for result in query_results:
        if keyword in result[2].lower():
            loop += 1
            jobsid.append(int(result[0]))

    if loop<200:
        for result in query_results:
            if int(result[0]) not in jobsid:
                if keyword in result[1].lower():
                    loop += 1
                    jobsid.append(int(result[0]))


    print "Number of users with job: ",loop
    if loop < 10:
        return 0

    #  Find top american location of people wth job with this keyword
    #top_locations = find_locations(db,jobsid)
    #print top_locations
    #exit()
    #


    gdicsort = most_popular_groups(db,jobsid)

    number_of_groups = 3

    loop = 0
    groupidstr = []
    for val in gdicsort:
        #print val
        loop += 1
        if loop>number_of_groups:
            break
        else:
            groupidstr.append(str(val[0]))
    print "Number of groups: ", loop

    groupidstr = '","'.join(groupidstr)
    sql = 'select userid FROM group_all_user WHERE groupid IN ("' + groupidstr + '")'
    db.query(sql)
    query_results = db.store_result().fetch_row(maxrows=0)
    userlist = []
    for result in query_results:
        userlist.append(int(result[0]))
    print "Number of users in groups:", len(set(userlist))


    # Append more users with jobs (from other groups)
    for uid in jobsid:
        if uid not in userlist:
            userlist.append(int(uid))


    userliststr = "','".join([str(i) for i in set(userlist)])
    sql = """select userid, num_connections, education FROM user_details 
            WHERE userid IN ('""" + userliststr + "')"
    db.query(sql)
    query_results = db.store_result().fetch_row(maxrows=0)

    sql = """CREATE TABLE user_features (userid int not null,num_connections int,
        job BOOLEAN,phd BOOLEAN,foreign key(userid) REFERENCES user(userid))"""
    cursor.execute(sql)

    sql = "INSERT INTO user_features values (%s,%s,%s,%s)"
    #user_features = []

    phd_keywords = ['phd','ph d','p h d', 'docorate','post docorate']
    loop = 0
    loop_job = 0
    loop_phd = 0
    for item in query_results:
        phd = False
        for word in phd_keywords:
            if word in item[2].lower():
                phd = True
                loop_phd +=1
        user_has_job = False
        if int(item[0]) in jobsid:
            user_has_job = True
            loop_job +=1
        loop += 1   
        cursor.execute(sql,(item[0],item[1],user_has_job,phd))


    print "Table with ",loop," entries created."
    print "Number of people with jobs: ",loop_job
    print "Number of people with PhDs: ",loop_phd
    db.commit()



def find_skills(keyword,matter):

    keyword = str(keyword.lower().replace(';',''))

    # Check if keyword already exists in database:
    filename = keyword.replace(' ','')
    location = ''
    if not matter:
        location = 'results/'+filename+'.p'
        if os.path.isfile(location):
            infile = open(location,'rb')
            job_skills = pickle.load(infile)
            infile.close()
            return job_skills
    else:
        location = 'results/'+filename+'_matter.p'
        if os.path.isfile(location):
            infile = open(location,'rb')
            job_skills = pickle.load(infile)
            infile.close()
            return job_skills


    db = MySQLdb.connect(user="root",host="localhost",port=3306,db="linkedinsight",unix_socket="/var/mysql/mysql.sock")
    cursor = db.cursor()

    sql = '''DROP TABLE IF EXISTS user_features'''
    cursor.execute(sql)
    val = keyword_table(db,keyword)
    if val == 0:
        print "Cannot find any users \n"
        return 0


    #get_education(db,keyword)
    #exit()


    sql = "SELECT su.skill, su.value, uf.num_connections from skill_user su join user_features uf on su.userid = uf.userid where uf.job = True and su.value>5;"
    sql2= "select count(*) from user_features uf where uf.job=True;"
    set_w_job, w_job = get_skill_list(db,sql,sql2)

    sql = "SELECT su.skill, su.value, uf.num_connections from skill_user su join user_features uf on su.userid = uf.userid where uf.job = False and su.value>5;"
    sql2="select count(*) from user_features uf where uf.job=False;"
    set_wo_job, wo_job = get_skill_list(db,sql,sql2)

    #print w_job[0:20]; print
    #print wo_job[0:20]; print 

    number_to_return = 5
    if not matter:
        job_skills = []
        for item in w_job:
            # job_skills.append([item[0],get_skill_percentage(db,[item[0]]))
            job_skills.append([item[0],get_skill_percentage(db,[item[0]]),int(item[1])])
            # job_skills.append([item[0],int(item[1])])
        print location
        outfile = open(location,'wb')
        pickle.dump(job_skills[0:number_to_return],outfile)
        outfile.close()
        return job_skills[0:number_to_return]

    # Normalize the skill fields - between jobs and no-jobs sets
    '''
    loop = 0
    avg_dist = 0
    for val in w_job:
        for val2 in wo_job:
            if val[0]==val2[0]:
                loop += 1
                avg_dist += (val2[1]/val[1])
                break
        if loop>5: ## this changes results - was 20
            break
    print loop,avg_dist; print
    '''

    num_features = 20
    features_ll = []
    for i in range(num_features):
        features_ll.append(w_job[i][0])
        features_ll.append(wo_job[i][0])
    print "Creating features:"
    temp = logistic_regression(db,list(set(features_ll))) # return ordered list of tuples 

    """ Compute distance between employed and unemployed skill sets
    dw_job = {}
    if loop != 0:
        avg_dist /= float(loop)
        print avg_dist
        for val in w_job:
            try:
                dw_job[val[0]] = avg_dist*val[1] - dict(wo_job)[val[0]]
            except:
                dw_job[val[0]] = avg_dist*val[1]
    else:
        dw_job = dict(w_job)
    temp = sorted(dw_job.items(), key=lambda x: -x[1])
    """

    scale = 150.
    job_skills = []
    for i in range(len(temp)):
        if str(temp[i][0]).lower() == keyword:
            job_skills.append([temp[i][0],int(scale*temp[i][1])])
            continue
        cycle=False
        word_list = temp[i][0].split(' ')
        if len(word_list) > 2:
            continue
        for word in word_list:
            if word.lower() in keyword:
                cycle = True
        if cycle == True:
            continue
        else:
            job_skills.append([temp[i][0],int(scale*temp[i][1])])


    outfile = open(location,'wb')
    pickle.dump(job_skills[0:number_to_return],outfile)
    outfile.close()

    return job_skills[0:number_to_return]


def find_people_groups(job_skills,keyword):

    if (job_skills==0):
        return 0

    filename0 = (''.join(keyword)).replace(' ','').lower()     
    filename = (''.join(job_skills)).replace(' ','').lower()
    location = 'results/'+filename0+filename+'.p'
    if os.path.isfile(location):
        infile = open(location,'rb')
        people_group = pickle.load(infile)
        infile.close()
        return people_group


    db = MySQLdb.connect(user="root",host="localhost",port=3306,db="linkedinsight",unix_socket="/var/mysql/mysql.sock")
    cursor = db.cursor()

    skillfrac = get_skill_percentage(db,job_skills)

    linkedin_url="http://www.linkedin.com"

    sql = """SELECT u.name,su.skill,u.url,u.userid,su.value from skill_user su join user_features uf 
                on su.userid = uf.userid join user u on u.userid = su.userid
                where uf.job = True and su.value>10"""
    leader_ids = get_skill_match(db,sql,job_skills)

    for i in range(len(leader_ids)):
        if leader_ids[i][1][0] == '/':
            leader_ids[i][1] = linkedin_url + leader_ids[i][1]
        else:
            leader_ids[i][1] = linkedin_url+'/' + leader_ids[i][1]

    #
    sql = """SELECT u.name,s.skill,u.url,u.userid,s.value from user u join skill_user s 
                on u.userid=s.userid where u.connection = True"""
    conn_ids = get_skill_match(db,sql,job_skills)

    for i in range(len(conn_ids)):
        conn_ids[i][1] = linkedin_url + conn_ids[i][1]

    # Most popular group evaluation ...
    #sql = """SELECT ga.name,ga.url,count(*) c from group_all ga
    #        join group_all_user gau on ga.groupid = gau.groupid 
    #        join user_features uf on uf.userid = gau.userid where
    #        uf.job = True group by ga.groupid order by c desc limit 5"""
    #db.query(sql)
    #qresults = db.store_result().fetch_row(maxrows=0)

    #sql = 'select userid FROM group_all_user WHERE groupid IN ("' + groupidstr + '")'

    # Collect all groups of members with particular skill
    job_skills_str = '","'.join(job_skills)
    sql = """ select ga.groupid,su.value, ga.name,ga.url from group_all ga join group_all_user gau
        on ga.groupid=gau.groupid join skill_user su on su.userid=gau.userid
        where su.skill in""" + '("' + job_skills_str + '")'
    #print sql
    db.query(sql)
    query_results = db.store_result().fetch_row(maxrows=0)

    groupsid = []
    for result in query_results:
        groupsid.append(int(result[0]))

    gtmp = set(groupsid)
    gcount = {}
    for item in gtmp:
        gcount[item] = groupsid.count(item)

    glist = sorted(gcount.items(), key=lambda x: -x[1]) # sorted list of groups as tuples
    gtmp = []
    for i in range(5):
        gtmp.append(str(glist[i][0]))

    glist_str = '","'.join(gtmp)

    sql = 'select ga.name, ga.url from group_all ga where ga.groupid in ("' + glist_str + '")'

    db.query(sql)
    qresults = db.store_result().fetch_row(maxrows=0)
    group_list = []
    for val in qresults:
        group_list.append([val[0],linkedin_url+str(val[1])])

    iend = 5
    '''
    print job_skills[0:iend]
    print
    print leader_ids[0:iend]
    print 
    print conn_ids[0:iend]
    print
    print group_list[0:iend]
    '''
    
    people_group = {}
    people_group['connection'] = conn_ids[0:iend]
    people_group['leader'] = leader_ids[0:iend]
    people_group['group'] = group_list[0:iend]
    people_group['jobfrac'] = skillfrac


    outfile = open(location,'wb')
    pickle.dump(people_group,outfile)
    outfile.close()

    return people_group


def find_locations(db,uid_list):

    cursor = db.cursor()

    utmp = []
    for i in range(len(uid_list)):
        utmp.append(str(uid_list[i]))
    uid_list_str = '","'.join(utmp)
    sql = 'select u.title from user u where u.userid in ("' + uid_list_str + '")'
    db.query(sql)
    qresults = db.store_result().fetch_row(maxrows=0)

    ltmp = []
    for val in qresults:
        #print val
        end = str(val[0][::-1].split(',')[0])
        #print end
        #print end[0:4]
        #raw_input()
        if end[0:4] == "aerA":
            front = end[::-1]
            ltmp.append(front[1:-5])
    #lset = set(ltmp)

    location = {}
    for val in ltmp:
        if val in location:
            location[val] +=1
        else:
            location[val] = 1

    location_sort = sorted(location.items(), key=lambda x: -x[1])

    return location_sort


def get_skill_percentage(db,job_skills):

    cursor = db.cursor()

    if len(job_skills) > 1:
        job_skills_str = '","'.join(job_skills)
    else:
        job_skills_str = str(job_skills[0])

    sql=""" select count(*) from (select count(*) as freq from skill_user su 
        join user_features uf on su.userid = uf.userid where uf.job=True and 
        su.skill in"""+ '("'+ job_skills_str + '") group by su.userid) as a;'


    db.query(sql)
    query_results = db.store_result().fetch_row(maxrows=0)
    for result in query_results:
        jobsum = float(result[0])


    sql="select count(*) from user_features uf where uf.job=True;"
    db.query(sql)
    query_results = db.store_result().fetch_row(maxrows=0)
    for result in query_results:
        jobtot = float(result[0])

    jobskillfrac = int(100.*float(jobsum)/float(jobtot))

    sql=""" select count(*) from (select count(*) as freq from skill_user su 
        join user_features uf on su.userid = uf.userid where uf.job=False and 
        su.skill in"""+ '("'+ job_skills_str + '") group by su.userid) as a;'
    db.query(sql)
    query_results = db.store_result().fetch_row(maxrows=0)
    for result in query_results:
        nojobsum = int(result[0])

    sql="select count(*) from user_features uf where uf.job=False;"
    db.query(sql)
    query_results = db.store_result().fetch_row(maxrows=0)
    for result in query_results:
        nojobtot = int(result[0])


    nojobskillfrac = 100.*int(float(nojobsum)/float(nojobtot))

    return jobskillfrac#(,nojobskillfrac)


def get_education(db,keyword):

    degree = {}
    
    degree[2] = ["phd","ph","doctor","postdoctoral","doctoral","docorate","dphil"]
    degree[1] = ["master","masters","msc","mba","mse"]#,"ma","mphil", "ms", "m"]
    degree[0] = ["bachelor","bachelors","ba","bse","bs"]#,"b","be","btech","bs"]

    degree_list = {1:["mathematics","statistics"],0:["computer"],
    2:["chemistry","biology","molecular","physics","astrophysics","space","astronomy"],
    3:["engineering","bioengineering"],4:["neural","neuroscience","cognitive","cognitive","genetics"],
    5:["machine","data","nlp"]}
    #6:["business","finance","management"],6:["machine","data","nlp"]}

    sql = """select ud.education from user_details ud join user_features uf
            on ud.userid=uf.userid where uf.job = True;"""

    db.query(sql)
    query_results = db.store_result().fetch_row(maxrows=0)
    years = []
    list_education = []
    for resultst in query_results:
        results = resultst[0].lower()
        results_list = results.split(' ')[0:15]
        temp = parse_education(degree,degree_list,results_list)
        if temp != 0:
            list_education.append(temp)

        tyear = []
        for word in results_list:
            if word.isdigit():
                if int(word) < 2014 and int(word) > 1970:
                    tyear.append(int(word))
        if len(tyear) > 0:
             years.append(max(tyear))


    yrs = np.array(years)

    sum_edu = np.zeros((3,7))
    for val in list_education:
        sum_edu[val[0]][val[1]] += 1.
    sum_edu = sum_edu/sum_edu.sum() * 100.
    sum_edu = (sum_edu+0.5).astype(int)

    N = 3
    ind = np.arange(3)
    width = 0.5
    pdata = []
    for i in range(6):
        pdata.append([sum_edu[0][i],sum_edu[1][i],sum_edu[2][i]])
    pdata = np.array(pdata)
    
    p1 = plt.bar(ind, pdata[0], width, color='r')
    p2 = plt.bar(ind, pdata[1], width, color='b', bottom=pdata[0])
    p3 = plt.bar(ind, pdata[2], width, color='g', bottom=pdata[0]+pdata[1])
    p4 = plt.bar(ind, pdata[3], width, color='y', bottom=pdata[0]+pdata[1]+pdata[2])
    p5 = plt.bar(ind, pdata[4], width, color='c', bottom=pdata[0]+pdata[1]+pdata[2]+pdata[3])
    p6 = plt.bar(ind, pdata[5], width, color='m', bottom=pdata[0]+pdata[1]+pdata[2]+pdata[3]+pdata[4])

    plt.ylabel('%',fontsize=24)
    #plt.title('Background of a Software Developer')
    plt.title('Background of a '+keyword,fontsize=24)

    plt.xticks(ind+width/2., ('Bachelor','Masters','Doctorate'),fontsize=18 )
    plt.yticks(np.arange(0,71,10))
    plt.legend( (p1[0], p2[0], p3[0], p4[0], p5[0], p6[0]),
        ('CS','Math','Sci','Eng','Cog','Data'),loc='upper left', shadow=True,fontsize=16)
 
    #plt.show()
    plt.savefig(keyword.replace(' ','')+'.png')



def parse_education(degree,department,results_list):

    education_list = []
    ldegree = False
    ldepartment = False
    #year = []
    for word in results_list:
        word = word.lower()
        for key in degree:
            if not ldegree and word in degree[key]:
                education_list.insert(0,key)
                ldegree = True
        for key in department:
            if not ldepartment and word in department[key]:
                education_list.append(key)
                ldepartment = True
    #     if len(year) < 4 and word.isdigit():
    #         if int(word) > 2014 or int(word) < 1970:
    #             year.append(int(word))
    # if len(year)>0:
    #     education_list[2] = max(year)

    if ldegree and ldepartment:# and len(year)>0:
        return list(education_list)
    else:
        return 0


if __name__ == '__main__':

    keyword = ""
    matter = False
    for i in range(1,len(sys.argv)):
        if sys.argv[i] == "True" or sys.argv[i] == "False":
            matter = (sys.argv[i]=="True")
        else:
            keyword += str(sys.argv[i]) + ' '

    if keyword == "":
        keyword = ""#data science"

    print "Searching for : ", keyword,". Matter=",matter
    skills = []
    tmp = find_skills(keyword,matter)
    if tmp:
        for val in tmp:
            skills.append(val[0])
        find_people_groups(skills,keyword)
        #main(keyword)




