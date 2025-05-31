# Firebase Functions for AI Weekly News Crawler
from firebase_functions import https_fn, scheduler_fn
from firebase_admin import initialize_app, firestore
import requests
from bs4 import BeautifulSoup
import feedparser
from datetime import datetime, timedelta
import logging

# Firebase 초기화
initialize_app()
db = firestore.client()

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 카테고리 매핑
CATEGORY_MAPPING = {
    'huggingface': '모델',
    'paperswithcode': '논문/학회', 
    'techcrunch': '서비스/앱',
    'ainews': '커뮤니티 이슈',
    'reddit': '커뮤니티 이슈',
    'hackernews': '실습/코드'
}

def save_keyword_to_firestore(keyword, category, source, url=None):
    """키워드를 Firestore에 저장"""
    try:
        # 중복 체크
        existing = db.collection('keywords').where('keyword', '==', keyword).limit(1).get()
        if len(existing) > 0:
            logger.info(f"키워드 '{keyword}' 이미 존재함")
            return
        
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
        
    except Exception as e:
        logger.error(f"Firestore 저장 오류: {e}")

def crawl_huggingface_papers():
    """Hugging Face Papers 크롤링"""
    try:
        url = "https://huggingface.co/papers"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 논문 제목들 추출 (실제 셀렉터는 사이트 구조에 따라 조정 필요)
        papers = soup.find_all('h3', class_='text-lg')
        
        for paper in papers[:10]:  # 최신 10개만
            title = paper.get_text().strip()
            if len(title) > 5:  # 의미있는 제목만
                save_keyword_to_firestore(title, CATEGORY_MAPPING['huggingface'], 'huggingface')
                
    except Exception as e:
        logger.error(f"Hugging Face 크롤링 오류: {e}")

def crawl_papers_with_code():
    """Papers with Code 크롤링"""
    try:
        url = "https://paperswithcode.com/latest"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 논문 제목들 추출
        papers = soup.find_all('h1')
        
        for paper in papers[:10]:
            title = paper.get_text().strip()
            if len(title) > 5:
                save_keyword_to_firestore(title, CATEGORY_MAPPING['paperswithcode'], 'paperswithcode')
                
    except Exception as e:
        logger.error(f"Papers with Code 크롤링 오류: {e}")

def crawl_techcrunch_ai():
    """TechCrunch AI RSS 크롤링"""
    try:
        rss_url = "https://techcrunch.com/category/artificial-intelligence/feed/"
        feed = feedparser.parse(rss_url)
        
        for entry in feed.entries[:10]:
            title = entry.title
            # AI 관련 키워드 추출
            ai_keywords = extract_ai_keywords(title)
            for keyword in ai_keywords:
                save_keyword_to_firestore(keyword, CATEGORY_MAPPING['techcrunch'], 'techcrunch', entry.link)
                
    except Exception as e:
        logger.error(f"TechCrunch 크롤링 오류: {e}")

def crawl_ai_news():
    """AI News 사이트 크롤링"""
    try:
        url = "https://www.artificialintelligence-news.com"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 기사 제목들 추출
        articles = soup.find_all('h2', class_='entry-title')
        
        for article in articles[:10]:
            title = article.get_text().strip()
            ai_keywords = extract_ai_keywords(title)
            for keyword in ai_keywords:
                save_keyword_to_firestore(keyword, CATEGORY_MAPPING['ainews'], 'ainews')
                
    except Exception as e:
        logger.error(f"AI News 크롤링 오류: {e}")

def extract_ai_keywords(text):
    """텍스트에서 AI 관련 키워드 추출"""
    ai_terms = [
        'GPT', 'Claude', 'Gemini', 'LLaMA', 'Mixtral', 'Phi-3', 'DeepSeek',
        'OpenAI', 'Anthropic', 'Google', 'Meta', 'Microsoft',
        'transformer', 'BERT', 'T5', 'PaLM', 'Bard', 'ChatGPT',
        'machine learning', 'deep learning', 'neural network',
        'AI model', 'language model', 'LLM', 'AGI'
    ]
    
    keywords = []
    text_lower = text.lower()
    
    for term in ai_terms:
        if term.lower() in text_lower:
            # 원본 케이스 유지해서 추출
            start_idx = text_lower.find(term.lower())
            if start_idx != -1:
                original_term = text[start_idx:start_idx + len(term)]
                keywords.append(original_term)
    
    return list(set(keywords))  # 중복 제거

@scheduler_fn.on_schedule(schedule="0 9,18 * * 1,3,5")  # 월,수,금 오전9시, 오후6시
def scheduled_crawl(event):
    """스케줄된 크롤링 실행"""
    logger.info("스케줄된 크롤링 시작")
    
    crawl_huggingface_papers()
    crawl_papers_with_code() 
    crawl_techcrunch_ai()
    crawl_ai_news()
    
    logger.info("스케줄된 크롤링 완료")
    
    return "크롤링 완료"

@https_fn.on_request()
def manual_crawl(req: https_fn.Request) -> https_fn.Response:
    """수동 크롤링 트리거"""
    try:
        logger.info("수동 크롤링 시작")
        
        crawl_huggingface_papers()
        crawl_papers_with_code()
        crawl_techcrunch_ai() 
        crawl_ai_news()
        
        return https_fn.Response("크롤링이 성공적으로 완료되었습니다!")
        
    except Exception as e:
        logger.error(f"수동 크롤링 오류: {e}")
        return https_fn.Response(f"크롤링 중 오류 발생: {str(e)}", status=500)

@https_fn.on_request()
def get_keywords(req: https_fn.Request) -> https_fn.Response:
    """저장된 키워드 조회"""
    try:
        # 최근 일주일 내 키워드만 조회
        week_ago = datetime.now() - timedelta(days=7)
        
        keywords_ref = db.collection('keywords').where('createdAt', '>=', week_ago).where('isActive', '==', True)
        keywords = []
        
        for doc in keywords_ref.stream():
            data = doc.to_dict()
            data['id'] = doc.id
            keywords.append(data)
        
        return https_fn.Response(
            {"keywords": keywords, "count": len(keywords)},
            headers={"Content-Type": "application/json"}
        )
        
    except Exception as e:
        logger.error(f"키워드 조회 오류: {e}")
        return https_fn.Response(f"조회 중 오류 발생: {str(e)}", status=500)