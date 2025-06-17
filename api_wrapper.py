from time import sleep
import urllib.parse
import FinanceDataReader as fdr
from datetime import datetime, timedelta
import pandas as pd
import json
import requests
import re
import urllib
from dotenv import load_dotenv
import os
from bs4 import BeautifulSoup
from sympy import timed
from tqdm import tqdm
import pytz

from melo.api import TTS

from index_calculate import calculate_buy_index

import base64


load_dotenv()
class ApiWrapper:
    """
    A Python class for interacting with the INVHAND API.

    This class provides methods to interact with the INVHAND API, including authentication and data retrieval.
    """

    NASDAQ_TICKERS = {
        "AAPL": "애플",
        "ABNB": "에어비앤비",
        "ADBE": "어도비",
        "ADI": "아날로그 디바이스",
        "ADP": "오토매틱 데이터 프로세싱",
        "ADSK": "오토데스크",
        "AEP": "아메리칸 일렉트릭 파워",
        "AMAT": "어플라이드 머티어리얼즈",
        "AMD": "어드밴스트 마이크로 디바이시스 (AMD)",
        "AMGN": "암젠",
        "AMZN": "아마존",
        "ANSS": "앤시스",
        "APP": "애플로빈",
        "ARM": "암홀딩스",
        "ASML": "ASML",
        "AVGO": "브로드컴",
        "AXON": "액손 엔터프라이즈",
        "AZN": "아스트라제네카",
        "BIIB": "바이오젠",
        "BKNG": "부킹 홀딩스",
        "BKR": "베이커 휴즈",
        "CCEP": "코카콜라 유로퍼시픽 파트너스",
        "CDNS": "케이던스 디자인 시스템즈",
        "CDW": "CDW",
        "CEG": "콘스텔레이션 에너지",
        "CHTR": "차터 커뮤니케이션즈",
        "CMCSA": "컴캐스트",
        "COST": "코스트코",
        "CPRT": "코파트",
        "CRWD": "크라우드스트라이크",
        "CSCO": "시스코",
        "CSGP": "코스타 그룹",
        "CSX": "CSX",
        "CTAS": "신타스",
        "CTSH": "코그니전트",
        "DASH": "도어대시",
        "DDOG": "데이터독",
        "DXCM": "덱스컴",
        "EA": "일렉트로닉 아츠",
        "EXC": "엑셀론",
        "FANG": "다이아몬드백 에너지",
        "FAST": "패스널",
        "FTNT": "포티넷",
        "GEHC": "GE 헬스케어",
        "GFS": "글로벌파운드리즈",
        "GILD": "길리어드 사이언스",
        "GOOG": "알파벳 C",
        "GOOGL": "알파벳 A",
        "HON": "허니웰",
        "IDXX": "아이덱스",
        "INTC": "인텔",
        "INTU": "인튜잇",
        "ISRG": "인튜이티브 서지컬",
        "KDP": "큐리그 닥터페퍼",
        "KHC": "크래프트 하인즈",
        "KLAC": "KLA",
        "LIN": "린데",
        "LRCX": "램리서치",
        "LULU": "룰루레몬",
        "MAR": "메리어트",
        "MCHP": "마이크로칩 테크놀로지",
        "MDB": "몽고DB",
        "MDLZ": "몬덜리즈",
        "MELI": "메르카도리브레",
        "META": "메타",
        "MNST": "몬스터 베버리지",
        "MRVL": "마벨 테크놀로지",
        "MSFT": "마이크로소프트",
        "MSTR": "마이크로스트래티지",
        "MU": "마이크론",
        "NFLX": "넷플릭스",
        "NVDA": "엔비디아",
        "NXPI": "NXP",
        "ODFL": "올드 도미니언",
        "ON": "온 세미컨덕터",
        "ORLY": "오라일리 오토모티브",
        "PANW": "팔로알토 네트웍스",
        "PAYX": "페이첵스",
        "PCAR": "팩카",
        "PDD": "핀둬둬",
        "PEP": "펩시코",
        "PLTR": "팔란티어",
        "PYPL": "페이팔",
        "QCOM": "퀄컴",
        "REGN": "리제네론",
        "ROP": "로퍼 테크놀로지스",
        "ROST": "로스 스토어즈",
        "SBUX": "스타벅스",
        "SNPS": "시놉시스",
        "TEAM": "아틀라시안",
        "TMUS": "T-모바일",
        "TSLA": "테슬라",
        "TTD": "더 트레이드 데스크",
        "TTWO": "테이크투 인터랙티브",
        "TXN": "텍사스 인스트루먼트",
        "VRSK": "베리스크",
        "VRTX": "버텍스 파마슈티컬",
        "WBD": "워너 브라더스 디스커버리",
        "WDAY": "워크데이",
        "XEL": "엑셀 에너지",
        "ZS": "지스케일러",
    }

    OTHER_TICKERS = {
        'IXIC': "나스닥 종합지수",
        'KS11': "KOSPI 지수",
        'KQ11': "KOSDAQ 지수",
        'KS200': "KOSPI 200",
        'DJI': "다우존스 지수",
        'S&P500': "S&P500 지수",
        'RUT': "러셀2000 지수",
        'VIX': "VIA지수",
        'SSEC': "상해 종합지수",
        'HSI': "항셍지수",
        'N225': "일본 닛케이지수",
        'FTSE': "영국 FTSE100",
        'FCHI': "프랑스 FCHI 지수",
        'GDAXI': "독일 닥스지수"
    }


    def __init__(self):
        # Initialize the API wrapper with necessary configurations and credentials
        self.__base_url = os.getenv('BASE_URL')
        self.__auth = {
            "userId": os.getenv('AUTH_USER_ID'),
            "password": os.getenv('AUTH_PASSWORD')
        }
        self.__exchange_rate_api_key = os.getenv('EXCHANGE_RATE_API_KEY')
        self.__youtube_api_key = os.getenv('YOUTUBE_API_KEY')
        self.__naver_news_client_id = os.getenv('NAVER_NEWS_CLIENT_ID')
        self.__naver_news_client_secret = os.getenv('NAVER_NEWS_CLIENT_SECRET')

        self.__naver_news_api_url = os.getenv('NAVER_NEWS_API_URL')
        self.__exchange_api_url = os.getenv('EXCHANGE_API_URL')
        self.__youtube_api_url = os.getenv('YOUTUBE_API_URL')

        # Initialize the token for authentication
        self.__token = self._get_token()
        self.news_list = None


    def _get_token(self):
        '''
        This function sends an authentication request to the API and returns the access token if successful.
        '''

        response = requests.post(f"{self.__base_url}auth/token", json=self.__auth)
        if response.status_code != 200:
            raise RuntimeError("login error!")
        
        token = response.json()["data"][0]["accessToken"]
        self.__token = token

        return token


    def sanitize(self, input_string: str):
        '''
        This function takes an HTML string as input and returns a sanitized version of the string with all HTML tags removed.
        
        Args:
            input_string (str): The HTML string to be sanitized.

        Returns:
            str: The sanitized string with HTML tags removed.
        '''
        clean_html = re.compile('<.*?>')
        cleaned_text = re.sub(clean_html, '', input_string)
        cleaned_text = re.sub(r'&[^;]+;', '', cleaned_text)
        return cleaned_text
    

    def get_news_data(self) -> dict:
        '''
        This function retrieves news data for a given ticker symbol from the API and returns it as a JSON object.
        Returns:
            dict: A dictionary containing the news data for the given ticker.
        '''

        if self.news_list != None:
            return self.news_list

        keys = ApiWrapper.NASDAQ_TICKERS
        # keys.update({'IXIC': "나스닥 종합지수"})

        news_list = {i: [] for i in keys.keys()}

        for ticker in tqdm(keys.keys(), desc="Fetching news data"):
            queries = urllib.parse.urlencode({
                "query": keys[ticker] + " 주가",
                "display": 50,
                "start": 1,
                "sort": "date"
            })

            header = {
                "X-Naver-Client-Id": self.__naver_news_client_id,
                "X-Naver-Client-Secret": self.__naver_news_client_secret,
            }

            response = requests.get(self.__naver_news_api_url + "?" + queries, headers=header)

            if response.status_code != 200:
                raise RuntimeError("news data fetch error.")
            result = response.json()

            for i in range(min(10, len(result["items"]))):
                title = self.sanitize(result["items"][i]["title"])
                url = result["items"][i]["link"]
                pubDate_str = result["items"][i]["pubDate"]
                published_date = datetime.strptime(pubDate_str, "%a, %d %b %Y %H:%M:%S %z").strftime("%Y-%m-%dT%H:%M:%S") + 'Z'
                description = self.sanitize(result["items"][i]["description"])

                data = {
                    "ticker": ticker,  # You can set a default ticker or make it optional
                    "title": title,
                    "link": url,
                    "description": description,
                    "publishedDate": published_date
                }
                news_list[ticker].append(data)
    
            sleep(0.2)
        
        self.news_list = news_list
        return news_list


    def get_stock_news_data(self, ticker: str='IXIC', ticker_name: str="나스닥", query: str="시황") -> dict:
        '''
        This function retrieves news data for a given ticker symbol from the API and returns it as a JSON object.
        Args:
            ticker: ticker string.
            ticker_name: ticker korean name.
            query: search query.
        Returns:
            dict: A dictionary containing the news data for the given ticker.
        '''
        news_list = {ticker: []}
        url = "https://m.search.naver.com/search.naver?ssc=tab.m_news.all&query=%EB%82%98%EC%8A%A4%EB%8B%A5%20%EC%8B%9C%ED%99%A9&sm=mtb_opt&sort=1&photo=0&field=0&pd=0&ds=2025.06.13&de=2025.06.13&docid=&related=0&mynews=0&office_type=0&office_section_code=0&news_office_checked=&nso=so%3Add%2Cp%3Aall&is_sug_officeid=0&office_category=&service_area="
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "lxml") #"html.parser")

        links = list(set([i["href"] for i in soup.select('a[href^="https://n.news.naver.com"]')]))
        
        for link in links:
            try:
                res = requests.get(link, headers=headers)
                article = BeautifulSoup(res.text, "lxml")
                
                # 제목
                title_tag = article.select_one('h2#title_area span')
                title = title_tag.text.strip() if title_tag else None
                
                # 날짜
                date_tag = article.select_one('span.media_end_head_info_datestamp_time')
                date_str = date_tag.text.strip().replace("오전", "AM").replace("오후", "PM")
                published_date = datetime.strptime(date_str, "%Y.%m.%d. %p %I:%M").strftime("%Y-%m-%dT%H:%M:%S") + 'Z'

                # 썸네일 
                thumbnail_tag = article.select_one('meta[property="og:image"]')
                thumbnail = thumbnail_tag['content'] if thumbnail_tag else None
                # dict 저장
                news_list[ticker].append({
                    "ticker": ticker,
                    "title": title,
                    "url": link,
                    "publishedDate": published_date,
                    "imageUrl": thumbnail
                })
            
            except Exception as e:
                print(f"Error parsing {link} : {e}")

        return news_list


    def get_stock_data(self, days=365) -> dict:
        """
        Fetch stock data for all NASDAQ tickers.
        Args:
            days (int): Number of days to fetch historical data for.
        Returns:
            dict: A dictionary containing stock data for all NASDAQ tickers.
        """

        result = {}

        keys = list(ApiWrapper.NASDAQ_TICKERS.keys()) + list(ApiWrapper.OTHER_TICKERS.keys())

        for ticker in tqdm(keys, desc="Fetching Stock Data"):
            df: pd.DataFrame = fdr.DataReader(
                ticker,
                (datetime.now() - timedelta(days))
                    .strftime("%Y%m%d"), datetime.now().strftime("%Y%m%d")
            )
            high52week, low52week = float(max(df.Close)), float(min(df.Close))
            currentPrice = float(df.Close.iloc[-1])

            stock_data = {
                datetime.fromtimestamp(int(ts) / 1000).strftime('%Y-%m-%d'): {
                    i.lower(): float(val[i]) for i in val.keys()
                    if val[i] is not None  # None 값 건너뜀
                }
                
                for ts, val in json.loads(df.T.to_json()).items()
            }

            for date_key in stock_data:
                if 'adj close' in stock_data[date_key]:
                    stock_data[date_key]['adjClose'] = stock_data[date_key].pop('adj close')


            data = {
                "ticker": ticker,
                "companyName": ApiWrapper.NASDAQ_TICKERS[ticker] if ticker in ApiWrapper.NASDAQ_TICKERS.keys() else ApiWrapper.OTHER_TICKERS[ticker],
                "currentPrice": currentPrice,
                "previousClosePrice": currentPrice,
                "high52week": high52week,
                "low52week": low52week,
                "prices": stock_data,
            }

            result[ticker] = data
            sleep(0.1)
        
        return result


    def upload_stock_data(self) -> dict:
        """
        Uploads stock data to the API.
        This method will be used to upload the stock data to the API.
        This method will be called by the main application to upload the stock data.
        """
        
        stocks = self.get_stock_data()
        for ticker in tqdm(stocks.keys(), desc="Uploading stock data"):
            
            df = fdr.DataReader(ticker, start=(datetime.now() - timedelta(days=365)).strftime("%Y%m%d"))

            buy_index = calculate_buy_index(df) or 0.5

            yesterday = df.loc[(datetime.now() - timedelta(1)).strftime("%Y-%m-%d")]["Close"]
            before_yesterday = df.loc[(datetime.now() - timedelta(2)).strftime("%Y-%m-%d")]["Close"]

            change = ((yesterday - before_yesterday) / before_yesterday) * 100

            data = {
                "authentication": self.__token,
                "ticker": ticker,
                "companyName": ApiWrapper.NASDAQ_TICKERS[ticker] if ticker in ApiWrapper.NASDAQ_TICKERS.keys() else ApiWrapper.OTHER_TICKERS[ticker],
                "currentPrice": stocks[ticker]["currentPrice"],
                "previousClosePrice": stocks[ticker]["currentPrice"],
                "high52week": stocks[ticker]["high52week"],
                "low52week": stocks[ticker]["low52week"],
                "buyIndex": buy_index,
                "prices": stocks[ticker]["prices"],
                "changeRate": change
            }

            result = requests.post(f"{self.__base_url}raw", json=data)

            if result.status_code != 200:
                raise RuntimeError("raw stock data upload error!")

        return stocks


    def upload_exchange_rate(self):
        """
        Upload exchange rate data to the server.

        Args:
            authkey (str): The authentication key for accessing the exchange rate API.
        """
        print("uploading exchange rate...", end="")


        queries = urllib.parse.urlencode({
            "authkey": self.__exchange_rate_api_key,
            "data": "AP01",
            "searchdate": (datetime.now() - timedelta(1)).strftime("%Y%m%d")
        })

        result_yesterday, result_today = 0, 0
        while True:
            response = None
            try:
                response = requests.get(self.__exchange_api_url + f"?{queries}", verify=False)
                break
            except:
                continue

        if response.status_code == 200:
            result_yesterday = response.json()
            for i in result_yesterday:
                if "cur_nm" in i.keys() and i["cur_nm"] == '미국 달러':
                    result_yesterday = i
                    break
        
        queries = urllib.parse.urlencode({
            "authkey": self.__exchange_rate_api_key,
            "data": "AP01",
            "searchdate": (datetime.now()).strftime("%Y%m%d")
        })

        while True:
            response = None
            try:
                response = requests.get(self.__exchange_api_url + f"?{queries}", verify=False)
                break
            except:
                continue

        if response.status_code == 200:
            result_today = response.json()
            for i in result_today:
                if "cur_nm" in i.keys() and i["cur_nm"] == '미국 달러':
                    result_today = i
                    break

        rate_yesterday = float(result_yesterday["deal_bas_r"].replace(",", ""))
        rate_today = float(result_today["deal_bas_r"].replace(",", ""))

        data = {}
        data["buyRate"] = float(result_today["ttb"].replace(",", ""))
        data["sellRate"] = float(result_today["tts"].replace(",", ""))
        data["date"] = datetime.now().strftime("%Y-%m-%d")
        data["dealBaseRate"] = float(result_today["deal_bas_r"].replace(",", ""))
        data["changeRate"] = (rate_today - rate_yesterday) * 100 / rate_yesterday
        data["currency"] = "USD"
        
        result = requests.post(f"{self.__base_url}/exchange/save", headers={"Authorization": "Bearer " + self.__token}, json=data)

        if result.status_code != 200:
            raise RuntimeError("exchange rate data upload error!")


    def upload_youtube_links(self):
        """
            Uploads YouTube links based on the query.
        """

        for ticker in tqdm(ApiWrapper.NASDAQ_TICKERS.keys(), desc="Uploading YouTube Links"):
            query = ApiWrapper.NASDAQ_TICKERS[ticker]
            url = self.__youtube_api_url \
                    + "?q=" \
                    + query + "%20증시" \
                    + "&part=snippet&maxResults=15&key=" \
                    + self.__youtube_api_key
            result = requests.get(url)
            if result.status_code != 200:
                raise RuntimeError("YouTube API request failed!")
            
            data = result.json()
             
            i = 0
            count = 0
            while i < 15 and count < 3:
                e = data["items"][i]
                if "videoId" not in e["id"]:
                    i += 1
                    continue

                vid = e["id"]["videoId"]
                if "title" not in e["snippet"]:
                    i += 1
                    continue

                title = e["snippet"]["title"]
                if "thumbnails" not in e["snippet"]:
                    i += 1
                    continue

                link = e["snippet"]["thumbnails"]["high"]["url"]

                result = {
                    "ticker": ticker,
                    "title": title,
                    "thumbnailUrl": link,
                    "videoId": vid,
                    "publishedAt": e["snippet"]["publishedAt"],
                }

                result = requests.post(
                    f"{self.__base_url}upload/youtube",
                    json=result,
                    headers={"Authorization": "Bearer " + self.__token}
                )

                count += 1
                i += 1

                if result.status_code != 200:
                    raise RuntimeError("youtube data upload error!")
                
                sleep(0.5)


    def upload_news(self):
        """
        Upload news articles based on a query.
        """

        news_list = self.get_news_data()
        for ticker in tqdm(news_list.keys(), desc="Uploading News Data"):
            ticker_news = news_list[ticker]

            for i in range(5):
                data = {
                    "ticker": ticker,
                    "title": ticker_news[i]["title"],
                    "url": ticker_news[i]["link"],
                    "description": ticker_news[i]["description"],
                    "publishedDate": ticker_news[i]["publishedDate"],
                    "imageUrl": "반갑습니다"
                }
                result = requests.post(
                    f"{self.__base_url}upload/news",
                    json=data,
                    headers={"Authorization": "Bearer " + self.__token}
                )

                if result.status_code != 200:
                    raise RuntimeError("news data upload error!")


    def upload_stock_news(self, ticker: str="IXIC", ticker_name: str="나스닥", query: str="시황"):
        news_list: dict = self.get_stock_news_data(ticker, ticker_name, query)
        for ticker in tqdm(news_list.keys(), desc="Uploading News Data"):
            ticker_news = news_list[ticker]

            for i in range(len(ticker_news)):
                data = {
                    "ticker": ticker,
                    "title": ticker_news[i]["title"],
                    "url": ticker_news[i]["url"],
                    "description": "반갑습니다",
                    "imageUrl": ticker_news[i]["imageUrl"],
                    "publishedDate": ticker_news[i]["publishedDate"]
                }
                result = requests.post(
                    f"{self.__base_url}upload/news",
                    json=data,
                    headers={"Authorization": "Bearer " + self.__token}
                )

                if result.status_code != 200:
                    raise RuntimeError("news data upload error!")


    def upload_summary(self, text: str, ticker: str):
        data = {
            "ticker": ticker,
            "summaryText": text,
            "uploadDate": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
        }

        result = requests.post(
            "http://10.7.0.2:8080/upload/summary",
            json=data,
            headers={"Authorization": "Bearer " + self.__token}
        )

        if result.status_code != 200:
            raise RuntimeError("summary data upload error!")


    def upload_podcast(self, ticker: str, text: str):
        speed = 0.95
        device = 'cpu' # or cuda:0

        if ticker == "IXIC":
            today = datetime.today()
            date_str = f"{today.year}년 {today.month}월 {today.day}일"
            text = f"안녕하십니까,\n {date_str} 기준 관심 종목 뉴스 요약 정보를 안내해 드리겠습니다.\n" + text

        text = text.replace("%", "퍼센트").replace("$", "달러").replace("&", "엔")
        text = re.sub(r'[^\w\s]', '', text)
        text = text.replace("스타벅스", "starbucks")
        text = text.replace("시놉시스", "synopsis")
        # text = text.replace("니다.", "니다.\n")
        # text = text.replace("한다.", "한다.\n")
        # text = text.replace("있다.", "있다.\n")
        text = text.replace("다 ", "다.\n")
        text = text.replace("다.", "다.\n")
        print(text)
        model = TTS(language='KR', device=device)
        speaker_ids = model.hps.data.spk2id

        output_path = "./tts/" + ticker + '.wav'
        model.tts_to_file(text, speaker_ids['KR'], output_path, speed=speed)

        date_str = datetime.now().strftime("%Y-%m-%d")
        if ticker == "IXIC":
            url = f"http://10.7.0.2:8080/tts/greeting/upload"
        else:
            url = f"http://10.7.0.2:8080/tts/upload"
        

        result = None
        with open(output_path, "rb") as f:
            files = {
                'file': (output_path, f, 'audio/wav')
            }
            params = {
                'date': date_str
            }
            if ticker != "IXIC":
                params.update({'ticker': ticker})
            headers = {
                "Authorization": "Bearer " + self.__token
            }
            result = requests.post(
                url,
                files=files,
                params=params,
                headers=headers
            )
        
        return result

    def query_llm(self, text: str) -> str:
        # studio_url = os.getenv('GOOGLE_AI_STUDIO_URL') + os.getenv('GOOGLE_AI_STUDIO_API_KEY')
        studio_url = os.getenv('GOOGLE_AI_STUDIO_URL_GEMMA') + os.getenv('GOOGLE_AI_STUDIO_API_KEY')
        header = {"Content-Type": "application/json"}
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": text
                        }
                    ]
                }
            ]
        }

        response = requests.post(studio_url, headers=header, data=json.dumps(payload))
        if response.status_code != 200:
            raise Exception(response.text)

        return response.json()["candidates"][0]["content"]["parts"][0]["text"]


    def get_summary(self):
        if self.news_list == None:
            self.get_news_data()

        keys = dict()
        keys.update(ApiWrapper.NASDAQ_TICKERS)
        keys.update({'IXIC': "나스닥 종합지수"})
        for ticker in tqdm(keys.keys()):
            if ticker == "IXIC":
                target = self.get_stock_news_data()[ticker]
            else:
                target = self.news_list[ticker]
            
            name = ApiWrapper.NASDAQ_TICKERS[ticker] if ticker in ApiWrapper.NASDAQ_TICKERS.keys() else "나스닥 종합지수"

            data = []
            if ticker != "IXIC":
                for i in target:
                    data.append(i["title"].replace(":", "")  + " : " + i["description"].replace(":", ""))

            if ticker == "IXIC":
                for i in target:
                    data.append(i["title"].replace(":", ""))

            prompt = \
            f"""
            당신은 증권사 애널리스트로, {name} 종목의 분석 보고서를 발간해야 합니다.

            [요구 사항]
            {name}의 헤드라인을 검토하고, 분석 보고서에 들어갈 시황, 주요 이슈를 2000자로 구성된 {name} 분석 보고서를 제작하십시오.
            개인 투자자 입장에서 주의하거나 생각해봐야 할 시사점들이 있다면 분석 보고서에 반영하십시오.
            헤드라인의 모든 내용이 {name}와 연관되어 있지 않을 수도 있으며, 연관된 내용만을 보고서에 반영하십시오.

            [제약 사항]
            각각의 문단은 연속되고 '~니다'로 완결되는 한국어 문장으로 구성되어야 합니다.
            별도의 제목이나 메타 정보, 부연 설명, markdown 양식은 생략하십시오.
            단락 구분 없이, 문장을 연속된 3개의 문단으로 완성해 주세요. 필요하다면 문단을 추가할 수 있습니다.

            [참고 사항]
            헤드라인은 한 줄의 '[기사 제목]: [description]' 으로 구성되어 있습니다.

            [{name}의 헤드라인]
            {"\n".join(data)}
            """

            result = self.query_llm(prompt)
            result = result.replace("다 ", "다. ")

            prompt = \
            f"""
            [요구 사항]
            다음 [내용]을 보고, 제목을 지어 주십시오. 별도의 메타 정보, 수식어, 설명은 생략하고, 제목만을 말씀 하십시오.

            [내용]
            {result}
            """

            title = self.query_llm(prompt)

            kst = pytz.timezone('Asia/Seoul')
            data = {
            "ticker": ticker,
            "uploadDate": datetime.now(kst).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
            "summaryText": result,
            "title": title
            }

            res = requests.post(
                self.__base_url + "upload/summary",
                json=data,
                headers={"Authorization": "Bearer " + self._get_token()}
            )

            if res.status_code != 200:
                print(res.status_code)
                print(res.text)
                raise RuntimeError("news data upload error!")

            self.upload_podcast(text=result, ticker=ticker)


if __name__ == "__main__":
    api = ApiWrapper()

    try:
        api.upload_stock_data()
    except:
        pass
    try:
        news_list = api.get_news_data()
        api.upload_news()
    except:
        pass
    try:
        api.upload_exchange_rate()
    except:
        pass
    try:
        api.upload_stock_news()
    except:
        pass
    try:
        api.upload_youtube_links()
    except:
        pass
    try:
        api.get_summary()
    except:
        pass
