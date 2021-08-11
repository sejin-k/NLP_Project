# 네이버 법 question-answer 데이터 세트 구축
#-*- coding:utf-8 -*-
from bs4 import BeautifulSoup
import requests
import re
from multiprocessing import Process
import json
import os
from time import sleep

import csv
import platform

class Writer(object):
    def __init__(self, category, lawer):
        self.category = category
        self.lawer = lawer

        self.file = None
        self.initializer_file(self.category, self.lawer)
        self.csv_writer = csv.writer(self.file)
        self.csv_writer.writerow(['FAQ', 'CONTENT', 'DIV_CASE', 'ANSWER'])
    
    def initializer_file(self, category, lawer):
        output_path = 'G:\내 드라이브\web_crawling'

        file_name = f'{output_path}/{category}{lawer}'+'.csv'

        if os.path.isfile(file_name):
            print("@@@@@@@ this file is remove and restart crawling! @@@@@@@")
        
        user_os = str(platform.system())
        if user_os == "Windows":
            self.file = open(file_name, 'w', encoding='utf-8', newline='')
        
    def write_row(self, row):
        self.csv_writer.writerow(row)
    
    def close(self):
        self.file.close()


class NaverLawCrawler(object):
    def __init__(self):
        self.main_url = "https://kin.naver.com" # 지식인 페이지
        self.expert_url = "https://kin.naver.com/qna/expertAnswerList.naver?dirId="
        self.notexpert_url = "https://kin.naver.com/qna/list.naver?dirId="

        self.dirIds = {
            '교통사고,위반' : "60201",
            '가족,이혼' : "60204",
            '소비자관련법,상법' : "60207",
            '재판,소송절차' : "60211",
            '형벌,형집행' : "60214",
            '외국법' : "60217",
            '민법' : "60220",
            '등기': "60223",
            '부동산' : "60202",
            '지식재산권' : "60205",
            '청소년관련법' : "60208",
            '계약' : "60212",
            '법학,법이론' : "60215",
            '헌법' : "60218",
            '민사소송' : "60221",
            '민사집행' : "60224",
            '신용,파산' : "60203",
            '형사사건' : "60206",
            '손해배상' : "60213",
            '언론,미디어법' : "60216",
            '행정법' : "60219",
            '노동법' : "60222",
            '산업재해' : "60225"
        }

    def crawling(self, category, lawer):
        # csv 파일 작성 setting
        answer = '_Lawer' if lawer else '_NotLawer'
        writer = Writer(category=category, lawer=answer)

        print("######## (",category, answer, ") crawling start ########")

        # 해당 카테고리의 법(질문) url 만들기
        sub_url = self.expert_url if lawer else self.notexpert_url
        category_url = sub_url + self.dirIds.get(category) + "&page="
        question_urls = []

        for i in range(1, 101): # 네이버는 법 질문이 최대 99페이지임
            temp_url = category_url + str(i)
            html_doc = requests.get(temp_url, timeout=15, headers={'User-Agent':'Mozilla/5.0'})
            html = BeautifulSoup(html_doc.content, 'html.parser')

            # 현재 페이지에 있는 리스트 목록 모두 가져오기
            titles = html.find('div', {'class': 'board_box'}).find('tbody', id="au_board_list")\
                .find_all('td', class_="title")

            # 현재 페이지에 있는 url들 모두 먼저 모아두기 (왜냐면 계속 query time에 따라 updat되니깐 미리 저장)
            if titles:
                for title in titles:
                    question_urls.append(self.main_url+title.find('a')['href'])
            else: # 만약에 더이상 없으면 title 출력 x 그럼 거기서 stop
                print("######## catergory : ", category, " => (max page :", len(question_urls),") ########")
                break
        else: print("######## catergory : ", category, " => (max page :", len(question_urls),") ########")

        # self.question_urls로 들어가서 시작하기
        for question in question_urls:
            response = requests.get(question, timeout=15, headers={'User-Agent':'Mozilla/5.0'})

            if response.status_code == 200:
                html = response.text
                soup = BeautifulSoup(html, 'html.parser')

                FAQ = soup.find("div", class_="title")
                FAQ = FAQ.get_text(" ", strip=True) if FAQ else ''

                CONTENT = soup.find("div", class_="c-heading__content")
                CONTENT = CONTENT.get_text(" ", strip=True) if CONTENT else ''

                try:
                    DIV_CASE = soup.find("div", class_="tag-list tag-list--end-title").find("a")
                    DIV_CASE = DIV_CASE.get_text(" ", strip=True)[10:] if DIV_CASE else ''
                except:
                    DIV_CASE = ''

                ANSWER = soup.find("div", class_="_endContentsText c-heading-answer__content-user")
                ANSWER = ANSWER.get_text(" ", strip=True) if ANSWER else ''
                
                # CSV파일에 작성
                writer.write_row([FAQ, CONTENT, DIV_CASE, ANSWER])
            else : 
                print("@@@@@@@ this page removed @@@@@@@@@")

        writer.close()
        print("######## (",category, ") save finish #########")
        return

if __name__ == "__main__":
    crawling_list = [
        '교통사고,위반', '가족,이혼', '소비자관련법,상법', '재판,소송절차',
        '형벌,형집행', '외국법', '민법', '등기', '부동산', '지식재산권', '청소년관련법',
        '계약', '법학,법이론', '헌법', '민사소송', '민사집행', '신용,파산',
        '형사사건', '손해배상', '언론,미디어법', '행정법', '노동법', '산업재해'
    ]
    Crawler = NaverLawCrawler() # 변호사 답변 질문 리스트
     # 변호사 답변 질문 리스트
    for category in crawling_list[18:]:
        Crawler.crawling(category, True)
        Crawler.crawling(category, False)
        
        