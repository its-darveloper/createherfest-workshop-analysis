#!/usr/bin/env python3
"""
75HER Workshop Facilitator Report Generator
Pulls data from JotForm → Google Sheets, analyzes, and generates report
"""

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import numpy as np
from collections import Counter
from datetime import datetime
from textblob import TextBlob

# ============================================
# CONFIGURATION
# ============================================
CREDENTIALS_FILE = 'credentials.json'
SHEET_NAME = '75HER Workshop Survey Responses'

# Workshop names (from your JotForm dropdown)
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
    
    except FileNotFoundError:
        print("❌ Error: credentials.json not found!")
        print("Please make sure credentials.json is in the same folder as this script.")
        return None
    except Exception as e:
        print(f"❌ Error connecting to Google Sheets: {e}")
        return None

# ============================================
# ANALYSIS FUNCTIONS
# ============================================

def calculate_confidence_score(df, confidence_col):
    """Calculate average confidence score (1-5 scale)"""
    try:
        # Convert to numeric, handling any text values
        scores = pd.to_numeric(df[confidence_col], errors='coerce')
        avg = scores.mean()
        
        # Return 0 if no valid scores, otherwise return the average
        return 0.0 if pd.isna(avg) else float(avg)
    except Exception as e:
        print(f"⚠️ Warning: Could not calculate confidence score - {e}")
        return 0.0

def analyze_facilitator_rating(df, rating_col):
    """Analyze facilitator rating distribution"""
    ratings = df[rating_col].value_counts()
    
    # Map emoji ratings to scores
    rating_map = {
        '🌟 Excellent - Clear, engaging, well-paced': 4,
        '✅ Good - Helpful and informative': 3,
        '😐 Okay - Some parts were unclear': 2,
        '📉 Needs improvement - Hard to follow': 1
    }
    
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
    """Analyze workshop pacing feedback"""
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

def extract_top_quotes(text_series, n=5):
    """Extract top N quotes from open-ended responses"""
    quotes = []
    for response in text_series.dropna():
        response = str(response).strip()
        if len(response) > 10:  # Skip very short responses
            quotes.append(response)
    
    # Return up to n random quotes (or all if fewer)
    return quotes[:n]

def analyze_hands_on(df, hands_on_col):
    """Analyze hands-on deliverable completion"""
    counts = df[hands_on_col].value_counts()
    total = len(df)
    
    created = counts.get('Yes - I created/started [code sample / prototype / document / project file]', 0)
    followed = counts.get('Yes - I followed along but need to finish it', 0)
    
    return {
        'created': created,
        'followed': followed,
        'completion_rate': ((created + followed) / total * 100) if total > 0 else 0
    }

def analyze_facilitator_strengths(df, strengths_col):
    """Analyze what facilitators did well (multi-select)"""
    # This column contains arrays, need to parse
    all_strengths = []
    for response in df[strengths_col].dropna():
        # Response might be a string like "['item1', 'item2']" or actual list
        if isinstance(response, str):
            # Parse string representation of list
            items = response.strip('[]').split(',')
            items = [item.strip().strip('"\'') for item in items]
            all_strengths.extend(items)
        else:
            all_strengths.append(response)
    
    strength_counts = Counter(all_strengths)
    return strength_counts.most_common(6)

# ============================================
# REPORT GENERATION
# ============================================

def generate_report(df, workshop_filter=None):
    """Generate workshop facilitator report"""

    # DEBUG: Print column names to verify
    print("\n🔍 DEBUG - Column names in your sheet:")
    for col in df.columns:
        print(f"   - '{col}'")
    print()
    
    # Filter by workshop if specified
    if workshop_filter:
        df = df[df['Which session did you attend?'] == workshop_filter]
        workshop_name = workshop_filter
    else:
        workshop_name = "All Workshops"
    
    if len(df) == 0:
        print(f"❌ No responses found for: {workshop_name}")
        return None
    
    print(f"📊 Analyzing {len(df)} responses for: {workshop_name}")
    
    # Column names from your JotForm
    COL_SESSION = 'Which session did you attend?'
    COL_CONFIDENCE = 'How confident do you feel implementing what you learned today? '
    COL_FACILITATOR_RATING = 'The facilitator today was:'
    COL_PACE = 'Was the workshop pace/level right for you?'
    COL_HANDS_ON = 'Did you create a hands-on deliverable today?'
    COL_FACILITATOR_STRENGTHS = 'The facilitator today: (Select all that apply)'
    COL_FACILITATOR_FEEDBACK = 'What did the facilitator do especially well? Any suggestions for improvement?'
    COL_ONE_THING = "What's ONE thing you'll try this week based on today's workshop?"
    COL_AFTER_WORKSHOP = "After today's workshop, I feel:"
    COL_BACKGROUND = 'Your background in this topic:'
    
    # Calculate metrics
    total_responses = len(df)
    confidence_score = calculate_confidence_score(df, COL_CONFIDENCE)
    facilitator_rating = analyze_facilitator_rating(df, COL_FACILITATOR_RATING)
    pace_analysis = analyze_pace(df, COL_PACE)
    hands_on_analysis = analyze_hands_on(df, COL_HANDS_ON)
    
    # Extract quotes
    what_well_quotes = extract_top_quotes(df[COL_FACILITATOR_FEEDBACK], n=5)
    one_thing_quotes = extract_top_quotes(df[COL_ONE_THING], n=5)
    
    # Analyze facilitator strengths
    try:
        facilitator_strengths = analyze_facilitator_strengths(df, COL_FACILITATOR_STRENGTHS)
    except:
        facilitator_strengths = []
    
    # Build the report
    report = f"""
# Workshop Report: {workshop_name}

**Generated:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}  
**Total Responses:** {total_responses}

---

## 📊 Overall Performance Summary

### ⭐ Confidence Score
**{confidence_score:.1f} / 5.0** - How confident builders feel implementing what they learned

{'✅ **Excellent** - Builders feel confident applying skills' if confidence_score >= 4.0 else '⚠️ **Needs Attention** - Builders need more support to apply skills' if confidence_score >= 3.0 else '🚨 **Action Required** - Significant confidence gap'}

---

### 👩‍🏫 Facilitator Rating

**Overall Quality:**
- 🌟 **Excellent:** {facilitator_rating['excellent']} responses ({facilitator_rating['excellent_pct']:.0f}%)
- ✅ **Good:** {facilitator_rating['good']} responses ({facilitator_rating['good_pct']:.0f}%)

{'🎉 **Outstanding!** Builders rated you excellent!' if facilitator_rating['excellent_pct'] >= 70 else '✅ **Great job!** Strong facilitator performance' if facilitator_rating['excellent_pct'] >= 50 else '⚠️ **Room to improve** - See feedback below'}

---

### ⏱️ Pacing Analysis

| Pace Feedback | Count | Percentage |
|--------------|-------|------------|
| **Just Right** | {pace_analysis['just_right']} | {pace_analysis['just_right_pct']:.0f}% |
| **Too Fast** | {pace_analysis['too_fast']} | {pace_analysis['too_fast_pct']:.0f}% |
| **Too Slow** | {pace_analysis['too_slow']} | {pace_analysis['too_slow_pct']:.0f}% |

{'✅ **Perfect pacing** for most builders' if pace_analysis['just_right_pct'] >= 60 else f"⚠️ **Adjust pacing:** {pace_analysis['too_fast']} felt rushed, {pace_analysis['too_slow']} wanted to go deeper"}

---

### 🛠️ Hands-On Engagement

**Deliverable Completion Rate:** {hands_on_analysis['completion_rate']:.0f}%

- ✅ **Created deliverable:** {hands_on_analysis['created']} builders
- 🔄 **Started but need to finish:** {hands_on_analysis['followed']} builders

{'🎉 **Excellent hands-on participation!**' if hands_on_analysis['completion_rate'] >= 70 else '⚠️ **Consider more guided practice time**' if hands_on_analysis['completion_rate'] >= 40 else '🚨 **Action needed:** Many builders struggled with hands-on portion'}

---

## 💪 What You Did REALLY Well

**Top Facilitator Strengths (from builder feedback):**

"""
    
    if facilitator_strengths:
        for i, (strength, count) in enumerate(facilitator_strengths[:6], 1):
            pct = (count / total_responses) * 100
            report += f"{i}. **{strength}** - {count} mentions ({pct:.0f}%)\n"
    else:
        report += "*Analyzing facilitator strengths...*\n"
    
    report += f"""

---

## 💬 Builder Testimonials

### What Builders Loved:

"""
    
    for i, quote in enumerate(what_well_quotes[:5], 1):
        report += f'{i}. > "{quote}"\n\n'
    
    report += f"""

---

## 🎯 Action Items Builders Will Try

**What builders plan to implement this week:**

"""
    
    for i, quote in enumerate(one_thing_quotes[:5], 1):
        report += f'{i}. "{quote}"\n'
    
    report += f"""

---

## 📈 Recommended Improvements

"""
    
    # Generate recommendations based on data
    recommendations = []
    
    if confidence_score < 3.5:
        recommendations.append("🎯 **Add more guided practice** - Builders need more hands-on support to build confidence")
    
    if pace_analysis['too_fast_pct'] > 30:
        recommendations.append("⏱️ **Slow down key concepts** - Add checkpoints to ensure everyone's following along")
    
    if hands_on_analysis['completion_rate'] < 60:
        recommendations.append("🛠️ **Extend hands-on time** - Allocate 10-15 more minutes for building/practice")
    
    if pace_analysis['too_slow_pct'] > 20:
        recommendations.append("🚀 **Offer advanced track** - Consider bonus challenges for experienced builders")
    
    if not recommendations:
        recommendations.append("✨ **Keep doing what you're doing!** - Your workshop is performing excellently")
    
    for rec in recommendations:
        report += f"- {rec}\n"
    
    report += f"""

---

## 📊 Full Data Export

**Detailed responses available in:** [Google Sheet]({SHEET_NAME})

---

*Report generated by 75HER Workshop Analytics | Questions? Contact the team*
"""
    
    return report

# ============================================
# MAIN EXECUTION
# ============================================

def main():
    """Main workflow"""
    print("="*60)
    print("   75HER WORKSHOP FACILITATOR REPORT GENERATOR")
    print("="*60)
    print()
    
    # Get data
    df = get_survey_data()
    
    if df is None or len(df) == 0:
        print("\n❌ No data available. Exiting.")
        return
    
    print(f"\n📋 Found responses for {df['Which session did you attend?'].nunique()} workshop(s)")
    print()
    
    # Ask user which workshop to analyze
    print("Which workshop would you like to analyze?")
    print("1. All workshops (combined report)")
    print("2. AI Agent Workshop")
    print("3. Confidence VISIBLE Workshop")
    print("4. Voice & Pitch Workshop")
    print()
    
    choice = input("Enter number (1-4): ").strip()
    
    workshop_filter = None
    if choice == "2":
        workshop_filter = WORKSHOPS['AI']
    elif choice == "3":
        workshop_filter = WORKSHOPS['Visibility']
    elif choice == "4":
        workshop_filter = WORKSHOPS['Voice']
    
    # Generate report
    print("\n📈 Analyzing data...\n")
    report = generate_report(df, workshop_filter)
    
    if report is None:
        return
    
    # Save report
    filename = f"workshop_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(report)
    
    # Display report
    print("\n" + "="*60)
    print(report)
    print("="*60)
    
    print(f"\n✅ Report saved to: {filename}")
    print("\n💡 Tip: Open this .md file in Notion or any markdown viewer!")

if __name__ == "__main__":
    main()
