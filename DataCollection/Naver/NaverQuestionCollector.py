# -*- coding: utf-8 -*-
"""
Created on Wed May 30 23:29:25 2018

@author: ykw-ailab
"""

import re
import json
import os
import urllib.request
from bs4 import BeautifulSoup


root_dir = os.getcwd()

# all varying information about this project is in config.json
config_file = 'config.json'
f_config = open(config_file, 'r')
config_json = json.loads(f_config.read())
end_point = config_json['end_point']

#regular expression pattern
htmltag_rge = re.compile('<.*?>')


def url_get(end_point, option_dict):
    url = end_point + '?'
    for key in option_dict.keys():
        if key == list(option_dict.keys())[-1]:
            url += key +  '=' +  urllib.parse.quote(str(option_dict[key]))
        else:
            url += key +  '=' +  urllib.parse.quote(str(option_dict[key])) + '&'
    return url


def query_naver(search_keyword, path, filename):
    
    option = {}
    option['query'] = search_keyword
    for i in range(10):
        option['start'] = 100 * i + 1
        url = url_get(end_point, option)
        print(url)
        request = urllib.request.Request(url)
        response = urllib.request.urlopen(request)
        rescode = response.getcode()
        if rescode == 200:
            response_body = response.read()
            file_path = root_dir + '\\' + path + '\\' + filename + '_' + str(i+1) + '.txt'
            directory = os.path.dirname(file_path)
            if not os.path.exists(directory):
                os.makedirs(directory)
            f = open(file_path, 'w')
            try:
                f.write(response_body.decode('utf-8'))
            except UnicodeEncodeError:
                print('Cannot collect data')
            f.close()
        else:
            print('Error code : ' + rescode)


# remove html tag
def query_normalization(query):
    processed_string = re.sub(htmltag_rge, '', query)
    return processed_string


def prepro_naverkin(json_text):
    print()
    
    
def crawling_naverkin(url):
    question_title = 'None'
    question_content = 'None'
    answer_contents = 'None'
    request = urllib.request.Request(url)
    response = urllib.request.urlopen(request)
    rescode = response.getcode()
    if rescode == 200:
        response_body = response.read()
        soup = BeautifulSoup(response_body, 'lxml')
        question_div = soup.find_all('div', class_='qna_detail_question')
        answer_div = soup.find_all('div', class_='qna_detail_answerList')
        answer_contents = list()
        for div in question_div:
            question_title = div.find('span', class_='title_text').text.strip()
            question_content = div.find('div', class_='_endContentsText').text.strip()
        for div in answer_div:
            for answer in div.find_all('div', class_='_endContentsText'):
                answer_contents.append(answer.text.strip())
            
    else:
        print('Error code : ' + rescode)
    return question_title, question_content, answer_contents
    
    

#query_naver('부산 광안대교 근처 맛집', '수영구', 'restaurants')
question_title, question_content, answer_contents = crawling_naverkin('https://kin.naver.com/qna/detail.nhn?d1id=8&dirId=80208&docId=251251146&qb=67aA7IKwIOunm+ynkeuyoOyKpO2KuA==&enc=utf8&section=kin&rank=1&search_sort=0&spq=0')
print(question_title)
print(question_content)
print(answer_contents)