#!/usr/bin/env python3
"""
Legal Preservation Calendar - Asset Preservation Reminder for Legal Proceedings
Usage: python preservation.py <pdf_path>

This script extracts preservation information from court documents and
creates calendar reminders in Apple Calendar (30 days before expiration).
"""

import sys
import os
import re
import subprocess
import json
from datetime import datetime, timedelta
from pathlib import Path


def extract_pdf_text(pdf_path):
    """Extract text from PDF using pdfplumber"""
    try:
        import pdfplumber
    except ImportError:
        print("❌ pdfplumber not installed. Run: pip install pdfplumber")
        return None

    print(f"📄 Extracting PDF: {pdf_path}")

    try:
        with pdfplumber.open(pdf_path) as pdf:
            full_text = ''
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text:
                    full_text += f'\n--- Page {i+1} ---\n{text}'

        if not full_text.strip():
            print("❌ No text extracted from PDF")
            return None

        print(f"✅ Extracted {len(full_text)} characters")
        return full_text

    except Exception as e:
        print(f"❌ PDF extraction failed: {e}")
        return None


def extract_with_llm(text_content):
    """Use LLM to extract preservation information"""
    try:
        import anthropic
    except ImportError:
        print("❌ anthropic not installed. Run: pip install anthropic")
        return None

    client = anthropic.Anthropic()

    prompt = f"""Please extract preservation information from the following legal document and return in JSON format.

Document content:
```
{text_content[:15000]}
```

Extract the following information and return JSON:
{{
    "case_number": "Case number, e.g.: (2024)粤0305民初1234号",
    "case_name": "Case name/cause of action",
    "applicant": "Applicant for preservation",
    "respondent": "Respondent/Preservation target",
    "preservation_items": [
        {{
            "type": "Property type: bank account/real estate/equity/vehicle/movable property/other",
            "detail": "Property details: account number, bank, address, equity amount, etc.",
            "duration": "Preservation duration, e.g.: 1 year, 2 years, 3 years",
            "duration_months": "Duration in months, as number",
            "start_date": "Preservation start date in YYYY-MM-DD format, leave empty if not specified",
            "end_date": "Preservation end date in YYYY-MM-DD format, leave empty if not specified",
            "account_tail": "For bank accounts, extract last 4 digits or key identifier"
        }}
    ],
    "document_date": "Document date in YYYY-MM-DD format",
    "has_handwritten_date": "true/false - whether the document contains handwritten dates",
    "court_name": "Court name"
}}

Important notes:
1. A single document may contain multiple preservation items - list each separately
2. Typical durations: bank accounts 1 year, real estate 3 years, equity 3 years, vehicles 2 years
3. If start date not specified, use document date or leave empty
4. **CRITICAL**: Check if dates appear handwritten or OCR-misrecognized (fragmented layout, misaligned numbers)
5. Return only JSON, no explanatory text"""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4000,
            temperature=0,
            messages=[{"role": "user", "content": prompt}]
        )

        content = response.content[0].text

        # Extract JSON
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        else:
            print("❌ Cannot parse JSON from LLM response")
            return None

    except Exception as e:
        print(f"❌ LLM extraction failed: {e}")
        return None


def calculate_reminder_date(start_date_str, duration_months, end_date_str=None, document_date_str=None):
    """Calculate reminder date (30 days before expiration)"""
    try:
        # If end_date is directly provided, use it
        if end_date_str:
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
        else:
            # Parse start date
            if start_date_str:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            elif document_date_str:
                start_date = datetime.strptime(document_date_str, "%Y-%m-%d")
            else:
                start_date = datetime.now()

            # Calculate end date
            months = int(duration_months)
            month = start_date.month + months
            year = start_date.year + (month - 1) // 12
            month = (month - 1) % 12 + 1

            # Handle day overflow (e.g., Feb 30 -> Feb 28/29)
            day = min(start_date.day, [31, 29 if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])

            end_date = datetime(year, month, day)

        # Reminder 30 days before expiration
        reminder_date = end_date - timedelta(days=30)

        return {
            'start_date': start_date_str or document_date_str or datetime.now().strftime("%Y-%m-%d"),
            'end_date': end_date.strftime("%Y-%m-%d"),
            'reminder_date': reminder_date.strftime("%Y-%m-%d")
        }
    except Exception as e:
        print(f"⚠️ Date calculation failed: {e}")
        return None


def create_calendar_event(case_number, item, date_info, calendar_name="工作"):
    """Create Apple Calendar event"""

    # Build title
    item_type = item.get('type', 'Property')
    account_tail = item.get('account_tail', '')

    if account_tail:
        title = f"【保全到期】{case_number} - {item_type}（尾号{account_tail}）"
    else:
        detail_short = item.get('detail', '')[:20]
        title = f"【保全到期】{case_number} - {item_type}（{detail_short}）"

    # Build notes
    notes_lines = [
        f"案号：{case_number}",
        f"财产类型：{item_type}",
        f"财产详情：{item.get('detail', '')}",
        f"保全期限：{item.get('duration', '')}",
        f"保全起始：{date_info['start_date']}",
        f"保全到期：{date_info['end_date']}",
        "",
        "⚠️ 请及时向法院申请续行保全"
    ]
    notes_text = '\\n'.join(notes_lines)

    # Parse reminder date
    reminder_date = date_info['reminder_date']
    year, month, day = reminder_date.split('-')

    month_names = ["January", "February", "March", "April", "May", "June",
                   "July", "August", "September", "October", "November", "December"]
    month_name = month_names[int(month) - 1]

    # AppleScript
    script = f'''
tell application "Calendar"
    tell calendar "{calendar_name}"
        set reminderDate to current date
        set time of reminderDate to 0
        set month of reminderDate to {month_name}
        set day of reminderDate to {day}
        set year of reminderDate to {year}
        set endDate to reminderDate + 60 * 60
        set theEvent to make new event with properties {{summary:"{title}", start date:reminderDate, end date:endDate, description:"{notes_text}", allday event:true}}
        make new display alarm at end of display alarms of theEvent with properties {{trigger interval:0}}
    end tell
end tell
'''

    result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)

    if result.returncode == 0:
        print(f"  ✅ Created reminder: {title} (Reminder date: {reminder_date})")
        return True
    else:
        print(f"  ❌ Failed to create: {result.stderr}")
        return False


def print_summary(info, results):
    """Print summary information"""
    print("\n" + "=" * 60)
    print("📋 Property Preservation Summary")
    print("=" * 60)
    print(f"Case Number: {info.get('case_number', 'Unknown')}")
    print(f"Case Name: {info.get('case_name', 'Unknown')}")
    print(f"Respondent: {info.get('respondent', 'Unknown')}")
    print(f"Document Date: {info.get('document_date', 'Unknown')}")
    if info.get('has_handwritten_date'):
        print("⚠️ WARNING: Document contains handwritten dates - Please verify!")
    print("-" * 60)
    print("Preservation Items:")

    for i, (item, result) in enumerate(zip(info.get('preservation_items', []), results), 1):
        status = "✅" if result else "❌"
        print(f"\n  {i}. {status} {item.get('type', 'Unknown')}")
        print(f"     Detail: {item.get('detail', '')[:50]}")
        print(f"     Duration: {item.get('duration', 'Unknown')}")
        if result:
            print(f"     Reminder: {result['reminder_date']} (30 days before expiration)")

    print("=" * 60)
    success_count = sum(1 for r in results if r)
    total_count = len(results)
    print(f"\nSuccessfully created {success_count}/{total_count} calendar reminders")

    if success_count > 0:
        print("\n📅 Please open Calendar app to view reminder events")


def main():
    if len(sys.argv) < 2:
        print("Usage: python preservation.py <pdf_path>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    if not os.path.exists(pdf_path):
        print(f"❌ File not found: {pdf_path}")
        sys.exit(1)

    # Extract text from PDF
    text_content = extract_pdf_text(pdf_path)
    if not text_content:
        sys.exit(1)

    print("\n🔍 Analyzing document content...")

    # Extract preservation information
    info = extract_with_llm(text_content)
    if not info:
        print("❌ Cannot extract preservation information")
        sys.exit(1)

    # Validate required fields
    if not info.get('case_number'):
        print("⚠️ Case number not recognized, using 'Unknown'")
        info['case_number'] = 'Unknown'

    items = info.get('preservation_items', [])
    if not items:
        print("⚠️ No preservation items recognized")
        sys.exit(1)

    # Check for handwritten dates warning
    if info.get('has_handwritten_date'):
        print("\n" + "⚠️" * 30)
        print("⚠️ WARNING: This document appears to contain HANDWRITTEN dates!")
        print("⚠️ Please carefully verify the extracted dates against the original document.")
        print("⚠️" * 30 + "\n")

    print(f"\n✅ Recognized {len(items)} preservation item(s)")

    # Show extracted info and ask for confirmation
    print("\n" + "=" * 60)
    print("Please verify the extracted information:")
    print("=" * 60)
    print(f"Case: {info.get('case_number')}")
    print(f"Respondent: {info.get('respondent')}")
    for i, item in enumerate(items, 1):
        print(f"\n{i}. {item.get('type')}")
        print(f"   Detail: {item.get('detail')}")
        print(f"   Duration: {item.get('duration')}")
        if item.get('start_date'):
            print(f"   Start: {item.get('start_date')}")
        if item.get('end_date'):
            print(f"   End: {item.get('end_date')}")

    # Note: In automated mode, proceed directly
    # For manual verification, uncomment below:
    # confirm = input("\nProceed with creating calendar reminders? (y/n): ")
    # if confirm.lower() != 'y':
    #     print("Cancelled")
    #     sys.exit(0)

    # Create calendar reminders for each item
    results = []
    for item in items:
        print(f"\n📌 Processing: {item.get('type', 'Unknown')}")

        # Calculate dates
        date_info = calculate_reminder_date(
            item.get('start_date'),
            item.get('duration_months', 12),
            item.get('end_date'),
            info.get('document_date')
        )

        if not date_info:
            print("  ⚠️ Date calculation failed, skipping")
            results.append(None)
            continue

        print(f"  Start: {date_info['start_date']}")
        print(f"  End: {date_info['end_date']}")
        print(f"  Reminder: {date_info['reminder_date']} (30 days before)")

        # Create calendar event
        success = create_calendar_event(
            info['case_number'],
            item,
            date_info
        )

        results.append(date_info if success else None)

    # Print summary
    print_summary(info, results)


if __name__ == '__main__':
    main()
