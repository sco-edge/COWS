#!/usr/bin/env python3
"""
Test Service - 확장된 Bookinfo 기능 테스트 서비스
"""

import os
import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# HTML 템플릿
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Extended Bookinfo - 테스트 페이지</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .service { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
        .status { padding: 5px 10px; border-radius: 3px; color: white; }
        .running { background-color: #28a745; }
        .error { background-color: #dc3545; }
        .info { background-color: #17a2b8; }
        button { padding: 10px 20px; margin: 5px; background-color: #007bff; color: white; border: none; border-radius: 3px; cursor: pointer; }
        button:hover { background-color: #0056b3; }
        .response { background-color: #f8f9fa; padding: 10px; margin: 10px 0; border-radius: 3px; }
    </style>
</head>
<body>
    <h1>🚀 Extended Bookinfo 애플리케이션</h1>
    <p>기존 Bookinfo에 10개의 추가 마이크로서비스가 확장되었습니다!</p>
    
    <div class="service">
        <h2>📊 서비스 상태</h2>
        <p><span class="status running">✅ 기존 서비스들</span> - 정상 실행 중</p>
        <p><span class="status error">❌ 확장된 서비스들</span> - 이미지 문제로 실행 중단</p>
    </div>
    
    <div class="service">
        <h2>🔧 확장된 서비스들</h2>
        <ul>
            <li><strong>user-service</strong> - 사용자 관리 및 인증</li>
            <li><strong>order-service</strong> - 주문 처리 및 관리</li>
            <li><strong>inventory-service</strong> - 재고 관리</li>
            <li><strong>payment-service</strong> - 결제 처리</li>
            <li><strong>notification-service</strong> - 알림 서비스</li>
            <li><strong>search-service</strong> - 도서 검색</li>
            <li><strong>recommendation-service</strong> - 추천 시스템</li>
            <li><strong>analytics-service</strong> - 사용자 행동 분석</li>
            <li><strong>catalog-service</strong> - 카탈로그 관리</li>
            <li><strong>shipping-service</strong> - 배송 관리</li>
        </ul>
    </div>
    
    <div class="service">
        <h2>🧪 테스트 기능</h2>
        <button onclick="testUserService()">사용자 서비스 테스트</button>
        <button onclick="testSearchService()">검색 서비스 테스트</button>
        <button onclick="testAnalyticsService()">분석 서비스 테스트</button>
        <div id="response" class="response" style="display:none;"></div>
    </div>
    
    <div class="service">
        <h2>📈 메트릭</h2>
        <p>각 서비스는 Prometheus 메트릭을 제공합니다:</p>
        <ul>
            <li>요청 수 카운터</li>
            <li>응답 시간 히스토그램</li>
            <li>헬스체크 엔드포인트</li>
        </ul>
    </div>
    
    <div class="service">
        <h2>🔍 Istio 기능</h2>
        <p>이 애플리케이션은 Istio의 다음 기능들을 활용합니다:</p>
        <ul>
            <li>서비스 메시 시각화</li>
            <li>트래픽 관리</li>
            <li>서킷 브레이커</li>
            <li>분산 추적</li>
            <li>메트릭 수집</li>
        </ul>
    </div>
    
    <script>
        function testUserService() {
            fetch('/api/test/user')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('response').innerHTML = '<h3>사용자 서비스 응답:</h3><pre>' + JSON.stringify(data, null, 2) + '</pre>';
                    document.getElementById('response').style.display = 'block';
                })
                .catch(error => {
                    document.getElementById('response').innerHTML = '<h3>오류:</h3><pre>' + error.message + '</pre>';
                    document.getElementById('response').style.display = 'block';
                });
        }
        
        function testSearchService() {
            fetch('/api/test/search')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('response').innerHTML = '<h3>검색 서비스 응답:</h3><pre>' + JSON.stringify(data, null, 2) + '</pre>';
                    document.getElementById('response').style.display = 'block';
                })
                .catch(error => {
                    document.getElementById('response').innerHTML = '<h3>오류:</h3><pre>' + error.message + '</pre>';
                    document.getElementById('response').style.display = 'block';
                });
        }
        
        function testAnalyticsService() {
            fetch('/api/test/analytics')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('response').innerHTML = '<h3>분석 서비스 응답:</h3><pre>' + JSON.stringify(data, null, 2) + '</pre>';
                    document.getElementById('response').style.display = 'block';
                })
                .catch(error => {
                    document.getElementById('response').innerHTML = '<h3>오류:</h3><pre>' + error.message + '</pre>';
                    document.getElementById('response').style.display = 'block';
                });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """메인 페이지"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/health')
def health():
    """헬스체크"""
    return jsonify({"status": "healthy", "service": "test-service"})

@app.route('/api/test/user')
def test_user_service():
    """사용자 서비스 테스트"""
    return jsonify({
        "service": "user-service",
        "status": "simulated",
        "data": {
            "users": [
                {"id": "user1", "username": "john_doe", "email": "john@example.com"},
                {"id": "user2", "username": "jane_smith", "email": "jane@example.com"}
            ],
            "message": "사용자 관리 기능이 정상적으로 작동합니다!"
        }
    })

@app.route('/api/test/search')
def test_search_service():
    """검색 서비스 테스트"""
    return jsonify({
        "service": "search-service",
        "status": "simulated",
        "data": {
            "query": "gatsby",
            "results": [
                {"id": "book1", "title": "The Great Gatsby", "author": "F. Scott Fitzgerald"},
                {"id": "book2", "title": "To Kill a Mockingbird", "author": "Harper Lee"}
            ],
            "message": "도서 검색 기능이 정상적으로 작동합니다!"
        }
    })

@app.route('/api/test/analytics')
def test_analytics_service():
    """분석 서비스 테스트"""
    return jsonify({
        "service": "analytics-service",
        "status": "simulated",
        "data": {
            "page_views": 150,
            "unique_users": 45,
            "popular_pages": {
                "/productpage": 50,
                "/details": 30,
                "/reviews": 25
            },
            "message": "사용자 행동 분석 기능이 정상적으로 작동합니다!"
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 9080))
    app.run(host='0.0.0.0', port=port, debug=False) 