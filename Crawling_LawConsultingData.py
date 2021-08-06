import requests
import re
import pandas as pd
import os
from bs4 import BeautifulSoup


url = 'https://www.klac.or.kr/legalinfo/counselView.do?folderId=000&scdFolderId=&pageIndex=1&searchCnd=0&searchWrd=&caseId=case-001-00003'
MODEL_PATH = "data/"
consulting_df = pd.DataFrame({"구분":[], "제목":[], "질문":[], "답변":[]})


def get_data(url, consulting_df, errorURL):
    response = requests.get(url)

    if response.status_code == 200:
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.find("div",{"class": "document_box"})
        data = text.find_all(["dt", "dd"])
        
        additional_data = {}
        for i in range(4):
            additional_data[data[2*i].get_text()] = data[2*i+1].get_text()
            
        consulting_df = consulting_df.append(additional_data, ignore_index=True)
        
        next_page = text.find_all("span",{"class": "pf_tit"})
        if len(next_page) != 2:
            next_page = soup.find_all("span",{"class": "pf_tit"})
            print("document_box load Error")
            print("current URL: ", url)
            errorURL.append(url)
        
        if next_page[1].get_text().strip() == "다음글이 없습니다.":
            return consulting_df, -1
        else:
            next_sub_url = next_page[1].a['onclick']
            next_sub_url = re.findall('\([\'a-z0-9\-]*\)*', next_sub_url)
            next_sub_url = next_sub_url[0][2:-2]
            nextURL = url[:-len(next_sub_url)] + next_sub_url
        
    else : 
        print(response.status_code)

    return consulting_df, nextURL

def save_data(df):
    if not(os.path.isdir(MODEL_PATH)):
        os.makedirs(os.path.join(MODEL_PATH))
        
    df.to_csv(MODEL_PATH + "Law_Consulting_Data.csv", encoding='utf-8-sig')

if __name__ == "__main__":
    errorURL = []
    
    # 첫번째 페이지
    consulting_df, nextURL = get_data(url, consulting_df, errorURL)

    while(nextURL != -1):
        try:
            consulting_df, nextURL = get_data(nextURL, consulting_df, errorURL)
        except Exception as e: # ConnectionError -> 빠르게 여러번 요청해서 오류 발생
            print(e)
            print("URL: "nextURL)
            time.sleep(5)

    save_data(consulting_df)