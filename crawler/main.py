# # Firebase Functions for AI Weekly News Crawler
# from firebase_functions import https_fn, scheduler_fn
# from firebase_admin import initialize_app, firestore
# import requests
# from bs4 import BeautifulSoup
# import feedparser
# from datetime import datetime, timedelta
# import logging

# # Firebase 초기화
# initialize_app()
# db = firestore.client()

# # 로깅 설정
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # 카테고리 매핑
# CATEGORY_MAPPING = {
#     'huggingface': '모델',
#     'paperswithcode': '논문/학회', 
#     'techcrunch': '서비스/앱',
#     'ainews': '커뮤니티 이슈',
#     'reddit': '커뮤니티 이슈',
#     'hackernews': '실습/코드'
# }

# def save_keyword_to_firestore(keyword, category, source, url=None):
#     """키워드를 Firestore에 저장"""
#     try:
#         # 중복 체크
#         existing = db.collection('keywords').where('keyword', '==', keyword).limit(1).get()
#         if len(existing) > 0:
#             logger.info(f"키워드 '{keyword}' 이미 존재함")
#             return
        
#         # 새 키워드 저장
#         doc_data = {
#             'keyword': keyword,
#             'category': category,
#             'source': source,
#             'url': url,
#             'createdAt': datetime.now(),
#             'isActive': True
#         }
        
#         db.collection('keywords').add(doc_data)
#         logger.info(f"새 키워드 저장: {keyword} ({category})")
        
#     except Exception as e:
#         logger.error(f"Firestore 저장 오류: {e}")

# def crawl_huggingface_papers():
#     """Hugging Face Papers 크롤링"""
#     try:
#         url = "https://huggingface.co/papers"
#         headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        
#         response = requests.get(url, headers=headers)
#         soup = BeautifulSoup(response.content, 'html.parser')
        
#         # 논문 제목들 추출 (실제 셀렉터는 사이트 구조에 따라 조정 필요)
#         papers = soup.find_all('h3', class_='text-lg')
        
#         for paper in papers[:10]:  # 최신 10개만
#             title = paper.get_text().strip()
#             if len(title) > 5:  # 의미있는 제목만
#                 save_keyword_to_firestore(title, CATEGORY_MAPPING['huggingface'], 'huggingface')
                
#     except Exception as e:
#         logger.error(f"Hugging Face 크롤링 오류: {e}")

# def crawl_papers_with_code():
#     """Papers with Code 크롤링"""
#     try:
#         url = "https://paperswithcode.com/latest"
#         headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        
#         response = requests.get(url, headers=headers)
#         soup = BeautifulSoup(response.content, 'html.parser')
        
#         # 논문 제목들 추출
#         papers = soup.find_all('h1')
        
#         for paper in papers[:10]:
#             title = paper.get_text().strip()
#             if len(title) > 5:
#                 save_keyword_to_firestore(title, CATEGORY_MAPPING['paperswithcode'], 'paperswithcode')
                
#     except Exception as e:
#         logger.error(f"Papers with Code 크롤링 오류: {e}")

# def crawl_techcrunch_ai():
#     """TechCrunch AI RSS 크롤링"""
#     try:
#         rss_url = "https://techcrunch.com/category/artificial-intelligence/feed/"
#         feed = feedparser.parse(rss_url)
        
#         for entry in feed.entries[:10]:
#             title = entry.title
#             # AI 관련 키워드 추출
#             ai_keywords = extract_ai_keywords(title)
#             for keyword in ai_keywords:
#                 save_keyword_to_firestore(keyword, CATEGORY_MAPPING['techcrunch'], 'techcrunch', entry.link)
                
#     except Exception as e:
#         logger.error(f"TechCrunch 크롤링 오류: {e}")

# def crawl_ai_news():
#     """AI News 사이트 크롤링"""
#     try:
#         url = "https://www.artificialintelligence-news.com"
#         headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        
#         response = requests.get(url, headers=headers)
#         soup = BeautifulSoup(response.content, 'html.parser')
        
#         # 기사 제목들 추출
#         articles = soup.find_all('h2', class_='entry-title')
        
#         for article in articles[:10]:
#             title = article.get_text().strip()
#             ai_keywords = extract_ai_keywords(title)
#             for keyword in ai_keywords:
#                 save_keyword_to_firestore(keyword, CATEGORY_MAPPING['ainews'], 'ainews')
                
#     except Exception as e:
#         logger.error(f"AI News 크롤링 오류: {e}")

# def extract_ai_keywords(text):
#     """텍스트에서 AI 관련 키워드 추출"""
#     ai_terms = [
#         'GPT', 'Claude', 'Gemini', 'LLaMA', 'Mixtral', 'Phi-3', 'DeepSeek',
#         'OpenAI', 'Anthropic', 'Google', 'Meta', 'Microsoft',
#         'transformer', 'BERT', 'T5', 'PaLM', 'Bard', 'ChatGPT',
#         'machine learning', 'deep learning', 'neural network',
#         'AI model', 'language model', 'LLM', 'AGI'
#     ]
    
#     keywords = []
#     text_lower = text.lower()
    
#     for term in ai_terms:
#         if term.lower() in text_lower:
#             # 원본 케이스 유지해서 추출
#             start_idx = text_lower.find(term.lower())
#             if start_idx != -1:
#                 original_term = text[start_idx:start_idx + len(term)]
#                 keywords.append(original_term)
    
#     return list(set(keywords))  # 중복 제거

# @scheduler_fn.on_schedule(schedule="0 9,18 * * 1,3,5")  # 월,수,금 오전9시, 오후6시
# def scheduled_crawl(event):
#     """스케줄된 크롤링 실행"""
#     logger.info("스케줄된 크롤링 시작")
    
#     crawl_huggingface_papers()
#     crawl_papers_with_code() 
#     crawl_techcrunch_ai()
#     crawl_ai_news()
    
#     logger.info("스케줄된 크롤링 완료")
    
#     return "크롤링 완료"

# @https_fn.on_request()
# def manual_crawl(req: https_fn.Request) -> https_fn.Response:
#     """수동 크롤링 트리거"""
#     try:
#         logger.info("수동 크롤링 시작")
        
#         crawl_huggingface_papers()
#         crawl_papers_with_code()
#         crawl_techcrunch_ai() 
#         crawl_ai_news()
        
#         return https_fn.Response("크롤링이 성공적으로 완료되었습니다!")
        
#     except Exception as e:
#         logger.error(f"수동 크롤링 오류: {e}")
#         return https_fn.Response(f"크롤링 중 오류 발생: {str(e)}", status=500)

# @https_fn.on_request()
# def get_keywords(req: https_fn.Request) -> https_fn.Response:
#     """저장된 키워드 조회"""
#     try:
#         # 최근 일주일 내 키워드만 조회
#         week_ago = datetime.now() - timedelta(days=7)
        
#         keywords_ref = db.collection('keywords').where('createdAt', '>=', week_ago).where('isActive', '==', True)
#         keywords = []
        
#         for doc in keywords_ref.stream():
#             data = doc.to_dict()
#             data['id'] = doc.id
#             keywords.append(data)
        
#         return https_fn.Response(
#             {"keywords": keywords, "count": len(keywords)},
#             headers={"Content-Type": "application/json"}
#         )
        
#     except Exception as e:
#         logger.error(f"키워드 조회 오류: {e}")
#         return https_fn.Response(f"조회 중 오류 발생: {str(e)}", status=500)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Weekly News Crawler for GitHub Actions
"""

import os
import json
import requests
from bs4 import BeautifulSoup
import feedparser
from datetime import datetime, timedelta
import logging
from google.cloud import firestore
from google.oauth2 import service_account
import time

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Firebase 초기화
def init_firestore():
    """Firebase Firestore 클라이언트 초기화"""
    try:
        # GitHub Secrets에서 서비스 키 가져오기
        service_key = os.getenv('FIREBASE_SERVICE_KEY')
        if not service_key:
            raise ValueError("FIREBASE_SERVICE_KEY 환경변수가 설정되지 않았습니다")
        
        # JSON 문자열을 딕셔너리로 변환
        service_account_info = json.loads(service_key)
        
        # 서비스 계정 자격증명 생성
        credentials = service_account.Credentials.from_service_account_info(
            service_account_info
        )
        
        # Firestore 클라이언트 생성
        db = firestore.Client(credentials=credentials, project=service_account_info['project_id'])
        logger.info("Firestore 클라이언트 초기화 완료")
        return db
        
    except Exception as e:
        logger.error(f"Firestore 초기화 오류: {e}")
        raise

# 번역 함수 추가
def translate_to_korean(text):
    """텍스트를 한국어로 번역"""
    try:
        # 텍스트가 너무 길면 자르기 (API 제한)
        if len(text) > 500:
            text = text[:500] + "..."
        
        # MyMemory 무료 번역 API 사용
        url = "https://api.mymemory.translated.net/get"
        params = {
            'q': text,
            'langpair': 'en|ko'
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('responseStatus') == 200:
            translated = data['responseData']['translatedText']
            logger.info(f"번역 완료: {text[:50]}... -> {translated[:50]}...")
            return translated
        else:
            logger.warning(f"번역 실패: {data.get('responseDetails', 'Unknown error')}")
            return text
            
    except Exception as e:
        logger.error(f"번역 오류: {e}")
        return text
    
    # API 호출 제한을 위한 딜레이
    time.sleep(0.5)

# 카테고리 매핑
CATEGORY_MAPPING = {
    'huggingface': '모델',
    'paperswithcode': '논문/학회', 
    'techcrunch': '서비스/앱',
    'ainews': '커뮤니티 이슈',
    'reddit': '커뮤니티 이슈',
    'hackernews': '실습/코드'
}

def save_keyword_to_firestore(db, keyword, category, source, url=None, translated_keyword=None):
    """키워드를 Firestore에 저장 (번역 포함)"""
    try:
        # 중복 체크 (원본 키워드 기준)
        existing = db.collection('keywords').where('keyword', '==', keyword).limit(1).get()
        if len(existing) > 0:
            logger.info(f"키워드 '{keyword}' 이미 존재함")
            return False
        
        # 번역이 없으면 번역 시도
        if not translated_keyword:
            translated_keyword = translate_to_korean(keyword)
        
        # 새 키워드 저장
        doc_data = {
            'keyword': keyword,
            'translatedKeyword': translated_keyword,
            'category': category,
            'source': source,
            'url': url,
            'createdAt': datetime.now(),
            'isActive': True
        }
        
        db.collection('keywords').add(doc_data)
        logger.info(f"새 키워드 저장: {keyword} ({translated_keyword}) [{category}]")
        return True
        
    except Exception as e:
        logger.error(f"Firestore 저장 오류: {e}")
        return False

def extract_ai_keywords(text):
    """텍스트에서 AI 관련 키워드 추출"""
    ai_terms = [
        'GPT-4o', 'GPT-4', 'Claude 3.5', 'Claude 3', 'Gemini 1.5', 'Gemini',
        'LLaMA', 'Mixtral', 'Phi-3', 'DeepSeek', 'Qwen', 'Nous Hermes',
        'OpenAI', 'Anthropic', 'Google DeepMind', 'Meta', 'Microsoft',
        'BERT', 'T5', 'PaLM', 'Bard', 'ChatGPT', 'LLaVA',
        'Transformer', 'CLIP', 'DALL-E', 'Midjourney', 'Stable Diffusion',
        'RAG', 'LoRA', 'PEFT', 'Fine-tuning', 'Prompt Engineering',
        'AGI', 'LLM', 'Neural Network', 'Deep Learning', 'Machine Learning',
        'Computer Vision', 'Natural Language Processing', 'NLP',
        'Reinforcement Learning', 'RLHF', 'Constitutional AI'
    ]
    
    keywords = []
    text_lower = text.lower()
    
    for term in ai_terms:
        if term.lower() in text_lower:
            # 정확한 매칭을 위해 단어 경계 확인
            import re
            pattern = r'\b' + re.escape(term.lower()) + r'\b'
            if re.search(pattern, text_lower):
                keywords.append(term)
    
    return list(set(keywords))  # 중복 제거

def crawl_huggingface_papers(db):
    """Hugging Face Papers 크롤링"""
    try:
        url = "https://huggingface.co/papers"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 논문 제목들 추출 (셀렉터는 실제 사이트 구조에 따라 조정 필요)
        paper_elements = soup.find_all(['h3', 'h4', 'a'], class_=lambda x: x and any(
            cls in str(x).lower() for cls in ['title', 'paper', 'link']
        ))
        
        count = 0
        for element in paper_elements[:15]:  # 최신 15개만
            title = element.get_text().strip()
            href = element.get('href', '')
            
            if len(title) > 10 and 'paper' not in title.lower():  # 의미있는 제목만
                # AI 키워드 추출
                ai_keywords = extract_ai_keywords(title)
                if ai_keywords:
                    # 제목 자체도 키워드로 추가
                    save_keyword_to_firestore(db, title[:100], CATEGORY_MAPPING['huggingface'], 'huggingface', href)
                    count += 1
                    
                    # 추출된 키워드들도 저장
                    for keyword in ai_keywords[:3]:  # 상위 3개만
                        save_keyword_to_firestore(db, keyword, CATEGORY_MAPPING['huggingface'], 'huggingface')
        
        logger.info(f"Hugging Face: {count}개 키워드 처리")
        
    except Exception as e:
        logger.error(f"Hugging Face 크롤링 오류: {e}")

def crawl_papers_with_code(db):
    """Papers with Code 크롤링"""
    try:
        url = "https://paperswithcode.com/latest"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 논문 제목들 추출
        paper_links = soup.find_all('a', href=lambda x: x and '/paper/' in str(x))
        
        count = 0
        for link in paper_links[:15]:
            title = link.get_text().strip()
            href = link.get('href', '')
            
            if len(title) > 10:
                ai_keywords = extract_ai_keywords(title)
                if ai_keywords:
                    save_keyword_to_firestore(db, title[:100], CATEGORY_MAPPING['paperswithcode'], 'paperswithcode', href)
                    count += 1
        
        logger.info(f"Papers with Code: {count}개 키워드 처리")
        
    except Exception as e:
        logger.error(f"Papers with Code 크롤링 오류: {e}")

def crawl_techcrunch_ai(db):
    """TechCrunch AI RSS 크롤링"""
    try:
        rss_url = "https://techcrunch.com/category/artificial-intelligence/feed/"
        feed = feedparser.parse(rss_url)
        
        count = 0
        for entry in feed.entries[:10]:
            title = entry.title
            link = entry.link
            
            # AI 관련 키워드 추출
            ai_keywords = extract_ai_keywords(title)
            if ai_keywords:
                save_keyword_to_firestore(db, title[:100], CATEGORY_MAPPING['techcrunch'], 'techcrunch', link)
                count += 1
                
                for keyword in ai_keywords[:2]:
                    save_keyword_to_firestore(db, keyword, CATEGORY_MAPPING['techcrunch'], 'techcrunch')
        
        logger.info(f"TechCrunch: {count}개 키워드 처리")
        
    except Exception as e:
        logger.error(f"TechCrunch 크롤링 오류: {e}")

def crawl_ai_news(db):
    """AI News 사이트 크롤링"""
    try:
        url = "https://www.artificialintelligence-news.com"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 기사 제목들 추출
        articles = soup.find_all(['h1', 'h2', 'h3'], class_=lambda x: x and 'title' in str(x).lower())
        
        count = 0
        for article in articles[:10]:
            title = article.get_text().strip()
            
            if len(title) > 10:
                ai_keywords = extract_ai_keywords(title)
                if ai_keywords:
                    save_keyword_to_firestore(db, title[:100], CATEGORY_MAPPING['ainews'], 'ainews')
                    count += 1
        
        logger.info(f"AI News: {count}개 키워드 처리")
        
    except Exception as e:
        logger.error(f"AI News 크롤링 오류: {e}")

def main():
    """메인 크롤링 함수"""
    logger.info("=== AI Weekly News 크롤링 시작 ===")
    
    try:
        # Firestore 초기화
        db = init_firestore()
        
        # 각 사이트 크롤링
        crawl_huggingface_papers(db)
        crawl_papers_with_code(db)
        crawl_techcrunch_ai(db)
        crawl_ai_news(db)
        
        # 크롤링 완료 로그
        logger.info("=== 크롤링 완료 ===")
        
        # 최근 일주일 키워드 개수 확인
        week_ago = datetime.now() - timedelta(days=7)
        recent_keywords = db.collection('keywords').where('createdAt', '>=', week_ago).get()
        logger.info(f"최근 일주일 총 키워드: {len(recent_keywords)}개")
        
    except Exception as e:
        logger.error(f"크롤링 중 오류 발생: {e}")
        raise

if __name__ == "__main__":
    main()