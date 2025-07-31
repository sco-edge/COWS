#!/usr/bin/env python3
"""
Payment Service - 결제 시스템
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

REQUEST_COUNT = Counter('payment_service_requests_total', 'Total requests to payment service')
REQUEST_LATENCY = Histogram('payment_service_request_duration_seconds', 'Request latency')

payments_db = [
    {
        "id": "pay1",
        "order_id": "order1",
        "amount": 69.97,
        "payment_method": "credit_card",
        "status": "completed",
        "created_at": "2025-01-15T10:30:00Z",
        "card_last4": "1234"
    },
    {
        "id": "pay2",
        "order_id": "order2",
        "amount": 15.99,
        "payment_method": "paypal",
        "status": "completed",
        "created_at": "2025-01-14T14:20:00Z",
        "card_last4": "5678"
    }
]

# HTML Template with Modern Corporate Style
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Payment Service - 결제 관리 시스템</title>
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
        
        .payment-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 24px;
            margin-bottom: 40px;
        }
        
        .payment-card {
            background: #ffffff;
            border: 1px solid #e0e0e0;
            border-radius: 12px;
            padding: 24px;
            transition: all 0.3s;
        }
        
        .payment-card:hover {
            box-shadow: 0 8px 24px rgba(0,0,0,0.1);
            transform: translateY(-4px);
        }
        
        .payment-card h3 {
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 12px;
            color: #000000;
        }
        
        .payment-card p {
            color: #666666;
            margin-bottom: 16px;
            line-height: 1.5;
        }
        
        .payment-amount {
            font-size: 24px;
            font-weight: 700;
            color: #f2c94c;
            margin-bottom: 8px;
        }
        
        .payment-status {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
            margin-bottom: 12px;
        }
        
        .status-completed {
            background: #e8f5e8;
            color: #388e3c;
        }
        
        .status-pending {
            background: #fff3e0;
            color: #f57c00;
        }
        
        .status-failed {
            background: #ffebee;
            color: #d32f2f;
        }
        
        .payment-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 16px;
            padding-top: 16px;
            border-top: 1px solid #f0f0f0;
        }
        
        .payment-date {
            font-size: 12px;
            color: #666666;
        }
        
        .payment-method {
            font-size: 12px;
            color: #666666;
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
            <a href="/" class="logo">payment</a>
            <ul class="nav-menu">
                <li><a href="/" class="active">결제</a></li>
                <li><a href="/api/transactions">거래내역</a></li>
                <li><a href="/api/methods">결제수단</a></li>
                <li><a href="/api/refunds">환불</a></li>
                <li><a href="/api/reports">리포트</a></li>
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
                <h1 class="hero-title">안전한 결제 시스템</h1>
                <p class="hero-subtitle">다양한 결제 수단을 지원하는 안전하고 편리한 결제 시스템입니다. 도서 대출료, 연체료, 예약료 등 모든 결제를 한 곳에서 관리하세요.</p>
                <a href="#payments" class="hero-button">
                    결제하기
                    <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                        <path fill-rule="evenodd" d="M1 8a.5.5 0 0 1 .5-.5h11.793l-3.147-3.146a.5.5 0 0 1 .708-.708l4 4a.5.5 0 0 1 0 .708l-4 4a.5.5 0 0 1-.708-.708L13.293 8.5H1.5A.5.5 0 0 1 1 8z"/>
                    </svg>
                </a>
            </div>
            <div class="hero-cards">
                <div class="hero-card">
                    <h3>다양한 결제수단</h3>
                    <p>신용카드, 계좌이체, 간편결제 지원</p>
                </div>
                <div class="hero-card white">
                    <h3>실시간 처리</h3>
                    <p>즉시 결제 처리와 실시간 확인</p>
                </div>
                <div class="hero-card">
                    <h3>안전한 보안</h3>
                    <p>SSL 암호화와 PCI DSS 인증</p>
                </div>
            </div>
        </section>

        <!-- Payment Transactions Section -->
        <section class="content-section">
            <h2 class="section-title">최근 결제 내역</h2>
            <div class="payment-grid">
                <div class="payment-card">
                    <h3>도서 대출료</h3>
                    <div class="payment-amount">₩3,000</div>
                    <div class="payment-status status-completed">완료</div>
                    <p>파이썬 프로그래밍 도서 대출료</p>
                    <div class="payment-meta">
                        <div class="payment-date">2025-01-15 14:30</div>
                        <div class="payment-method">신용카드</div>
                    </div>
                </div>
                
                <div class="payment-card">
                    <h3>연체료</h3>
                    <div class="payment-amount">₩1,500</div>
                    <div class="payment-status status-completed">완료</div>
                    <p>웹 개발 완전정복 도서 연체료</p>
                    <div class="payment-meta">
                        <div class="payment-date">2025-01-14 09:15</div>
                        <div class="payment-method">계좌이체</div>
                    </div>
                </div>
                
                <div class="payment-card">
                    <h3>예약료</h3>
                    <div class="payment-amount">₩1,000</div>
                    <div class="payment-status status-pending">처리중</div>
                    <p>머신러닝 입문 도서 예약료</p>
                    <div class="payment-meta">
                        <div class="payment-date">2025-01-15 16:45</div>
                        <div class="payment-method">간편결제</div>
                    </div>
                </div>
                
                <div class="payment-card">
                    <h3>도서 대출료</h3>
                    <div class="payment-amount">₩3,000</div>
                    <div class="payment-status status-completed">완료</div>
                    <p>데이터베이스 설계 도서 대출료</p>
                    <div class="payment-meta">
                        <div class="payment-date">2025-01-13 11:20</div>
                        <div class="payment-method">신용카드</div>
                    </div>
                </div>
                
                <div class="payment-card">
                    <h3>연체료</h3>
                    <div class="payment-amount">₩2,000</div>
                    <div class="payment-status status-failed">실패</div>
                    <p>알고리즘 문제해결 도서 연체료</p>
                    <div class="payment-meta">
                        <div class="payment-date">2025-01-12 13:10</div>
                        <div class="payment-method">신용카드</div>
                    </div>
                </div>
                
                <div class="payment-card">
                    <h3>도서 대출료</h3>
                    <div class="payment-amount">₩3,000</div>
                    <div class="payment-status status-completed">완료</div>
                    <p>React 완전정복 도서 대출료</p>
                    <div class="payment-meta">
                        <div class="payment-date">2025-01-11 10:30</div>
                        <div class="payment-method">간편결제</div>
                    </div>
                </div>
            </div>
        </section>
    </main>

    <!-- Footer -->
    <footer class="footer">
        <div class="footer-content">
            <div class="footer-links">
                <a href="/api/transactions">거래내역</a>
                <a href="/api/methods">결제수단</a>
                <a href="/api/refunds">환불</a>
                <a href="/api/reports">리포트</a>
                <a href="/api/security">보안</a>
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
    return jsonify({"status": "healthy", "service": "payment-service"})

@app.route('/metrics', methods=['GET'])
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

@app.route('/payments', methods=['GET'])
@REQUEST_LATENCY.time()
def get_payments():
    REQUEST_COUNT.inc()
    logger.info("Getting all payments")
    return jsonify(payments_db)

@app.route('/payments/<payment_id>', methods=['GET'])
@REQUEST_LATENCY.time()
def get_payment(payment_id):
    REQUEST_COUNT.inc()
    logger.info(f"Getting payment {payment_id}")
    
    for payment in payments_db:
        if payment['id'] == payment_id:
            return jsonify(payment)
    
    return jsonify({"error": "Payment not found"}), 404

@app.route('/payments', methods=['POST'])
@REQUEST_LATENCY.time()
def create_payment():
    REQUEST_COUNT.inc()
    data = request.get_json()
    
    new_payment = {
        "id": f"pay{len(payments_db) + 1}",
        "order_id": data.get('order_id'),
        "amount": data.get('amount', 0),
        "payment_method": data.get('payment_method', 'credit_card'),
        "status": "completed",
        "created_at": datetime.now().isoformat() + "Z",
        "card_last4": "1234"
    }
    
    payments_db.append(new_payment)
    logger.info(f"Created new payment: {new_payment['id']}")
    
    return jsonify(new_payment), 201

@app.route('/api/transactions')
def get_transactions():
    transactions = [
        {
            "id": 1,
            "type": "loan_fee",
            "amount": 3000,
            "description": "파이썬 프로그래밍 도서 대출료",
            "status": "completed",
            "method": "credit_card",
            "timestamp": "2025-01-15T14:30:00Z"
        },
        {
            "id": 2,
            "type": "late_fee",
            "amount": 1500,
            "description": "웹 개발 완전정복 도서 연체료",
            "status": "completed",
            "method": "bank_transfer",
            "timestamp": "2025-01-14T09:15:00Z"
        },
        {
            "id": 3,
            "type": "reservation_fee",
            "amount": 1000,
            "description": "머신러닝 입문 도서 예약료",
            "status": "pending",
            "method": "simple_pay",
            "timestamp": "2025-01-15T16:45:00Z"
        }
    ]
    return jsonify({"transactions": transactions})

@app.route('/api/methods')
def get_payment_methods():
    methods = [
        {
            "id": 1,
            "name": "신용카드",
            "type": "credit_card",
            "enabled": True,
            "supported_cards": ["Visa", "MasterCard", "American Express"]
        },
        {
            "id": 2,
            "name": "계좌이체",
            "type": "bank_transfer",
            "enabled": True,
            "supported_banks": ["KB국민", "신한", "우리", "하나"]
        },
        {
            "id": 3,
            "name": "간편결제",
            "type": "simple_pay",
            "enabled": True,
            "supported_providers": ["신용카드", "계좌이체", "간편결제"]
        }
    ]
    return jsonify({"methods": methods})

@app.route('/api/refunds')
def get_refunds():
    refunds = [
        {
            "id": 1,
            "transaction_id": 5,
            "amount": 2000,
            "reason": "결제 오류",
            "status": "completed",
            "timestamp": "2025-01-12T15:30:00Z"
        },
        {
            "id": 2,
            "transaction_id": 3,
            "amount": 1000,
            "reason": "도서 입고 지연",
            "status": "pending",
            "timestamp": "2025-01-15T17:00:00Z"
        }
    ]
    return jsonify({"refunds": refunds})

@app.route('/api/reports')
def get_payment_reports():
    reports = [
        {
            "id": 1,
            "title": "월간 결제 리포트",
            "period": "2025-01",
            "total_amount": 12500,
            "transaction_count": 8,
            "status": "completed"
        },
        {
            "id": 2,
            "title": "결제 수단별 통계",
            "period": "2025-01",
            "credit_card": 60,
            "bank_transfer": 25,
            "simple_pay": 15,
            "status": "completed"
        }
    ]
    return jsonify({"reports": reports})

@app.route('/api/security')
def get_security_info():
    security = {
        "ssl_enabled": True,
        "pci_dss_compliant": True,
        "encryption": "AES-256",
        "fraud_detection": True,
        "last_audit": "2025-01-01"
    }
    return jsonify(security)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 9080))
    app.run(host='0.0.0.0', port=port, debug=False) 