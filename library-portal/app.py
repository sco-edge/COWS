#!/usr/bin/env python3
"""
Library Portal - 통합 도서관 홈페이지
기존 Bookinfo와 10개 확장 서비스를 연결하는 메인 포털
"""
import os
import json
import logging
from datetime import datetime
from flask import Flask, jsonify, render_template_string
import requests
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# HTML Template with Modern Corporate Style
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Library Portal - 통합 도서관 관리 시스템</title>
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
        
        /* Main Container */
        .main-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 60px 40px;
        }
        
        /* Hero Section */
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
            color: #000000;
            margin-bottom: 24px;
            line-height: 1.2;
        }
        
        .hero-subtitle {
            font-size: 18px;
            color: #666666;
            margin-bottom: 32px;
            line-height: 1.6;
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
            gap: 16px;
        }
        
        .hero-card {
            background: #f2c94c;
            padding: 24px;
            border-radius: 12px;
            color: #000000;
        }
        
        .hero-card.white {
            background: #ffffff;
            border: 1px solid #e0e0e0;
        }
        
        .hero-card h3 {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 8px;
        }
        
        .hero-card p {
            font-size: 14px;
            color: #666666;
        }
        
        /* Content Sections */
        .content-section {
            margin-bottom: 80px;
        }
        
        .section-title {
            font-size: 32px;
            font-weight: 700;
            color: #000000;
            margin-bottom: 40px;
            text-align: center;
        }
        
        .services-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 24px;
            margin-bottom: 40px;
        }
        
        .service-card {
            background: #ffffff;
            border: 1px solid #e0e0e0;
            border-radius: 12px;
            padding: 24px;
            transition: all 0.3s;
            text-decoration: none;
            color: inherit;
            cursor: pointer;
        }
        
        .service-card:hover {
            box-shadow: 0 8px 24px rgba(0,0,0,0.1);
            transform: translateY(-4px);
        }
        
        .service-card h3 {
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 12px;
            color: #000000;
        }
        
        .service-card p {
            color: #666666;
            margin-bottom: 16px;
            line-height: 1.5;
        }
        
        .service-status {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
            margin-bottom: 12px;
        }
        
        .status-online {
            background: #e8f5e8;
            color: #388e3c;
        }
        
        .status-offline {
            background: #ffebee;
            color: #d32f2f;
        }
        
        .service-info {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 16px;
            padding-top: 16px;
            border-top: 1px solid #f0f0f0;
        }
        
        .service-url {
            font-size: 14px;
            color: #666666;
            font-weight: 500;
        }
        
        .service-port {
            font-size: 12px;
            color: #666666;
        }
        
        .service-description {
            font-size: 18px;
            font-weight: 700;
            color: #f2c94c;
            margin-top: 8px;
        }
        
        /* Service Frame */
        .service-frame {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: #ffffff;
            z-index: 2000;
            display: none;
        }
        
        .service-frame iframe {
            width: 100%;
            height: 100%;
            border: none;
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
            <a href="/" class="logo">library</a>
            <ul class="nav-menu">
                <li><a href="/" class="active">홈</a></li>
                <li><a href="/api/services">서비스</a></li>
                <li><a href="/api/status">상태</a></li>
                <li><a href="/api/analytics">분석</a></li>
                <li><a href="/api/settings">설정</a></li>
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
                <h1 class="hero-title">Extended version of Istio's Bookinfo</h1>
                <p class="hero-subtitle">10개의 마이크로서비스로 구성된 현대적인 도서관 관리 시스템입니다. 사용자 관리부터 도서 검색, 주문 처리까지 모든 기능을 통합 관리합니다.</p>
                <a href="#services" class="hero-button">
                    서비스 확인
                    <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                        <path fill-rule="evenodd" d="M1 8a.5.5 0 0 1 .5-.5h11.793l-3.147-3.146a.5.5 0 0 1 .708-.708l4 4a.5.5 0 0 1 0 .708l-4 4a.5.5 0 0 1-.708-.708L13.293 8.5H1.5A.5.5 0 0 1 1 8z"/>
                    </svg>
                </a>
            </div>
            <div class="hero-cards">
                <div class="hero-card">
                    <h3>통합 관리</h3>
                    <p>10개 서비스 통합 관리</p>
                </div>
                <div class="hero-card white">
                    <h3>실시간 모니터링</h3>
                    <p>서비스 상태 실시간 추적</p>
                </div>
                <div class="hero-card">
                    <h3>자동화 시스템</h3>
                    <p>스마트 도서관 관리</p>
                </div>
            </div>
        </section>

        <!-- Services Section -->
        <section class="content-section">
            <h2 class="section-title">서비스 현황</h2>
            <div class="services-grid">
                <div class="service-card" data-url="http://192.168.76.2:30080" data-title="Bookinfo (기존)">
                    <h3>Bookinfo (기존)</h3>
                    <div class="service-status status-online">온라인</div>
                    <p>Istio 기본 Bookinfo 애플리케이션으로 제품 정보, 리뷰, 평점을 제공합니다.</p>
                    <div class="service-description">기본 서비스</div>
                    <div class="service-info">
                        <div class="service-url">bookinfo</div>
                        <div class="service-port">30080</div>
                    </div>
                </div>
                
                <div class="service-card" data-url="http://192.168.76.2:30092" data-title="User Service">
                    <h3>User Service</h3>
                    <div class="service-status status-online">온라인</div>
                    <p>사용자 계정 관리, 권한 제어, 인증 서비스를 제공합니다.</p>
                    <div class="service-description">사용자 관리</div>
                    <div class="service-info">
                        <div class="service-url">user-service</div>
                        <div class="service-port">30092</div>
                    </div>
                </div>
                
                <div class="service-card" data-url="http://192.168.76.2:30093" data-title="Search Service">
                    <h3>Search Service</h3>
                    <div class="service-status status-online">온라인</div>
                    <p>도서 검색, 필터링, 정렬 기능을 제공하는 검색 시스템입니다.</p>
                    <div class="service-description">도서 검색</div>
                    <div class="service-info">
                        <div class="service-url">search-service</div>
                        <div class="service-port">30093</div>
                    </div>
                </div>
                
                <div class="service-card" data-url="http://192.168.76.2:30094" data-title="Analytics Service">
                    <h3>Analytics Service</h3>
                    <div class="service-status status-online">온라인</div>
                    <p>도서관 이용 통계, 트렌드 분석, 데이터 시각화를 제공합니다.</p>
                    <div class="service-description">데이터 분석</div>
                    <div class="service-info">
                        <div class="service-url">analytics-service</div>
                        <div class="service-port">30094</div>
                    </div>
                </div>
                
                <div class="service-card" data-url="http://192.168.76.2:30085" data-title="Order Service">
                    <h3>Order Service</h3>
                    <div class="service-status status-online">온라인</div>
                    <p>도서 대출 주문 처리, 배송 추적, 반품 관리를 담당합니다.</p>
                    <div class="service-description">주문 관리</div>
                    <div class="service-info">
                        <div class="service-url">order-service</div>
                        <div class="service-port">30085</div>
                    </div>
                </div>
                
                <div class="service-card" data-url="http://192.168.76.2:30090" data-title="Catalog Service">
                    <h3>Catalog Service</h3>
                    <div class="service-status status-online">온라인</div>
                    <p>도서 카탈로그 관리, 분류, 메타데이터 관리를 제공합니다.</p>
                    <div class="service-description">카탈로그 관리</div>
                    <div class="service-info">
                        <div class="service-url">catalog-service</div>
                        <div class="service-port">30090</div>
                    </div>
                </div>
                
                <div class="service-card" data-url="http://192.168.76.2:30087" data-title="Payment Service">
                    <h3>Payment Service</h3>
                    <div class="service-status status-online">온라인</div>
                    <p>결제 처리, 환불, 정산 관리를 담당하는 결제 시스템입니다.</p>
                    <div class="service-description">결제 관리</div>
                    <div class="service-info">
                        <div class="service-url">payment-service</div>
                        <div class="service-port">30087</div>
                    </div>
                </div>
                
                <div class="service-card" data-url="http://192.168.76.2:30086" data-title="Inventory Service">
                    <h3>Inventory Service</h3>
                    <div class="service-status status-online">온라인</div>
                    <p>도서 재고 관리, 입고/출고, 재고 추적을 담당합니다.</p>
                    <div class="service-description">재고 관리</div>
                    <div class="service-info">
                        <div class="service-url">inventory-service</div>
                        <div class="service-port">30086</div>
                    </div>
                </div>
                
                <div class="service-card" data-url="http://192.168.76.2:30088" data-title="Notification Service">
                    <h3>Notification Service</h3>
                    <div class="service-status status-online">온라인</div>
                    <p>이메일, SMS, 푸시 알림을 통한 사용자 알림 서비스를 제공합니다.</p>
                    <div class="service-description">알림 서비스</div>
                    <div class="service-info">
                        <div class="service-url">notification-service</div>
                        <div class="service-port">30088</div>
                    </div>
                </div>
                
                <div class="service-card" data-url="http://192.168.76.2:30089" data-title="Recommendation Service">
                    <h3>Recommendation Service</h3>
                    <div class="service-status status-online">온라인</div>
                    <p>개인화된 도서 추천, 협업 필터링, 콘텐츠 기반 추천을 제공합니다.</p>
                    <div class="service-description">추천 시스템</div>
                    <div class="service-info">
                        <div class="service-url">recommendation-service</div>
                        <div class="service-port">30089</div>
                    </div>
                </div>
                
                <div class="service-card" data-url="http://192.168.76.2:30091" data-title="Shipping Service">
                    <h3>Shipping Service</h3>
                    <div class="service-status status-online">온라인</div>
                    <p>배송 관리, 택배 추적, 배송 상태 관리를 담당합니다.</p>
                    <div class="service-description">배송 관리</div>
                    <div class="service-info">
                        <div class="service-url">shipping-service</div>
                        <div class="service-port">30091</div>
                    </div>
                </div>
            </div>
        </section>
    </main>

    <!-- Service Frame -->
    <div class="service-frame" id="serviceFrame">
        <iframe id="serviceIframe" src=""></iframe>
    </div>

    <!-- Footer -->
    <footer class="footer">
        <div class="footer-content">
            <div class="footer-links">
                <a href="/api/services">서비스 목록</a>
                <a href="/api/status">상태 확인</a>
                <a href="/api/analytics">분석</a>
                <a href="/api/settings">설정</a>
                <a href="/api/monitoring">모니터링</a>
            </div>
            <div class="copyright">
                © Korea University NetLab JunhoBae. All rights reserved.
            </div>
        </div>
    </footer>

    <script>
        // Service card click handler
        document.querySelectorAll('.service-card').forEach(card => {
            card.addEventListener('click', function() {
                const url = this.getAttribute('data-url');
                const title = this.getAttribute('data-title');
                
                // Add to browser history
                window.history.pushState({url: url, title: title}, title, '?service=' + encodeURIComponent(title));
                
                // Show service frame
                document.getElementById('serviceFrame').style.display = 'block';
                
                // Load service in iframe
                document.getElementById('serviceIframe').src = url;
                
                // Update page title
                document.title = title + ' - Library Portal';
            });
        });
        
        // Browser back button handler
        window.addEventListener('popstate', function(event) {
            // Hide service frame
            document.getElementById('serviceFrame').style.display = 'none';
            
            // Clear iframe src
            document.getElementById('serviceIframe').src = '';
            
            // Restore original title
            document.title = 'Library Portal - 통합 도서관 관리 시스템';
        });
        
        // Handle direct URL access with service parameter
        window.addEventListener('load', function() {
            const urlParams = new URLSearchParams(window.location.search);
            const service = urlParams.get('service');
            if (service) {
                // Find the service card and load service without adding to history
                const serviceCards = document.querySelectorAll('.service-card');
                for (let card of serviceCards) {
                    if (card.getAttribute('data-title') === service) {
                        const url = card.getAttribute('data-url');
                        const title = card.getAttribute('data-title');
                        
                        // Show service frame
                        document.getElementById('serviceFrame').style.display = 'block';
                        
                        // Load service in iframe
                        document.getElementById('serviceIframe').src = url;
                        
                        // Update page title
                        document.title = title + ' - Library Portal';
                        break;
                    }
                }
            }
        });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return HTML_TEMPLATE

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "library-portal"})

@app.route('/api/services')
def get_services():
    services = [
        {
            "name": "Bookinfo",
            "url": "http://192.168.76.2:30080",
            "status": "online",
            "description": "Istio 기본 Bookinfo 애플리케이션"
        },
        {
            "name": "User Service",
            "url": "http://192.168.76.2:30092",
            "status": "online",
            "description": "사용자 관리 시스템"
        },
        {
            "name": "Search Service",
            "url": "http://192.168.76.2:30093",
            "status": "online",
            "description": "도서 검색 시스템"
        },
        {
            "name": "Analytics Service",
            "url": "http://192.168.76.2:30094",
            "status": "online",
            "description": "데이터 분석 시스템"
        },
        {
            "name": "Order Service",
            "url": "http://192.168.76.2:30085",
            "status": "online",
            "description": "주문 관리 시스템"
        },
        {
            "name": "Catalog Service",
            "url": "http://192.168.76.2:30096",
            "status": "online",
            "description": "카탈로그 관리 시스템"
        },
        {
            "name": "Notification Service",
            "url": "http://192.168.76.2:30097",
            "status": "online",
            "description": "알림 서비스"
        },
        {
            "name": "Recommendation Service",
            "url": "http://192.168.76.2:30098",
            "status": "online",
            "description": "추천 시스템"
        },
        {
            "name": "Payment Service",
            "url": "http://192.168.76.2:30099",
            "status": "online",
            "description": "결제 관리 시스템"
        },
        {
            "name": "Inventory Service",
            "url": "http://192.168.76.2:30100",
            "status": "online",
            "description": "재고 관리 시스템"
        },
        {
            "name": "Shipping Service",
            "url": "http://192.168.76.2:30101",
            "status": "online",
            "description": "배송 관리 시스템"
        }
    ]
    return jsonify({"services": services})

@app.route('/api/status')
def get_system_status():
    status = {
        "total_services": 11,
        "online_services": 11,
        "offline_services": 0,
        "uptime": "99.9%",
        "last_check": "2025-01-20T15:30:00Z"
    }
    return jsonify(status)

@app.route('/api/analytics')
def get_portal_analytics():
    analytics = {
        "total_visits": 1250,
        "unique_visitors": 890,
        "avg_session_duration": "5분 30초",
        "most_visited_service": "User Service",
        "system_health": "Excellent"
    }
    return jsonify(analytics)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9080, debug=True) 