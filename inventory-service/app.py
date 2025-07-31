#!/usr/bin/env python3
"""
Inventory Service - 재고 관리 서비스
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

REQUEST_COUNT = Counter('inventory_service_requests_total', 'Total requests to inventory service')
REQUEST_LATENCY = Histogram('inventory_service_request_duration_seconds', 'Request latency')

inventory_db = [
    {
        "id": "inv1",
        "book_title": "The Great Gatsby",
        "isbn": "978-0743273565",
        "quantity": 45,
        "location": "A-1-1",
        "last_updated": "2025-01-15T10:30:00Z",
        "status": "in_stock"
    },
    {
        "id": "inv2",
        "book_title": "To Kill a Mockingbird",
        "isbn": "978-0446310789",
        "quantity": 32,
        "location": "A-1-2",
        "last_updated": "2025-01-14T14:20:00Z",
        "status": "in_stock"
    },
    {
        "id": "inv3",
        "book_title": "1984",
        "isbn": "978-0451524935",
        "quantity": 18,
        "location": "A-2-1",
        "last_updated": "2025-01-13T09:15:00Z",
        "status": "low_stock"
    },
    {
        "id": "inv4",
        "book_title": "Pride and Prejudice",
        "isbn": "978-0141439518",
        "quantity": 0,
        "location": "A-2-2",
        "last_updated": "2025-01-12T16:45:00Z",
        "status": "out_of_stock"
    }
]

# HTML Template with Modern Corporate Style
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Inventory Service - 재고 관리 시스템</title>
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
        
        .inventory-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 24px;
            margin-bottom: 40px;
        }
        
        .inventory-card {
            background: #ffffff;
            border: 1px solid #e0e0e0;
            border-radius: 12px;
            padding: 24px;
            transition: all 0.3s;
        }
        
        .inventory-card:hover {
            box-shadow: 0 8px 24px rgba(0,0,0,0.1);
            transform: translateY(-4px);
        }
        
        .inventory-card h3 {
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 12px;
            color: #000000;
        }
        
        .inventory-card p {
            color: #666666;
            margin-bottom: 16px;
            line-height: 1.5;
        }
        
        .stock-info {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 16px;
            padding-top: 16px;
            border-top: 1px solid #f0f0f0;
        }
        
        .stock-quantity {
            font-size: 24px;
            font-weight: 700;
            color: #f2c94c;
        }
        
        .stock-label {
            font-size: 12px;
            color: #666666;
        }
        
        .stock-status {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
            margin-bottom: 12px;
        }
        
        .status-available {
            background: #e8f5e8;
            color: #388e3c;
        }
        
        .status-low {
            background: #fff3e0;
            color: #f57c00;
        }
        
        .status-out {
            background: #ffebee;
            color: #d32f2f;
        }
        
        .location-info {
            font-size: 12px;
            color: #666666;
            margin-top: 8px;
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
            <a href="/" class="logo">inventory</a>
            <ul class="nav-menu">
                <li><a href="/" class="active">재고</a></li>
                <li><a href="/api/books">도서 목록</a></li>
                <li><a href="/api/locations">위치 관리</a></li>
                <li><a href="/api/movements">이동 내역</a></li>
                <li><a href="/api/alerts">알림</a></li>
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
                <h1 class="hero-title">실시간 재고 관리</h1>
                <p class="hero-subtitle">도서관의 모든 도서 재고를 실시간으로 추적하고 관리합니다. RFID 기술과 바코드 시스템을 활용한 정확한 재고 관리로 서비스 품질을 향상시킵니다.</p>
                <a href="#inventory" class="hero-button">
                    재고 확인
                    <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                        <path fill-rule="evenodd" d="M1 8a.5.5 0 0 1 .5-.5h11.793l-3.147-3.146a.5.5 0 0 1 .708-.708l4 4a.5.5 0 0 1 0 .708l-4 4a.5.5 0 0 1-.708-.708L13.293 8.5H1.5A.5.5 0 0 1 1 8z"/>
                    </svg>
                </a>
            </div>
            <div class="hero-cards">
                <div class="hero-card">
                    <h3>실시간 추적</h3>
                    <p>RFID 기술로 정확한 재고 위치 추적</p>
                </div>
                <div class="hero-card white">
                    <h3>자동 알림</h3>
                    <p>재고 부족 시 자동 알림 시스템</p>
                </div>
                <div class="hero-card">
                    <h3>이동 관리</h3>
                    <p>도서 이동 내역 실시간 기록</p>
                </div>
            </div>
        </section>

        <!-- Inventory Status Section -->
        <section class="content-section">
            <h2 class="section-title">재고 현황</h2>
            <div class="inventory-grid">
                <div class="inventory-card">
                    <h3>파이썬 프로그래밍</h3>
                    <div class="stock-status status-available">재고 있음</div>
                    <p>기초부터 고급까지 파이썬 프로그래밍의 모든 것</p>
                    <div class="stock-info">
                        <div>
                            <div class="stock-quantity">15</div>
                            <div class="stock-label">보유 수량</div>
                        </div>
                    </div>
                    <div class="location-info">위치: 프로그래밍 구역 A-1</div>
                </div>
                
                <div class="inventory-card">
                    <h3>머신러닝 입문</h3>
                    <div class="stock-status status-low">재고 부족</div>
                    <p>데이터 과학을 위한 머신러닝 기초</p>
                    <div class="stock-info">
                        <div>
                            <div class="stock-quantity">3</div>
                            <div class="stock-label">보유 수량</div>
                        </div>
                    </div>
                    <div class="location-info">위치: AI/ML 구역 B-2</div>
                </div>
                
                <div class="inventory-card">
                    <h3>웹 개발 완전정복</h3>
                    <div class="stock-status status-available">재고 있음</div>
                    <p>HTML, CSS, JavaScript로 만드는 현대적 웹사이트</p>
                    <div class="stock-info">
                        <div>
                            <div class="stock-quantity">8</div>
                            <div class="stock-label">보유 수량</div>
                        </div>
                    </div>
                    <div class="location-info">위치: 웹개발 구역 C-1</div>
                </div>
                
                <div class="inventory-card">
                    <h3>데이터베이스 설계</h3>
                    <div class="stock-status status-out">재고 없음</div>
                    <p>효율적인 데이터베이스 설계와 최적화</p>
                    <div class="stock-info">
                        <div>
                            <div class="stock-quantity">0</div>
                            <div class="stock-label">보유 수량</div>
                        </div>
                    </div>
                    <div class="location-info">위치: 데이터베이스 구역 D-3</div>
                </div>
                
                <div class="inventory-card">
                    <h3>알고리즘 문제해결</h3>
                    <div class="stock-status status-available">재고 있음</div>
                    <p>코딩 테스트를 위한 알고리즘 문제해결</p>
                    <div class="stock-info">
                        <div>
                            <div class="stock-quantity">12</div>
                            <div class="stock-label">보유 수량</div>
                        </div>
                    </div>
                    <div class="location-info">위치: 알고리즘 구역 E-2</div>
                </div>
                
                <div class="inventory-card">
                    <h3>React 완전정복</h3>
                    <div class="stock-status status-low">재고 부족</div>
                    <p>현대적인 React 개발을 위한 완벽 가이드</p>
                    <div class="stock-info">
                        <div>
                            <div class="stock-quantity">2</div>
                            <div class="stock-label">보유 수량</div>
                        </div>
                    </div>
                    <div class="location-info">위치: 웹개발 구역 C-2</div>
                </div>
            </div>
        </section>
    </main>

    <!-- Footer -->
    <footer class="footer">
        <div class="footer-content">
            <div class="footer-links">
                <a href="/api/books">도서 목록</a>
                <a href="/api/locations">위치 관리</a>
                <a href="/api/movements">이동 내역</a>
                <a href="/api/alerts">알림</a>
                <a href="/api/reports">리포트</a>
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
        {
            "id": 1,
            "title": "파이썬 프로그래밍",
            "quantity": 15,
            "location": "프로그래밍 구역 A-1",
            "status": "available"
        },
        {
            "id": 2,
            "title": "머신러닝 입문",
            "quantity": 3,
            "location": "AI/ML 구역 B-2",
            "status": "low"
        },
        {
            "id": 3,
            "title": "웹 개발 완전정복",
            "quantity": 8,
            "location": "웹개발 구역 C-1",
            "status": "available"
        }
    ]
    return jsonify({"books": books})

@app.route('/api/locations')
def get_locations():
    locations = [
        {
            "id": 1,
            "name": "프로그래밍 구역",
            "section": "A",
            "capacity": 500,
            "current_count": 342
        },
        {
            "id": 2,
            "name": "AI/ML 구역",
            "section": "B",
            "capacity": 300,
            "current_count": 189
        },
        {
            "id": 3,
            "name": "웹개발 구역",
            "section": "C",
            "capacity": 400,
            "current_count": 256
        }
    ]
    return jsonify({"locations": locations})

@app.route('/api/movements')
def get_movements():
    movements = [
        {
            "id": 1,
            "book_id": 1,
            "from_location": "입고실",
            "to_location": "프로그래밍 구역 A-1",
            "quantity": 5,
            "timestamp": "2025-01-15T10:30:00Z"
        },
        {
            "id": 2,
            "book_id": 2,
            "from_location": "AI/ML 구역 B-2",
            "to_location": "대출실",
            "quantity": 1,
            "timestamp": "2025-01-15T14:20:00Z"
        },
        {
            "id": 3,
            "book_id": 3,
            "from_location": "웹개발 구역 C-1",
            "to_location": "반납실",
            "quantity": 1,
            "timestamp": "2025-01-15T16:45:00Z"
        }
    ]
    return jsonify({"movements": movements})

@app.route('/api/alerts')
def get_alerts():
    alerts = [
        {
            "id": 1,
            "type": "low_stock",
            "book_title": "머신러닝 입문",
            "current_quantity": 3,
            "threshold": 5,
            "timestamp": "2025-01-15T09:00:00Z"
        },
        {
            "id": 2,
            "type": "out_of_stock",
            "book_title": "데이터베이스 설계",
            "current_quantity": 0,
            "threshold": 1,
            "timestamp": "2025-01-14T15:30:00Z"
        }
    ]
    return jsonify({"alerts": alerts})

@app.route('/api/reports')
def get_inventory_reports():
    reports = [
        {
            "id": 1,
            "title": "월간 재고 리포트",
            "period": "2025-01",
            "total_books": 1250,
            "available_books": 1180,
            "low_stock_books": 45,
            "out_of_stock_books": 25
        },
        {
            "id": 2,
            "title": "카테고리별 재고 현황",
            "period": "2025-01",
            "programming": 342,
            "ai_ml": 189,
            "web_development": 256,
            "database": 156,
            "algorithm": 207
        }
    ]
    return jsonify({"reports": reports})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9080, debug=True) 