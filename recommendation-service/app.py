#!/usr/bin/env python3
"""
Recommendation Service - 추천 시스템
"""
import os
import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import requests
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

REQUEST_COUNT = Counter('recommendation_service_requests_total', 'Total requests to recommendation service')
REQUEST_LATENCY = Histogram('recommendation_service_request_duration_seconds', 'Request latency')

recommendations_db = [
    {
        "id": "rec1",
        "user_id": "user1",
        "book_title": "The Great Gatsby",
        "reason": "사용자가 읽은 'To Kill a Mockingbird'와 유사한 클래식",
        "score": 0.95,
        "created_at": "2025-01-15T10:30:00Z",
        "category": "classic"
    },
    {
        "id": "rec2",
        "user_id": "user2",
        "book_title": "1984",
        "reason": "사용자의 독서 패턴을 분석한 결과",
        "score": 0.88,
        "created_at": "2025-01-14T14:20:00Z",
        "category": "dystopian"
    },
    {
        "id": "rec3",
        "user_id": "user1",
        "book_title": "Pride and Prejudice",
        "reason": "최근 인기 도서와 유사한 장르",
        "score": 0.82,
        "created_at": "2025-01-13T09:15:00Z",
        "category": "romance"
    }
]

# HTML Template with Modern Corporate Style
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Recommendation Service - 도서 추천 시스템</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: #ffffff;
            color: #000000;
            line-height: 1.6;
        }
        
        /* Header */
        .header {
            background: #ffffff;
            border-bottom: 1px solid #f0f0f0;
            padding: 0 40px;
            position: sticky;
            top: 0;
            z-index: 1000;
        }
        
        .nav-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
            height: 60px;
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .logo {
            font-size: 24px;
            font-weight: 700;
            color: #000000;
            text-decoration: none;
        }
        
        .nav-menu {
            display: flex;
            list-style: none;
            gap: 40px;
        }
        
        .nav-menu a {
            text-decoration: none;
            color: #000000;
            font-size: 16px;
            font-weight: 500;
            transition: color 0.3s;
        }
        
        .nav-menu a:hover {
            color: #f2c94c;
        }
        
        .nav-menu a.active {
            color: #f2c94c;
            border-bottom: 2px solid #f2c94c;
        }
        
        .utility-icons {
            display: flex;
            gap: 20px;
        }
        
        .icon {
            width: 20px;
            height: 20px;
            cursor: pointer;
            opacity: 0.7;
            transition: opacity 0.3s;
        }
        
        .icon:hover {
            opacity: 1;
        }
        
        /* Main Content */
        .main-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 60px 40px;
        }
        
        .hero-section {
            display: grid;
            grid-template-columns: 1fr 400px;
            gap: 60px;
            margin-bottom: 80px;
        }
        
        .hero-content {
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        
        .hero-title {
            font-size: 48px;
            font-weight: 700;
            margin-bottom: 24px;
            line-height: 1.2;
        }
        
        .hero-subtitle {
            font-size: 20px;
            color: #666666;
            margin-bottom: 40px;
            line-height: 1.5;
        }
        
        .hero-button {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: #000000;
            color: #ffffff;
            padding: 16px 32px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            font-size: 16px;
            transition: all 0.3s;
            width: fit-content;
        }
        
        .hero-button:hover {
            background: #333333;
            transform: translateY(-2px);
        }
        
        .hero-cards {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        
        .hero-card {
            background: #f2c94c;
            padding: 24px;
            border-radius: 12px;
            color: #000000;
        }
        
        .hero-card h3 {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 8px;
        }
        
        .hero-card p {
            font-size: 14px;
            opacity: 0.8;
        }
        
        .hero-card.white {
            background: #ffffff;
            border: 1px solid #e0e0e0;
        }
        
        /* Content Sections */
        .content-section {
            margin-bottom: 80px;
        }
        
        .section-title {
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 40px;
            text-align: center;
        }
        
        .recommendation-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 24px;
            margin-bottom: 40px;
        }
        
        .recommendation-card {
            background: #ffffff;
            border: 1px solid #e0e0e0;
            border-radius: 12px;
            padding: 24px;
            transition: all 0.3s;
        }
        
        .recommendation-card:hover {
            box-shadow: 0 8px 24px rgba(0,0,0,0.1);
            transform: translateY(-4px);
        }
        
        .recommendation-card h3 {
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 12px;
            color: #000000;
        }
        
        .recommendation-card p {
            color: #666666;
            margin-bottom: 16px;
            line-height: 1.5;
        }
        
        .recommendation-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 16px;
            padding-top: 16px;
            border-top: 1px solid #f0f0f0;
        }
        
        .confidence {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .confidence-bar {
            width: 60px;
            height: 6px;
            background: #e0e0e0;
            border-radius: 3px;
            overflow: hidden;
        }
        
        .confidence-fill {
            height: 100%;
            background: #f2c94c;
            border-radius: 3px;
        }
        
        .confidence-text {
            font-size: 12px;
            color: #666666;
        }
        
        .category-tag {
            display: inline-block;
            padding: 4px 12px;
            background: #f8f9fa;
            color: #666666;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
        }
        
        /* Footer */
        .footer {
            background: #f8f9fa;
            padding: 40px;
            margin-top: 80px;
        }
        
        .footer-content {
            max-width: 1200px;
            margin: 0 auto;
            text-align: center;
        }
        
        .footer-links {
            display: flex;
            justify-content: center;
            gap: 40px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        
        .footer-links a {
            color: #666666;
            text-decoration: none;
            font-size: 14px;
            transition: color 0.3s;
        }
        
        .footer-links a:hover {
            color: #000000;
        }
        
        .copyright {
            color: #999999;
            font-size: 12px;
            margin-top: 20px;
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            .hero-section {
                grid-template-columns: 1fr;
                gap: 40px;
            }
            
            .hero-title {
                font-size: 36px;
            }
            
            .nav-menu {
                display: none;
            }
            
            .main-container {
                padding: 40px 20px;
            }
        }
    </style>
</head>
<body>
    <!-- Header -->
    <header class="header">
        <nav class="nav-container">
            <a href="/" class="logo">recommendation</a>
            <ul class="nav-menu">
                <li><a href="/" class="active">추천</a></li>
                <li><a href="/api/personalized">개인화</a></li>
                <li><a href="/api/collaborative">협업 필터링</a></li>
                <li><a href="/api/content">콘텐츠 기반</a></li>
                <li><a href="/api/trending">트렌딩</a></li>
            </ul>
            <div class="utility-icons">
                <svg class="icon" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd"></path>
                </svg>
                <svg class="icon" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM1 8a7 7 0 0112.78-4.5L10 10l-7.22-6.5A7 7 0 011 8z" clip-rule="evenodd"></path>
                </svg>
                <svg class="icon" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z"></path>
                </svg>
            </div>
        </nav>
    </header>

    <!-- Main Content -->
    <main class="main-container">
        <!-- Hero Section -->
        <section class="hero-section">
            <div class="hero-content">
                <h1 class="hero-title">AI 기반 도서 추천</h1>
                <p class="hero-subtitle">머신러닝 알고리즘을 활용한 개인화된 도서 추천 시스템입니다. 사용자의 독서 패턴을 분석하여 가장 적합한 도서를 추천해드립니다.</p>
                <a href="#recommendations" class="hero-button">
                    추천 받기
                    <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                        <path fill-rule="evenodd" d="M1 8a.5.5 0 0 1 .5-.5h11.793l-3.147-3.146a.5.5 0 0 1 .708-.708l4 4a.5.5 0 0 1 0 .708l-4 4a.5.5 0 0 1-.708-.708L13.293 8.5H1.5A.5.5 0 0 1 1 8z"/>
                    </svg>
                </a>
            </div>
            <div class="hero-cards">
                <div class="hero-card">
                    <h3>개인화 추천</h3>
                    <p>사용자 취향을 분석한 맞춤형 도서 추천</p>
                </div>
                <div class="hero-card white">
                    <h3>협업 필터링</h3>
                    <p>비슷한 사용자들의 선호도를 기반</p>
                </div>
                <div class="hero-card">
                    <h3>콘텐츠 기반</h3>
                    <p>도서의 특성을 분석한 추천</p>
                </div>
            </div>
        </section>

        <!-- Recommendations Section -->
        <section class="content-section">
            <h2 class="section-title">개인화 추천 도서</h2>
            <div class="recommendation-grid">
                <div class="recommendation-card">
                    <h3>딥러닝 기초</h3>
                    <p>최근 본 "머신러닝 입문"과 연관된 도서입니다. AI/ML 분야에 관심이 많으신 것 같아 추천드립니다.</p>
                    <div class="category-tag">AI/ML</div>
                    <div class="recommendation-meta">
                        <div class="confidence">
                            <div class="confidence-bar">
                                <div class="confidence-fill" style="width: 92%;"></div>
                            </div>
                            <span class="confidence-text">92%</span>
                        </div>
                    </div>
                </div>
                
                <div class="recommendation-card">
                    <h3>React 완전정복</h3>
                    <p>웹 개발 관심도가 높으신 것을 확인했습니다. 최신 프론트엔드 기술을 다룬 도서입니다.</p>
                    <div class="category-tag">웹개발</div>
                    <div class="recommendation-meta">
                        <div class="confidence">
                            <div class="confidence-bar">
                                <div class="confidence-fill" style="width: 88%;"></div>
                            </div>
                            <span class="confidence-text">88%</span>
                        </div>
                    </div>
                </div>
                
                <div class="recommendation-card">
                    <h3>SQL 마스터</h3>
                    <p>데이터베이스 카테고리를 자주 이용하시는군요. 실무에서 바로 활용할 수 있는 SQL 도서입니다.</p>
                    <div class="category-tag">데이터베이스</div>
                    <div class="recommendation-meta">
                        <div class="confidence">
                            <div class="confidence-bar">
                                <div class="confidence-fill" style="width: 85%;"></div>
                            </div>
                            <span class="confidence-text">85%</span>
                        </div>
                    </div>
                </div>
                
                <div class="recommendation-card">
                    <h3>코딩 테스트 준비</h3>
                    <p>알고리즘 문제해결 도서를 즐겨 읽으시는군요. 실전 코딩 테스트 대비를 위한 도서입니다.</p>
                    <div class="category-tag">알고리즘</div>
                    <div class="recommendation-meta">
                        <div class="confidence">
                            <div class="confidence-bar">
                                <div class="confidence-fill" style="width: 78%;"></div>
                            </div>
                            <span class="confidence-text">78%</span>
                        </div>
                    </div>
                </div>
                
                <div class="recommendation-card">
                    <h3>Git 완전정복</h3>
                    <p>프로그래밍 도구에 관심이 많으신 것 같습니다. 버전 관리 시스템의 모든 것을 다룬 도서입니다.</p>
                    <div class="category-tag">프로그래밍</div>
                    <div class="recommendation-meta">
                        <div class="confidence">
                            <div class="confidence-bar">
                                <div class="confidence-fill" style="width: 75%;"></div>
                            </div>
                            <span class="confidence-text">75%</span>
                        </div>
                    </div>
                </div>
                
                <div class="recommendation-card">
                    <h3>Docker 컨테이너</h3>
                    <p>최신 개발 환경에 관심이 많으신군요. 컨테이너 기술의 핵심을 다룬 실용적인 도서입니다.</p>
                    <div class="category-tag">DevOps</div>
                    <div class="recommendation-meta">
                        <div class="confidence">
                            <div class="confidence-bar">
                                <div class="confidence-fill" style="width: 72%;"></div>
                            </div>
                            <span class="confidence-text">72%</span>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    </main>

    <!-- Footer -->
    <footer class="footer">
        <div class="footer-content">
            <div class="footer-links">
                <a href="/api/personalized">개인화 추천</a>
                <a href="/api/collaborative">협업 필터링</a>
                <a href="/api/content">콘텐츠 기반</a>
                <a href="/api/trending">트렌딩</a>
                <a href="/api/preferences">선호도 설정</a>
            </div>
            <div class="copyright">
                © Korea University NetLab JunhoBae. All rights reserved.
            </div>
        </div>
    </footer>
</body>
</html>
'''

@app.route('/')
def index():
    return HTML_TEMPLATE

@app.route('/api/personalized')
def get_personalized_recommendations():
    recommendations = [
        {
            "id": 1,
            "title": "딥러닝 기초",
            "reason": "최근 본 머신러닝 입문과 연관",
            "confidence": 0.92,
            "category": "AI/ML"
        },
        {
            "id": 2,
            "title": "React 완전정복",
            "reason": "웹 개발 관심도 기반",
            "confidence": 0.88,
            "category": "웹개발"
        },
        {
            "id": 3,
            "title": "SQL 마스터",
            "reason": "데이터베이스 카테고리 선호",
            "confidence": 0.85,
            "category": "데이터베이스"
        }
    ]
    return jsonify({"recommendations": recommendations})

@app.route('/api/collaborative')
def get_collaborative_recommendations():
    recommendations = [
        {
            "id": 1,
            "title": "알고리즘 문제해결",
            "similar_users": 156,
            "avg_rating": 4.7,
            "category": "알고리즘"
        },
        {
            "id": 2,
            "title": "파이썬 프로그래밍",
            "similar_users": 234,
            "avg_rating": 4.8,
            "category": "프로그래밍"
        },
        {
            "id": 3,
            "title": "웹 개발 완전정복",
            "similar_users": 189,
            "avg_rating": 4.6,
            "category": "웹개발"
        }
    ]
    return jsonify({"recommendations": recommendations})

@app.route('/api/content')
def get_content_based_recommendations():
    recommendations = [
        {
            "id": 1,
            "title": "머신러닝 실전",
            "similarity": 0.89,
            "features": ["AI", "ML", "Python"],
            "category": "AI/ML"
        },
        {
            "id": 2,
            "title": "JavaScript ES6+",
            "similarity": 0.85,
            "features": ["웹개발", "JavaScript", "Frontend"],
            "category": "웹개발"
        },
        {
            "id": 3,
            "title": "NoSQL 데이터베이스",
            "similarity": 0.82,
            "features": ["데이터베이스", "NoSQL", "MongoDB"],
            "category": "데이터베이스"
        }
    ]
    return jsonify({"recommendations": recommendations})

@app.route('/api/trending')
def get_trending_recommendations():
    trending = [
        {
            "id": 1,
            "title": "Kubernetes 완전정복",
            "trend_score": 95.2,
            "category": "DevOps",
            "growth": "+25%"
        },
        {
            "id": 2,
            "title": "TypeScript 핵심",
            "trend_score": 88.7,
            "category": "웹개발",
            "growth": "+18%"
        },
        {
            "id": 3,
            "title": "FastAPI 웹개발",
            "trend_score": 82.3,
            "category": "프로그래밍",
            "growth": "+15%"
        }
    ]
    return jsonify({"trending": trending})

@app.route('/api/preferences')
def get_user_preferences():
    preferences = {
        "favorite_categories": ["프로그래밍", "AI/ML", "웹개발"],
        "reading_level": "intermediate",
        "preferred_languages": ["한국어", "영어"],
        "max_pages": 500,
        "publication_years": ["2020", "2021", "2022", "2023", "2025"]
    }
    return jsonify(preferences)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9080, debug=True) 