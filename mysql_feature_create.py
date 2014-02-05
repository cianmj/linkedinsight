import os, os.path
import MySQLdb
import cPickle as pickle
import re

def alpha_num(mystring):
    reexp = r':(?=..(?<!\d:\d\d))|[^a-zA-Z0-9 ](?<!:)'
    temp = re.sub(reexp,"",str(mystring))
    return ' '.join(temp.split())  
    
def numb(mystring):
    reexp = r':(?=..(?<!\d:\d\d))|[^0-9 ](?<!:)'
    temp = re.sub(reexp,"",str(mystring))
    return int(' '.join(temp.split()))

class populate_database(object):

    def __init__(self):
        self.db = MySQLdb.connect(user="root",host="localhost",port=3306,db="linkedinsight",unix_socket="/var/mysql/mysql.sock")
        self.cursor = self.db.cursor()

    def load_basic(self):
        #print 'Dropping tables, press enter:',raw_input()
        #sql = "DROP TABLE group_user,groupt,user"
        #cursor.execute(sql)
        #self.db.commit()

        # Main user table 
        sql = "CREATE TABLE user (userid int not null primary key, name varchar(200),title varchar(500), connection Boolean, url varchar(200))"
        self.cursor.execute(sql)

        # Reference to Group Table:
        sql = "CREATE TABLE mygroup (groupid int not null primary key, name text, url text)"
        self.cursor.execute(sql)
        #sql = "CREATE TABLE group_user (userid int not null, groupid int, foreign key(userid) REFERENCES user(userid),foreign key(groupid) REFERENCES groupt(groupid))"
        sql = "CREATE TABLE mygroup_user (userid int not null, groupid int)"
        self.cursor.execute(sql)


        infile = open('member_data.p','rb')
        member_data = pickle.load(infile)
        infile.close()
        #member_data[int(mid)]=(str(name),str(desc),False,[gid],list(),str(url))

        infile = open('group_data.p','rb')
        group_data = pickle.load(infile)
        infile.close()
        #group_data[int(group_id)] = [name,url]

        sql="INSERT INTO user VALUES (%s,%s,%s,%s,%s)"
        for mid in member_data:
            self.cursor.execute(sql,(mid,member_data[mid][0],member_data[mid][1],member_data[mid][2],member_data[mid][5]))

        sql="INSERT INTO mygroup VALUES (%s,%s,%s)"
        for gid in group_data:
            self.cursor.execute(sql,(gid,alpha_num(group_data[gid][0]),group_data[gid][1]))

        sql="INSERT INTO mygroup_user VALUES (%s,%s)"
        for mid in member_data:
            for gid in member_data[mid][3]:
                self.cursor.execute(sql,(mid,gid))

        self.db.commit()



    def load_groups(self):

        path, dirs, files = os.walk("user_data").next()
        loop = 0; skip = 0;
        user_group = {}
        for filename in os.listdir('user_data'):
            filename = filename.replace('#','')
            location = str('user_data/'+filename)
            #location = "user_data/86040596.p"
            try:
                #user_tuple = (uid,n_connec,skills,background,education,groups)
                infile = open(location,'rb')
                user_tuple = pickle.load(infile)
                infile.close()
                loop += 1
            except:
                #print 'Could not load file', location
                skip += 1
                continue
            uid = numb(filename)
            user_group[uid] = user_tuple[5] # group dictionary of a list by gid


        sql = "CREATE TABLE group_all (groupid int not null primary key, name text, url text)"
        self.cursor.execute(sql)
        #sql = "CREATE TABLE group_user (userid int not null, groupid int, foreign key(userid) REFERENCES user(userid),foreign key(groupid) REFERENCES groupt(groupid))"
        sql = "CREATE TABLE group_all_user (userid int not null, groupid int)"
        self.cursor.execute(sql)

        # After loop create user-group database
        sql="INSERT INTO group_all VALUES (%s,%s,%s)"
        ghold = []
        for uid in user_group:
            for gid in user_group[uid]:
                if int(gid) not in ghold:
                    self.cursor.execute(sql,(gid,alpha_num(user_group[uid][gid][0]),user_group[uid][gid][1]))
                    ghold.append(int(gid))

        sql="INSERT INTO group_all_user VALUES (%s,%s)"
        for uid in user_group.keys():
            for gid in user_group[uid]:
                self.cursor.execute(sql,(uid,gid))

        self.db.commit()
        print 'Files loaded:',loop
        print 'Files skipped:',skip



    def load_user_details(self):

        # Put all skill data in one table -- no referencing
        sql = "CREATE TABLE skill_user (userid int not null, skill text, value int, foreign key(userid) REFERENCES user(userid))"
        self.cursor.execute(sql)

        sql = "CREATE TABLE user_details (userid int not null,num_connections int,background text,education text,foreign key(userid) REFERENCES user(userid))"
        self.cursor.execute(sql)

        #member_data[int(mid)]=(str(name),str(desc),False,[gid],list(),str(url))
        infile = open('member_data.p','rb')
        member_data = pickle.load(infile)
        infile.close()


        path, dirs, files = os.walk("user_data").next()
        number_users = len(files)
        skill_list = []
        loop = 0
        skip = 0
        #user_group = {}
        for filename in os.listdir('user_data'):
            filename = filename.replace('#','')
            location = str('user_data/'+filename)
            #location = "user_data/86040596.p"
            try:
                #user_tuple = (uid,n_connec,skills,background,education,groups)
                infile = open(location,'rb')
                user_tuple = pickle.load(infile)
                infile.close()
                loop += 1
            except:
                #print 'Could not load file', location
                skip += 1
                continue

            uid = numb(str(user_tuple[0])) ## PATCH -- user_tuplep[0] NOT an INT

            sql = "INSERT INTO skill_user VALUES (%s,%s,%s)"
            #for uid in user_tuple:
            for skill,value in user_tuple[2].iteritems():
                #skill_index = skill_list.index(skill)
                self.cursor.execute(sql,(uid,skill,value))

            # userid int not null,num_connections int,jobid int,job BOOLEAN,phd BOOLEAN
            sql = "INSERT INTO user_details VALUES (%s,%s,%s,%s)"


            n_connec = user_tuple[1]
            if str(n_connec) == '':
                n_connec = 0

            self.cursor.execute(sql,(uid,int(n_connec),str(user_tuple[3]),str(user_tuple[4])))


        self.db.commit()
        print 'Files loaded:',loop
        print 'Files skipped:',skip



if __name__ == '__main__':

    maindb = populate_database()

    print 'Dropping tables, press enter:',raw_input()
    sql = '''DROP TABLE IF EXISTS user_features,skill_user,user_details,group_all_user,
    group_all,mygroup_user,mygroup,user'''
    maindb.cursor.execute(sql)

    print 'Loading basic database'
    maindb.load_basic()

    print 'Loading group database'
    maindb.load_groups()

    sql = '''DROP TABLE IF EXISTS skill_user,user_details'''
    maindb.cursor.execute(sql)
    print "Loading  user details"
    maindb.load_user_details()





