#!/usr/bin/env python3
"""
75HER Workshop Facilitator Report - PDF Generator with Branding
Creates beautifully branded PDF reports from JotForm survey data
"""

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import datetime
from weasyprint import HTML, CSS
from io import StringIO
import base64

# ============================================
# CONFIGURATION
# ============================================
CREDENTIALS_FILE = 'credentials.json'
SHEET_NAME = '75HER Workshop Survey Responses'

# CreateHER Brand Colors
COLORS = {
    'primary': '#473dc6',           # Deep purple
    'light_bg': '#f1eae7',          # Warm cream
    'light_blue': '#cfe6ff',        # Light blue
    'accent': '#caa3d6',            # Mauve/pink
    'dark': '#150e60',              # Dark navy
    'text': '#2b2b2b',              # Dark gray
}

WORKSHOPS = {
    'AI': 'Building a Production AI Agent : Women in Tech and Innovation',
    'Visibility': 'Making Your Confidence VISIBLE : Women Creators and Technologists',
    'Voice': 'Voice & Pitch for Power: Communicating Technical Ideas With Clarity and Authority'
}

# ============================================
# GOOGLE SHEETS CONNECTION
# ============================================
def get_survey_data():
    """Connect to Google Sheets and pull all survey responses"""
    print("🔗 Connecting to Google Sheets...")
    
    scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
    ]
    
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            CREDENTIALS_FILE, scope
        )
        client = gspread.authorize(creds)
        sheet = client.open(SHEET_NAME).sheet1
        data = sheet.get_all_records()
        
        print(f"✅ Connected! Found {len(data)} survey responses")
        return pd.DataFrame(data)
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

# ============================================
# ANALYSIS FUNCTIONS
# ============================================

def calculate_confidence_score(df, confidence_col):
    """Calculate average confidence score (1-5 scale)"""
    try:
        scores = pd.to_numeric(df[confidence_col], errors='coerce')
        avg = scores.mean()
        return 0.0 if pd.isna(avg) else float(avg)
    except:
        return 0.0

def analyze_facilitator_rating(df, rating_col):
    """Analyze facilitator rating"""
    ratings = df[rating_col].value_counts()
    total = len(df)
    
    excellent = ratings.get('🌟 Excellent - Clear, engaging, well-paced', 0)
    good = ratings.get('✅ Good - Helpful and informative', 0)
    
    excellent_pct = (excellent / total * 100) if total > 0 else 0
    good_pct = (good / total * 100) if total > 0 else 0
    
    return {
        'excellent': excellent,
        'excellent_pct': excellent_pct,
        'good': good,
        'good_pct': good_pct,
        'total': total
    }

def analyze_pace(df, pace_col):
    """Analyze workshop pacing"""
    pace_counts = df[pace_col].value_counts()
    total = len(df)
    
    just_right = pace_counts.get('Just right - Perfect pace for my level', 0)
    too_fast = pace_counts.get('Slightly too fast - I could barely keep up', 0) + \
               pace_counts.get('Too advanced - I felt lost', 0)
    too_slow = pace_counts.get('Slightly too slow - I wanted to go deeper', 0) + \
               pace_counts.get('Too basic - I already knew most of this', 0)
    
    return {
        'just_right': just_right,
        'just_right_pct': (just_right / total * 100) if total > 0 else 0,
        'too_fast': too_fast,
        'too_fast_pct': (too_fast / total * 100) if total > 0 else 0,
        'too_slow': too_slow,
        'too_slow_pct': (too_slow / total * 100) if total > 0 else 0
    }

def analyze_hands_on(df, hands_on_col):
    """Analyze hands-on completion"""
    counts = df[hands_on_col].value_counts()
    total = len(df)
    
    created = counts.get('Yes - I created/started [code sample / prototype / document / project file]', 0)
    followed = counts.get('Yes - I followed along but need to finish it', 0)
    
    return {
        'created': created,
        'followed': followed,
        'completion_rate': ((created + followed) / total * 100) if total > 0 else 0
    }

def extract_top_quotes(text_series, n=5):
    """Extract top quotes"""
    quotes = []
    for response in text_series.dropna():
        response = str(response).strip()
        if len(response) > 10:
            quotes.append(response)
    return quotes[:n]

# ============================================
# HTML REPORT GENERATION
# ============================================

def generate_html_report(df, workshop_filter=None):
    """Generate beautifully branded HTML report"""
    
    # Filter by workshop
    if workshop_filter:
        df = df[df['Which session did you attend?'] == workshop_filter]
        workshop_name = workshop_filter
    else:
        workshop_name = "All Workshops"
    
    if len(df) == 0:
        print(f"❌ No responses found for: {workshop_name}")
        return None
    
    print(f"📊 Analyzing {len(df)} responses...")
    
    # Column references (with space fix)
    COL_CONFIDENCE = 'How confident do you feel implementing what you learned today? '
    COL_FACILITATOR_RATING = 'The facilitator today was:'
    COL_PACE = 'Was the workshop pace/level right for you?'
    COL_HANDS_ON = 'Did you create a hands-on deliverable today?'
    COL_FEEDBACK = 'What did the facilitator do especially well? Any suggestions for improvement?'
    COL_ONE_THING = "What's ONE thing you'll try this week based on today's workshop?"
    
    # Calculate metrics
    total_responses = len(df)
    confidence_score = calculate_confidence_score(df, COL_CONFIDENCE)
    facilitator_rating = analyze_facilitator_rating(df, COL_FACILITATOR_RATING)
    pace_analysis = analyze_pace(df, COL_PACE)
    hands_on_analysis = analyze_hands_on(df, COL_HANDS_ON)
    
    # Extract quotes
    feedback_quotes = extract_top_quotes(df[COL_FEEDBACK], n=4)
    action_quotes = extract_top_quotes(df[COL_ONE_THING], n=4)
    
    # Generate HTML
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Workshop Report: {workshop_name}</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Urbanist:wght@600;700;800&display=swap" rel="stylesheet">
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                color: {COLORS['text']};
                line-height: 1.6;
                background: {COLORS['light_bg']};
                padding: 0;
            }}
            
            .container {{
                max-width: 850px;
                margin: 0 auto;
                background: white;
                page-break-after: always;
            }}
            
            /* COVER SECTION */
            .cover {{
                background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['accent']} 100%);
                color: white;
                padding: 60px 40px;
                text-align: center;
            }}
            
            .cover h1 {{
                font-family: 'Urbanist', sans-serif;
                font-size: 42px;
                font-weight: 800;
                margin-bottom: 20px;
                line-height: 1.2;
            }}
            
            .cover .meta {{
                font-size: 14px;
                opacity: 0.95;
                margin-top: 30px;
            }}
            
            .cover .brand {{
                font-size: 11px;
                letter-spacing: 2px;
                text-transform: uppercase;
                opacity: 0.8;
                margin-bottom: 20px;
            }}
            
            /* HEADER */
            .header {{
                background: {COLORS['light_blue']};
                padding: 25px 40px;
                border-left: 5px solid {COLORS['primary']};
            }}
            
            .header h2 {{
                font-family: 'Urbanist', sans-serif;
                font-size: 26px;
                font-weight: 700;
                color: {COLORS['primary']};
                margin-bottom: 12px;
            }}
            
            .header p {{
                font-size: 13px;
                color: {COLORS['text']};
                opacity: 0.8;
            }}
            
            /* MAIN CONTENT */
            .content {{
                padding: 40px;
            }}
            
            .section {{
                margin-bottom: 40px;
            }}
            
            .section h3 {{
                font-family: 'Urbanist', sans-serif;
                font-size: 20px;
                font-weight: 700;
                color: {COLORS['primary']};
                margin-bottom: 20px;
                padding-bottom: 12px;
                border-bottom: 2px solid {COLORS['light_blue']};
            }}
            
            /* METRICS */
            .metrics {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
                margin-bottom: 30px;
            }}
            
            .metric-box {{
                background: {COLORS['light_bg']};
                padding: 20px;
                border-radius: 8px;
                border-left: 4px solid {COLORS['accent']};
            }}
            
            .metric-label {{
                font-size: 12px;
                text-transform: uppercase;
                letter-spacing: 1px;
                color: {COLORS['primary']};
                font-weight: 600;
                margin-bottom: 8px;
            }}
            
            .metric-value {{
                font-size: 28px;
                font-weight: 700;
                color: {COLORS['dark']};
                margin-bottom: 4px;
            }}
            
            .metric-subtitle {{
                font-size: 12px;
                color: {COLORS['text']};
                opacity: 0.7;
            }}
            
            /* TABLE */
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
                font-size: 13px;
            }}
            
            th {{
                background: {COLORS['primary']};
                color: white;
                padding: 12px;
                text-align: left;
                font-weight: 600;
                font-family: 'Urbanist', sans-serif;
            }}
            
            td {{
                padding: 12px;
                border-bottom: 1px solid {COLORS['light_bg']};
            }}
            
            tr:nth-child(even) {{
                background: {COLORS['light_bg']};
            }}
            
            /* QUOTES */
            .quote-box {{
                background: {COLORS['light_blue']};
                border-left: 4px solid {COLORS['accent']};
                padding: 16px;
                margin: 12px 0;
                border-radius: 4px;
                font-size: 13px;
                font-style: italic;
                color: {COLORS['dark']};
            }}
            
            /* RECOMMENDATIONS */
            .recommendation {{
                background: {COLORS['light_bg']};
                border-left: 4px solid {COLORS['primary']};
                padding: 12px 16px;
                margin: 10px 0;
                border-radius: 4px;
                font-size: 13px;
            }}
            
            /* STATUS BADGES */
            .badge {{
                display: inline-block;
                padding: 6px 12px;
                border-radius: 20px;
                font-size: 11px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                margin-right: 8px;
            }}
            
            .badge.excellent {{
                background: #d4edda;
                color: #155724;
            }}
            
            .badge.good {{
                background: #d1ecf1;
                color: #0c5460;
            }}
            
            .badge.warning {{
                background: #fff3cd;
                color: #856404;
            }}
            
            /* FOOTER */
            .footer {{
                background: {COLORS['dark']};
                color: white;
                padding: 20px 40px;
                text-align: center;
                font-size: 11px;
                margin-top: 40px;
            }}
            
            .footer a {{
                color: {COLORS['light_blue']};
                text-decoration: none;
            }}
            
            /* PAGE BREAK */
            .page-break {{
                page-break-after: always;
                margin: 40px 0;
                border-top: 2px dashed {COLORS['light_blue']};
            }}
        </style>
    </head>
    <body>
        <!-- COVER -->
        <div class="container">
            <div class="cover">
                <div class="brand">📊 #75HER Workshop Analysis</div>
                <h1>{workshop_name}</h1>
                <div class="meta">
                    <p><strong>Generated:</strong> {datetime.now().strftime('%B %d, %Y')}</p>
                    <p><strong>Total Responses:</strong> {total_responses}</p>
                </div>
            </div>
            
            <!-- SUMMARY SECTION -->
            <div class="content">
                <div class="header">
                    <h2>📊 Performance Overview</h2>
                    <p>Key metrics from {total_responses} builder feedback responses</p>
                </div>
                
                <!-- METRICS GRID -->
                <div class="metrics">
                    <div class="metric-box">
                        <div class="metric-label">Confidence Score</div>
                        <div class="metric-value">{confidence_score:.1f}</div>
                        <div class="metric-subtitle">out of 5.0</div>
                    </div>
                    
                    <div class="metric-box">
                        <div class="metric-label">Facilitator Rating</div>
                        <div class="metric-value">{facilitator_rating['excellent_pct']:.0f}%</div>
                        <div class="metric-subtitle">rated excellent</div>
                    </div>
                    
                    <div class="metric-box">
                        <div class="metric-label">Perfect Pacing</div>
                        <div class="metric-value">{pace_analysis['just_right_pct']:.0f}%</div>
                        <div class="metric-subtitle">just right pace</div>
                    </div>
                    
                    <div class="metric-box">
                        <div class="metric-label">Hands-on Completion</div>
                        <div class="metric-value">{hands_on_analysis['completion_rate']:.0f}%</div>
                        <div class="metric-subtitle">completed deliverables</div>
                    </div>
                </div>
                
                <!-- FACILITATOR RATING -->
                <div class="section">
                    <h3>👩‍🏫 Facilitator Quality</h3>
                    <table>
                        <tr>
                            <th>Rating</th>
                            <th>Responses</th>
                            <th>Percentage</th>
                        </tr>
                        <tr>
                            <td><span class="badge excellent">🌟 Excellent</span></td>
                            <td>{facilitator_rating['excellent']}</td>
                            <td>{facilitator_rating['excellent_pct']:.0f}%</td>
                        </tr>
                        <tr>
                            <td><span class="badge good">✅ Good</span></td>
                            <td>{facilitator_rating['good']}</td>
                            <td>{facilitator_rating['good_pct']:.0f}%</td>
                        </tr>
                    </table>
                </div>
                
                <!-- PACING -->
                <div class="section">
                    <h3>⏱️ Pacing Analysis</h3>
                    <table>
                        <tr>
                            <th>Feedback</th>
                            <th>Count</th>
                            <th>Percentage</th>
                        </tr>
                        <tr>
                            <td>Just Right ✅</td>
                            <td>{pace_analysis['just_right']}</td>
                            <td>{pace_analysis['just_right_pct']:.0f}%</td>
                        </tr>
                        <tr>
                            <td>Too Fast 🚀</td>
                            <td>{pace_analysis['too_fast']}</td>
                            <td>{pace_analysis['too_fast_pct']:.0f}%</td>
                        </tr>
                        <tr>
                            <td>Too Slow 🐢</td>
                            <td>{pace_analysis['too_slow']}</td>
                            <td>{pace_analysis['too_slow_pct']:.0f}%</td>
                        </tr>
                    </table>
                </div>
                
                <!-- HANDS-ON -->
                <div class="section">
                    <h3>🛠️ Hands-On Engagement</h3>
                    <p>Completion Rate: <strong>{hands_on_analysis['completion_rate']:.0f}%</strong></p>
                    <ul style="margin-left: 20px; margin-top: 10px; font-size: 13px;">
                        <li>✅ Created deliverables: {hands_on_analysis['created']} builders</li>
                        <li>🔄 Started but need to finish: {hands_on_analysis['followed']} builders</li>
                    </ul>
                </div>
            </div>
        </div>
        
        <!-- PAGE 2 -->
        <div class="container">
            <div class="content" style="padding-top: 60px;">
                <!-- TESTIMONIALS -->
                <div class="section">
                    <h3>💬 What Builders Loved</h3>
    """
    
    for i, quote in enumerate(feedback_quotes, 1):
        html_content += f'<div class="quote-box">"{quote}"</div>\n'
    
    html_content += f"""
                </div>
                
                <!-- ACTION ITEMS -->
                <div class="section">
                    <h3>🎯 What Builders Will Try</h3>
    """
    
    for i, quote in enumerate(action_quotes, 1):
        html_content += f'<div class="recommendation">• "{quote}"</div>\n'
    
    html_content += f"""
                </div>
                
                <!-- RECOMMENDATIONS -->
                <div class="section">
                    <h3>📈 Recommended Improvements</h3>
    """
    
    recommendations = []
    if confidence_score < 3.5:
        recommendations.append("🎯 Add more guided practice – Builders need more hands-on support")
    if pace_analysis['too_fast_pct'] > 30:
        recommendations.append("⏱️ Slow down key concepts – Add checkpoints for everyone to follow")
    if hands_on_analysis['completion_rate'] < 60:
        recommendations.append("🛠️ Extend hands-on time – Allocate 10-15 more minutes")
    if pace_analysis['too_slow_pct'] > 20:
        recommendations.append("🚀 Offer advanced track – Prepare challenges for experienced builders")
    
    if not recommendations:
        recommendations.append("✨ Keep doing what you're doing – Excellent performance!")
    
    for rec in recommendations:
        html_content += f'<div class="recommendation">{rec}</div>\n'
    
    html_content += f"""
                </div>
                
                <!-- CLOSING -->
                <div class="section" style="margin-top: 50px; text-align: center; padding: 40px; background: {COLORS['light_bg']}; border-radius: 8px;">
                    <h3 style="border: none; color: {COLORS['primary']};"></h3>
                    <p style="font-size: 16px; color: {COLORS['dark']};"><strong>Thank you for facilitating an amazing workshop! 💜</strong></p>
                    <p style="font-size: 13px; color: {COLORS['text']}; opacity: 0.7; margin-top: 10px;">Your impact on the #75HER community is invaluable.</p>
                </div>
            </div>
            
            <!-- FOOTER -->
            <div class="footer">
                <p>🏗️ <strong>#75HER Workshop Facilitator Report</strong></p>
                <p>CreateHER Fest • Empowering Women in Tech</p>
                <p style="margin-top: 10px; opacity: 0.7; font-size: 10px;">Generated {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_content

# ============================================
# PDF GENERATION
# ============================================

def generate_pdf(html_content, workshop_name):
    """Convert HTML to PDF using WeasyPrint"""
    print("🎨 Generating branded PDF...")
    
    try:
        # Generate filename
        filename = f"workshop_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        # Convert HTML to PDF
        HTML(string=html_content).write_pdf(filename)
        
        print(f"✅ PDF generated: {filename}")
        return filename
    
    except Exception as e:
        print(f"❌ Error generating PDF: {e}")
        return None

# ============================================
# MAIN EXECUTION
# ============================================

def main():
    """Main workflow"""
    print("="*60)
    print("   75HER WORKSHOP REPORT GENERATOR - PDF")
    print("="*60)
    print()
    
    # Get data
    df = get_survey_data()
    
    if df is None or len(df) == 0:
        print("❌ No data available. Exiting.")
        return
    
    print(f"\n📋 Found responses for {df['Which session did you attend?'].nunique()} workshop(s)")
    print()
    
    # Ask user which workshop
    print("Which workshop would you like to analyze?")
    print("1. All workshops (combined report)")
    print("2. AI Agent Workshop")
    print("3. Confidence VISIBLE Workshop")
    print("4. Voice & Pitch Workshop")
    print()
    
    choice = input("Enter number (1-4): ").strip()
    
    workshop_filter = None
    workshop_name = "All Workshops"
    
    if choice == "2":
        workshop_filter = WORKSHOPS['AI']
        workshop_name = "AI Agent"
    elif choice == "3":
        workshop_filter = WORKSHOPS['Visibility']
        workshop_name = "Confidence Visible"
    elif choice == "4":
        workshop_filter = WORKSHOPS['Voice']
        workshop_name = "Voice & Pitch"
    
    # Generate HTML report
    print("\n📈 Analyzing data...\n")
    html_content = generate_html_report(df, workshop_filter)
    
    if html_content is None:
        return
    
    # Generate PDF
    pdf_file = generate_pdf(html_content, workshop_name)
    
    if pdf_file:
        print(f"\n✅ Success! Your report is ready: {pdf_file}")
        print(f"📧 You can now email this to the facilitator!")

if __name__ == "__main__":
    main()
