#!/bin/bash


# System update and essentials
sudo apt-get update

sudo apt-get install python-pip python-dev build-essential

sudo apt-get install mysql-server mysql-client
sudo apt-get install python-mysqldb

# Created folder and symbolic link (-since my *.py files referenced this)
sudo mkdir /var/mysql
sudo ln -s /var/mysql/mysql.sock /run/mysql/mysqld.sock


# Python libraries

sudo apt-get install python-numpy
sudo apt-get install python-scipy
sudo apt-get install python-sklearn


sudo apt-get install python-mechanize
sudo apt-get install python-beautifulsoup
sudo apt-get install python-nltk

sudo apt-get install git


# Programs for web interface

sudo pip install flask
sudo pip install gunicorn supervisor

# Create gunicorn and supervisor config file (change app!)
cat >simple.conf <<EOL
[program:myserver]
command=gunicorn hello:app -w 4 -b 0.0.0.0:80

[supervisord]
logfile=/home/ubuntu/supervisord.log
loglevel=debug
user=root
EOL

# Start up supervisor
sudo supervisord -c simple.conf


#sudo mysqld_safe
