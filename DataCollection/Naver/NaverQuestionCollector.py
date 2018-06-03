# -*- coding: utf-8 -*-
"""
Created on Wed May 30 23:29:25 2018

@author: ykw-ailab
"""

import numpy as np
import time
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
htmltag_rge = re.compile('<.*?>') # tag
blank_reg = re.compile('\s+') # whitespace
text_reg = re.compile('\[[\w|\W]+\]|[\W|\_]|[ㅠ|ㅜ|ㅎ|ㅋ]|[a-zA-Z0-9]') #any brackt | special_character | ㅋ or ㅠ | english and number


def url_get(end_point, option_dict):
    url = end_point + '?'
    for key in option_dict.keys():
        if key == list(option_dict.keys())[-1]:
            url += key +  '=' +  urllib.parse.quote(str(option_dict[key]))
        else:
            url += key +  '=' +  urllib.parse.quote(str(option_dict[key])) + '&'
    return url


# preprocessed 
def text_normalization(text):
    text = text.replace('\\xa0', '').replace('\\n',' ')
    text = re.sub(text_reg, ' ', text)
    text = re.sub(blank_reg, ' ', text)
    return text.strip()
    
    
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
            question_title = text_normalization(div.find('span', class_='title_text').text)
            question_content = text_normalization(div.find('div', class_='_endContentsText').text)
        for div in answer_div:
            for answer in div.find_all('div', class_='_endContentsText'):
                answer_contents.append(text_normalization(answer.text))
    else:
        print('Error code : ' + rescode)
    return question_title, question_content, answer_contents
    
    
def query_naver(search_keyword, path, filename):
    option = {}
    option['query'] = search_keyword
    for i in range(1):
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
            try:
                json_body = json.loads(response_body.decode('utf-8'), encoding='utf-8')
                time_gap = np.abs(np.random.normal(0, 1, 100))
                for i, item in enumerate(json_body['items']):
                    time.sleep(time_gap[i])
                    print(item['link'], i)
                    question_title, question_content, answer_contents = crawling_naverkin(item['link'])
                    obj_kin = {}
                    obj_kin['link'] = item['link']
                    obj_kin['question_title'] = question_title
                    obj_kin['question_content'] = question_content
                    obj_kin['answer_contents'] = answer_contents
                    json_kin = json.dumps(obj_kin, ensure_ascii=False)
                    json_body['items'][i] = json_kin
                f = open(file_path, 'w', encoding='utf-8')
                f.write(json.dumps(json_body, ensure_ascii=False))
                f.close()
            except UnicodeEncodeError:
                print('Cannot collect data')
            
                
        else:
            print('Error code : ' + rescode)


    
query_naver('부산 광안대교 근처 맛집', '수영구', '부산 광안대교 근처 맛집')
