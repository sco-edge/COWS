#!/usr/bin/env python3
"""
Notification Service - 알림 서비스
"""
import os
import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import requests
import random
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

REQUEST_COUNT = Counter('notification_service_requests_total', 'Total requests to notification service')
REQUEST_LATENCY = Histogram('notification_service_request_duration_seconds', 'Request latency')

notifications_db = [
    {
        "id": "notif1",
        "user_id": "user1",
        "type": "order_confirmation",
        "title": "주문 확인",
        "message": "주문 #order1이 성공적으로 처리되었습니다.",
        "status": "sent",
        "created_at": "2025-01-15T10:30:00Z",
        "channel": "email"
    },
    {
        "id": "notif2",
        "user_id": "user2",
        "type": "shipping_update",
        "title": "배송 업데이트",
        "message": "주문 #order2가 배송 중입니다.",
        "status": "sent",
        "created_at": "2025-01-14T14:20:00Z",
        "channel": "sms"
    }
]

# HTML Template with Modern Corporate Style
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Notification Service - 알림 관리 시스템</title>
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
        
        .notification-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 24px;
            margin-bottom: 40px;
        }
        
        .notification-card {
            background: #ffffff;
            border: 1px solid #e0e0e0;
            border-radius: 12px;
            padding: 24px;
            transition: all 0.3s;
            position: relative;
        }
        
        .notification-card:hover {
            box-shadow: 0 8px 24px rgba(0,0,0,0.1);
            transform: translateY(-4px);
        }
        
        .notification-card.unread {
            border-left: 4px solid #f2c94c;
        }
        
        .notification-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 12px;
        }
        
        .notification-title {
            font-size: 18px;
            font-weight: 600;
            color: #000000;
            margin-bottom: 8px;
        }
        
        .notification-time {
            font-size: 12px;
            color: #666666;
        }
        
        .notification-content {
            color: #666666;
            line-height: 1.5;
            margin-bottom: 16px;
        }
        
        .notification-type {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
            margin-bottom: 12px;
        }
        
        .type-info {
            background: #e3f2fd;
            color: #1976d2;
        }
        
        .type-warning {
            background: #fff3e0;
            color: #f57c00;
        }
        
        .type-success {
            background: #e8f5e8;
            color: #388e3c;
        }
        
        .type-error {
            background: #ffebee;
            color: #d32f2f;
        }
        
        .notification-actions {
            display: flex;
            gap: 12px;
            margin-top: 16px;
        }
        
        .action-btn {
            padding: 8px 16px;
            border: 1px solid #e0e0e0;
            border-radius: 6px;
            background: #ffffff;
            color: #666666;
            text-decoration: none;
            font-size: 12px;
            transition: all 0.3s;
        }
        
        .action-btn:hover {
            background: #f2c94c;
            color: #000000;
            border-color: #f2c94c;
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
            <a href="/" class="logo">notification</a>
            <ul class="nav-menu">
                <li><a href="/" class="active">알림</a></li>
                <li><a href="/api/notifications">알림 목록</a></li>
                <li><a href="/api/settings">설정</a></li>
                <li><a href="/api/templates">템플릿</a></li>
                <li><a href="/api/history">히스토리</a></li>
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
                <h1 class="hero-title">스마트 알림 시스템</h1>
                <p class="hero-subtitle">실시간 알림과 개인화된 메시지로 사용자 경험을 향상시킵니다. 도서 대출, 반납, 예약 등 모든 중요한 이벤트를 놓치지 마세요.</p>
                <a href="#notifications" class="hero-button">
                    알림 설정하기
                    <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                        <path fill-rule="evenodd" d="M1 8a.5.5 0 0 1 .5-.5h11.793l-3.147-3.146a.5.5 0 0 1 .708-.708l4 4a.5.5 0 0 1 0 .708l-4 4a.5.5 0 0 1-.708-.708L13.293 8.5H1.5A.5.5 0 0 1 1 8z"/>
                    </svg>
                </a>
            </div>
            <div class="hero-cards">
                <div class="hero-card">
                    <h3>실시간 알림</h3>
                    <p>도서 대출/반납 상태를 즉시 알려드립니다</p>
                </div>
                <div class="hero-card white">
                    <h3>개인화 메시지</h3>
                    <p>사용자 취향에 맞는 맞춤형 알림</p>
                </div>
                <div class="hero-card">
                    <h3>다중 채널</h3>
                    <p>이메일, SMS, 푸시 알림 지원</p>
                </div>
            </div>
        </section>

        <!-- Notifications Section -->
        <section class="content-section">
            <h2 class="section-title">최근 알림</h2>
            <div class="notification-grid">
                <div class="notification-card unread">
                    <div class="notification-header">
                        <div>
                            <div class="notification-title">도서 대출 완료</div>
                            <div class="notification-time">2분 전</div>
                        </div>
                    </div>
                    <div class="notification-type type-success">대출</div>
                    <div class="notification-content">
                        "파이썬 프로그래밍" 도서가 성공적으로 대출되었습니다. 반납 예정일은 2025년 2월 15일입니다.
                    </div>
                    <div class="notification-actions">
                        <a href="#" class="action-btn">상세보기</a>
                        <a href="#" class="action-btn">읽음 처리</a>
                    </div>
                </div>
                
                <div class="notification-card">
                    <div class="notification-header">
                        <div>
                            <div class="notification-title">예약 도서 입고</div>
                            <div class="notification-time">1시간 전</div>
                        </div>
                    </div>
                    <div class="notification-type type-info">예약</div>
                    <div class="notification-content">
                        예약하신 "머신러닝 입문" 도서가 입고되었습니다. 3일 이내에 대출해주세요.
                    </div>
                    <div class="notification-actions">
                        <a href="#" class="action-btn">상세보기</a>
                        <a href="#" class="action-btn">예약 취소</a>
                    </div>
                </div>
                
                <div class="notification-card">
                    <div class="notification-header">
                        <div>
                            <div class="notification-title">반납 예정일 알림</div>
                            <div class="notification-time">3시간 전</div>
                        </div>
                    </div>
                    <div class="notification-type type-warning">반납</div>
                    <div class="notification-content">
                        "웹 개발 완전정복" 도서의 반납 예정일이 2일 남았습니다. 연체를 방지하기 위해 반납해주세요.
                    </div>
                    <div class="notification-actions">
                        <a href="#" class="action-btn">상세보기</a>
                        <a href="#" class="action-btn">연장 신청</a>
                    </div>
                </div>
                
                <div class="notification-card">
                    <div class="notification-header">
                        <div>
                            <div class="notification-title">새로운 도서 알림</div>
                            <div class="notification-time">1일 전</div>
                        </div>
                    </div>
                    <div class="notification-type type-info">신간</div>
                    <div class="notification-content">
                        관심 카테고리 "프로그래밍"에 새로운 도서가 추가되었습니다. "딥러닝 기초"를 확인해보세요.
                    </div>
                    <div class="notification-actions">
                        <a href="#" class="action-btn">상세보기</a>
                        <a href="#" class="action-btn">관심도서 등록</a>
                    </div>
                </div>
                
                <div class="notification-card">
                    <div class="notification-header">
                        <div>
                            <div class="notification-title">시스템 점검 안내</div>
                            <div class="notification-time">2일 전</div>
                        </div>
                    </div>
                    <div class="notification-type type-warning">공지</div>
                    <div class="notification-content">
                        시스템 점검이 2025년 1월 20일 새벽 2시부터 4시까지 진행됩니다. 서비스 이용에 참고하세요.
                    </div>
                    <div class="notification-actions">
                        <a href="#" class="action-btn">상세보기</a>
                        <a href="#" class="action-btn">알림 설정</a>
                    </div>
                </div>
                
                <div class="notification-card">
                    <div class="notification-header">
                        <div>
                            <div class="notification-title">연체 도서 반납</div>
                            <div class="notification-time">3일 전</div>
                        </div>
                    </div>
                    <div class="notification-type type-error">연체</div>
                    <div class="notification-content">
                        "데이터베이스 설계" 도서가 5일 연체되었습니다. 즉시 반납해주시기 바랍니다.
                    </div>
                    <div class="notification-actions">
                        <a href="#" class="action-btn">상세보기</a>
                        <a href="#" class="action-btn">반납 신청</a>
                    </div>
                </div>
            </div>
        </section>
    </main>

    <!-- Footer -->
    <footer class="footer">
        <div class="footer-content">
            <div class="footer-links">
                <a href="/api/notifications">알림 목록</a>
                <a href="/api/settings">설정</a>
                <a href="/api/templates">템플릿</a>
                <a href="/api/history">히스토리</a>
                <a href="/api/channels">채널 관리</a>
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

@app.route('/api/notifications')
def get_notifications():
    notifications = [
        {
            "id": 1,
            "type": "loan",
            "title": "도서 대출 완료",
            "content": "파이썬 프로그래밍 도서가 성공적으로 대출되었습니다.",
            "timestamp": "2025-01-15T10:30:00Z",
            "read": False
        },
        {
            "id": 2,
            "type": "reservation",
            "title": "예약 도서 입고",
            "content": "예약하신 머신러닝 입문 도서가 입고되었습니다.",
            "timestamp": "2025-01-15T09:15:00Z",
            "read": True
        },
        {
            "id": 3,
            "type": "return",
            "title": "반납 예정일 알림",
            "content": "웹 개발 완전정복 도서의 반납 예정일이 2일 남았습니다.",
            "timestamp": "2025-01-15T07:30:00Z",
            "read": True
        }
    ]
    return jsonify({"notifications": notifications})

@app.route('/api/settings')
def get_notification_settings():
    settings = {
        "email_enabled": True,
        "sms_enabled": False,
        "push_enabled": True,
        "loan_notifications": True,
        "return_notifications": True,
        "reservation_notifications": True,
        "new_book_notifications": False,
        "system_notifications": True
    }
    return jsonify(settings)

@app.route('/api/templates')
def get_notification_templates():
    templates = [
        {
            "id": 1,
            "name": "대출 완료 알림",
            "type": "loan",
            "subject": "도서 대출이 완료되었습니다",
            "content": "{{book_title}} 도서가 성공적으로 대출되었습니다."
        },
        {
            "id": 2,
            "name": "반납 예정일 알림",
            "type": "return",
            "subject": "반납 예정일 알림",
            "content": "{{book_title}} 도서의 반납 예정일이 {{days_left}}일 남았습니다."
        },
        {
            "id": 3,
            "name": "예약 도서 입고",
            "type": "reservation",
            "subject": "예약 도서 입고 알림",
            "content": "예약하신 {{book_title}} 도서가 입고되었습니다."
        }
    ]
    return jsonify({"templates": templates})

@app.route('/api/history')
def get_notification_history():
    history = [
        {
            "id": 1,
            "type": "loan",
            "title": "도서 대출 완료",
            "sent_at": "2025-01-15T10:30:00Z",
            "delivery_status": "delivered",
            "channel": "email"
        },
        {
            "id": 2,
            "type": "return",
            "title": "반납 예정일 알림",
            "sent_at": "2025-01-14T15:20:00Z",
            "delivery_status": "delivered",
            "channel": "push"
        },
        {
            "id": 3,
            "type": "reservation",
            "title": "예약 도서 입고",
            "sent_at": "2025-01-13T09:45:00Z",
            "delivery_status": "failed",
            "channel": "sms"
        }
    ]
    return jsonify({"history": history})

@app.route('/api/channels')
def get_notification_channels():
    channels = [
        {
            "id": 1,
            "name": "이메일",
            "type": "email",
            "enabled": True,
            "config": {
                "smtp_server": "smtp.example.com",
                "port": 587,
                "use_tls": True
            }
        },
        {
            "id": 2,
            "name": "SMS",
            "type": "sms",
            "enabled": False,
            "config": {
                "provider": "twilio",
                "api_key": "***"
            }
        },
        {
            "id": 3,
            "name": "푸시 알림",
            "type": "push",
            "enabled": True,
            "config": {
                "firebase_project_id": "library-app",
                "api_key": "***"
            }
        }
    ]
    return jsonify({"channels": channels})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9080, debug=True) 