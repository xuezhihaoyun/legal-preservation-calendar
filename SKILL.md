---
name: legal-preservation-calendar
description: Asset Preservation Reminder for Legal Proceedings. Upload PDF documents of property preservation (court orders, preservation result notices, or assistance execution notices), automatically extract preservation information (case number, property type, account/details, preservation duration), and create calendar reminders in Apple Calendar (30 days before expiration). Trigger words: "保全提醒", "财产保全", "preservation reminder", "legal preservation".
version: 1.0.0
author: 叶律师
license: MIT
---

# Legal Preservation Calendar

A Claude Code Skill for tracking asset preservation deadlines in legal proceedings.

## Overview

This Skill automatically extracts preservation information from court documents and creates calendar reminders before expiration dates.

## Features

1. **PDF Text Extraction** - Extract text from preservation documents using pdfplumber
2. **Information Parsing** - Automatically extract:
   - Case number
   - Parties (applicant/respondent)
   - Property type (bank account, real estate, equity, vehicle, etc.)
   - Property details (account number, address, equity amount)
   - Preservation duration
   - Start and end dates
3. **Smart Calculation** - Calculate reminder dates (30 days before expiration)
4. **Calendar Integration** - Batch create events in Apple Calendar

## Supported Document Types

- Property Preservation Orders (财产保全裁定书)
- Preservation Result Notices (保全结果告知书/通知书)
- Assistance Execution Notices (协助执行通知书)
- Preservation Status Notifications (财产保全情况告知书)

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/legal-preservation-calendar.git

# Install dependencies
pip install pdfplumber anthropic

# Copy to Claude Code skills directory
cp -r legal-preservation-calendar ~/.claude/skills/
```

## Usage

### Method 1: Direct PDF Upload
Upload a PDF file and say: "帮我创建保全提醒" or "preservation reminder"

### Method 2: Specify Path
Say: "帮我创建保全提醒，文件在 /path/to/document.pdf"

## Calendar Event Format

| Field | Content |
|-------|---------|
| Title | 【保全到期】Case Number - Property Type (Identifier) |
| Date | 30 days before expiration |
| All Day | Yes |
| Calendar | "工作" (Work) |
| Notes | Full case info, property details, renewal reminder |

## Handling Mixed Preservation Types

When a document contains properties with different preservation periods:
- Bank accounts: typically 1 year
- Real estate: typically 3 years
- Equity: typically 3 years
- Vehicles: typically 2 years

Each property gets its own calendar reminder.

## Important Notes

⚠️ **Handwritten Dates**: Court documents often contain handwritten dates that may be incorrectly recognized by OCR. Always verify dates against the original document.

⚠️ **Date Verification**: The Skill will display extracted information for verification before creating calendar events.

## Requirements

- Python 3.8+
- pdfplumber
- anthropic (Claude API)
- macOS with Apple Calendar

## License

MIT License - See LICENSE file for details
