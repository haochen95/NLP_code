import os
import shutil
from nltk import WordNetLemmatizer
import re
import string
import nltk


def proOSHA(file):

    with open(file, "r") as f:

        file_data = ''
        for line in f:
            line = line.replace(line, re.sub('[%s]' % string.punctuation, '', line.lower()))
            file_data +=line

    with open(file, 'w') as f:
        f.write(file_data)

kok = input("Please enter the keywords you being used to crawl data from OSHA-------->>>")

source = os.path.abspath(os.path.dirname(os.getcwd())) + '\\Crawl_cases_from_OSHA\\' + kok.replace(' ','').lower() + '.txt'
destination = os.path.abspath(os.path.dirname(os.getcwd())) + '\\dataset'
shutil.copy(source, destination)

proOSHA(destination + "\\" + kok.replace(' ','').lower() + '.txt')

meragefiledir = os.path.abspath(os.path.dirname(os.getcwd())+os.path.sep+".") + '\\dataset'
filenames = os.listdir(meragefiledir)
file = open(meragefiledir + '\\'+ 'final_data.txt', 'w')
for f in filenames:
    filepath = meragefiledir + '\\'
    filepath = filepath + f
    for line in open(filepath):
        file.writelines(line)
    file.write('\n')
file.close()

