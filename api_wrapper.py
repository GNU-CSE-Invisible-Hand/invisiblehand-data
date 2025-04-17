from time import sleep
import FinanceDataReader as fdr
from datetime import datetime, timedelta
import pandas as pd
import json
import requests
import re
import urllib
from dotenv import load_dotenv
import os

from tqdm import tqdm


load_dotenv()
class ApiWrapper:
    """
    A Python class for interacting with the INVHAND API.

    This class provides methods to interact with the INVHAND API, including authentication and data retrieval.
    """

    NAVER_NEWS_API_URL = "https://openapi.naver.com/v1/search/news.json"
    EXCHANGE_API_URL = "https://www.koreaexim.go.kr/site/program/financial/exchangeJSON"
    YOUTUBE_API_URL = "https://www.googleapis.com/youtube/v3/search"
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

        # Initialize the token for authentication
        self.__token = self._get_token()


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

        news_list = {i: [] for i in ApiWrapper.NASDAQ_TICKERS.keys()}

        print("Fetching news data...")
        for ticker in tqdm(ApiWrapper.NASDAQ_TICKERS.keys()):
            queries = urllib.parse.urlencode({
                "query": ApiWrapper.NASDAQ_TICKERS[ticker],
                "display": 20,
                "start": 1,
                "sort": "date"
            })

            header = {
                "X-Naver-Client-Id": self.__naver_news_client_id,
                "X-Naver-Client-Secret": self.__naver_news_client_secret,
            }

            response = requests.get(ApiWrapper.NAVER_NEWS_API_URL + "?" + queries, headers=header)

            if response.status_code != 200:
                raise RuntimeError("news data fetch error.")
            result = response.json()

            for i in range(10):
                title = self.sanitize(result["items"][i]["title"])
                url = result["items"][i]["link"]
                pubDate_str = result["items"][i]["pubDate"]
                published_date = datetime.strptime(pubDate_str, "%a, %d %b %Y %H:%M:%S %z").strftime("%Y-%m-%dT%H:%M:%S") + 'Z'
                description = self.sanitize(result["items"][i]["description"])

                data = {
                    "ticker": "",  # You can set a default ticker or make it optional
                    "title": title,
                    "link": url,
                    "description": description,
                    "publishedDate": published_date
                }
                news_list[ticker].append(data)
            
            sleep(0.2)
        return news_list


    def get_stock_data(self, days=365) -> dict:
        """
        Fetch stock data for all NASDAQ tickers.
        Args:
            days (int): Number of days to fetch historical data for.
        Returns:
            dict: A dictionary containing stock data for all NASDAQ tickers.
        """

        print("Fetching stock data...", end="")
        result = {}
        for ticker in tqdm(ApiWrapper.NASDAQ_TICKERS.keys()):
            df: pd.DataFrame = fdr.DataReader(
                ticker,
                (datetime.now() - timedelta(days))
                    .strftime("%Y%m%d"), datetime.now().strftime("%Y%m%d")
            )
            high52week, low52week = max(df.Close), min(df.Close)
            currentPrice = df.Close.iloc[-1]

            stock_data = {
                datetime.fromtimestamp(int(ts) / 1000).strftime('%Y-%m-%d'): val
                for ts, val in json.loads(df.T.to_json()).items()
            }

            data = {
                "ticker": ticker,
                "companyName": ApiWrapper.NASDAQ_TICKERS[ticker],
                "currentPrice": currentPrice,
                "previousClosePrice": currentPrice,
                "high52week": high52week,
                "low52week": low52week,
                "prices": stock_data,
            }

            result[ticker] = data
            sleep(0.2)
        
        return result


    def upload_stock_data(self):
        '''
        This function uploads stock data for a given ticker symbol from the FRED API
        and returns the data as a JSON object.
        '''

        stocks = self.get_stock_data()
        for ticker in stocks.keys():
            data = {
                "Authentication": self.__token,
                "ticker": ticker,
                "companyName": ApiWrapper.NASDAQ_TICKERS[ticker],
                "currentPrice": stocks[ticker]["currentPrice"],
                "previousClosePrice": stocks[ticker]["currentPrice"],
                "high52week": stocks[ticker]["high52week"],
                "low52week": stocks[ticker]["low52week"],
                "prices": stocks[ticker]["prices"],
            }

            result = requests.post(f"{self.__base_url}raw", json=data)

            if result.status_code != 200:
                raise RuntimeError("raw stock data upload error!")


    def upload_exchange_rate(self):
        """
        Upload exchange rate data to the server.

        Args:
            authkey (str): The authentication key for accessing the exchange rate API.
        """

        queries = urllib.parse.urlencode({
            "authkey": self.__exchange_rate_api_key,
            "data": "AP01"
        })

        while True:
            response = None
            try:
                response = requests.get(ApiWrapper.EXCHANGE_API_URL + f"?{queries}", verify=False)
                break
            except:
                continue

        if response.status_code == 200:
            result = response.json()
            for i in result:
                if "cur_nm" in i.keys() and i["cur_nm"] == '미국 달러':
                    result = i
                    break

        data = {}
        data["buyRate"] = float(result["ttb"].replace(",", ""))
        data["sellRate"] = float(result["tts"].replace(",", ""))
        data["date"] = datetime.now().strftime("%Y-%m-%d")
        data["dealBaseRate"] = float(result["deal_bas_r"].replace(",", ""))
        data["currency"] = "USD"

        result = requests.post(f"{self.__base_url}/exchange/save", json=data)

        if result.status_code != 200:
            raise RuntimeError("exchange rate data upload error!")


    def upload_youtube_links(self):
        """
            Uploads YouTube links based on the query.
        """

        for ticker in tqdm(ApiWrapper.NASDAQ_TICKERS.keys()):
            query = ApiWrapper.NASDAQ_TICKERS[ticker]
            url = ApiWrapper.YOUTUBE_API_URL \
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
                    headers={"Authorization": self.__token}
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
        for ticker in news_list.keys():
            ticker_news = news_list[ticker]

            for i in range(5):
                data = {
                    "ticker": ticker,
                    "title": ticker_news[i]["title"],
                    "url": ticker_news[i]["link"],
                    "description": ticker_news[i]["description"],
                    "publishedDate": ticker_news[i]["publishedDate"]
                }
                result = requests.post(
                    f"{self.__base_url}upload/news",
                    json=data,
                    headers={"Authorization": self.__token}
                )

                if result.status_code != 200:
                    raise RuntimeError("news data upload error!")


if __name__ == "__main__":
    api = ApiWrapper()
    # api.upload_stock_data()
    # api.upload_youtube_links()
    # api.upload_news()
    # api.upload_exchange_rate()
