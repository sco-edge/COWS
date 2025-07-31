#!/usr/bin/env python3
"""
Order Service - 주문 관리 서비스
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

REQUEST_COUNT = Counter('order_service_requests_total', 'Total requests to order service')
REQUEST_LATENCY = Histogram('order_service_request_duration_seconds', 'Request latency')

orders_db = [
    {
        "id": "order1",
        "user_id": "user1",
        "books": [
            {"title": "The Great Gatsby", "quantity": 1, "price": 29.99},
            {"title": "To Kill a Mockingbird", "quantity": 2, "price": 19.99}
        ],
        "total_amount": 69.97,
        "status": "processing",
        "created_at": "2025-01-15T10:30:00Z",
        "estimated_delivery": "2025-01-20"
    },
    {
        "id": "order2",
        "user_id": "user2",
        "books": [
            {"title": "1984", "quantity": 1, "price": 15.99}
        ],
        "total_amount": 15.99,
        "status": "shipped",
        "created_at": "2025-01-14T14:20:00Z",
        "estimated_delivery": "2025-01-18"
    }
]

# HTML Template with Modern Corporate Style
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Order Service - 주문 관리 시스템</title>
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
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .logo-icon {
            width: 32px;
            height: 32px;
            background: linear-gradient(135deg, #f2c94c 0%, #f2994a 100%);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 18px;
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
        main {
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
        }
        
        /* Hero Section */
        .hero-section {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 60px;
            margin-bottom: 80px;
            align-items: center;
        }
        
        .hero-content {
            max-width: 500px;
        }
        
        .hero-title {
            font-size: 48px;
            font-weight: 700;
            margin-bottom: 20px;
            background: linear-gradient(135deg, #f2c94c 0%, #f2994a 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .hero-subtitle {
            font-size: 18px;
            color: #666;
            margin-bottom: 30px;
            line-height: 1.6;
        }
        
        .hero-button {
            display: inline-flex;
            align-items: center;
            gap: 10px;
            background: linear-gradient(135deg, #f2c94c 0%, #f2994a 100%);
            color: white;
            padding: 15px 30px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            transition: transform 0.3s;
        }
        
        .hero-button:hover {
            transform: translateY(-2px);
        }
        
        .hero-stats {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
        }
        
        .stat-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            border: 1px solid #e9ecef;
        }
        
        .stat-number {
            font-size: 32px;
            font-weight: 700;
            color: #f2c94c;
            margin-bottom: 5px;
        }
        
        .stat-label {
            font-size: 14px;
            color: #666;
            font-weight: 500;
        }
        
        /* Analytics Section */
        .analytics-section {
            background: #f8f9fa;
            border-radius: 16px;
            padding: 40px;
            margin-bottom: 80px;
        }
        
        .section-title {
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 40px;
            text-align: center;
            color: #333;
        }
        
        .analytics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 30px;
        }
        
        .analytics-card {
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
        }
        
        .analytics-header {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 20px;
        }
        
        .analytics-icon {
            width: 40px;
            height: 40px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            color: white;
        }
        
        .icon-orders { background: linear-gradient(135deg, #f2c94c 0%, #f2994a 100%); }
        .icon-pending { background: linear-gradient(135deg, #feca57 0%, #ff9ff3 100%); }
        .icon-completed { background: linear-gradient(135deg, #48dbfb 0%, #0abde3 100%); }
        .icon-revenue { background: linear-gradient(135deg, #1dd1a1 0%, #10ac84 100%); }
        
        .analytics-title {
            font-size: 16px;
            font-weight: 600;
            color: #333;
        }
        
        .analytics-value {
            font-size: 28px;
            font-weight: 700;
            color: #f2c94c;
            margin-bottom: 5px;
        }
        
        .analytics-change {
            font-size: 14px;
            color: #28a745;
            font-weight: 500;
        }
        
        /* Orders Section */
        .content-section {
            margin-bottom: 80px;
        }
        
        .order-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 30px;
        }
        
        .order-card {
            background: white;
            border-radius: 16px;
            padding: 30px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
            border: 1px solid #f0f0f0;
            transition: transform 0.3s, box-shadow 0.3s;
            position: relative;
            overflow: hidden;
        }
        
        .order-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(135deg, #f2c94c 0%, #f2994a 100%);
        }
        
        .order-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
        }
        
        .order-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        
        .order-id {
            font-size: 18px;
            font-weight: 600;
            color: #333;
        }
        
        .order-status {
            padding: 6px 16px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
        }
        
        .status-pending {
            background: #fff3cd;
            color: #856404;
        }
        
        .status-processing {
            background: #cce5ff;
            color: #004085;
        }
        
        .status-completed {
            background: #d4edda;
            color: #155724;
        }
        
        .status-cancelled {
            background: #f8d7da;
            color: #721c24;
        }
        
        .order-details {
            margin-bottom: 20px;
        }
        
        .order-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 0;
            border-bottom: 1px solid #f0f0f0;
        }
        
        .order-item:last-child {
            border-bottom: none;
        }
        
        .item-info {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .item-icon {
            width: 40px;
            height: 40px;
            border-radius: 8px;
            background: linear-gradient(135deg, #f2c94c 0%, #f2994a 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 16px;
        }
        
        .item-details h4 {
            font-size: 16px;
            font-weight: 600;
            color: #333;
            margin-bottom: 4px;
        }
        
        .item-details p {
            font-size: 14px;
            color: #666;
        }
        
        .item-price {
            font-size: 18px;
            font-weight: 700;
            color: #f2c94c;
        }
        
        .order-footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #f0f0f0;
        }
        
        .order-total {
            font-size: 20px;
            font-weight: 700;
            color: #333;
        }
        
        .order-date {
            font-size: 14px;
            color: #666;
        }
        
        /* Footer */
        .footer {
            background: #f8f9fa;
            padding: 40px 0;
            margin-top: 80px;
            text-align: center;
        }
        
        .footer-content {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }
        
        .footer-text {
            color: #666;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <!-- Header -->
    <header class="header">
        <div class="nav-container">
            <a href="#" class="logo">
                <div class="logo-icon">📦</div>
                Order Service
            </a>
            <nav>
                <ul class="nav-menu">
                    <li><a href="#" class="active">대시보드</a></li>
                    <li><a href="#">주문 관리</a></li>
                    <li><a href="#">배송 추적</a></li>
                    <li><a href="#">반품 관리</a></li>
                </ul>
            </nav>
            <div class="utility-icons">
                <svg class="icon" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-6-3a2 2 0 11-4 0 2 2 0 014 0zm-2 4a5 5 0 00-4.546 2.916A5.986 5.986 0 0010 16a5.986 5.986 0 004.546-2.084A5 5 0 0010 11z" clip-rule="evenodd"/>
                </svg>
                <svg class="icon" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M10 2a6 6 0 00-6 6v3.586l-.707.707A1 1 0 004 14h12a1 1 0 00.707-1.707L16 11.586V8a6 6 0 00-6-6zM10 18a3 3 0 01-3-3h6a3 3 0 01-3 3z"/>
                </svg>
            </div>
        </div>
    </header>

    <main>
        <!-- Hero Section -->
        <section class="hero-section">
            <div class="hero-content">
                <h1 class="hero-title">주문 관리 시스템</h1>
                <p class="hero-subtitle">도서 주문 처리, 배송 추적, 결제 관리를 통합적으로 제공하는 스마트 주문 관리 시스템입니다.</p>
                <a href="#orders" class="hero-button">
                    주문 관리
                    <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                        <path fill-rule="evenodd" d="M1 8a.5.5 0 0 1 .5-.5h11.793l-3.147-3.146a.5.5 0 0 1 .708-.708l4 4a.5.5 0 0 1 0 .708l-4 4a.5.5 0 0 1-.708-.708L13.293 8.5H1.5A.5.5 0 0 1 1 8z"/>
                    </svg>
                </a>
            </div>
            <div class="hero-stats">
                <div class="stat-card">
                    <div class="stat-number">2,847</div>
                    <div class="stat-label">총 주문</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">94%</div>
                    <div class="stat-label">완료율</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">89</div>
                    <div class="stat-label">오늘 주문</div>
                </div>
            </div>
        </section>

        <!-- Analytics Section -->
        <section class="analytics-section">
            <h2 class="section-title">주문 통계</h2>
            <div class="analytics-grid">
                <div class="analytics-card">
                    <div class="analytics-header">
                        <div class="analytics-icon icon-orders">📦</div>
                        <div class="analytics-title">총 주문 수</div>
                    </div>
                    <div class="analytics-value">2,847</div>
                    <div class="analytics-change">+15% 이번 달</div>
                </div>
                
                <div class="analytics-card">
                    <div class="analytics-header">
                        <div class="analytics-icon icon-pending">⏳</div>
                        <div class="analytics-title">대기 중</div>
                    </div>
                    <div class="analytics-value">156</div>
                    <div class="analytics-change">-8% 이번 주</div>
                </div>
                
                <div class="analytics-card">
                    <div class="analytics-header">
                        <div class="analytics-icon icon-completed">✅</div>
                        <div class="analytics-title">완료된 주문</div>
                    </div>
                    <div class="analytics-value">2,691</div>
                    <div class="analytics-change">+12% 이번 달</div>
                </div>
                
                <div class="analytics-card">
                    <div class="analytics-header">
                        <div class="analytics-icon icon-revenue">💰</div>
                        <div class="analytics-title">총 매출</div>
                    </div>
                    <div class="analytics-value">₩45.2M</div>
                    <div class="analytics-change">+18% 이번 달</div>
                </div>
            </div>
        </section>

        <!-- Orders Section -->
        <section class="content-section">
            <h2 class="section-title">최근 주문</h2>
            <div class="order-grid">
                <div class="order-card">
                    <div class="order-header">
                                                    <div class="order-id">#ORD-2025-001</div>
                        <div class="order-status status-completed">완료</div>
                    </div>
                    <div class="order-details">
                        <div class="order-item">
                            <div class="item-info">
                                <div class="item-icon">📚</div>
                                <div class="item-details">
                                    <h4>파이썬 프로그래밍</h4>
                                    <p>컴퓨터/프로그래밍</p>
                                </div>
                            </div>
                            <div class="item-price">₩25,000</div>
                        </div>
                        <div class="order-item">
                            <div class="item-info">
                                <div class="item-icon">📚</div>
                                <div class="item-details">
                                    <h4>데이터 사이언스 입문</h4>
                                    <p>컴퓨터/데이터</p>
                                </div>
                            </div>
                            <div class="item-price">₩32,000</div>
                        </div>
                    </div>
                    <div class="order-footer">
                        <div class="order-total">총액: ₩57,000</div>
                                                    <div class="order-date">2025-01-15</div>
                    </div>
                </div>
                
                <div class="order-card">
                    <div class="order-header">
                                                    <div class="order-id">#ORD-2025-002</div>
                        <div class="order-status status-processing">처리중</div>
                    </div>
                    <div class="order-details">
                        <div class="order-item">
                            <div class="item-info">
                                <div class="item-icon">📚</div>
                                <div class="item-details">
                                    <h4>머신러닝 기초</h4>
                                    <p>컴퓨터/인공지능</p>
                                </div>
                            </div>
                            <div class="item-price">₩28,000</div>
                        </div>
                    </div>
                    <div class="order-footer">
                        <div class="order-total">총액: ₩28,000</div>
                                                    <div class="order-date">2025-01-16</div>
                    </div>
                </div>
                
                <div class="order-card">
                    <div class="order-header">
                                                    <div class="order-id">#ORD-2025-003</div>
                        <div class="order-status status-pending">대기중</div>
                    </div>
                    <div class="order-details">
                        <div class="order-item">
                            <div class="item-info">
                                <div class="item-icon">📚</div>
                                <div class="item-details">
                                    <h4>웹 개발 완전 가이드</h4>
                                    <p>컴퓨터/웹개발</p>
                                </div>
                            </div>
                            <div class="item-price">₩35,000</div>
                        </div>
                        <div class="order-item">
                            <div class="item-info">
                                <div class="item-icon">📚</div>
                                <div class="item-details">
                                    <h4>React 실전 프로젝트</h4>
                                    <p>컴퓨터/프론트엔드</p>
                                </div>
                            </div>
                            <div class="item-price">₩42,000</div>
                        </div>
                    </div>
                    <div class="order-footer">
                        <div class="order-total">총액: ₩77,000</div>
                                                    <div class="order-date">2025-01-17</div>
                    </div>
                </div>
                
                <div class="order-card">
                    <div class="order-header">
                                                    <div class="order-id">#ORD-2025-004</div>
                        <div class="order-status status-cancelled">취소됨</div>
                    </div>
                    <div class="order-details">
                        <div class="order-item">
                            <div class="item-info">
                                <div class="item-icon">📚</div>
                                <div class="item-details">
                                    <h4>클라우드 아키텍처</h4>
                                    <p>컴퓨터/클라우드</p>
                                </div>
                            </div>
                            <div class="item-price">₩38,000</div>
                        </div>
                    </div>
                    <div class="order-footer">
                        <div class="order-total">총액: ₩38,000</div>
                                                    <div class="order-date">2025-01-18</div>
                    </div>
                </div>
                
                <div class="order-card">
                    <div class="order-header">
                                                    <div class="order-id">#ORD-2025-005</div>
                        <div class="order-status status-completed">완료</div>
                    </div>
                    <div class="order-details">
                        <div class="order-item">
                            <div class="item-info">
                                <div class="item-icon">📚</div>
                                <div class="item-details">
                                    <h4>DevOps 핸드북</h4>
                                    <p>컴퓨터/DevOps</p>
                                </div>
                            </div>
                            <div class="item-price">₩45,000</div>
                        </div>
                        <div class="order-item">
                            <div class="item-info">
                                <div class="item-icon">📚</div>
                                <div class="item-details">
                                    <h4>마이크로서비스 패턴</h4>
                                    <p>컴퓨터/아키텍처</p>
                                </div>
                            </div>
                            <div class="item-price">₩52,000</div>
                        </div>
                    </div>
                    <div class="order-footer">
                        <div class="order-total">총액: ₩97,000</div>
                                                    <div class="order-date">2025-01-19</div>
                    </div>
                </div>
                
                <div class="order-card">
                    <div class="order-header">
                                                    <div class="order-id">#ORD-2025-006</div>
                        <div class="order-status status-processing">처리중</div>
                    </div>
                    <div class="order-details">
                        <div class="order-item">
                            <div class="item-info">
                                <div class="item-icon">📚</div>
                                <div class="item-details">
                                    <h4>블록체인 기술</h4>
                                    <p>컴퓨터/블록체인</p>
                                </div>
                            </div>
                            <div class="item-price">₩33,000</div>
                        </div>
                    </div>
                    <div class="order-footer">
                        <div class="order-total">총액: ₩33,000</div>
                                                    <div class="order-date">2025-01-20</div>
                    </div>
                </div>
            </div>
        </section>
    </main>

    <!-- Footer -->
    <footer class="footer">
        <div class="footer-content">
                            <p class="footer-text">© 2025 Korea University NetLab JunhoBae. All rights reserved.</p>
        </div>
    </footer>
</body>
</html>
'''

@app.route('/')
def index():
    return HTML_TEMPLATE

@app.route('/api/orders')
def get_orders():
    orders = [
        {
            "id": 1,
            "book_title": "파이썬 프로그래밍",
            "user_name": "김철수",
            "user_address": "서울시 강남구",
            "order_number": "ORD-2025-001",
            "status": "confirmed",
            "total": 3000,
            "created_at": "2025-01-15T10:30:00Z"
        },
        {
            "id": 2,
            "book_title": "머신러닝 입문",
            "user_name": "이영희",
            "user_address": "서울시 서초구",
            "order_number": "ORD-2025-002",
            "status": "processing",
            "total": 3000,
            "created_at": "2025-01-15T11:15:00Z"
        },
        {
            "id": 3,
            "book_title": "웹 개발 완전정복",
            "user_name": "박민수",
            "user_address": "서울시 마포구",
            "order_number": "ORD-2025-003",
            "status": "shipped",
            "total": 3000,
            "created_at": "2025-01-15T14:20:00Z"
        }
    ]
    return jsonify({"orders": orders})

@app.route('/api/status')
def get_order_status():
    statuses = [
        {
            "order_id": 1,
            "status": "confirmed",
            "timestamp": "2025-01-15T10:30:00Z",
            "description": "주문이 확정되었습니다"
        },
        {
            "order_id": 2,
            "status": "processing",
            "timestamp": "2025-01-15T11:15:00Z",
            "description": "주문이 처리 중입니다"
        },
        {
            "order_id": 3,
            "status": "shipped",
            "timestamp": "2025-01-15T14:20:00Z",
            "description": "배송이 시작되었습니다"
        }
    ]
    return jsonify({"statuses": statuses})

@app.route('/api/tracking')
def get_order_tracking():
    tracking = [
        {
            "order_id": 1,
            "tracking_number": "TRK-2025-001",
            "carrier": "CJ대한통운",
            "estimated_delivery": "2025-01-16",
            "current_location": "서울시 강남구"
        },
        {
            "order_id": 2,
            "tracking_number": "TRK-2025-002",
            "carrier": "한진택배",
            "estimated_delivery": "2025-01-17",
            "current_location": "서울시 서초구"
        }
    ]
    return jsonify({"tracking": tracking})

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
        }
    ]
    return jsonify({"returns": returns})

@app.route('/api/analytics')
def get_order_analytics():
    analytics = {
        "total_orders": 156,
        "confirmed_orders": 142,
        "processing_orders": 8,
        "shipped_orders": 6,
        "avg_order_value": 3000,
        "customer_satisfaction": 4.6
    }
    return jsonify(analytics)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9080, debug=True) 