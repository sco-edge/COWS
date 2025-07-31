#!/usr/bin/env python3
"""
Catalog Service - 카탈로그 관리
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

REQUEST_COUNT = Counter('catalog_service_requests_total', 'Total requests to catalog service')
REQUEST_LATENCY = Histogram('catalog_service_request_duration_seconds', 'Request latency')

catalog_db = [
    {
        "id": "cat1",
        "category": "소설",
        "subcategory": "현대소설",
        "book_count": 1250,
        "description": "현대 한국 및 세계 소설",
        "created_at": "2025-01-15T10:30:00Z",
        "status": "active"
    },
    {
        "id": "cat2",
        "category": "역사",
        "subcategory": "한국사",
        "book_count": 890,
        "description": "한국 역사 관련 도서",
        "created_at": "2025-01-14T14:20:00Z",
        "status": "active"
    },
    {
        "id": "cat3",
        "category": "과학",
        "subcategory": "물리학",
        "book_count": 456,
        "description": "물리학 관련 도서",
        "created_at": "2025-01-13T09:15:00Z",
        "status": "active"
    },
    {
        "id": "cat4",
        "category": "경제",
        "subcategory": "경영학",
        "book_count": 678,
        "description": "경영 및 경제 관련 도서",
        "created_at": "2025-01-12T16:45:00Z",
        "status": "active"
    }
]

# HTML Template with Modern Corporate Style
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Catalog Service - 카탈로그 관리 시스템</title>
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
        
        /* Search Section */
        .search-section {
            background: #f8f9fa;
            border-radius: 16px;
            padding: 40px;
            margin-bottom: 80px;
        }
        
        .search-container {
            max-width: 600px;
            margin: 0 auto;
        }
        
        .search-box {
            display: flex;
            gap: 15px;
            margin-bottom: 30px;
        }
        
        .search-input {
            flex: 1;
            padding: 15px 20px;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        
        .search-input:focus {
            outline: none;
            border-color: #f2c94c;
        }
        
        .search-button {
            background: linear-gradient(135deg, #f2c94c 0%, #f2994a 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.3s;
        }
        
        .search-button:hover {
            transform: translateY(-2px);
        }
        
        .search-filters {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            justify-content: center;
        }
        
        .filter-button {
            padding: 8px 16px;
            border: 1px solid #e9ecef;
            border-radius: 20px;
            background: white;
            color: #666;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .filter-button:hover,
        .filter-button.active {
            background: #f2c94c;
            color: white;
            border-color: #f2c94c;
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
        
        .icon-books { background: linear-gradient(135deg, #f2c94c 0%, #f2994a 100%); }
        .icon-categories { background: linear-gradient(135deg, #3498db 0%, #2980b9 100%); }
        .icon-available { background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%); }
        .icon-new { background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%); }
        
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
        
        /* Books Section */
        .content-section {
            margin-bottom: 80px;
        }
        
        .book-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
        }
        
        .book-card {
            background: white;
            border-radius: 16px;
            padding: 30px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
            border: 1px solid #f0f0f0;
            transition: transform 0.3s, box-shadow 0.3s;
            position: relative;
            overflow: hidden;
        }
        
        .book-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(135deg, #f2c94c 0%, #f2994a 100%);
        }
        
        .book-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
        }
        
        .book-header {
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .book-cover {
            width: 60px;
            height: 80px;
            border-radius: 8px;
            background: linear-gradient(135deg, #f2c94c 0%, #f2994a 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 24px;
        }
        
        .book-info {
            flex: 1;
        }
        
        .book-title {
            font-size: 18px;
            font-weight: 600;
            color: #333;
            margin-bottom: 5px;
        }
        
        .book-author {
            font-size: 14px;
            color: #666;
            margin-bottom: 8px;
        }
        
        .book-status {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
        }
        
        .status-available {
            background: #d4edda;
            color: #155724;
        }
        
        .status-unavailable {
            background: #f8d7da;
            color: #721c24;
        }
        
        .book-description {
            color: #666;
            margin-bottom: 20px;
            line-height: 1.5;
        }
        
        .book-details {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-top: 20px;
        }
        
        .book-detail {
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
                <div class="logo-icon">📚</div>
                Catalog Service
            </a>
            <nav>
                <ul class="nav-menu">
                    <li><a href="#" class="active">대시보드</a></li>
                    <li><a href="#">도서 검색</a></li>
                    <li><a href="#">카테고리</a></li>
                    <li><a href="#">신간 도서</a></li>
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
                <h1 class="hero-title">카탈로그 관리 시스템</h1>
                <p class="hero-subtitle">도서 정보 관리, 검색, 분류를 통합적으로 제공하는 스마트 카탈로그 관리 시스템입니다.</p>
                <a href="#books" class="hero-button">
                    도서 검색
                    <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                        <path fill-rule="evenodd" d="M1 8a.5.5 0 0 1 .5-.5h11.793l-3.147-3.146a.5.5 0 0 1 .708-.708l4 4a.5.5 0 0 1 0 .708l-4 4a.5.5 0 0 1-.708-.708L13.293 8.5H1.5A.5.5 0 0 1 1 8z"/>
                    </svg>
                </a>
            </div>
            <div class="hero-stats">
                <div class="stat-card">
                    <div class="stat-number">15,847</div>
                    <div class="stat-label">총 도서</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">89%</div>
                    <div class="stat-label">대출 가능</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">156</div>
                    <div class="stat-label">신간 도서</div>
                </div>
            </div>
        </section>

        <!-- Search Section -->
        <section class="search-section">
            <div class="search-container">
                <h2 class="section-title">도서 검색</h2>
                <div class="search-box">
                    <input type="text" class="search-input" placeholder="도서명, 저자, ISBN을 입력하세요...">
                    <button class="search-button">검색</button>
                </div>
                <div class="search-filters">
                    <button class="filter-button active">전체</button>
                    <button class="filter-button">컴퓨터/IT</button>
                    <button class="filter-button">문학</button>
                    <button class="filter-button">과학</button>
                    <button class="filter-button">경제/경영</button>
                    <button class="filter-button">역사</button>
                </div>
            </div>
        </section>

        <!-- Analytics Section -->
        <section class="analytics-section">
            <h2 class="section-title">도서 통계</h2>
            <div class="analytics-grid">
                <div class="analytics-card">
                    <div class="analytics-header">
                        <div class="analytics-icon icon-books">📚</div>
                        <div class="analytics-title">총 도서 수</div>
                    </div>
                    <div class="analytics-value">15,847</div>
                    <div class="analytics-change">+234 이번 달</div>
                </div>
                
                <div class="analytics-card">
                    <div class="analytics-header">
                        <div class="analytics-icon icon-categories">📂</div>
                        <div class="analytics-title">카테고리</div>
                    </div>
                    <div class="analytics-value">24</div>
                    <div class="analytics-change">+2 이번 달</div>
                </div>
                
                <div class="analytics-card">
                    <div class="analytics-header">
                        <div class="analytics-icon icon-available">✅</div>
                        <div class="analytics-title">대출 가능</div>
                    </div>
                    <div class="analytics-value">14,104</div>
                    <div class="analytics-change">89% 비율</div>
                </div>
                
                <div class="analytics-card">
                    <div class="analytics-header">
                        <div class="analytics-icon icon-new">🆕</div>
                        <div class="analytics-title">신간 도서</div>
                    </div>
                    <div class="analytics-value">156</div>
                    <div class="analytics-change">+23 이번 주</div>
                </div>
            </div>
        </section>

        <!-- Books Section -->
        <section class="content-section">
            <h2 class="section-title">추천 도서</h2>
            <div class="book-grid">
                <div class="book-card">
                    <div class="book-header">
                        <div class="book-cover">📚</div>
                        <div class="book-info">
                            <div class="book-title">파이썬 프로그래밍</div>
                            <div class="book-author">김철수 저</div>
                            <div class="book-status status-available">대출 가능</div>
                        </div>
                    </div>
                    <p class="book-description">파이썬 언어의 기초부터 고급 문법까지 체계적으로 학습할 수 있는 입문서입니다.</p>
                    <div class="book-details">
                        <div class="book-detail">
                            <svg class="detail-icon" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clip-rule="evenodd"/>
                            </svg>
                            컴퓨터/프로그래밍
                        </div>
                        <div class="book-detail">
                            <svg class="detail-icon" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd"/>
                            </svg>
                            2025-01-15
                        </div>
                    </div>
                </div>
                
                <div class="book-card">
                    <div class="book-header">
                        <div class="book-cover">📚</div>
                        <div class="book-info">
                            <div class="book-title">머신러닝 기초</div>
                            <div class="book-author">이영희 저</div>
                            <div class="book-status status-available">대출 가능</div>
                        </div>
                    </div>
                    <p class="book-description">머신러닝의 기본 개념과 알고리즘을 실습을 통해 학습할 수 있는 책입니다.</p>
                    <div class="book-details">
                        <div class="book-detail">
                            <svg class="detail-icon" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clip-rule="evenodd"/>
                            </svg>
                            컴퓨터/인공지능
                        </div>
                        <div class="book-detail">
                            <svg class="detail-icon" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd"/>
                            </svg>
                            2025-01-16
                        </div>
                    </div>
                </div>
                
                <div class="book-card">
                    <div class="book-header">
                        <div class="book-cover">📚</div>
                        <div class="book-info">
                            <div class="book-title">웹 개발 완전 가이드</div>
                            <div class="book-author">박민수 저</div>
                            <div class="book-status status-unavailable">대출 중</div>
                        </div>
                    </div>
                    <p class="book-description">HTML, CSS, JavaScript부터 React, Node.js까지 웹 개발의 모든 것을 다룹니다.</p>
                    <div class="book-details">
                        <div class="book-detail">
                            <svg class="detail-icon" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clip-rule="evenodd"/>
                            </svg>
                            컴퓨터/웹개발
                        </div>
                        <div class="book-detail">
                            <svg class="detail-icon" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd"/>
                            </svg>
                            2025-01-17
                        </div>
                    </div>
                </div>
                
                <div class="book-card">
                    <div class="book-header">
                        <div class="book-cover">📚</div>
                        <div class="book-info">
                            <div class="book-title">데이터 사이언스 입문</div>
                            <div class="book-author">최지영 저</div>
                            <div class="book-status status-available">대출 가능</div>
                        </div>
                    </div>
                    <p class="book-description">데이터 분석과 시각화를 위한 기본 개념과 실습을 제공합니다.</p>
                    <div class="book-details">
                        <div class="book-detail">
                            <svg class="detail-icon" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clip-rule="evenodd"/>
                            </svg>
                            컴퓨터/데이터
                        </div>
                        <div class="book-detail">
                            <svg class="detail-icon" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd"/>
                            </svg>
                            2025-01-18
                        </div>
                    </div>
                </div>
                
                <div class="book-card">
                    <div class="book-header">
                        <div class="book-cover">📚</div>
                        <div class="book-info">
                            <div class="book-title">클라우드 아키텍처</div>
                            <div class="book-author">정현우 저</div>
                            <div class="book-status status-available">대출 가능</div>
                        </div>
                    </div>
                    <p class="book-description">AWS, Azure, GCP를 활용한 클라우드 인프라 설계와 구축 방법을 다룹니다.</p>
                    <div class="book-details">
                        <div class="book-detail">
                            <svg class="detail-icon" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clip-rule="evenodd"/>
                            </svg>
                            컴퓨터/클라우드
                        </div>
                        <div class="book-detail">
                            <svg class="detail-icon" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd"/>
                            </svg>
                            2025-01-19
                        </div>
                    </div>
                </div>
                
                <div class="book-card">
                    <div class="book-header">
                        <div class="book-cover">📚</div>
                        <div class="book-info">
                            <div class="book-title">DevOps 핸드북</div>
                            <div class="book-author">김서연 저</div>
                            <div class="book-status status-available">대출 가능</div>
                        </div>
                    </div>
                    <p class="book-description">CI/CD, 컨테이너, 오케스트레이션을 통한 현대적인 개발 운영 방법론을 다룹니다.</p>
                    <div class="book-details">
                        <div class="book-detail">
                            <svg class="detail-icon" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clip-rule="evenodd"/>
                            </svg>
                            컴퓨터/DevOps
                        </div>
                        <div class="book-detail">
                            <svg class="detail-icon" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd"/>
                            </svg>
                            2025-01-20
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

@app.route('/api/books')
def get_books():
    books = [
        {
            "id": 1,
            "title": "파이썬 프로그래밍",
            "author": "김철수",
            "category": "programming",
            "year": 2023,
            "isbn": "978-89-1234-567-8",
            "status": "available",
            "description": "파이썬 언어의 기초부터 고급 기법까지 체계적으로 학습할 수 있는 도서입니다."
        },
        {
            "id": 2,
            "title": "머신러닝 입문",
            "author": "이영희",
            "category": "science",
            "year": 2023,
            "isbn": "978-89-1234-567-9",
            "status": "borrowed",
            "description": "머신러닝의 기본 개념과 실제 적용 사례를 다루는 입문서입니다."
        },
        {
            "id": 3,
            "title": "웹 개발 완전정복",
            "author": "박민수",
            "category": "programming",
            "year": 2023,
            "isbn": "978-89-1234-568-0",
            "status": "available",
            "description": "HTML, CSS, JavaScript를 활용한 현대적인 웹 개발 방법을 소개합니다."
        }
    ]
    return jsonify({"books": books})

@app.route('/api/categories')
def get_categories():
    categories = [
        {
            "id": 1,
            "name": "프로그래밍",
            "code": "programming",
            "book_count": 45,
            "description": "컴퓨터 프로그래밍 관련 도서"
        },
        {
            "id": 2,
            "name": "과학/기술",
            "code": "science",
            "book_count": 32,
            "description": "과학과 기술 관련 도서"
        },
        {
            "id": 3,
            "name": "문학",
            "code": "literature",
            "book_count": 28,
            "description": "소설, 시, 에세이 등 문학 도서"
        },
        {
            "id": 4,
            "name": "경영/경제",
            "code": "business",
            "book_count": 23,
            "description": "경영과 경제 관련 도서"
        }
    ]
    return jsonify({"categories": categories})

@app.route('/api/search')
def search_books():
    search_results = [
        {
            "id": 1,
            "title": "파이썬 프로그래밍",
            "author": "김철수",
            "category": "programming",
            "relevance_score": 0.95
        },
        {
            "id": 2,
            "title": "머신러닝 입문",
            "author": "이영희",
            "category": "science",
            "relevance_score": 0.87
        }
    ]
    return jsonify({"search_results": search_results})

@app.route('/api/analytics')
def get_catalog_analytics():
    analytics = {
        "total_books": 128,
        "available_books": 89,
        "borrowed_books": 39,
        "categories_count": 8,
        "popular_category": "programming",
        "avg_books_per_category": 16
    }
    return jsonify(analytics)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9080, debug=True) 