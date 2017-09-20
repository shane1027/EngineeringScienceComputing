#!/usr/bin/env python3.6

# script for gathering new print log information from COLOR_ONLY and sending
# the data in a .csv to PUG for proper logging... note: should also be able to
# run the sorting / storage script on pug remotely using this program.

import requests
import os
import re
import sys
import time
from pprint import pprint

#TODO:	run on PUG, set up pip / requests, and add as a cronjob
# also add checks to see if a job is larger than a given value and trigger some
# sort of warning, in a log or in an email
# move on to making scripts that check the status of the other printers and
# send out an email to the ESC everyday list when that is the case


# set some constants for URL and packet management

BASE_PAGE='http://engcolor4.campus.nd.edu:8000/'
LOG_PAGE='http://engcolor4.campus.nd.edu:8000/rps/jlp.cgi?Flag=Html_Data&LogType=0&CorePGTAG=2'
LOGIN_PAGE='http://engcolor4.campus.nd.edu:8000/login'
SYSMON_PAGE=BASE_PAGE + 'sysmonitor'
LOG_CSV='http://engcolor4.campus.nd.edu:8000/rps/pprint.csv?LogType=0&Flag=Csv_Data'
LOG_CSV_HEADER={'user-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:55.0)Gecko/20100101 Firefox/55.0',
        'Host': 'engcolor4.campus.nd.edu:8000',
        'Accept':
        'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5', 'Accept-Encoding':
        'gzip, deflate', 'Referer':
        'http://engcolor4.campus.nd.edu:8000/rps/jlp.cgi?Flag=Html_Data&LogType=0&CorePGTAG=2',
        'Connection': 'keep-alive'}
LOGIN_PAYLOAD={'loginType' : 'admin', 'deptid' : '1496', 'password' : '1496533'}


# set constants for other related program components

OUT_DIR='.'
PUG_SCRIPT=False

if int(time.strftime('%H')) < 10:
    letter = 'a'
elif int(time.strftime('%H')) < 15:
    letter = 'b'
else:
    letter = 'c'


FILENAME="pprint.{0}s{1}.csv".format(time.strftime("%m%d%y"), letter)


# Usage function

def usage(status=0):
    print('''Usage: {0} [ -f FILENAME -d OUTPUT_DIRECTORY ]
    -f FILENAME             Name of the .csv containing print logs (default: {1})
    -d OUTPUT_DIRECTORY     Location to store output log (default: {2})
    -r RUN_SORTING_SCRIPT   True or False, 1 or 0, run PUG sorting script (default: {3})'''.format(os.path.basename(sys.argv[0]), FILENAME, OUT_DIR, PUG_SCRIPT))
    sys.exit(status)


# Parse command line options

args = sys.argv[1:]

while len(args) >= 2 and args[0].startswith('-') and len(args[0]) > 1:
    current_arg = args.pop(0)
    if current_arg == '-f':
        FILENAME = args.pop(0)
    elif current_arg == '-d':
        OUT_DIR = args.pop(0)
    elif current_arg == '-r':
        PUG_SCRIPT = args.pop(0)
    elif current_arg == '-h':
        usage(0)
    else:
        usage(1)

if len(args) >= 1:
    usage(1)


# Function to connect to the printer and download the .csv log to the output dir

def log_scraper():

    print('Connecting to printer...')

    # setup the web request by setting up a session + logging into the UI
    session = requests.session()
    login_response = session.post(LOGIN_PAGE, data=LOGIN_PAYLOAD)
    # now grab the base UI page to obtain proper cookies for authentication
    base_response = session.get(BASE_PAGE)
    # now we should have cookies... connect to /sysmonitor to extract dummy var
    # which is used as a certificate of login validity (saved in cookie jar)
    sysmonitor_response = session.get(SYSMON_PAGE)
    # now request the print log
    log_response = session.get(LOG_CSV, headers=LOG_CSV_HEADER)
    #TODO: add check for timeout to say we cannot connect to printer
    #(placeholder below)
    if False:
        print('Timeout detected.  Cannot reach printer.',
            'Is this machine\'s IP address added to the whitelist on COLOR_ONLY?')
    elif base_response.status_code != 200:
        print('Unable to download print log!')
        sys.exit(1)

    # alrighty, if we've made it this far, we've established valid contact with
    # the printer!  Should be downloading a file on the return.

    # uncomment the following line to print out the content
    # print(log_response.text)

    # save to the appropriate file name
    with open(OUT_DIR+'/'+FILENAME, 'a') as f:
        f.write(log_response.text)

# check if the output directory exists... if not, create it
if (os.path.isdir(OUT_DIR)):
    print('Output directory {0} exists!'.format(OUT_DIR))
else:
    print('Output directory {0} does not exist!'.format(OUT_DIR))
    #TODO: create output dir here
    exit(1)

# Call the scraping function
log_scraper()

# Optionally push the file to PUG and run the sorting script
if (PUG_SCRIPT):
    push_pug()

print('Done!')
print('Print log saved successfully as {0}.  PUG script: {1}.'.format(FILENAME,
    PUG_SCRIPT))



