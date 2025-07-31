#!/usr/bin/env python3
"""
User Service - 사용자 관리
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
    <title>User Service - 사용자 관리 시스템</title>
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
        
        /* Users Section */
        .content-section {
            margin-bottom: 80px;
        }
        
        .section-title {
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 40px;
            text-align: center;
            color: #333;
        }
        
        .user-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 30px;
        }
        
        .user-card {
            background: white;
            border-radius: 16px;
            padding: 30px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
            border: 1px solid #f0f0f0;
            transition: transform 0.3s, box-shadow 0.3s;
            position: relative;
            overflow: hidden;
        }
        
        .user-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(135deg, #f2c94c 0%, #f2994a 100%);
        }
        
        .user-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
        }
        
        .user-header {
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .user-avatar {
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background: linear-gradient(135deg, #f2c94c 0%, #f2994a 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 20px;
            font-weight: 600;
        }
        
        .user-info-main {
            flex: 1;
        }
        
        .user-name {
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 5px;
            color: #333;
        }
        
        .user-status {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
        }
        
        .status-active {
            background: #d4edda;
            color: #155724;
        }
        
        .status-inactive {
            background: #f8d7da;
            color: #721c24;
        }
        
        .user-description {
            color: #666;
            margin-bottom: 15px;
            line-height: 1.5;
        }
        
        .user-details {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-top: 20px;
        }
        
        .user-detail {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 14px;
            color: #666;
        }
        
        .detail-icon {
            width: 16px;
            height: 16px;
            opacity: 0.6;
        }
        
        /* Analytics Section */
        .analytics-section {
            background: #f8f9fa;
            border-radius: 16px;
            padding: 40px;
            margin-bottom: 80px;
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
        
        .icon-users { background: linear-gradient(135deg, #f2c94c 0%, #f2994a 100%); }
        .icon-activity { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
        .icon-security { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
        
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
                <div class="logo-icon">👥</div>
                User Service
            </a>
            <nav>
                <ul class="nav-menu">
                    <li><a href="#" class="active">대시보드</a></li>
                    <li><a href="#">사용자 관리</a></li>
                    <li><a href="#">권한 관리</a></li>
                    <li><a href="#">활동 로그</a></li>
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
                <h1 class="hero-title">사용자 관리 시스템</h1>
                <p class="hero-subtitle">도서관 사용자 계정 관리, 권한 제어, 인증 서비스를 제공하는 통합 사용자 관리 시스템입니다.</p>
                <a href="#users" class="hero-button">
                    사용자 관리
                    <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                        <path fill-rule="evenodd" d="M1 8a.5.5 0 0 1 .5-.5h11.793l-3.147-3.146a.5.5 0 0 1 .708-.708l4 4a.5.5 0 0 1 0 .708l-4 4a.5.5 0 0 1-.708-.708L13.293 8.5H1.5A.5.5 0 0 1 1 8z"/>
                    </svg>
                </a>
            </div>
            <div class="hero-stats">
                <div class="stat-card">
                    <div class="stat-number">1,247</div>
                    <div class="stat-label">총 사용자</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">89%</div>
                    <div class="stat-label">활성 사용자</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">156</div>
                    <div class="stat-label">오늘 접속</div>
                </div>
            </div>
        </section>

        <!-- Analytics Section -->
        <section class="analytics-section">
            <h2 class="section-title">사용자 통계</h2>
            <div class="analytics-grid">
                <div class="analytics-card">
                    <div class="analytics-header">
                        <div class="analytics-icon icon-users">👥</div>
                        <div class="analytics-title">총 사용자 수</div>
                    </div>
                    <div class="analytics-value">1,247</div>
                    <div class="analytics-change">+12% 이번 달</div>
                </div>
                
                <div class="analytics-card">
                    <div class="analytics-header">
                        <div class="analytics-icon icon-activity">📊</div>
                        <div class="analytics-title">활성 사용자</div>
                    </div>
                    <div class="analytics-value">1,109</div>
                    <div class="analytics-change">+8% 이번 주</div>
                </div>
                
                <div class="analytics-card">
                    <div class="analytics-header">
                        <div class="analytics-icon icon-security">🔒</div>
                        <div class="analytics-title">보안 인증</div>
                    </div>
                    <div class="analytics-value">99.9%</div>
                    <div class="analytics-change">안정적</div>
                </div>
            </div>
        </section>

        <!-- Users Section -->
        <section class="content-section">
            <h2 class="section-title">사용자 현황</h2>
            <div class="user-grid">
                <div class="user-card">
                    <div class="user-header">
                        <div class="user-avatar">김</div>
                        <div class="user-info-main">
                            <div class="user-name">김도서</div>
                            <div class="user-status status-active">활성</div>
                        </div>
                    </div>
                    <p class="user-description">도서관 관리자로 전체 시스템 관리 권한을 가지고 있습니다.</p>
                    <div class="user-details">
                        <div class="user-detail">
                            <svg class="detail-icon" fill="currentColor" viewBox="0 0 20 20">
                                <path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z"/>
                                <path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z"/>
                            </svg>
                            admin@library.com
                        </div>
                        <div class="user-detail">
                            <svg class="detail-icon" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M6 6V5a3 3 0 013-3h2a3 3 0 013 3v1h2a2 2 0 012 2v3.57A22.952 22.952 0 0110 13a22.95 22.95 0 01-8-1.43V8a2 2 0 012-2h2zm2-1a1 1 0 011-1h2a1 1 0 011 1v1H8V5zm1 5a1 1 0 011-1h.01a1 1 0 110 2H10a1 1 0 01-1-1z" clip-rule="evenodd"/>
                            </svg>
                            ADMIN
                        </div>
                    </div>
                </div>
                
                <div class="user-card">
                    <div class="user-header">
                        <div class="user-avatar">이</div>
                        <div class="user-info-main">
                            <div class="user-name">이사서</div>
                            <div class="user-status status-active">활성</div>
                        </div>
                    </div>
                    <p class="user-description">사서로 도서 관리 및 대출/반납 업무를 담당합니다.</p>
                    <div class="user-details">
                        <div class="user-detail">
                            <svg class="detail-icon" fill="currentColor" viewBox="0 0 20 20">
                                <path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z"/>
                                <path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z"/>
                            </svg>
                            librarian@library.com
                        </div>
                        <div class="user-detail">
                            <svg class="detail-icon" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M6 6V5a3 3 0 013-3h2a3 3 0 013 3v1h2a2 2 0 012 2v3.57A22.952 22.952 0 0110 13a22.95 22.95 0 01-8-1.43V8a2 2 0 012-2h2zm2-1a1 1 0 011-1h2a1 1 0 011 1v1H8V5zm1 5a1 1 0 011-1h.01a1 1 0 110 2H10a1 1 0 01-1-1z" clip-rule="evenodd"/>
                            </svg>
                            LIBRARIAN
                        </div>
                    </div>
                </div>
                
                <div class="user-card">
                    <div class="user-header">
                        <div class="user-avatar">박</div>
                        <div class="user-info-main">
                            <div class="user-name">박학생</div>
                            <div class="user-status status-active">활성</div>
                        </div>
                    </div>
                    <p class="user-description">일반 사용자로 도서 대출 및 검색 서비스를 이용합니다.</p>
                    <div class="user-details">
                        <div class="user-detail">
                            <svg class="detail-icon" fill="currentColor" viewBox="0 0 20 20">
                                <path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z"/>
                                <path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z"/>
                            </svg>
                            student@university.edu
                        </div>
                        <div class="user-detail">
                            <svg class="detail-icon" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M6 6V5a3 3 0 013-3h2a3 3 0 013 3v1h2a2 2 0 012 2v3.57A22.952 22.952 0 0110 13a22.95 22.95 0 01-8-1.43V8a2 2 0 012-2h2zm2-1a1 1 0 011-1h2a1 1 0 011 1v1H8V5zm1 5a1 1 0 011-1h.01a1 1 0 110 2H10a1 1 0 01-1-1z" clip-rule="evenodd"/>
                            </svg>
                            STUDENT
                        </div>
                    </div>
                </div>
                
                <div class="user-card">
                    <div class="user-header">
                        <div class="user-avatar">최</div>
                        <div class="user-info-main">
                            <div class="user-name">최교수</div>
                            <div class="user-status status-active">활성</div>
                        </div>
                    </div>
                    <p class="user-description">교수로 연구 자료 검색 및 대출 서비스를 이용합니다.</p>
                    <div class="user-details">
                        <div class="user-detail">
                            <svg class="detail-icon" fill="currentColor" viewBox="0 0 20 20">
                                <path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z"/>
                                <path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z"/>
                            </svg>
                            professor@university.edu
                        </div>
                        <div class="user-detail">
                            <svg class="detail-icon" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M6 6V5a3 3 0 013-3h2a3 3 0 013 3v1h2a2 2 0 012 2v3.57A22.952 22.952 0 0110 13a22.95 22.95 0 01-8-1.43V8a2 2 0 012-2h2zm2-1a1 1 0 011-1h2a1 1 0 011 1v1H8V5zm1 5a1 1 0 011-1h.01a1 1 0 110 2H10a1 1 0 01-1-1z" clip-rule="evenodd"/>
                            </svg>
                            PROFESSOR
                        </div>
                    </div>
                </div>
                
                <div class="user-card">
                    <div class="user-header">
                        <div class="user-avatar">정</div>
                        <div class="user-info-main">
                            <div class="user-name">정방문자</div>
                            <div class="user-status status-inactive">비활성</div>
                        </div>
                    </div>
                    <p class="user-description">일시 방문자로 제한된 서비스만 이용 가능합니다.</p>
                    <div class="user-details">
                        <div class="user-detail">
                            <svg class="detail-icon" fill="currentColor" viewBox="0 0 20 20">
                                <path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z"/>
                                <path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z"/>
                            </svg>
                            guest@library.com
                        </div>
                        <div class="user-detail">
                            <svg class="detail-icon" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M6 6V5a3 3 0 013-3h2a3 3 0 013 3v1h2a2 2 0 012 2v3.57A22.952 22.952 0 0110 13a22.95 22.95 0 01-8-1.43V8a2 2 0 012-2h2zm2-1a1 1 0 011-1h2a1 1 0 011 1v1H8V5zm1 5a1 1 0 011-1h.01a1 1 0 110 2H10a1 1 0 01-1-1z" clip-rule="evenodd"/>
                            </svg>
                            GUEST
                        </div>
                    </div>
                </div>
                
                <div class="user-card">
                    <div class="user-header">
                        <div class="user-avatar">한</div>
                        <div class="user-info-main">
                            <div class="user-name">한시스템</div>
                            <div class="user-status status-active">활성</div>
                        </div>
                    </div>
                    <p class="user-description">시스템 관리자로 기술적 지원 및 유지보수를 담당합니다.</p>
                    <div class="user-details">
                        <div class="user-detail">
                            <svg class="detail-icon" fill="currentColor" viewBox="0 0 20 20">
                                <path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z"/>
                                <path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z"/>
                            </svg>
                            system@library.com
                        </div>
                        <div class="user-detail">
                            <svg class="detail-icon" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M6 6V5a3 3 0 013-3h2a3 3 0 013 3v1h2a2 2 0 012 2v3.57A22.952 22.952 0 0110 13a22.95 22.95 0 01-8-1.43V8a2 2 0 012-2h2zm2-1a1 1 0 011-1h2a1 1 0 011 1v1H8V5zm1 5a1 1 0 011-1h.01a1 1 0 110 2H10a1 1 0 01-1-1z" clip-rule="evenodd"/>
                            </svg>
                            SYSTEM
                        </div>
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

@app.route('/api/users')
def get_users():
    users = [
        {
            "id": "user1",
            "name": "김철수",
            "email": "kim@example.com",
            "role": "admin",
            "status": "active",
                    "created_at": "2025-01-15T10:30:00Z",
        "last_login": "2025-01-20T14:30:00Z"
        },
        {
            "id": "user2",
            "name": "이영희",
            "email": "lee@example.com",
            "role": "user",
            "status": "active",
                    "created_at": "2025-01-14T14:20:00Z",
        "last_login": "2025-01-19T09:15:00Z"
        },
        {
            "id": "user3",
            "name": "박민수",
            "email": "park@example.com",
            "role": "user",
            "status": "inactive",
                    "created_at": "2025-01-13T09:15:00Z",
        "last_login": "2025-01-18T16:45:00Z"
        }
    ]
    return jsonify({"users": users})

@app.route('/api/roles')
def get_roles():
    roles = [
        {
            "id": 1,
            "name": "관리자",
            "code": "admin",
            "permissions": ["read", "write", "delete", "manage_users"],
            "user_count": 2
        },
        {
            "id": 2,
            "name": "일반 사용자",
            "code": "user",
            "permissions": ["read", "borrow", "return"],
            "user_count": 15
        },
        {
            "id": 3,
            "name": "게스트",
            "code": "guest",
            "permissions": ["read"],
            "user_count": 8
        }
    ]
    return jsonify({"roles": roles})

@app.route('/api/analytics')
def get_user_analytics():
    analytics = {
        "total_users": 25,
        "active_users": 22,
        "inactive_users": 3,
        "admin_users": 2,
        "regular_users": 20,
        "guest_users": 3,
        "avg_login_frequency": 3.2
    }
    return jsonify(analytics)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9080, debug=True) 