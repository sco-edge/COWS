#!/usr/bin/env python3
"""
Search Service - 도서 검색 서비스
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

REQUEST_COUNT = Counter('search_service_requests_total', 'Total requests to search service')
REQUEST_LATENCY = Histogram('search_service_request_duration_seconds', 'Request latency')

books_db = [
    {
        "id": "book1",
        "title": "The Great Gatsby",
        "author": "F. Scott Fitzgerald",
        "genre": "Fiction",
        "published_year": 1925,
        "isbn": "978-0743273565",
        "description": "A story of the fabulously wealthy Jay Gatsby and his love for the beautiful Daisy Buchanan."
    },
    {
        "id": "book2",
        "title": "To Kill a Mockingbird",
        "author": "Harper Lee",
        "genre": "Fiction",
        "published_year": 1960,
        "isbn": "978-0446310789",
        "description": "The story of young Scout Finch and her father Atticus in a racially divided Alabama town."
    },
    {
        "id": "book3",
        "title": "1984",
        "author": "George Orwell",
        "genre": "Dystopian",
        "published_year": 1949,
        "isbn": "978-0451524935",
        "description": "A dystopian novel about totalitarianism and surveillance society."
    },
    {
        "id": "book4",
        "title": "Pride and Prejudice",
        "author": "Jane Austen",
        "genre": "Romance",
        "published_year": 1813,
        "isbn": "978-0141439518",
        "description": "The story of Elizabeth Bennet and Mr. Darcy in Georgian-era England."
    }
]

# HTML Template with Modern Corporate Style
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Search Service - 도서 검색 시스템</title>
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
        
        .search-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 24px;
            margin-bottom: 40px;
        }
        
        .search-card {
            background: #ffffff;
            border: 1px solid #e0e0e0;
            border-radius: 12px;
            padding: 24px;
            transition: all 0.3s;
        }
        
        .search-card:hover {
            box-shadow: 0 8px 24px rgba(0,0,0,0.1);
            transform: translateY(-4px);
        }
        
        .search-card h3 {
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 12px;
            color: #000000;
        }
        
        .search-card p {
            color: #666666;
            margin-bottom: 16px;
            line-height: 1.5;
        }
        
        .search-stats {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 16px;
            padding-top: 16px;
            border-top: 1px solid #f0f0f0;
        }
        
        .stat {
            text-align: center;
        }
        
        .stat-number {
            font-size: 24px;
            font-weight: 700;
            color: #f2c94c;
        }
        
        .stat-label {
            font-size: 12px;
            color: #666666;
            margin-top: 4px;
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
            <a href="/" class="logo">search</a>
            <ul class="nav-menu">
                <li><a href="/" class="active">검색</a></li>
                <li><a href="/api/books">도서 목록</a></li>
                <li><a href="/api/authors">작가 검색</a></li>
                <li><a href="/api/categories">카테고리</a></li>
                <li><a href="/api/trending">인기 검색</a></li>
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
                <h1 class="hero-title">스마트 도서 검색 시스템</h1>
                <p class="hero-subtitle">AI 기반 추천 알고리즘으로 당신에게 딱 맞는 책을 찾아드립니다. 실시간 검색과 개인화된 추천으로 독서 경험을 한 단계 업그레이드하세요.</p>
                <a href="#search" class="hero-button">
                    검색 시작하기
                    <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                        <path fill-rule="evenodd" d="M1 8a.5.5 0 0 1 .5-.5h11.793l-3.147-3.146a.5.5 0 0 1 .708-.708l4 4a.5.5 0 0 1 0 .708l-4 4a.5.5 0 0 1-.708-.708L13.293 8.5H1.5A.5.5 0 0 1 1 8z"/>
                    </svg>
                </a>
            </div>
            <div class="hero-cards">
                <div class="hero-card">
                    <h3>실시간 검색</h3>
                    <p>0.1초 만에 원하는 책을 찾아보세요</p>
                </div>
                <div class="hero-card white">
                    <h3>AI 추천</h3>
                    <p>개인 취향을 분석한 맞춤형 도서 추천</p>
                </div>
                <div class="hero-card">
                    <h3>트렌드 분석</h3>
                    <p>실시간 인기 도서와 검색 트렌드</p>
                </div>
            </div>
        </section>

        <!-- Search Results Section -->
        <section class="content-section">
            <h2 class="section-title">검색 결과</h2>
            <div class="search-grid">
                <div class="search-card">
                    <h3>파이썬 프로그래밍</h3>
                    <p>기초부터 고급까지 파이썬 프로그래밍의 모든 것</p>
                    <div class="search-stats">
                        <div class="stat">
                            <div class="stat-number">4.8</div>
                            <div class="stat-label">평점</div>
                        </div>
                        <div class="stat">
                            <div class="stat-number">1,234</div>
                            <div class="stat-label">리뷰</div>
                        </div>
                        <div class="stat">
                            <div class="stat-number">2023</div>
                            <div class="stat-label">출판년도</div>
                        </div>
                    </div>
                </div>
                
                <div class="search-card">
                    <h3>머신러닝 입문</h3>
                    <p>데이터 과학을 위한 머신러닝 기초</p>
                    <div class="search-stats">
                        <div class="stat">
                            <div class="stat-number">4.6</div>
                            <div class="stat-label">평점</div>
                        </div>
                        <div class="stat">
                            <div class="stat-number">856</div>
                            <div class="stat-label">리뷰</div>
                        </div>
                        <div class="stat">
                            <div class="stat-number">2022</div>
                            <div class="stat-label">출판년도</div>
                        </div>
                    </div>
                </div>
                
                <div class="search-card">
                    <h3>웹 개발 완전정복</h3>
                    <p>HTML, CSS, JavaScript로 만드는 현대적 웹사이트</p>
                    <div class="search-stats">
                        <div class="stat">
                            <div class="stat-number">4.9</div>
                            <div class="stat-label">평점</div>
                        </div>
                        <div class="stat">
                            <div class="stat-number">2,156</div>
                            <div class="stat-label">리뷰</div>
                        </div>
                        <div class="stat">
                            <div class="stat-number">2023</div>
                            <div class="stat-label">출판년도</div>
                        </div>
                    </div>
                </div>
                
                <div class="search-card">
                    <h3>데이터베이스 설계</h3>
                    <p>효율적인 데이터베이스 설계와 최적화</p>
                    <div class="search-stats">
                        <div class="stat">
                            <div class="stat-number">4.7</div>
                            <div class="stat-label">평점</div>
                        </div>
                        <div class="stat">
                            <div class="stat-number">1,089</div>
                            <div class="stat-label">리뷰</div>
                        </div>
                        <div class="stat">
                            <div class="stat-number">2022</div>
                            <div class="stat-label">출판년도</div>
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
                <a href="/api/books">도서 목록</a>
                <a href="/api/authors">작가 검색</a>
                <a href="/api/categories">카테고리</a>
                <a href="/api/trending">인기 검색</a>
                <a href="/api/recommendations">추천 도서</a>
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

@app.route('/api/books')
def get_books():
    books = [
        {"id": 1, "title": "파이썬 프로그래밍", "author": "김파이썬", "category": "프로그래밍", "rating": 4.8, "reviews": 1234},
        {"id": 2, "title": "머신러닝 입문", "author": "이머신", "category": "AI/ML", "rating": 4.6, "reviews": 856},
        {"id": 3, "title": "웹 개발 완전정복", "author": "박웹", "category": "웹개발", "rating": 4.9, "reviews": 2156},
        {"id": 4, "title": "데이터베이스 설계", "author": "최데이터", "category": "데이터베이스", "rating": 4.7, "reviews": 1089},
        {"id": 5, "title": "알고리즘 문제해결", "author": "정알고", "category": "알고리즘", "rating": 4.5, "reviews": 2341}
    ]
    return jsonify({"books": books})

@app.route('/api/authors')
def get_authors():
    authors = [
        {"id": 1, "name": "김파이썬", "books_count": 15, "avg_rating": 4.6},
        {"id": 2, "name": "이머신", "books_count": 8, "avg_rating": 4.4},
        {"id": 3, "name": "박웹", "books_count": 12, "avg_rating": 4.7},
        {"id": 4, "name": "최데이터", "books_count": 6, "avg_rating": 4.3},
        {"id": 5, "name": "정알고", "books_count": 20, "avg_rating": 4.8}
    ]
    return jsonify({"authors": authors})

@app.route('/api/categories')
def get_categories():
    categories = [
        {"id": 1, "name": "프로그래밍", "books_count": 156, "trending": True},
        {"id": 2, "name": "AI/ML", "books_count": 89, "trending": True},
        {"id": 3, "name": "웹개발", "books_count": 234, "trending": False},
        {"id": 4, "name": "데이터베이스", "books_count": 67, "trending": False},
        {"id": 5, "name": "알고리즘", "books_count": 123, "trending": True}
    ]
    return jsonify({"categories": categories})

@app.route('/api/trending')
def get_trending():
    trending = [
        {"id": 1, "title": "파이썬 프로그래밍", "search_count": 15420, "trend": "+15%"},
        {"id": 2, "title": "머신러닝 입문", "search_count": 12340, "trend": "+8%"},
        {"id": 3, "title": "웹 개발 완전정복", "search_count": 9876, "trend": "+22%"},
        {"id": 4, "title": "데이터베이스 설계", "search_count": 7654, "trend": "+5%"},
        {"id": 5, "title": "알고리즘 문제해결", "search_count": 6543, "trend": "+12%"}
    ]
    return jsonify({"trending": trending})

@app.route('/api/recommendations')
def get_recommendations():
    recommendations = [
        {"id": 1, "title": "딥러닝 기초", "reason": "최근 본 머신러닝 입문과 연관", "confidence": 0.92},
        {"id": 2, "title": "React 완전정복", "reason": "웹 개발 관심도 기반", "confidence": 0.88},
        {"id": 3, "title": "SQL 마스터", "reason": "데이터베이스 카테고리 선호", "confidence": 0.85},
        {"id": 4, "title": "코딩 테스트 준비", "reason": "알고리즘 문제해결과 연관", "confidence": 0.78},
        {"id": 5, "title": "Git 완전정복", "reason": "프로그래밍 도구 관심", "confidence": 0.75}
    ]
    return jsonify({"recommendations": recommendations})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9080, debug=True) 