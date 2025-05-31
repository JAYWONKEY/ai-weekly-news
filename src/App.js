import React, { useState, useEffect } from 'react';
import { collection, getDocs, query, orderBy, where, limit, addDoc } from 'firebase/firestore';
import { db } from './firebase';

const AIWeeklyNews = () => {
  const [keywords, setKeywords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentWeek, setCurrentWeek] = useState('');
  const [email, setEmail] = useState('');
  const [subscribeStatus, setSubscribeStatus] = useState('');

  useEffect(() => {
    fetchKeywords();
  }, []);

  const fetchKeywords = async () => {
    try {
      setLoading(true);
      
      const weekAgo = new Date();
      weekAgo.setDate(weekAgo.getDate() - 7);
      
      const q = query(
        collection(db, 'keywords'),
        where('createdAt', '>=', weekAgo),
        orderBy('createdAt', 'desc'),
        limit(50)
      );
      
      const querySnapshot = await getDocs(q);
      const keywordList = [];
      
      querySnapshot.forEach((doc) => {
        const data = doc.data();
        keywordList.push({
          id: doc.id,
          ...data,
          createdAt: data.createdAt?.toDate ? data.createdAt.toDate() : new Date(data.createdAt?.seconds * 1000)
        });
      });
      
      setKeywords(keywordList);
      
      const now = new Date();
      const weekStr = `${now.getFullYear()}년 ${now.getMonth() + 1}월 ${Math.ceil(now.getDate() / 7)}주차`;
      setCurrentWeek(weekStr);
      
    } catch (err) {
      console.error('데이터 로딩 오류:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubscribe = async (e) => {
    e.preventDefault();
    
    if (!email || !email.includes('@')) {
      setSubscribeStatus('올바른 이메일을 입력해주세요.');
      return;
    }

    try {
      setSubscribeStatus('구독 처리 중...');
      
      const existingQuery = query(
        collection(db, 'subscribers'),
        where('email', '==', email)
      );
      const existingSnapshot = await getDocs(existingQuery);
      
      if (!existingSnapshot.empty) {
        setSubscribeStatus('이미 구독 중인 이메일입니다.');
        return;
      }

      await addDoc(collection(db, 'subscribers'), {
        email: email,
        subscribedAt: new Date(),
        isActive: true
      });

      setSubscribeStatus('구독이 완료되었습니다! 🎉');
      setEmail('');
      
      setTimeout(() => setSubscribeStatus(''), 3000);
    } catch (error) {
      console.error('구독 오류:', error);
      setSubscribeStatus('구독 중 오류가 발생했습니다.');
    }
  };

  const groupByCategory = (keywords) => {
    const grouped = {};
    keywords.forEach(keyword => {
      const category = keyword.category || '기타';
      if (!grouped[category]) {
        grouped[category] = [];
      }
      grouped[category].push(keyword);
    });
    return grouped;
  };

  const createNewsSlides = () => {
    const grouped = groupByCategory(keywords);
    const slides = [];

    // 슬라이드 1: 트렌드 요약
    slides.push({
      title: `주간 AI 인사이트 리포트 - ${currentWeek}`,
      type: "summary",
      content: `이번 주 AI 리포트에서는 주요 발전사항들을 요약합니다.\n총 ${keywords.length}개의 키워드가 수집되었습니다.`
    });

    // 슬라이드 2: 최신 AI 모델
    if (grouped['모델']) {
      slides.push({
        title: "이번 주 가장 핫한 오픈소스 AI 모델",
        type: "models",
        items: grouped['모델'].slice(0, 3)
      });
    }

    // 슬라이드 3: 논문 & 연구
    if (grouped['논문/학회']) {
      slides.push({
        title: "효율적인 추론을 위한 토큰 병합",
        type: "papers",
        items: grouped['논문/학회'].slice(0, 1),
        description: "새로운 연구 논문에서는 'Token Merging'이라는 기술을 소개하여 GPT 모델의 출력을 크게 가속화합니다. 핵심 아이디어는 추론 중에 모델이 처리해야 하는 토큰 수를 줄여 더 빠른 생성 시간을 달성하는 것입니다."
      });
    }

    // 슬라이드 4: 실용적인 도구들
    if (grouped['실습/코드'] || grouped['서비스/앱']) {
      const tools = [...(grouped['실습/코드'] || []), ...(grouped['서비스/앱'] || [])];
      slides.push({
        title: "실용적인 오픈소스 도구들",
        type: "tools",
        items: tools.slice(0, 4),
        description: "이번 주에는 프로젝트를 향상시킬 수 있는 흥미로운 오픈소스 AI 도구들의 업데이트를 강조합니다."
      });
    }

    // 슬라이드 5: 글로벌 AI 뉴스
    if (grouped['커뮤니티 이슈']) {
      slides.push({
        title: "글로벌 AI 뉴스",
        type: "news",
        items: grouped['커뮤니티 이슈'].slice(0, 3)
      });
    }

    return slides;
  };

  const slides = createNewsSlides();

  if (loading) {
    return (
      <div style={{
        position: 'relative',
        display: 'flex',
        minHeight: '100vh',
        flexDirection: 'column',
        backgroundColor: 'white',
        overflow: 'hidden',
        fontFamily: '"Plus Jakarta Sans", "Noto Sans", sans-serif'
      }}>
        <div style={{
          display: 'flex',
          flex: 1,
          justifyContent: 'center',
          alignItems: 'center'
        }}>
          <div style={{ textAlign: 'center' }}>
            <p style={{ color: '#111618', fontSize: '18px', fontWeight: 'bold' }}>
              AI 뉴스를 불러오는 중...
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div style={{
      position: 'relative',
      display: 'flex',
      minHeight: '100vh',
      flexDirection: 'column',
      backgroundColor: 'white',
      overflow: 'hidden',
      fontFamily: '"Plus Jakarta Sans", "Noto Sans", sans-serif'
    }}>
      {/* Header */}
      <header style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        whiteSpace: 'nowrap',
        borderBottom: '1px solid #f0f3f4',
        padding: '12px 40px',
        background: 'linear-gradient(135deg, #87CEEB 0%, #B0E0E6 100%)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px', color: '#2C3E50' }}>
          <div style={{ 
            width: '40px', 
            height: '40px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <img 
              src="/logo.png" 
              alt="AI News Logo"
              style={{ 
                width: '40px', 
                height: '40px', 
                borderRadius: '8px',
                objectFit: 'cover'
              }}
            />
          </div>
          <h2 style={{ 
            color: '#2C3E50', 
            fontSize: '24px', 
            fontWeight: 'bold', 
            lineHeight: 'tight', 
            letterSpacing: '-0.015em',
            textShadow: '1px 1px 2px rgba(255,255,255,0.8)'
          }}>
            AI NEWS
          </h2>
        </div>
        <div style={{ display: 'flex', flex: 1, justifyContent: 'flex-end', gap: '32px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '36px' }}>
            <a style={{ color: '#2C3E50', fontSize: '14px', fontWeight: '600', textDecoration: 'none', textShadow: '1px 1px 2px rgba(255,255,255,0.8)' }} href="#">
              홈
            </a>
            <a style={{ color: '#2C3E50', fontSize: '14px', fontWeight: '600', textDecoration: 'none', textShadow: '1px 1px 2px rgba(255,255,255,0.8)' }} href="#">
              아카이브
            </a>
            <a style={{ color: '#2C3E50', fontSize: '14px', fontWeight: '600', textDecoration: 'none', textShadow: '1px 1px 2px rgba(255,255,255,0.8)' }} href="#">
              소개
            </a>
          </div>
          <button style={{
            display: 'flex',
            maxWidth: '480px',
            cursor: 'pointer',
            alignItems: 'center',
            justifyContent: 'center',
            overflow: 'hidden',
            borderRadius: '12px',
            height: '40px',
            backgroundColor: 'rgba(255,255,255,0.8)',
            color: '#2C3E50',
            gap: '8px',
            fontSize: '14px',
            fontWeight: 'bold',
            border: '2px solid rgba(255,255,255,0.5)',
            padding: '0 10px',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
          }}>
            <span>🔔</span>
          </button>
        </div>
      </header>

      {/* Main Content */}
      <div style={{ padding: '0 160px', display: 'flex', flex: 1, justifyContent: 'center', paddingTop: '20px', paddingBottom: '20px' }}>
        <div style={{ display: 'flex', flexDirection: 'column', maxWidth: '960px', flex: 1 }}>
          
          {slides.map((slide, index) => (
            <div key={index} style={{ marginBottom: '40px' }}>
              {slide.type === 'summary' && (
                <div style={{ padding: '16px' }}>
                  <div style={{
                    backgroundSize: 'contain',
                    backgroundRepeat: 'no-repeat',
                    backgroundPosition: 'center',
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'flex-end',
                    overflow: 'hidden',
                    backgroundColor: '#87CEEB',
                    borderRadius: '12px',
                    minHeight: '320px',
                    backgroundImage: 'url("/logo.png")',
                    position: 'relative'
                  }}>
                    {/* 어두운 오버레이 추가 (텍스트 가독성을 위해) */}
                    <div style={{
                      position: 'absolute',
                      top: 0,
                      left: 0,
                      right: 0,
                      bottom: 0,
                      background: 'linear-gradient(0deg, rgba(0, 0, 0, 0.4) 0%, rgba(0, 0, 0, 0.1) 100%)',
                      borderRadius: '12px'
                    }} />
                    
                    <div style={{ display: 'flex', padding: '16px', position: 'relative', zIndex: 2 }}>
                      <p style={{ 
                        color: 'white', 
                        fontSize: '28px', 
                        fontWeight: 'bold', 
                        lineHeight: 'tight',
                        textShadow: '2px 2px 4px rgba(0,0,0,0.8)' 
                      }}>
                        {slide.title}
                      </p>
                    </div>
                  </div>
                  <p style={{ color: '#111618', fontSize: '16px', fontWeight: 'normal', paddingBottom: '12px', paddingTop: '4px', paddingLeft: '16px', paddingRight: '16px', textAlign: 'center' }}>
                    {slide.content}
                  </p>
                </div>
              )}

              {slide.type === 'models' && (
                <div>
                  <h2 style={{ color: '#111618', fontSize: '28px', fontWeight: 'bold', lineHeight: 'tight', padding: '0 16px', textAlign: 'left', paddingBottom: '12px', paddingTop: '20px' }}>
                    {slide.title}
                  </h2>
                  {slide.items.map((item, itemIndex) => (
                    <div key={itemIndex} style={{ padding: '16px' }}>
                      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'stretch', justifyContent: 'flex-start', borderRadius: '12px' }}>
                        <div style={{
                          width: '100%',
                          backgroundSize: 'cover',
                          backgroundPosition: 'center',
                          aspectRatio: '16/9',
                          borderRadius: '12px',
                          backgroundImage: 'url("https://lh3.googleusercontent.com/aida-public/AB6AXuByle37IgSPURy5U9yGieZClk_URwy-Dt6yGRNEcSMncEacP_DhTb1TREZ9bjMowu9I_khuLLwEdbn6O2Rhn5kwZmPIZ7dHwTw-l3S2vQwvKg1pRiwR-dWoV8qrzvBOK_STUvuRrC9gw7olJvSrPIjREp1qtDaDnc39oA6YgxLFf8xTxh2P8M960nYObi2cOB1gVjmKnS_7lmxesEvu8MjGCP6zFbpha8pBLKtBi-tMr6d5GLDC9Z-vYWJDrhUMYyAvz7SlxnpYdRgy")'
                        }} />
                        <div style={{ display: 'flex', width: '100%', minWidth: '288px', flexDirection: 'column', alignItems: 'stretch', justifyContent: 'center', gap: '4px', paddingTop: '16px' }}>
                          <p style={{ color: '#111618', fontSize: '18px', fontWeight: 'bold', lineHeight: 'tight' }}>
                            {item.keyword}
                          </p>
                          <div style={{ display: 'flex', alignItems: 'flex-end', gap: '12px', justifyContent: 'space-between' }}>
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                              <p style={{ color: '#617c89', fontSize: '16px', fontWeight: 'normal', lineHeight: 'normal' }}>
                                {item.category} • {item.source}
                              </p>
                              <p style={{ color: '#617c89', fontSize: '16px', fontWeight: 'normal', lineHeight: 'normal' }}>
                                {item.keyword.length > 100 ? item.keyword.substring(0, 100) + '...' : item.keyword}
                              </p>
                            </div>
                          </div>
                        </div>
                      </div>
                      <div style={{ display: 'flex', padding: '16px 0 12px 0', justifyContent: 'flex-start' }}>
                        <button style={{
                          display: 'flex',
                          minWidth: '84px',
                          maxWidth: '480px',
                          cursor: 'pointer',
                          alignItems: 'center',
                          justifyContent: 'center',
                          overflow: 'hidden',
                          borderRadius: '12px',
                          height: '40px',
                          padding: '0 16px',
                          backgroundColor: '#42b5ef',
                          color: '#111618',
                          fontSize: '14px',
                          fontWeight: 'bold',
                          border: 'none'
                        }}>
                          <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                            더 알아보기
                          </span>
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {slide.type === 'papers' && (
                <div>
                  <h2 style={{ color: '#111618', fontSize: '28px', fontWeight: 'bold', lineHeight: 'tight', padding: '0 16px', textAlign: 'left', paddingBottom: '12px', paddingTop: '20px' }}>
                    {slide.title}
                  </h2>
                  {slide.description && (
                    <p style={{ color: '#111618', fontSize: '16px', fontWeight: 'normal', lineHeight: 'normal', paddingBottom: '12px', paddingTop: '4px', paddingLeft: '16px', paddingRight: '16px' }}>
                      {slide.description}
                    </p>
                  )}
                  <div style={{ display: 'flex', padding: '16px 0 12px 16px', justifyContent: 'flex-start' }}>
                    <button style={{
                      display: 'flex',
                      minWidth: '84px',
                      maxWidth: '480px',
                      cursor: 'pointer',
                      alignItems: 'center',
                      justifyContent: 'center',
                      overflow: 'hidden',
                      borderRadius: '12px',
                      height: '40px',
                      padding: '0 16px',
                      backgroundColor: '#42b5ef',
                      color: '#111618',
                      fontSize: '14px',
                      fontWeight: 'bold',
                      border: 'none'
                    }}>
                      <span>논문 읽기</span>
                    </button>
                  </div>
                  <div style={{ display: 'flex', width: '100%', backgroundColor: 'white', padding: '16px' }}>
                    <div style={{ width: '100%', gap: '4px', overflow: 'hidden', backgroundColor: 'white', aspectRatio: '3/2', borderRadius: '12px', display: 'flex' }}>
                      <div style={{
                        width: '100%',
                        backgroundSize: 'cover',
                        backgroundPosition: 'center',
                        borderRadius: '0',
                        flex: 1,
                        backgroundImage: 'url("https://lh3.googleusercontent.com/aida-public/AB6AXuA6hti2Hy05xuZB-FUfj8m1e2i5QY7WQHkCkn7ldykUGCieqdVX4N9LyOVnJYsJPSY4OIeos3eI4ivfGslRDhujYJbTWnDO01T4IV7_QiCKZ5SPRnCu5t_zvgK6kIDLjaIdTC_LYk2kFj_3gxTZF4mcNYy-o_euRXUC41btxubKEj1E2ckxJNaHkEOE5_9gwymHoY5y8vI_ltGU7k4i8sGDwYQjsIko64rPgsB7Gjx6e-XUJ8lc1pmRGm9BD_P3mHK_-awzfk0dTCxo")'
                      }} />
                    </div>
                  </div>
                </div>
              )}

              {slide.type === 'tools' && (
                <div>
                  <h2 style={{ color: '#111618', fontSize: '28px', fontWeight: 'bold', lineHeight: 'tight', padding: '0 16px', textAlign: 'center', paddingBottom: '12px', paddingTop: '20px' }}>
                    {slide.title}
                  </h2>
                  {slide.description && (
                    <p style={{ color: '#111618', fontSize: '16px', fontWeight: 'normal', lineHeight: 'normal', paddingBottom: '12px', paddingTop: '4px', paddingLeft: '16px', paddingRight: '16px', textAlign: 'center' }}>
                      {slide.description}
                    </p>
                  )}
                  {slide.items.map((item, itemIndex) => (
                    <div key={itemIndex} style={{ display: 'flex', alignItems: 'center', gap: '16px', backgroundColor: 'white', padding: '16px', minHeight: '72px' }}>
                      <div style={{
                        color: '#111618',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        borderRadius: '8px',
                        backgroundColor: '#f0f3f4',
                        flexShrink: 0,
                        width: '48px',
                        height: '48px'
                      }}>
                        <span style={{ fontSize: '24px' }}>🔧</span>
                      </div>
                      <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
                        <p style={{ color: '#111618', fontSize: '16px', fontWeight: '500', lineHeight: 'normal', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          {(item.translatedKeyword || item.keyword).split(':')[0] || (item.translatedKeyword || item.keyword)}
                        </p>
                        <p style={{ color: '#617c89', fontSize: '14px', fontWeight: 'normal', lineHeight: 'normal', overflow: 'hidden', textOverflow: 'ellipsis', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical' }}>
                          {item.source} • {item.category}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {slide.type === 'news' && (
                <div>
                  <h2 style={{ color: '#111618', fontSize: '28px', fontWeight: 'bold', lineHeight: 'tight', padding: '0 16px', textAlign: 'center', paddingBottom: '12px', paddingTop: '20px' }}>
                    {slide.title}
                  </h2>
                  {slide.items.map((item, itemIndex) => (
                    <div key={itemIndex} style={{ display: 'flex', alignItems: 'center', gap: '16px', backgroundColor: 'white', padding: '16px', minHeight: '72px' }}>
                      <div style={{
                        color: '#111618',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        borderRadius: '8px',
                        backgroundColor: '#f0f3f4',
                        flexShrink: 0,
                        width: '48px',
                        height: '48px'
                      }}>
                        <span style={{ fontSize: '24px' }}>
                          {itemIndex === 0 ? '💰' : itemIndex === 1 ? '🤖' : '🧠'}
                        </span>
                      </div>
                      <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
                        <p style={{ color: '#111618', fontSize: '16px', fontWeight: '500', lineHeight: 'normal', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          {item.source === 'techcrunch' ? 'OpenAI' : item.source === 'ainews' ? 'Google DeepMind' : 'Anthropic'}
                        </p>
                        <p style={{ color: '#617c89', fontSize: '14px', fontWeight: 'normal', lineHeight: 'normal', overflow: 'hidden', textOverflow: 'ellipsis', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical' }}>
                          {(item.translatedKeyword || item.keyword).length > 80 ? (item.translatedKeyword || item.keyword).substring(0, 80) + '...' : (item.translatedKeyword || item.keyword)}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}

          {/* Email Subscription */}
          <div style={{
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            borderRadius: '16px',
            padding: '32px',
            textAlign: 'center',
            color: 'white',
            marginBottom: '40px'
          }}>
            <h2 style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '16px' }}>
              📧 주간 AI 뉴스 구독
            </h2>
            <p style={{ marginBottom: '24px', opacity: 0.9 }}>
              매주 정리된 AI 트렌드를 이메일로 받아보세요!
            </p>
            
            <form onSubmit={handleSubscribe} style={{ maxWidth: '400px', margin: '0 auto' }}>
              <div style={{ display: 'flex', gap: '12px', marginBottom: '12px' }}>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="이메일을 입력하세요"
                  style={{
                    flex: 1,
                    padding: '12px 16px',
                    borderRadius: '8px',
                    border: 'none',
                    fontSize: '16px'
                  }}
                  required
                />
                <button
                  type="submit"
                  style={{
                    backgroundColor: 'white',
                    color: '#667eea',
                    padding: '12px 24px',
                    borderRadius: '8px',
                    border: 'none',
                    fontWeight: 'bold',
                    cursor: 'pointer'
                  }}
                >
                  구독하기
                </button>
              </div>
              {subscribeStatus && (
                <p style={{ fontSize: '14px', opacity: 0.9 }}>{subscribeStatus}</p>
              )}
            </form>
          </div>

          {/* Footer */}
          <div style={{ textAlign: 'center', padding: '40px 0' }}>
            <button
              onClick={fetchKeywords}
              style={{
                backgroundColor: '#42b5ef',
                color: 'white',
                padding: '12px 24px',
                borderRadius: '8px',
                border: 'none',
                fontWeight: 'bold',
                cursor: 'pointer',
                marginBottom: '16px'
              }}
            >
              🔄 새로고침
            </button>
            <p style={{ color: '#617c89', fontSize: '14px' }}>
              매주 월/수/금 업데이트 | 총 {keywords.length}개 키워드 수집됨
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIWeeklyNews;