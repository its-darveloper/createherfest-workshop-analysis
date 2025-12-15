#!/usr/bin/env python3
"""
#75HER Workshop Facilitator Report Dashboard
- Enhanced UX/UI with improved accessibility, visual hierarchy, and data humanist approach
"""

import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# =========================
# CONFIG
# =========================

CREDENTIALS_FILE = "credentials.json"
SHEET_NAME = "75HER Workshop Survey Responses"

# ==================================
# CSS - ENHANCED DARK MODE
# ==================================

DARK_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Urbanist:wght@600;700;800&family=Inter:wght@400;500;600&display=swap');

:root {
  /* DARK MODE PALETTE - Enhanced Contrast */
  --background: #0d0d0f; 
  --card-bg: #1a1a1c; 
  --card-hover: #202022;
  --border-subtle: rgba(255, 255, 255, 0.12); 

  --primary: #6597f7; 
  --primary-soft: #1f273d; 
  --primary-hover: #7ba9ff;
  
  --body-text: #ffffff; 
  --muted-text: #a8a8a8; 
  
  --success: #34c759; 
  --warning: #ff9500; 
  --alert: #ff3b30; 
  
  --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.3);
  --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.4);
  --shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.5);
}

/* Base App Styling */
.stApp {
  background-color: var(--background);
  font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
  color: var(--body-text);
  line-height: 1.7;
}

.main-container {
  max-width: 1100px;
  margin: 0 auto;
  padding: 40px 24px;
}

/* Typography & Headings */
h1 {
  font-family: 'Urbanist', system-ui, sans-serif;
  font-weight: 700;
  font-size: 2.75rem; 
  letter-spacing: -0.02em; 
  color: var(--body-text);
  margin-bottom: 0.5rem;
  line-height: 1.2;
}

h2 {
  font-family: 'Urbanist', system-ui, sans-serif;
  font-weight: 700;
  font-size: 1.75rem;
  color: var(--body-text);
  letter-spacing: -0.01em;
  margin-top: 3rem;
  margin-bottom: 1.5rem;
  line-height: 1.3;
}

h3 {
  font-family: 'Urbanist', system-ui, sans-serif;
  font-weight: 600;
  font-size: 1.125rem;
  color: var(--muted-text);
  letter-spacing: 0.01em;
  text-transform: uppercase;
  font-size: 0.85rem;
  margin-bottom: 0.75rem;
}

h4 {
  font-family: 'Urbanist', system-ui, sans-serif;
  font-weight: 600;
  font-size: 1.25rem;
  color: var(--body-text);
  margin-bottom: 1rem;
}

.subtitle {
  font-size: 1.125rem;
  color: var(--muted-text);
  margin-top: -0.5rem;
  margin-bottom: 2rem;
  line-height: 1.6;
}

.small-label {
  font-size: 0.85rem; 
  text-transform: uppercase;
  letter-spacing: 0.1em; 
  color: var(--muted-text);
  font-weight: 600;
}

/* Section Dividers */
.section-divider {
  height: 1px;
  background: var(--border-subtle);
  margin: 3rem 0;
}

/* Filter Section */
.filter-section {
  background: var(--card-bg);
  border: 1px solid var(--border-subtle);
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 2rem;
  box-shadow: var(--shadow-sm);
}

/* Hero Card - Enhanced */
.hero-card {
  background: linear-gradient(135deg, var(--primary) 0%, #4a7ed1 100%);
  color: white;
  padding: 32px;
  border-radius: 20px;
  margin: 2rem 0;
  box-shadow: var(--shadow-lg);
  border: none;
  position: relative;
  overflow: hidden;
}

.hero-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0) 100%);
  pointer-events: none;
}

.hero-card > * {
  position: relative;
  z-index: 1;
}

.hero-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: white;
  margin-bottom: 0.75rem;
  font-family: 'Urbanist', sans-serif;
  letter-spacing: -0.01em;
}

.hero-row {
  display: flex;
  align-items: baseline;
  gap: 1rem;
  margin-bottom: 1rem;
}

.hero-health {
  font-size: 2.5rem;
  font-weight: 800;
  font-family: 'Urbanist', sans-serif;
  color: white;
  line-height: 1;
}

.hero-insights {
  font-size: 1rem;
  line-height: 1.7;
  margin: 1.25rem 0;
  opacity: 0.95;
}

/* Recommendation Block - More Prominent */
.recommendation-block {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border-radius: 14px;
  padding: 20px;
  margin-top: 1.5rem;
  border-left: 4px solid rgba(255, 255, 255, 0.8);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.recommendation-label {
  font-size: 0.85rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin-bottom: 0.5rem;
  color: white;
}

.recommendation-text {
  font-size: 1.05rem;
  line-height: 1.6;
  font-weight: 500;
  color: white;
}

.hero-meta {
  font-size: 0.9rem;
  opacity: 0.85;
  margin-top: 1.5rem;
  font-weight: 500;
  color: white;
}

/* Metric Cards - Enhanced Depth */
.metric-card {
  background: var(--card-bg);
  border: 1px solid var(--border-subtle);
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 1.5rem;
  position: relative;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: var(--shadow-sm);
}

.metric-card:hover {
  background: var(--card-hover);
  border-color: rgba(255, 255, 255, 0.2);
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.metric-card h3 {
  margin-top: 0;
  margin-bottom: 1rem;
}

.metric-value {
  font-size: 3rem;
  font-weight: 800;
  font-family: 'Urbanist', sans-serif;
  color: var(--body-text);
  line-height: 1;
  margin-bottom: 0.75rem;
  letter-spacing: -0.02em;
}

.metric-sub {
  font-size: 0.95rem;
  color: var(--muted-text);
  margin-bottom: 1.25rem;
  font-weight: 500;
}

/* Progress Bars - Enhanced with Context */
.progress-bar {
  width: 100%;
  height: 12px;
  background-color: rgba(255, 255, 255, 0.08);
  border-radius: 6px;
  overflow: visible;
  position: relative;
  margin-top: 1rem;
  margin-bottom: 0.75rem;
}

.progress-fill {
  height: 100%;
  border-radius: 6px;
  transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
}

.progress-fill.excellent { 
  background: linear-gradient(90deg, var(--success) 0%, #28a745 100%);
  box-shadow: 0 2px 8px rgba(52, 199, 89, 0.3);
}

.progress-fill.good { 
  background: linear-gradient(90deg, var(--primary) 0%, #5384e6 100%);
  box-shadow: 0 2px 8px rgba(101, 151, 247, 0.3);
}

.progress-fill.warning { 
  background: linear-gradient(90deg, var(--warning) 0%, #ff8800 100%);
  box-shadow: 0 2px 8px rgba(255, 149, 0, 0.3);
}

.progress-fill.alert { 
  background: linear-gradient(90deg, var(--alert) 0%, #ff2020 100%);
  box-shadow: 0 2px 8px rgba(255, 59, 48, 0.3);
}

/* Target Line Indicator */
.target-line {
  position: absolute;
  top: -4px;
  bottom: -4px;
  width: 2px;
  background-color: rgba(255, 255, 255, 0.5);
  z-index: 2;
  transition: all 0.3s ease;
}

.target-line::before {
  content: 'Target';
  position: absolute;
  top: -20px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 0.7rem;
  color: rgba(255, 255, 255, 0.6);
  white-space: nowrap;
  font-weight: 600;
}

/* Pacing Bar - Segmented */
.pacing-bar {
  display: flex;
  width: 100%;
  height: 12px;
  border-radius: 6px;
  overflow: hidden;
  margin: 1rem 0 0.75rem;
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.3);
}

.pace-segment {
  height: 100%;
  transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.pace-just { background: linear-gradient(90deg, var(--success) 0%, #28a745 100%); }
.pace-fast { background: linear-gradient(90deg, var(--warning) 0%, #ff8800 100%); }
.pace-slow { background: linear-gradient(90deg, var(--primary) 0%, #5384e6 100%); }

.pace-legend {
  display: flex;
  justify-content: space-between;
  font-size: 0.85rem;
  margin-top: 0.75rem;
  gap: 1rem;
  flex-wrap: wrap;
}

.pace-legend span {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 500;
}

/* Quote Cards - Enhanced */
.quote-card {
  background: var(--card-bg);
  border: 1px solid var(--border-subtle);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 1rem;
  font-size: 1rem;
  line-height: 1.7;
  color: var(--body-text);
  position: relative;
  padding-left: 3rem;
  box-shadow: var(--shadow-sm);
  transition: all 0.2s ease;
}

.quote-card:hover {
  background: var(--card-hover);
  border-color: rgba(255, 255, 255, 0.2);
  transform: translateX(4px);
}

.quote-card::before {
  content: '"';
  position: absolute;
  left: 16px;
  top: 12px;
  font-size: 3rem;
  font-weight: 700;
  color: var(--primary);
  opacity: 0.4;
  font-family: Georgia, serif;
  line-height: 1;
}

.positive-quote::before {
  color: var(--success);
}

.suggestion-quote::before {
  color: var(--warning);
}

/* Accessibility - Focus States */
button:focus-visible,
select:focus-visible,
input:focus-visible,
a:focus-visible {
  outline: 3px solid var(--primary);
  outline-offset: 2px;
  border-radius: 4px;
}

/* Streamlit Component Overrides */
div[data-testid="stVerticalBlock"] > div:nth-child(1) {
  border-top: none !important;
}

.stSelectbox > div > div {
  background-color: var(--card-bg);
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  color: var(--body-text);
}

.stRadio > div {
  gap: 1rem;
}

.stExpander {
  background-color: var(--card-bg);
  border: 1px solid var(--border-subtle);
  border-radius: 12px;
  margin-bottom: 1.5rem;
}

/* Footer */
.report-footer {
  margin-top: 4rem;
  padding-top: 2rem;
  border-top: 1px solid var(--border-subtle);
  color: var(--muted-text);
  font-size: 0.95rem;
  line-height: 1.7;
}

.report-footer a {
  color: var(--primary);
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s ease;
}

.report-footer a:hover {
  color: var(--primary-hover);
  text-decoration: underline;
}

/* Print Styles */
@media print {
  .stApp { 
    background-color: #ffffff !important; 
    color: #2b2b2b !important; 
  }
  
  header, footer, [data-testid="stSidebar"], 
  button, .stButton, .stRadio, .stSelectbox {
    display: none !important;
  }
  
  .main-container { 
    padding-top: 0;
    max-width: 100%;
  }
  
  .hero-card {
    background: linear-gradient(135deg, #4f7ee3 0%, #3a5fc9 100%) !important;
    page-break-inside: avoid;
    margin-bottom: 1rem;
    padding: 1.5rem;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }
  
  .metric-card { 
    box-shadow: none !important; 
    border: 1px solid #e5e7eb !important; 
    background-color: #ffffff !important;
    page-break-inside: avoid;
    margin-bottom: 1rem;
    padding: 1.25rem;
  }
  
  .quote-card { 
    page-break-inside: avoid;
    padding: 1rem;
    padding-left: 2.5rem;
    margin-bottom: 0.75rem;
    background-color: #ffffff !important;
    border: 1px solid #e5e7eb !important;
  }
  
  .quote-card:nth-child(n+4) { 
    display: none; 
  }
  
  .metric-value { 
    color: #150e60 !important; 
    font-size: 2.25rem;
  }
  
  .section-divider {
    margin: 1.5rem 0;
  }
  
  h2 {
    margin-top: 1.5rem;
    font-size: 1.5rem;
    page-break-after: avoid;
  }
  
  * {
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }
}

/* Responsive Design */
@media (max-width: 768px) {
  .main-container {
    padding: 24px 16px;
  }
  
  h1 {
    font-size: 2rem;
  }
  
  .hero-card {
    padding: 24px;
  }
  
  .hero-health {
    font-size: 2rem;
  }
  
  .metric-value {
    font-size: 2.25rem;
  }
  
  .metric-card {
    padding: 20px;
  }
  
  .pace-legend {
    flex-direction: column;
    gap: 0.5rem;
  }
}
</style>
"""

# ==================================
# CSS - ENHANCED LIGHT MODE
# ==================================

LIGHT_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Urbanist:wght@600;700;800&family=Inter:wght@400;500;600&display=swap');

:root {
  /* LIGHT MODE PALETTE - Enhanced Contrast */
  --background: #f8f9fa;
  --card-bg: #ffffff;
  --card-hover: #fafbfc;
  --border-subtle: #e1e4e8;

  --primary: #4f7ee3;
  --primary-soft: #edf3ff;
  --primary-hover: #3a5fc9;
  
  --body-text: #1a1a1a;
  --muted-text: #6b7280;
  
  --success: #16a34a;
  --warning: #f97316;
  --alert: #dc2626;
  
  --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.08);
  --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.12);
}

/* Base App Styling */
.stApp {
  background-color: var(--background);
  font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
  color: var(--body-text);
  line-height: 1.7;
}

.main-container {
  max-width: 1100px;
  margin: 0 auto;
  padding: 40px 24px;
}

/* Typography & Headings */
h1 {
  font-family: 'Urbanist', system-ui, sans-serif;
  font-weight: 700;
  font-size: 2.75rem;
  letter-spacing: -0.02em;
  color: var(--body-text);
  margin-bottom: 0.5rem;
  line-height: 1.2;
}

h2 {
  font-family: 'Urbanist', system-ui, sans-serif;
  font-weight: 700;
  font-size: 1.75rem;
  color: var(--body-text);
  letter-spacing: -0.01em;
  margin-top: 3rem;
  margin-bottom: 1.5rem;
  line-height: 1.3;
}

h3 {
  font-family: 'Urbanist', system-ui, sans-serif;
  font-weight: 600;
  font-size: 1.125rem;
  color: var(--muted-text);
  letter-spacing: 0.01em;
  text-transform: uppercase;
  font-size: 0.85rem;
  margin-bottom: 0.75rem;
}

h4 {
  font-family: 'Urbanist', system-ui, sans-serif;
  font-weight: 600;
  font-size: 1.25rem;
  color: var(--body-text);
  margin-bottom: 1rem;
}

.subtitle {
  font-size: 1.125rem;
  color: var(--muted-text);
  margin-top: -0.5rem;
  margin-bottom: 2rem;
  line-height: 1.6;
}

.small-label {
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--muted-text);
  font-weight: 600;
}

/* Section Dividers */
.section-divider {
  height: 1px;
  background: var(--border-subtle);
  margin: 3rem 0;
}

/* Filter Section */
.filter-section {
  background: var(--card-bg);
  border: 1px solid var(--border-subtle);
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 2rem;
  box-shadow: var(--shadow-sm);
}

/* Hero Card - Enhanced */
.hero-card {
  background: linear-gradient(135deg, var(--primary) 0%, #3a5fc9 100%);
  color: white;
  padding: 32px;
  border-radius: 20px;
  margin: 2rem 0;
  box-shadow: var(--shadow-lg);
  border: none;
  position: relative;
  overflow: hidden;
}

.hero-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0) 100%);
  pointer-events: none;
}

.hero-card > * {
  position: relative;
  z-index: 1;
}

.hero-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: white;
  margin-bottom: 0.75rem;
  font-family: 'Urbanist', sans-serif;
  letter-spacing: -0.01em;
}

.hero-row {
  display: flex;
  align-items: baseline;
  gap: 1rem;
  margin-bottom: 1rem;
}

.hero-health {
  font-size: 2.5rem;
  font-weight: 800;
  font-family: 'Urbanist', sans-serif;
  color: white;
  line-height: 1;
}

.hero-insights {
  font-size: 1rem;
  line-height: 1.7;
  margin: 1.25rem 0;
  opacity: 0.95;
}

/* Recommendation Block - More Prominent */
.recommendation-block {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border-radius: 14px;
  padding: 20px;
  margin-top: 1.5rem;
  border-left: 4px solid rgba(255, 255, 255, 0.8);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.recommendation-label {
  font-size: 0.85rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin-bottom: 0.5rem;
  color: white;
}

.recommendation-text {
  font-size: 1.05rem;
  line-height: 1.6;
  font-weight: 500;
  color: white;
}

.hero-meta {
  font-size: 0.9rem;
  opacity: 0.85;
  margin-top: 1.5rem;
  font-weight: 500;
  color: white;
}

/* Metric Cards - Enhanced Depth */
.metric-card {
  background: var(--card-bg);
  border: 1px solid var(--border-subtle);
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 1.5rem;
  position: relative;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: var(--shadow-sm);
}

.metric-card:hover {
  background: var(--card-hover);
  border-color: #cbd5e0;
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.metric-card h3 {
  margin-top: 0;
  margin-bottom: 1rem;
}

.metric-value {
  font-size: 3rem;
  font-weight: 800;
  font-family: 'Urbanist', sans-serif;
  color: var(--body-text);
  line-height: 1;
  margin-bottom: 0.75rem;
  letter-spacing: -0.02em;
}

.metric-sub {
  font-size: 0.95rem;
  color: var(--muted-text);
  margin-bottom: 1.25rem;
  font-weight: 500;
}

/* Progress Bars - Enhanced with Context */
.progress-bar {
  width: 100%;
  height: 12px;
  background-color: #f0f0f0;
  border-radius: 6px;
  overflow: visible;
  position: relative;
  margin-top: 1rem;
  margin-bottom: 0.75rem;
}

.progress-fill {
  height: 100%;
  border-radius: 6px;
  transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
}

.progress-fill.excellent {
  background: linear-gradient(90deg, var(--success) 0%, #14a048 100%);
  box-shadow: 0 2px 8px rgba(22, 163, 74, 0.25);
}

.progress-fill.good {
  background: linear-gradient(90deg, var(--primary) 0%, #3a5fc9 100%);
  box-shadow: 0 2px 8px rgba(79, 126, 227, 0.25);
}

.progress-fill.warning {
  background: linear-gradient(90deg, var(--warning) 0%, #ea580c 100%);
  box-shadow: 0 2px 8px rgba(249, 115, 22, 0.25);
}

.progress-fill.alert {
  background: linear-gradient(90deg, var(--alert) 0%, #b91c1c 100%);
  box-shadow: 0 2px 8px rgba(220, 38, 38, 0.25);
}

/* Target Line Indicator */
.target-line {
  position: absolute;
  top: -4px;
  bottom: -4px;
  width: 2px;
  background-color: rgba(0, 0, 0, 0.4);
  z-index: 2;
  transition: all 0.3s ease;
}

.target-line::before {
  content: 'Target';
  position: absolute;
  top: -20px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 0.7rem;
  color: rgba(0, 0, 0, 0.6);
  white-space: nowrap;
  font-weight: 600;
}

/* Pacing Bar - Segmented */
.pacing-bar {
  display: flex;
  width: 100%;
  height: 12px;
  border-radius: 6px;
  overflow: hidden;
  margin: 1rem 0 0.75rem;
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.1);
}

.pace-segment {
  height: 100%;
  transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.pace-just { background: linear-gradient(90deg, var(--success) 0%, #14a048 100%); }
.pace-fast { background: linear-gradient(90deg, var(--warning) 0%, #ea580c 100%); }
.pace-slow { background: linear-gradient(90deg, var(--primary) 0%, #3a5fc9 100%); }

.pace-legend {
  display: flex;
  justify-content: space-between;
  font-size: 0.85rem;
  margin-top: 0.75rem;
  gap: 1rem;
  flex-wrap: wrap;
}

.pace-legend span {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 500;
}

/* Quote Cards - Enhanced */
.quote-card {
  background: var(--card-bg);
  border: 1px solid var(--border-subtle);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 1rem;
  font-size: 1rem;
  line-height: 1.7;
  color: var(--body-text);
  position: relative;
  padding-left: 3rem;
  box-shadow: var(--shadow-sm);
  transition: all 0.2s ease;
}

.quote-card:hover {
  background: var(--card-hover);
  border-color: #cbd5e0;
  transform: translateX(4px);
}

.quote-card::before {
  content: '"';
  position: absolute;
  left: 16px;
  top: 12px;
  font-size: 3rem;
  font-weight: 700;
  color: var(--primary);
  opacity: 0.3;
  font-family: Georgia, serif;
  line-height: 1;
}

.positive-quote::before {
  color: var(--success);
}

.suggestion-quote::before {
  color: var(--warning);
}

/* Accessibility - Focus States */
button:focus-visible,
select:focus-visible,
input:focus-visible,
a:focus-visible {
  outline: 3px solid var(--primary);
  outline-offset: 2px;
  border-radius: 4px;
}

/* Streamlit Component Overrides */
div[data-testid="stVerticalBlock"] > div:nth-child(1) {
  border-top: none !important;
}

.stSelectbox > div > div {
  background-color: var(--card-bg);
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  color: var(--body-text);
}

.stRadio > div {
  gap: 1rem;
}

.stExpander {
  background-color: var(--card-bg);
  border: 1px solid var(--border-subtle);
  border-radius: 12px;
  margin-bottom: 1.5rem;
}

/* Footer */
.report-footer {
  margin-top: 4rem;
  padding-top: 2rem;
  border-top: 1px solid var(--border-subtle);
  color: var(--muted-text);
  font-size: 0.95rem;
  line-height: 1.7;
}

.report-footer a {
  color: var(--primary);
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s ease;
}

.report-footer a:hover {
  color: var(--primary-hover);
  text-decoration: underline;
}

/* Print Styles */
@media print {
  .stApp {
    background-color: #ffffff !important;
    color: #2b2b2b !important;
  }
  
  header, footer, [data-testid="stSidebar"],
  button, .stButton, .stRadio, .stSelectbox {
    display: none !important;
  }
  
  .main-container {
    padding-top: 0;
    max-width: 100%;
  }
  
  .hero-card {
    background: linear-gradient(135deg, #4f7ee3 0%, #3a5fc9 100%) !important;
    page-break-inside: avoid;
    margin-bottom: 1rem;
    padding: 1.5rem;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }
  
  .metric-card {
    box-shadow: none !important;
    border: 1px solid #e5e7eb !important;
    background-color: #ffffff !important;
    page-break-inside: avoid;
    margin-bottom: 1rem;
    padding: 1.25rem;
  }
  
  .quote-card {
    page-break-inside: avoid;
    padding: 1rem;
    padding-left: 2.5rem;
    margin-bottom: 0.75rem;
    background-color: #ffffff !important;
    border: 1px solid #e5e7eb !important;
  }
  
  .quote-card:nth-child(n+4) {
    display: none;
  }
  
  .metric-value {
    color: #150e60 !important;
    font-size: 2.25rem;
  }
  
  .section-divider {
    margin: 1.5rem 0;
  }
  
  h2 {
    margin-top: 1.5rem;
    font-size: 1.5rem;
    page-break-after: avoid;
  }
  
  * {
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }
}

/* Responsive Design */
@media (max-width: 768px) {
  .main-container {
    padding: 24px 16px;
  }
  
  h1 {
    font-size: 2rem;
  }
  
  .hero-card {
    padding: 24px;
  }
  
  .hero-health {
    font-size: 2rem;
  }
  
  .metric-value {
    font-size: 2.25rem;
  }
  
  .metric-card {
    padding: 20px;
  }
  
  .pace-legend {
    flex-direction: column;
    gap: 0.5rem;
  }
}
</style>
"""

# =========================
# DATA LOADER
# =========================

@st.cache_data
def load_data():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            CREDENTIALS_FILE, scope
        )
        client = gspread.authorize(creds)
        sheet = client.open(SHEET_NAME).sheet1
        data = sheet.get_all_records()
        return pd.DataFrame(data)
    except FileNotFoundError:
        st.error("Credential file not found. Using dummy data for demonstration.")
        data = {
            'Which session did you attend?': ['Data Viz Fundamentals', 'Data Viz Fundamentals', 'Advanced Python', 'Advanced Python'],
            'How confident do you feel implementing what you learned today? ': [5, 4, 3, 5],
            'The facilitator today was:': ['🌟 Excellent - Clear, engaging, well-paced', '✅ Good - Helpful and informative', '✅ Good - Helpful and informative', '🌟 Excellent - Clear, engaging, well-paced'],
            'Was the workshop pace/level right for you?': ['Just right - Perfect pace for my level', 'Slightly too slow - I wanted to go deeper', 'Slightly too fast - I could barely keep up', 'Just right - Perfect pace for my level'],
            "Did you create a hands-on deliverable today?": ['Yes - I created/started [code sample / prototype / document / project file]', 'Yes - I followed along but need to finish it', 'No - I ran out of time', 'Yes - I created/started [code sample / prototype / document / project file]'],
            "Your background in this topic:": ["Beginner", "Intermediate", "Expert", "Beginner"],
            "What did the facilitator do especially well? Any suggestions for improvement?": ["Very clear examples and great energy.", "I wish we had more time for Q&A.", "Too fast for me, slow down!", "Pacing was spot-on. Solid content."],
            "What's ONE thing you'll try this week based on today's workshop?": ["Apply the Gestalt principles to my next report.", "Refactor my old Python script with new functions.", "Nothing yet, need to review my notes.", "Build a new dashboard with Streamlit."]
        }
        df = pd.DataFrame(data)
        return df

# =========================
# METRIC CALCULATION
# =========================

def calculate_metrics(df_w: pd.DataFrame) -> dict:
    total = len(df_w)
    if total == 0:
        return {
            "total": 0, "confidence": 0, "excellent_pct": 0, "good_pct": 0,
            "pace_just": 0, "pace_fast": 0, "pace_slow": 0,
            "hands_completion": 0, "hands_created": 0, "hands_followed": 0
        }

    col_conf = "How confident do you feel implementing what you learned today? "
    col_fac = "The facilitator today was:"
    col_pace = "Was the workshop pace/level right for you?"
    col_hands = "Did you create a hands-on deliverable today?"

    conf = pd.to_numeric(df_w[col_conf], errors="coerce").mean()

    # Facilitator
    fac_counts = df_w[col_fac].value_counts()
    exc = fac_counts.get("🌟 Excellent - Clear, engaging, well-paced", 0)
    good = fac_counts.get("✅ Good - Helpful and informative", 0)
    excellent_pct = (exc / total * 100)
    good_pct = ((exc + good) / total * 100)

    # Pacing
    pace_counts = df_w[col_pace].value_counts()
    just = pace_counts.get("Just right - Perfect pace for my level", 0)
    fast = (
        pace_counts.get("Slightly too fast - I could barely keep up", 0)
        + pace_counts.get("Too advanced - I felt lost", 0)
    )
    slow = (
        pace_counts.get("Slightly too slow - I wanted to go deeper", 0)
        + pace_counts.get("Too basic - I already knew most of this", 0)
    )
    pace_just = (just / total * 100)
    pace_fast = (fast / total * 100)
    pace_slow = (slow / total * 100)

    # Hands-on
    hands_counts = df_w[col_hands].value_counts()
    created = hands_counts.get(
        "Yes - I created/started [code sample / prototype / document / project file]", 0
    )
    followed = hands_counts.get(
        "Yes - I followed along but need to finish it", 0
    )
    hands_completion = ((created + followed) / total * 100)
    hands_created = (created / total * 100)
    hands_followed = (followed / total * 100)

    return {
        "total": total,
        "confidence": float(conf) if pd.notna(conf) else 0.0,
        "excellent_pct": excellent_pct,
        "good_pct": good_pct,
        "pace_just": pace_just,
        "pace_fast": pace_fast,
        "pace_slow": pace_slow,
        "hands_completion": hands_completion,
        "hands_created": hands_created,
        "hands_followed": hands_followed,
    }

# =========================
# RENDER FUNCTIONS
# =========================

def render_hero_card(metrics: dict, workshop_name: str, total_responses: int):
    health_score = (
        (metrics["confidence"] / 5.0) * 25
        + (metrics["excellent_pct"] / 100) * 25
        + (metrics["hands_created"] / 100) * 25
        + (metrics["pace_just"] / 100) * 25
    )

    # Enhanced recommendation logic
    if metrics["confidence"] < 3.5 and metrics["hands_created"] < 40:
        recommendation = "Add more structured, guided, hands-on time with a simpler, clear deliverable."
    elif metrics["pace_fast"] > 30:
        recommendation = "Slow down or add comprehension checkpoints after key concepts."
    elif metrics["pace_slow"] > 25:
        recommendation = "Increase content density or add optional, deeper content for experts."
    elif health_score >= 80:
        recommendation = "Workshop performing excellently—maintain current structure and content!"
    else:
        recommendation = "Solid foundation. Focus on improving one of the four key metrics below."

    insights = []
    if metrics["confidence"] >= 4.0:
        insights.append("✓ Strong confidence gains")
    elif metrics["confidence"] < 3.5:
        insights.append("⚠ Confidence below 3.5 target")

    if metrics["hands_created"] >= 50:
        insights.append("✓ High hands-on deliverable rate")
    elif metrics["hands_created"] < 30:
        insights.append("⚠ Increase guided practice time")
        
    if metrics["pace_fast"] > 20:
        insights.append(f"⚠ Pacing too fast for {metrics['pace_fast']:.0f}% of builders")

    hero_html = f"""
    <div class="hero-card">
      <div class="hero-title">{workshop_name}</div>
      <div class="hero-row">
        <span class="small-label">Overall Health</span>
        <span class="hero-health">{health_score:.0f}/100</span>
      </div>
      <div class="hero-insights">
        {' · '.join(insights) if insights else "Steady performance across core metrics."}
      </div>
      
      <div class="recommendation-block">
        <div class="recommendation-label">🎯 Next Action Focus</div>
        <div class="recommendation-text">{recommendation}</div>
      </div>
      
      <div class="hero-meta">
        {total_responses} responses · Generated {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
      </div>
    </div>
    """
    st.markdown(hero_html, unsafe_allow_html=True)


def render_confidence_card(metrics: dict):
    confidence = metrics["confidence"]
    total = metrics["total"]
    
    if confidence >= 4.0:
        bar_color, status = "excellent", "🎯 Excellent"
    elif confidence >= 3.5:
        bar_color, status = "good", "✅ Meets Target"
    elif confidence >= 3.0:
        bar_color, status = "warning", "⚠️ Fair"
    else:
        bar_color, status = "alert", "❗ Needs Work"
    
    width = (confidence / 5.0) * 100
    value_color_var = f"var(--{bar_color})" if bar_color in ["warning", "alert", "excellent", "good"] else "var(--body-text)"
    status_text = status 
    
    if total < 10 and total > 0:
        value_color_var = "var(--muted-text)" 
        status_text = f"❗ LOW SAMPLE ({total} responses)"
    elif total == 0:
        value_color_var = "var(--muted-text)"
        status_text = f"No Responses"

    html = f"""
    <div class="metric-card">
      <h3>Confidence Gains</h3>
      <div class="metric-value" style="color:{value_color_var};">{confidence:.1f}<span style="font-size:1.5rem;color:var(--muted-text);">/5.0</span></div>
      <div class="metric-sub">{status_text}</div>
      <div class="progress-bar">
        <div class="target-line" style="left:70%;"></div> 
        <div class="progress-fill {bar_color}" style="width:{width}%;"></div>
      </div>
      <div style="font-size:0.85rem; color:var(--muted-text); margin-top:8px; display:flex; justify-content: space-between;">
        <span>Low (1.0)</span>
        <span style="font-weight:600;">Target (3.5)</span>
        <span>High (5.0)</span>
      </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_pacing_card(metrics: dict):
    j, f, s = metrics["pace_just"], metrics["pace_fast"], metrics["pace_slow"]
    
    dominant_pace_html = f"{j:.0f}% <span style='font-size:1.5rem;color:var(--muted-text);'>just right</span>"
    pace_text_color = "var(--success)"

    if f > j and f > s:
        dominant_pace_html = f"{f:.0f}% <span style='font-size:1.5rem;color:var(--muted-text);'>too fast</span>"
        pace_text_color = "var(--warning)"
    elif s > j and s > f:
        dominant_pace_html = f"{s:.0f}% <span style='font-size:1.5rem;color:var(--muted-text);'>too slow</span>"
        pace_text_color = "var(--primary)"

    html = f"""
    <div class="metric-card">
      <h3>Workshop Pacing</h3>
      <div class="metric-value" style="color:{pace_text_color};">{dominant_pace_html}</div>
      <div class="pacing-bar">
        <div class="pace-segment pace-just" style="width:{j}%;"></div>
        <div class="pace-segment pace-fast" style="width:{f}%;"></div>
        <div class="pace-segment pace-slow" style="width:{s}%;"></div>
      </div>
      <div class="pace-legend">
        <span style="color:var(--success);">✓ Just Right: {j:.0f}%</span>
        <span style="color:var(--warning);">⚡ Too Fast: {f:.0f}%</span>
        <span style="color:var(--primary);">🐢 Too Slow: {s:.0f}%</span>
      </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_facilitator_card(metrics: dict):
    excellent_pct = metrics["excellent_pct"]
    good_pct = metrics["good_pct"]

    if excellent_pct >= 70:
        status_icon, status_text, bar_color = "🌟", "Outstanding", "excellent"
    elif excellent_pct >= 50:
        status_icon, status_text, bar_color = "✅", "Strong", "good"
    else:
        status_icon, status_text, bar_color = "📊", "Developing", "warning"
        
    width = excellent_pct

    html = f"""
    <div class="metric-card">
      <h3>Facilitator Rating</h3>
      <div class="metric-value">{excellent_pct:.0f}%<span style="font-size:1.5rem;color:var(--muted-text);"> excellent</span></div>
      <div class="metric-sub">{status_icon} {status_text}</div>
      <div class="progress-bar">
        <div class="progress-fill {bar_color}" style="width:{width}%;"></div>
      </div>
      <div style="font-size:0.85rem;color:var(--muted-text);margin-top:0.75rem;">
        {good_pct:.0f}% rated "Good" or higher (Target: 80%)
      </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_hands_on_card(metrics: dict):
    created = metrics["hands_created"]
    followed = metrics["hands_followed"]
    completion = metrics["hands_completion"]

    if created >= 50:
        bar_color, status = "excellent", "🎨 High Deliverable Rate"
    elif created >= 30:
        bar_color, status = "good", "✅ Good Participation"
    else:
        bar_color, status = "warning", "⚠️ Increase Guided Practice"

    html = f"""
    <div class="metric-card">
      <h3>Hands-On Engagement</h3>
      <div class="metric-value">{created:.0f}%<span style="font-size:1.5rem;color:var(--muted-text);"> created deliverable</span></div>
      <div class="metric-sub">{status} ({completion:.0f}% total completion)</div>
      
      <div class="pacing-bar" style="height:8px; margin: 8px 0;">
        <div class="pace-segment progress-fill excellent" style="width:{created}%;"></div>
        <div class="pace-segment progress-fill good" style="width:{followed}%;"></div>
      </div>
      
      <div class="pace-legend" style="font-size:0.85rem;">
        <span style="color:var(--success);">Created: {created:.0f}%</span>
        <span style="color:var(--primary);">Followed: {followed:.0f}%</span>
      </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_summary_quotes(df_w: pd.DataFrame):
    pos_col = "What did the facilitator do especially well? Any suggestions for improvement?"
    act_col = "What's ONE thing you'll try this week based on today's workshop?"
    
    if pos_col in df_w.columns:
        positive_feedback = [q for q in df_w[pos_col].dropna() if all(k not in q.lower() for k in ["suggestion", "improve", "faster", "slower"])][:5]
        suggestions = [q for q in df_w[pos_col].dropna() if any(k in q.lower() for k in ["suggestion", "improve", "faster", "slower"])][:5]

        with st.expander("💬 Review Feedback & Suggestions", expanded=True):
            
            st.markdown("### 💚 What builders loved")
            if positive_feedback:
                for q in positive_feedback:
                    st.markdown(f'<div class="quote-card positive-quote">"{q}"</div>', unsafe_allow_html=True)
            else:
                st.info("No explicit positive feedback found.")

            st.markdown("### 🚧 Constructive Suggestions")
            if suggestions:
                for q in suggestions:
                    st.markdown(f'<div class="quote-card suggestion-quote">"{q}"</div>', unsafe_allow_html=True)
            else:
                st.info("No explicit suggestions for improvement found.")
    
    st.markdown("### 🚀 Commitment to Action")
    if act_col in df_w.columns:
        action_items = df_w[act_col].dropna().head(4)
        if not action_items.empty:
            for q in action_items:
                st.markdown(f'<div class="quote-card">"{q}"</div>', unsafe_allow_html=True)
        else:
            st.info("No actionable commitments recorded yet.")

# =========================
# THEME TOGGLE
# =========================

def toggle_theme():
    if 'theme' not in st.session_state:
        st.session_state['theme'] = 'dark'
    
    st.session_state['theme'] = 'light' if st.session_state['theme'] == 'dark' else 'dark'

# =========================
# MAIN
# =========================

def main():
    # Initialize Theme
    if 'theme' not in st.session_state:
        st.session_state['theme'] = 'dark'

    # Set Page Config & Apply Dynamic CSS
    st.set_page_config(page_title="#75HER Workshop Report", layout="wide")
    
    current_css = DARK_CSS if st.session_state['theme'] == 'dark' else LIGHT_CSS
    st.markdown(current_css, unsafe_allow_html=True)
    
    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    # Sidebar with Theme Toggle
    with st.sidebar:
        theme_icon = "💡" if st.session_state['theme'] == 'dark' else "🌙"
        theme_label = "Switch to Light Mode" if st.session_state['theme'] == 'dark' else "Switch to Dark Mode"
        st.button(f"{theme_icon} {theme_label}", on_click=toggle_theme, use_container_width=True)
        st.markdown("---")
        st.markdown("### About This Dashboard")
        st.markdown("""
        This report provides actionable insights from participant feedback to help facilitators improve their workshops.
        
        **Key Metrics:**
        - Confidence gains
        - Facilitator effectiveness
        - Pacing balance
        - Hands-on engagement
        """)

    st.title("✨ #75HER Workshop Facilitator Report")
    st.markdown('<div class="subtitle">Actionable insights derived from participant feedback.</div>', unsafe_allow_html=True)

    df = load_data()

    workshop_col = "Which session did you attend?"
    bg_col = "Your background in this topic:"
    
    if df.empty or workshop_col not in df.columns:
        st.error("Data could not be loaded or is empty. Please check the credentials and sheet name.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    workshops = df[workshop_col].dropna().unique()
    
    # Enhanced Filter Section
    st.markdown('<div class="filter-section">', unsafe_allow_html=True)
    st.markdown("### 🎯 Workshop Selection & Filters")
    
    col_select, col_filter = st.columns([2, 1])

    with col_select:
        selected = st.selectbox(
            "Select Workshop Focus",
            sorted(workshops),
            key="workshop_select",
            help="Choose which workshop to analyze"
        )
        
    df_w = df[df[workshop_col] == selected].copy()

    with col_filter:
        opts = ["All backgrounds"] + sorted(df_w[bg_col].dropna().unique().tolist())
        choice = st.selectbox(
            "Filter by Background",
            opts,
            key="background_filter",
            help="Filter responses by participant experience level"
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    if choice != "All backgrounds":
        df_w = df_w[df_w[bg_col] == choice]
    
    if len(df_w) == 0:
        st.warning(f"No responses for **{selected}** with the background: **{choice}**.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    metrics = calculate_metrics(df_w)

    # Hero Card
    render_hero_card(metrics, selected, len(df_w))

    # Section Divider
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # Metric Cards
    st.markdown('## 📊 Core Metric Analysis')
    
    col1, col2 = st.columns(2)
    with col1:
        render_confidence_card(metrics)
        render_hands_on_card(metrics)
    with col2:
        render_facilitator_card(metrics)
        render_pacing_card(metrics)

    # Section Divider
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # View Toggle - Move Higher
    st.markdown('## 💬 Participant Feedback')
    
    view_mode = st.radio(
        "Response View",
        ["📋 Summary (Quotes & Actions)", "📈 Detailed Distributions (Charts)"],
        horizontal=True,
    )
    
    if view_mode == "📋 Summary (Quotes & Actions)":
        render_summary_quotes(df_w)
    else:
        st.markdown("### 📈 Detailed Response Distributions")
        
        conf_col = "How confident do you feel implementing what you learned today? "
        if conf_col in df_w.columns:
            st.markdown("#### Confidence Level (1-5)")
            conf_data = df_w[conf_col].value_counts().reset_index()
            conf_data.columns = ['Confidence Score', 'Count']
            conf_data['Confidence Score'] = conf_data['Confidence Score'].astype(str)

            st.bar_chart(conf_data.set_index('Confidence Score'), use_container_width=True, color='#6597f7')
            
        fac_col = "The facilitator today was:"
        if fac_col in df_w.columns:
            st.markdown("#### Facilitator Rating")
            fac_data = df_w[fac_col].value_counts().reset_index()
            fac_data.columns = ['Rating', 'Count']
            
            st.dataframe(fac_data, use_container_width=True, hide_index=True)

    # Section Divider
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # Export instructions
    with st.expander("📄 Export & Share This Report"):
        st.markdown("""
        ### How to Generate a PDF
        
        Use your browser's print function to generate a clean PDF report optimized for sharing.
        
        **Instructions (Chrome/Safari/Edge):**
        1. Press `Cmd + P` (Mac) or `Ctrl + P` (Windows)
        2. Set **Destination** to: **Save as PDF**
        3. Ensure **'Background graphics'** is **enabled**
        4. Set **Layout** to: **Portrait**
        5. Click **Save**
        
        The PDF will automatically hide interactive elements and optimize spacing for a professional one-page report.
        """)

    # Footer
    footer_html = """
    <div class="report-footer">
        <p>
            <strong>Thank you for contributing to CreateHER Fest as a workshop facilitator!</strong> Your dedication helps empower the builder community.
        </p>
        <p>
            This impact report was built by <a href="https://www.linkedin.com/in/darveloper/" target="_blank">Darveloper</a> 
            and powered by <a href="https://createherfest.com" target="_blank">CreateHER Fest</a>.
        </p>
        <p>
            We value your feedback. Let us know if this report was helpful or share suggestions by emailing 
            <a href="mailto:darlyze@createherfest.com">darlyze@createherfest.com</a>.
        </p>
    </div>
    """
    st.markdown(footer_html, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()