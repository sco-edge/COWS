#!/usr/bin/env python3
"""
Shipping Service - 배송 관리
"""
import os
import json
import logging
from datetime import datetime
from flask import Flask, jsonify, render_template_string
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import requests
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

REQUEST_COUNT = Counter('shipping_service_requests_total', 'Total requests to shipping service')
REQUEST_LATENCY = Histogram('shipping_service_request_duration_seconds', 'Request latency')

shipping_db = [
    {
        "id": "ship1",
        "order_id": "order1",
        "tracking_number": "TRK123456789",
        "status": "in_transit",
        "carrier": "CJ대한통운",
        "estimated_delivery": "2025-01-20",
        "current_location": "서울 중앙분류소",
        "created_at": "2025-01-15T10:30:00Z"
    },
    {
        "id": "ship2",
        "order_id": "order2",
        "tracking_number": "TRK987654321",
        "status": "delivered",
        "carrier": "한진택배",
        "estimated_delivery": "2025-01-18",
        "current_location": "배송 완료",
        "created_at": "2025-01-14T14:20:00Z"
    },
    {
        "id": "ship3",
        "order_id": "order3",
        "tracking_number": "TRK456789123",
        "status": "pending",
        "carrier": "로젠택배",
        "estimated_delivery": "2025-01-25",
        "current_location": "배송 준비 중",
        "created_at": "2025-01-13T09:15:00Z"
    }
]

# HTML Template with Modern Corporate Style
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Shipping Service - 배송 관리 시스템</title>
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
        
        .shipping-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 24px;
            margin-bottom: 40px;
        }
        
        .shipping-card {
            background: #ffffff;
            border: 1px solid #e0e0e0;
            border-radius: 12px;
            padding: 24px;
            transition: all 0.3s;
        }
        
        .shipping-card:hover {
            box-shadow: 0 8px 24px rgba(0,0,0,0.1);
            transform: translateY(-4px);
        }
        
        .shipping-card h3 {
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 12px;
            color: #000000;
        }
        
        .shipping-card p {
            color: #666666;
            margin-bottom: 16px;
            line-height: 1.5;
        }
        
        .shipping-status {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
            margin-bottom: 12px;
        }
        
        .status-delivered {
            background: #e8f5e8;
            color: #388e3c;
        }
        
        .status-in-transit {
            background: #e3f2fd;
            color: #1976d2;
        }
        
        .status-pending {
            background: #fff3e0;
            color: #f57c00;
        }
        
        .status-delayed {
            background: #ffebee;
            color: #d32f2f;
        }
        
        .shipping-info {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 16px;
            padding-top: 16px;
            border-top: 1px solid #f0f0f0;
        }
        
        .tracking-number {
            font-size: 14px;
            color: #666666;
            font-weight: 500;
        }
        
        .shipping-date {
            font-size: 12px;
            color: #666666;
        }
        
        .shipping-progress {
            margin-top: 16px;
        }
        
        .progress-step {
            display: flex;
            align-items: center;
            margin-bottom: 8px;
        }
        
        .progress-dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 12px;
        }
        
        .dot-completed {
            background: #f2c94c;
        }
        
        .dot-current {
            background: #f2c94c;
            border: 2px solid #e0e0e0;
        }
        
        .dot-pending {
            background: #e0e0e0;
        }
        
        .progress-text {
            font-size: 14px;
            color: #666666;
        }
        
        .progress-text.completed {
            color: #000000;
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
            <a href="/" class="logo">shipping</a>
            <ul class="nav-menu">
                <li><a href="/" class="active">배송</a></li>
                <li><a href="/api/orders">주문 관리</a></li>
                <li><a href="/api/tracking">배송 추적</a></li>
                <li><a href="/api/carriers">운송업체</a></li>
                <li><a href="/api/returns">반품</a></li>
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
                <h1 class="hero-title">스마트 배송 관리</h1>
                <p class="hero-subtitle">도서 대출과 반납을 위한 효율적인 배송 시스템입니다. 실시간 추적과 자동화된 배송 프로세스로 사용자 경험을 향상시킵니다.</p>
                <a href="#shipping" class="hero-button">
                    배송 추적
                    <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                        <path fill-rule="evenodd" d="M1 8a.5.5 0 0 1 .5-.5h11.793l-3.147-3.146a.5.5 0 0 1 .708-.708l4 4a.5.5 0 0 1 0 .708l-4 4a.5.5 0 0 1-.708-.708L13.293 8.5H1.5A.5.5 0 0 1 1 8z"/>
                    </svg>
                </a>
            </div>
            <div class="hero-cards">
                <div class="hero-card">
                    <h3>실시간 추적</h3>
                    <p>배송 상태를 실시간으로 확인</p>
                </div>
                <div class="hero-card white">
                    <h3>자동화 배송</h3>
                    <p>스마트 로봇을 활용한 자동 배송</p>
                </div>
                <div class="hero-card">
                    <h3>다중 운송업체</h3>
                    <p>여러 운송업체와 연동</p>
                </div>
            </div>
        </section>

        <!-- Shipping Orders Section -->
        <section class="content-section">
            <h2 class="section-title">배송 주문 현황</h2>
            <div class="shipping-grid">
                <div class="shipping-card">
                    <h3>파이썬 프로그래밍</h3>
                    <div class="shipping-status status-delivered">배송 완료</div>
                    <p>사용자: 김철수 (서울시 강남구)</p>
                    <div class="shipping-info">
                        <div class="tracking-number">TRK-2025-001</div>
                        <div class="shipping-date">2025-01-15</div>
                    </div>
                    <div class="shipping-progress">
                        <div class="progress-step">
                            <div class="progress-dot dot-completed"></div>
                            <div class="progress-text completed">주문 접수</div>
                        </div>
                        <div class="progress-step">
                            <div class="progress-dot dot-completed"></div>
                            <div class="progress-text completed">배송 준비</div>
                        </div>
                        <div class="progress-step">
                            <div class="progress-dot dot-completed"></div>
                            <div class="progress-text completed">배송 중</div>
                        </div>
                        <div class="progress-step">
                            <div class="progress-dot dot-completed"></div>
                            <div class="progress-text completed">배송 완료</div>
                        </div>
                    </div>
                </div>
                
                <div class="shipping-card">
                    <h3>머신러닝 입문</h3>
                    <div class="shipping-status status-in-transit">배송 중</div>
                    <p>사용자: 이영희 (서울시 서초구)</p>
                    <div class="shipping-info">
                        <div class="tracking-number">TRK-2025-002</div>
                        <div class="shipping-date">2025-01-15</div>
                    </div>
                    <div class="shipping-progress">
                        <div class="progress-step">
                            <div class="progress-dot dot-completed"></div>
                            <div class="progress-text completed">주문 접수</div>
                        </div>
                        <div class="progress-step">
                            <div class="progress-dot dot-completed"></div>
                            <div class="progress-text completed">배송 준비</div>
                        </div>
                        <div class="progress-step">
                            <div class="progress-dot dot-current"></div>
                            <div class="progress-text completed">배송 중</div>
                        </div>
                        <div class="progress-step">
                            <div class="progress-dot dot-pending"></div>
                            <div class="progress-text">배송 완료</div>
                        </div>
                    </div>
                </div>
                
                <div class="shipping-card">
                    <h3>웹 개발 완전정복</h3>
                    <div class="shipping-status status-pending">배송 준비</div>
                    <p>사용자: 박민수 (서울시 마포구)</p>
                    <div class="shipping-info">
                        <div class="tracking-number">TRK-2025-003</div>
                        <div class="shipping-date">2025-01-15</div>
                    </div>
                    <div class="shipping-progress">
                        <div class="progress-step">
                            <div class="progress-dot dot-completed"></div>
                            <div class="progress-text completed">주문 접수</div>
                        </div>
                        <div class="progress-step">
                            <div class="progress-dot dot-current"></div>
                            <div class="progress-text completed">배송 준비</div>
                        </div>
                        <div class="progress-step">
                            <div class="progress-dot dot-pending"></div>
                            <div class="progress-text">배송 중</div>
                        </div>
                        <div class="progress-step">
                            <div class="progress-dot dot-pending"></div>
                            <div class="progress-text">배송 완료</div>
                        </div>
                    </div>
                </div>
                
                <div class="shipping-card">
                    <h3>데이터베이스 설계</h3>
                    <div class="shipping-status status-delayed">배송 지연</div>
                    <p>사용자: 최지영 (서울시 송파구)</p>
                    <div class="shipping-info">
                        <div class="tracking-number">TRK-2025-004</div>
                        <div class="shipping-date">2025-01-14</div>
                    </div>
                    <div class="shipping-progress">
                        <div class="progress-step">
                            <div class="progress-dot dot-completed"></div>
                            <div class="progress-text completed">주문 접수</div>
                        </div>
                        <div class="progress-step">
                            <div class="progress-dot dot-completed"></div>
                            <div class="progress-text completed">배송 준비</div>
                        </div>
                        <div class="progress-step">
                            <div class="progress-dot dot-current"></div>
                            <div class="progress-text completed">배송 중</div>
                        </div>
                        <div class="progress-step">
                            <div class="progress-dot dot-pending"></div>
                            <div class="progress-text">배송 완료</div>
                        </div>
                    </div>
                </div>
                
                <div class="shipping-card">
                    <h3>알고리즘 문제해결</h3>
                    <div class="shipping-status status-delivered">배송 완료</div>
                    <p>사용자: 정현우 (서울시 종로구)</p>
                    <div class="shipping-info">
                        <div class="tracking-number">TRK-2025-005</div>
                        <div class="shipping-date">2025-01-14</div>
                    </div>
                    <div class="shipping-progress">
                        <div class="progress-step">
                            <div class="progress-dot dot-completed"></div>
                            <div class="progress-text completed">주문 접수</div>
                        </div>
                        <div class="progress-step">
                            <div class="progress-dot dot-completed"></div>
                            <div class="progress-text completed">배송 준비</div>
                        </div>
                        <div class="progress-step">
                            <div class="progress-dot dot-completed"></div>
                            <div class="progress-text completed">배송 중</div>
                        </div>
                        <div class="progress-step">
                            <div class="progress-dot dot-completed"></div>
                            <div class="progress-text completed">배송 완료</div>
                        </div>
                    </div>
                </div>
                
                <div class="shipping-card">
                    <h3>React 완전정복</h3>
                    <div class="shipping-status status-pending">배송 준비</div>
                    <p>사용자: 김서연 (서울시 강서구)</p>
                    <div class="shipping-info">
                        <div class="tracking-number">TRK-2025-006</div>
                        <div class="shipping-date">2025-01-15</div>
                    </div>
                    <div class="shipping-progress">
                        <div class="progress-step">
                            <div class="progress-dot dot-completed"></div>
                            <div class="progress-text completed">주문 접수</div>
                        </div>
                        <div class="progress-step">
                            <div class="progress-dot dot-current"></div>
                            <div class="progress-text completed">배송 준비</div>
                        </div>
                        <div class="progress-step">
                            <div class="progress-dot dot-pending"></div>
                            <div class="progress-text">배송 중</div>
                        </div>
                        <div class="progress-step">
                            <div class="progress-dot dot-pending"></div>
                            <div class="progress-text">배송 완료</div>
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
                <a href="/api/orders">주문 관리</a>
                <a href="/api/tracking">배송 추적</a>
                <a href="/api/carriers">운송업체</a>
                <a href="/api/returns">반품</a>
                <a href="/api/analytics">분석</a>
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

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "shipping-service"})

@app.route('/metrics', methods=['GET'])
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

@app.route('/shipping', methods=['GET'])
@REQUEST_LATENCY.time()
def get_shipping():
    REQUEST_COUNT.inc()
    logger.info("Getting all shipping")
    return jsonify(shipping_db)

@app.route('/shipping/<ship_id>', methods=['GET'])
@REQUEST_LATENCY.time()
def get_shipping_item(ship_id):
    REQUEST_COUNT.inc()
    logger.info(f"Getting shipping {ship_id}")
    
    for ship in shipping_db:
        if ship['id'] == ship_id:
            return jsonify(ship)
    
    return jsonify({"error": "Shipping not found"}), 404

@app.route('/shipping', methods=['POST'])
@REQUEST_LATENCY.time()
def create_shipping():
    REQUEST_COUNT.inc()
    data = request.get_json()
    
    new_ship = {
        "id": f"ship{len(shipping_db) + 1}",
        "order_id": data.get('order_id'),
        "tracking_number": f"TRK{len(shipping_db) + 1:09d}",
        "status": data.get('status', 'pending'),
        "carrier": data.get('carrier', 'CJ대한통운'),
        "estimated_delivery": data.get('estimated_delivery', '2025-01-25'),
        "current_location": data.get('current_location', '배송 준비 중'),
        "created_at": datetime.now().isoformat() + "Z"
    }
    
    shipping_db.append(new_ship)
    logger.info(f"Created new shipping: {new_ship['tracking_number']}")
    
    return jsonify(new_ship), 201

@app.route('/api/orders')
def get_orders():
    orders = [
        {
            "id": 1,
            "book_title": "파이썬 프로그래밍",
            "user_name": "김철수",
            "user_address": "서울시 강남구",
            "tracking_number": "TRK-2025-001",
            "status": "delivered",
            "created_at": "2025-01-15T10:30:00Z"
        },
        {
            "id": 2,
            "book_title": "머신러닝 입문",
            "user_name": "이영희",
            "user_address": "서울시 서초구",
            "tracking_number": "TRK-2025-002",
            "status": "in_transit",
            "created_at": "2025-01-15T11:15:00Z"
        },
        {
            "id": 3,
            "book_title": "웹 개발 완전정복",
            "user_name": "박민수",
            "user_address": "서울시 마포구",
            "tracking_number": "TRK-2025-003",
            "status": "pending",
            "created_at": "2025-01-15T14:20:00Z"
        }
    ]
    return jsonify({"orders": orders})

@app.route('/api/tracking')
def get_tracking_info():
    tracking = [
        {
            "tracking_number": "TRK-2025-001",
            "status": "delivered",
            "carrier": "CJ대한통운",
            "estimated_delivery": "2025-01-16",
            "actual_delivery": "2025-01-15",
            "history": [
                {"status": "주문 접수", "timestamp": "2025-01-15T10:30:00Z"},
                {"status": "배송 준비", "timestamp": "2025-01-15T11:00:00Z"},
                {"status": "배송 중", "timestamp": "2025-01-15T13:00:00Z"},
                {"status": "배송 완료", "timestamp": "2025-01-15T16:00:00Z"}
            ]
        }
    ]
    return jsonify({"tracking": tracking})

@app.route('/api/carriers')
def get_carriers():
    carriers = [
        {
            "id": 1,
            "name": "CJ대한통운",
            "code": "CJ",
            "enabled": True,
            "rating": 4.5
        },
        {
            "id": 2,
            "name": "한진택배",
            "code": "HJ",
            "enabled": True,
            "rating": 4.3
        },
        {
            "id": 3,
            "name": "로젠택배",
            "code": "LZ",
            "enabled": True,
            "rating": 4.2
        }
    ]
    return jsonify({"carriers": carriers})

@app.route('/api/returns')
def get_returns():
    returns = [
        {
            "id": 1,
            "order_id": 1,
            "book_title": "파이썬 프로그래밍",
            "user_name": "김철수",
            "reason": "책 상태 불량",
            "status": "processing",
            "created_at": "2025-01-15T17:30:00Z"
        },
        {
            "id": 2,
            "order_id": 3,
            "book_title": "웹 개발 완전정복",
            "user_name": "박민수",
            "reason": "잘못된 도서 배송",
            "status": "completed",
            "created_at": "2025-01-14T15:20:00Z"
        }
    ]
    return jsonify({"returns": returns})

@app.route('/api/analytics')
def get_shipping_analytics():
    analytics = {
        "total_orders": 156,
        "delivered_orders": 142,
        "in_transit_orders": 8,
        "pending_orders": 6,
        "avg_delivery_time": 2.3,
        "customer_satisfaction": 4.6
    }
    return jsonify(analytics)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 9080))
    app.run(host='0.0.0.0', port=port, debug=False) 