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

# 카테고리 매핑
CATEGORY_MAPPING = {
    'huggingface': '모델',
    'paperswithcode': '논문/학회', 
    'techcrunch': '서비스/앱',
    'ainews': '커뮤니티 이슈',
    'reddit': '커뮤니티 이슈',
    'hackernews': '실습/코드'
}

def save_keyword_to_firestore(db, keyword, category, source, url=None):
    """키워드를 Firestore에 저장"""
    try:
        # 중복 체크
        existing = db.collection('keywords').where('keyword', '==', keyword).limit(1).get()
        if len(existing) > 0:
            logger.info(f"키워드 '{keyword}' 이미 존재함")
            return False
        
        # 새 키워드 저장
        doc_data = {
            'keyword': keyword,
            'category': category,
            'source': source,
            'url': url,
            'createdAt': datetime.now(),
            'isActive': True
        }
        
        db.collection('keywords').add(doc_data)
        logger.info(f"새 키워드 저장: {keyword} ({category})")
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