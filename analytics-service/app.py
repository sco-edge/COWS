#!/usr/bin/env python3
"""
Analytics Service - 사용자 행동 분석 서비스
"""
import os
import json
import logging
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template_string
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import requests
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

REQUEST_COUNT = Counter('analytics_service_requests_total', 'Total requests to analytics service')
REQUEST_LATENCY = Histogram('analytics_service_request_duration_seconds', 'Request latency')

# 시뮬레이션된 분석 데이터
analytics_data = {
    "page_views": {
        "/productpage": 1250,
        "/details": 890,
        "/reviews": 650,
        "/ratings": 420,
        "/search": 320,
        "/user/profile": 180
    },
    "user_behavior": {
        "total_users": 450,
        "active_users": 320,
        "new_users_today": 25,
        "avg_session_duration": 8.5
    },
    "popular_books": [
        {"title": "The Great Gatsby", "views": 180, "rating": 4.2},
        {"title": "To Kill a Mockingbird", "views": 165, "rating": 4.5},
        {"title": "1984", "views": 142, "rating": 4.1},
        {"title": "Pride and Prejudice", "views": 128, "rating": 4.3}
    ],
    "search_analytics": {
        "total_searches": 890,
        "popular_queries": [
            {"query": "gatsby", "count": 45},
            {"query": "fiction", "count": 38},
            {"query": "classic", "count": 32},
            {"query": "romance", "count": 28}
        ]
    }
}

# HTML Template with Modern Corporate Style
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Analytics Service - 데이터 분석 시스템</title>
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
        
        .analytics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 24px;
            margin-bottom: 40px;
        }
        
        .analytics-card {
            background: #ffffff;
            border: 1px solid #e0e0e0;
            border-radius: 12px;
            padding: 24px;
            transition: all 0.3s;
        }
        
        .analytics-card:hover {
            box-shadow: 0 8px 24px rgba(0,0,0,0.1);
            transform: translateY(-4px);
        }
        
        .analytics-card h3 {
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 12px;
            color: #000000;
        }
        
        .analytics-card p {
            color: #666666;
            margin-bottom: 16px;
            line-height: 1.5;
        }
        
        .metric {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 16px;
            padding-top: 16px;
            border-top: 1px solid #f0f0f0;
        }
        
        .metric-value {
            font-size: 24px;
            font-weight: 700;
            color: #f2c94c;
        }
        
        .metric-label {
            font-size: 12px;
            color: #666666;
        }
        
        .chart-container {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            margin-top: 16px;
            height: 120px;
            display: flex;
            align-items: end;
            gap: 4px;
        }
        
        .chart-bar {
            background: #f2c94c;
            border-radius: 2px;
            flex: 1;
            transition: all 0.3s;
        }
        
        .chart-bar:hover {
            background: #e6b800;
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
            <a href="/" class="logo">analytics</a>
            <ul class="nav-menu">
                <li><a href="/" class="active">대시보드</a></li>
                <li><a href="/api/usage">사용량 통계</a></li>
                <li><a href="/api/performance">성능 분석</a></li>
                <li><a href="/api/trends">트렌드 분석</a></li>
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
                <h1 class="hero-title">실시간 데이터 분석</h1>
                <p class="hero-subtitle">도서관 시스템의 모든 데이터를 실시간으로 분석하고 시각화합니다. 사용자 행동 패턴부터 인기 도서 트렌드까지, 데이터 기반의 인사이트를 제공합니다.</p>
                <a href="#analytics" class="hero-button">
                    분석 시작하기
                    <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                        <path fill-rule="evenodd" d="M1 8a.5.5 0 0 1 .5-.5h11.793l-3.147-3.146a.5.5 0 0 1 .708-.708l4 4a.5.5 0 0 1 0 .708l-4 4a.5.5 0 0 1-.708-.708L13.293 8.5H1.5A.5.5 0 0 1 1 8z"/>
                    </svg>
                </a>
            </div>
            <div class="hero-cards">
                <div class="hero-card">
                    <h3>실시간 모니터링</h3>
                    <p>시스템 성능과 사용자 활동을 실시간으로 추적</p>
                </div>
                <div class="hero-card white">
                    <h3>예측 분석</h3>
                    <p>AI 기반 트렌드 예측과 수요 분석</p>
                </div>
                <div class="hero-card">
                    <h3>인사이트 리포트</h3>
                    <p>주간/월간 데이터 분석 리포트 자동 생성</p>
                </div>
            </div>
        </section>

        <!-- Analytics Dashboard Section -->
        <section class="content-section">
            <h2 class="section-title">분석 대시보드</h2>
            <div class="analytics-grid">
                <div class="analytics-card">
                    <h3>일일 활성 사용자</h3>
                    <p>오늘 방문한 고유 사용자 수</p>
                    <div class="metric">
                        <div>
                            <div class="metric-value">1,247</div>
                            <div class="metric-label">+12% 어제 대비</div>
                        </div>
                    </div>
                    <div class="chart-container">
                        <div class="chart-bar" style="height: 60%;"></div>
                        <div class="chart-bar" style="height: 80%;"></div>
                        <div class="chart-bar" style="height: 45%;"></div>
                        <div class="chart-bar" style="height: 90%;"></div>
                        <div class="chart-bar" style="height: 70%;"></div>
                        <div class="chart-bar" style="height: 85%;"></div>
                        <div class="chart-bar" style="height: 95%;"></div>
                    </div>
                </div>
                
                <div class="analytics-card">
                    <h3>도서 대출량</h3>
                    <p>오늘 대출된 도서의 총 개수</p>
                    <div class="metric">
                        <div>
                            <div class="metric-value">3,456</div>
                            <div class="metric-label">+8% 어제 대비</div>
                        </div>
                    </div>
                    <div class="chart-container">
                        <div class="chart-bar" style="height: 75%;"></div>
                        <div class="chart-bar" style="height: 65%;"></div>
                        <div class="chart-bar" style="height: 85%;"></div>
                        <div class="chart-bar" style="height: 70%;"></div>
                        <div class="chart-bar" style="height: 90%;"></div>
                        <div class="chart-bar" style="height: 80%;"></div>
                        <div class="chart-bar" style="height: 95%;"></div>
                    </div>
                </div>
                
                <div class="analytics-card">
                    <h3>검색 쿼리</h3>
                    <p>오늘 수행된 검색 쿼리 수</p>
                    <div class="metric">
                        <div>
                            <div class="metric-value">8,923</div>
                            <div class="metric-label">+15% 어제 대비</div>
                        </div>
                    </div>
                    <div class="chart-container">
                        <div class="chart-bar" style="height: 85%;"></div>
                        <div class="chart-bar" style="height: 70%;"></div>
                        <div class="chart-bar" style="height: 90%;"></div>
                        <div class="chart-bar" style="height: 75%;"></div>
                        <div class="chart-bar" style="height: 95%;"></div>
                        <div class="chart-bar" style="height: 80%;"></div>
                        <div class="chart-bar" style="height: 100%;"></div>
                    </div>
                </div>
                
                <div class="analytics-card">
                    <h3>시스템 응답시간</h3>
                    <p>평균 API 응답 시간 (ms)</p>
                    <div class="metric">
                        <div>
                            <div class="metric-value">142</div>
                            <div class="metric-label">-5% 어제 대비</div>
                        </div>
                    </div>
                    <div class="chart-container">
                        <div class="chart-bar" style="height: 60%;"></div>
                        <div class="chart-bar" style="height: 75%;"></div>
                        <div class="chart-bar" style="height: 50%;"></div>
                        <div class="chart-bar" style="height: 65%;"></div>
                        <div class="chart-bar" style="height: 55%;"></div>
                        <div class="chart-bar" style="height: 70%;"></div>
                        <div class="chart-bar" style="height: 45%;"></div>
                    </div>
                </div>
            </div>
        </section>
    </main>

    <!-- Footer -->
    <footer class="footer">
        <div class="footer-content">
            <div class="footer-links">
                <a href="/api/usage">사용량 통계</a>
                <a href="/api/performance">성능 분석</a>
                <a href="/api/trends">트렌드 분석</a>
                <a href="/api/reports">리포트</a>
                <a href="/api/alerts">알림 설정</a>
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
    return jsonify({"status": "healthy", "service": "analytics-service"})

@app.route('/metrics', methods=['GET'])
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

@app.route('/analytics', methods=['GET'])
@REQUEST_LATENCY.time()
def get_analytics():
    REQUEST_COUNT.inc()
    logger.info("Getting analytics data")
    return jsonify(analytics_data)

@app.route('/analytics/page-views', methods=['GET'])
@REQUEST_LATENCY.time()
def get_page_views():
    REQUEST_COUNT.inc()
    logger.info("Getting page views analytics")
    return jsonify({
        "page_views": analytics_data["page_views"],
        "total_page_views": sum(analytics_data["page_views"].values()),
        "most_viewed_page": max(analytics_data["page_views"], key=analytics_data["page_views"].get)
    })

@app.route('/analytics/user-behavior', methods=['GET'])
@REQUEST_LATENCY.time()
def get_user_behavior():
    REQUEST_COUNT.inc()
    logger.info("Getting user behavior analytics")
    return jsonify(analytics_data["user_behavior"])

@app.route('/analytics/popular-books', methods=['GET'])
@REQUEST_LATENCY.time()
def get_popular_books():
    REQUEST_COUNT.inc()
    logger.info("Getting popular books analytics")
    return jsonify({
        "popular_books": analytics_data["popular_books"],
        "total_books_analyzed": len(analytics_data["popular_books"])
    })

@app.route('/analytics/search', methods=['GET'])
@REQUEST_LATENCY.time()
def get_search_analytics():
    REQUEST_COUNT.inc()
    logger.info("Getting search analytics")
    return jsonify(analytics_data["search_analytics"])

@app.route('/analytics/track', methods=['POST'])
@REQUEST_LATENCY.time()
def track_event():
    REQUEST_COUNT.inc()
    data = request.get_json()
    event_type = data.get('event_type')
    page = data.get('page', '/')
    user_id = data.get('user_id', 'anonymous')
    
    logger.info(f"Tracking event: {event_type} on {page} by user {user_id}")
    
    # 실제 구현에서는 데이터베이스에 저장
    return jsonify({
        "status": "tracked",
        "event_type": event_type,
        "page": page,
        "user_id": user_id,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/analytics/report', methods=['GET'])
@REQUEST_LATENCY.time()
def generate_report():
    REQUEST_COUNT.inc()
    logger.info("Generating analytics report")
    
    total_page_views = sum(analytics_data["page_views"].values())
    avg_rating = sum(book["rating"] for book in analytics_data["popular_books"]) / len(analytics_data["popular_books"])
    
    report = {
        "summary": {
            "total_page_views": total_page_views,
            "total_users": analytics_data["user_behavior"]["total_users"],
            "active_users": analytics_data["user_behavior"]["active_users"],
            "avg_rating": round(avg_rating, 2),
            "total_searches": analytics_data["search_analytics"]["total_searches"]
        },
        "top_pages": sorted(analytics_data["page_views"].items(), key=lambda x: x[1], reverse=True)[:3],
        "top_books": sorted(analytics_data["popular_books"], key=lambda x: x["views"], reverse=True)[:3],
        "top_searches": analytics_data["search_analytics"]["popular_queries"][:3],
        "generated_at": datetime.now().isoformat()
    }
    
    return jsonify(report)

@app.route('/api/usage')
def get_usage_stats():
    usage_stats = {
        "daily_active_users": 1247,
        "weekly_active_users": 8234,
        "monthly_active_users": 45678,
        "total_books_borrowed": 3456,
        "total_searches": 8923,
        "avg_session_duration": 15.4
    }
    return jsonify(usage_stats)

@app.route('/api/performance')
def get_performance_metrics():
    performance = {
        "avg_response_time": 142,
        "uptime_percentage": 99.8,
        "error_rate": 0.02,
        "throughput": 1250,
        "memory_usage": 68.5,
        "cpu_usage": 45.2
    }
    return jsonify(performance)

@app.route('/api/trends')
def get_trends():
    trends = [
        {"category": "프로그래밍", "growth": 15.2, "volume": 2340},
        {"category": "AI/ML", "growth": 22.8, "volume": 1890},
        {"category": "웹개발", "growth": 8.5, "volume": 3120},
        {"category": "데이터베이스", "growth": 12.3, "volume": 1456},
        {"category": "알고리즘", "growth": 18.7, "volume": 2789}
    ]
    return jsonify({"trends": trends})

@app.route('/api/reports')
def get_reports():
    reports = [
        {"id": 1, "title": "주간 사용량 리포트", "date": "2025-01-15", "type": "weekly"},
        {"id": 2, "title": "월간 트렌드 분석", "date": "2025-01-01", "type": "monthly"},
        {"id": 3, "title": "성능 최적화 리포트", "date": "2025-01-10", "type": "performance"},
        {"id": 4, "title": "사용자 행동 분석", "date": "2025-01-08", "type": "behavior"}
    ]
    return jsonify({"reports": reports})

@app.route('/api/alerts')
def get_alerts():
    alerts = [
        {"id": 1, "type": "warning", "message": "시스템 응답시간 증가", "timestamp": "2025-01-15T10:30:00Z"},
        {"id": 2, "type": "info", "message": "새로운 도서 카테고리 추가", "timestamp": "2025-01-15T09:15:00Z"},
        {"id": 3, "type": "success", "message": "백업 완료", "timestamp": "2025-01-15T08:00:00Z"}
    ]
    return jsonify({"alerts": alerts})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 9080))
    app.run(host='0.0.0.0', port=port, debug=False) 