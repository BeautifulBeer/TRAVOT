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
text_reg = re.compile('\[[\w|\W]+\]|[\W|\_]|[ㅠ|ㅜ|ㅎ|ㅋ]|[a-zA-Z]') #any brackt | special_character | ㅋ or ㅠ | english and number
number_reg = re.compile('[0-9]+')

def url_get(end_point, option_dict):
    url = end_point + '?'
    for key in option_dict.keys():
        if key == list(option_dict.keys())[-1]:
            url += key +  '=' +  urllib.parse.quote(str(option_dict[key]))
        else:
            url += key +  '=' +  urllib.parse.quote(str(option_dict[key])) + '&'
    return url


# remove unuseful text
def text_normalization(text):
    text = text.replace('\\xa0', '').replace('\\n',' ')
    text = re.sub(text_reg, ' ', text)
    text = re.sub(blank_reg, ' ', text)
    text = re.sub(number_reg, '<number>', text)
    return text.strip()
 
    
# crawling naver kin webpage
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


# extract unique link set to process data
def build_set_data():
    category_dir_list = [f for f in os.listdir(root_dir+'\\Raw\\') if re.match('.*[^\.a-zA-Z]+',f)]
    data = {}
    data_set = list()
    for category_dir in category_dir_list:
        directory_path = root_dir + '\\Raw\\' + category_dir
        file_list = [f for f in os.listdir(directory_path) if re.match('.*\.txt', f)]
        for file_name in file_list:
            file_path = directory_path + '\\' + file_name
            file = open(file_path, 'r', encoding='utf-8')
            json_data = json.loads(file.read(), encoding='utf-8')
            file.close()
            for item in json_data['items']:
                item = json.loads(item)
                data_set.append(item['link'])
    data_set = list(set(data_set))
    data['len'] = len(data_set)
    data['contents'] = data_set
    if not os.path.exists(root_dir + '\\Processed\\'):
        os.makedirs(root_dir + '\\Processed\\')
    f = open(root_dir + '\\Processed\\' + 'data.json', 'w', encoding='utf-8')
    f.write(json.dumps(data, ensure_ascii=False))
    f.close()


# process json file based on set data - make unique
def build_json_set_data():
    f = open(root_dir + '\\Processed\\' + 'data.json', 'r', encoding='utf-8')
    json_data = json.loads(f.read(), encoding='utf-8')
    f.close()
    data_set = dict((content, 0) for content in list(json_data['contents']))
    category_dir_list = [f for f in os.listdir(root_dir+'\\Raw\\') if re.match('.*[^\.a-zA-Z]+',f)]
    for category_dir in category_dir_list:
        directory_path = root_dir + '\\Raw\\' + category_dir
        file_list = [f for f in os.listdir(directory_path) if re.match('.*\.txt', f)]
        for file_name in file_list:
            r_file_path = directory_path + '\\' + file_name
            w_file_path = root_dir + '\\Processed\\' + category_dir + '\\' + file_name
            if not os.path.exists(os.path.dirname(w_file_path)):
                os.makedirs(os.path.dirname(w_file_path))        
            f = open(r_file_path, 'r', encoding='utf-8')
            json_data = json.loads(f.read(), encoding='utf-8')
            f.close()
            for idx, item in enumerate(json_data['items']):
                item = json.loads(item)
                if data_set[item['link']] == 0:
                    data_set[item['link']] = 1
                else:
                    del json_data['items'][idx]
            f = open(w_file_path, 'w', encoding='utf-8')
            f.write(json.dumps(json_data, ensure_ascii=False))
            f.close()


# querying naver api
def query_naver(search_keyword, path):
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
            file_path = root_dir + '\\Raw\\' + path + '\\' + search_keyword + '_' + str(i+1) + '.txt'
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


# odd number only works
def make_n_grams(string, n):
    result = list()
    string_list = string.split()
    str_list_len = len(string_list)
    window_size = int(n/2)
    for idx in range(str_list_len):
        if idx-window_size >= 0:
            if idx < str_list_len-window_size:
                tmp = list()
                for ng_idx in range(n):
                    tmp.append(string_list[idx-window_size+ng_idx])
                result.append(tmp)
            else:
                break
            
    if len(result) == 0:
        diff = n-len(string_list)
        for i in range(diff):
            string_list.append('<NONE>')
        result.append(string_list)
    return result

#query_naver('자갈치시장 맛집', '남포동')
#build_json_set_data()
print(make_n_grams('자갈치시', 5))