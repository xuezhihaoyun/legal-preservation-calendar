#!/usr/bin/env python3
"""
Legal Preservation Calendar - Asset Preservation Reminder for Legal Proceedings
财产保全到期提醒 - 识别 PDF 保全文书并创建日历提醒

Usage: python preservation.py <pdf_path>
用法: python preservation.py <pdf路径>

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


def convert_pdf_with_mineru(pdf_path):
    """使用 mineru-ocr 转换 PDF 为 markdown / Use MinerU OCR to convert PDF to markdown"""
    mineru_script = Path.home() / ".claude/skills/mineru-ocr/scripts/convert.js"

    if not mineru_script.exists():
        print("❌ 未找到 mineru-ocr 脚本 / MinerU OCR script not found. Please install mineru-ocr skill first.")
        return None

    print(f"📄 正在转换 PDF / Converting PDF: {pdf_path}")

    # 调用 mineru-ocr 转换
    result = subprocess.run(
        ["/usr/bin/osascript", "-l", "JavaScript", str(mineru_script), pdf_path],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"❌ PDF 转换失败 / Conversion failed: {result.stderr}")
        return None

    # 找到生成的 markdown 文件
    pdf_path = Path(pdf_path)
    md_path = pdf_path.with_suffix('.md')

    if not md_path.exists():
        # 尝试查找同名 md 文件
        possible_md = list(pdf_path.parent.glob(f"{pdf_path.stem}*.md"))
        if possible_md:
            md_path = possible_md[0]
        else:
            print("❌ 未找到转换后的 markdown 文件 / Converted markdown file not found")
            return None

    print(f"✅ PDF 转换完成 / Conversion completed: {md_path}")
    return str(md_path)


def extract_with_llm(markdown_content):
    """使用 LLM 提取保全信息 / Use LLM to extract preservation information"""
    try:
        import anthropic
    except ImportError:
        print("❌ anthropic not installed. Run: pip install anthropic")
        return None

    client = anthropic.Anthropic()

    prompt = f"""请从以下财产保全文书中提取关键信息，以 JSON 格式返回。
Please extract preservation information from the following legal document and return in JSON format.

文书内容 / Document content:
```
{markdown_content[:15000]}
```

请提取以下信息并返回 JSON / Please extract the following and return JSON:
{{
    "case_number": "案号 / Case number, e.g.: (2024)粤0305民初1234号",
    "case_name": "案件名称/案由 / Case name/cause of action",
    "applicant": "申请保全人 / Applicant for preservation",
    "respondent": "被保全人 / Respondent/Preservation target",
    "preservation_items": [
        {{
            "type": "财产类型 / Property type: 银行账户/bank account, 不动产/real estate, 股权/equity, 车辆/vehicle, 动产/movable property, 其他/other",
            "detail": "财产具体信息 / Property details: account number, bank, address, equity amount, etc.",
            "duration": "保全期限 / Preservation duration, e.g.: 1年/1 year, 2年/2 years, 3年/3 years",
            "duration_months": "期限转换为月数 / Duration in months, as number",
            "start_date": "保全起始日期 / Start date in YYYY-MM-DD format, leave empty if not specified",
            "end_date": "保全结束日期 / End date in YYYY-MM-DD format, leave empty if not specified",
            "account_tail": "如果是银行账户，提取尾号4位或关键标识 / For bank accounts, extract last 4 digits or key identifier"
        }}
    ],
    "document_date": "文书日期 / Document date in YYYY-MM-DD format",
    "has_handwritten_date": "是否有手写日期 / true/false - whether the document contains handwritten dates",
    "court_name": "法院名称 / Court name"
}}

注意事项 / Important notes:
1. 同一份文书可能有多种保全财产，每种都要单独列出 / A single document may contain multiple preservation items - list each separately
2. 银行账户通常保全1年，不动产通常3年，股权通常3年，车辆通常2年 / Typical durations: bank accounts 1 year, real estate 3 years, equity 3 years, vehicles 2 years
3. 如果文书未明确起始日期，使用文书日期或留空 / If start date not specified, use document date or leave empty
4. **重要/CRITICAL**: 检查日期是否为手写或OCR识别错误 / Check if dates appear handwritten or OCR-misrecognized
5. 只返回 JSON，不要其他解释文字 / Return only JSON, no explanatory text"""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4000,
            temperature=0,
            messages=[{"role": "user", "content": prompt}]
        )

        content = response.content[0].text

        # 提取 JSON / Extract JSON
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        else:
            print("❌ 无法解析 LLM 返回的 JSON / Cannot parse JSON from LLM response")
            return None

    except Exception as e:
        print(f"❌ LLM 提取失败 / LLM extraction failed: {e}")
        return None


def calculate_reminder_date(start_date_str, duration_months, end_date_str=None, document_date_str=None):
    """计算提醒日期（到期前30天）/ Calculate reminder date (30 days before expiration)"""
    try:
        # 如果直接提供了结束日期 / If end_date is directly provided
        if end_date_str:
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
        else:
            # 解析起始日期 / Parse start date
            if start_date_str:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            elif document_date_str:
                start_date = datetime.strptime(document_date_str, "%Y-%m-%d")
            else:
                start_date = datetime.now()

            # 计算到期日 / Calculate end date
            months = int(duration_months)
            month = start_date.month + months
            year = start_date.year + (month - 1) // 12
            month = (month - 1) % 12 + 1

            # 处理日期溢出（如2月30日应调整为2月28/29日）/ Handle day overflow
            day = min(start_date.day, [31, 29 if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])

            end_date = datetime(year, month, day)

        # 提前30天提醒 / Reminder 30 days before expiration
        reminder_date = end_date - timedelta(days=30)

        return {
            'start_date': start_date_str or document_date_str or datetime.now().strftime("%Y-%m-%d"),
            'end_date': end_date.strftime("%Y-%m-%d"),
            'reminder_date': reminder_date.strftime("%Y-%m-%d")
        }
    except Exception as e:
        print(f"⚠️ 日期计算失败 / Date calculation failed: {e}")
        return None


def create_calendar_event(case_number, item, date_info, calendar_name="工作"):
    """创建苹果日历事件 / Create Apple Calendar event"""

    # 构建标题 / Build title
    item_type = item.get('type', '财产/Property')
    account_tail = item.get('account_tail', '')

    if account_tail:
        title = f"【保全到期】{case_number} - {item_type}（尾号{account_tail}）"
    else:
        detail_short = item.get('detail', '')[:20]
        title = f"【保全到期】{case_number} - {item_type}（{detail_short}）"

    # 构建备注 / Build notes
    notes_lines = [
        f"案号/Case: {case_number}",
        f"财产类型/Type: {item_type}",
        f"财产详情/Detail: {item.get('detail', '')}",
        f"保全期限/Duration: {item.get('duration', '')}",
        f"保全起始/Start: {date_info['start_date']}",
        f"保全到期/End: {date_info['end_date']}",
        "",
        "⚠️ 请及时向法院申请续行保全 / Please apply for renewal preservation in time"
    ]
    notes_text = '\n'.join(notes_lines)

    # 解析提醒日期 / Parse reminder date
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
        print(f"  ✅ 已创建提醒 / Created: {title}（提醒日期/Reminder: {reminder_date}）")
        return True
    else:
        print(f"  ❌ 创建失败 / Failed: {result.stderr}")
        return False


def print_summary(info, results):
    """打印汇总信息 / Print summary information"""
    print("\n" + "=" * 60)
    print("📋 财产保全信息汇总 / Property Preservation Summary")
    print("=" * 60)
    print(f"案号/Case: {info.get('case_number', '未知/Unknown')}")
    print(f"案由/Case Name: {info.get('case_name', '未知/Unknown')}")
    print(f"被保全人/Respondent: {info.get('respondent', '未知/Unknown')}")
    print(f"文书日期/Document Date: {info.get('document_date', '未知/Unknown')}")
    if info.get('has_handwritten_date'):
        print("⚠️ 警告：文书包含手写日期，请核实！/ WARNING: Document contains handwritten dates!")
    print("-" * 60)
    print("保全财产清单 / Preservation Items:")

    for i, (item, result) in enumerate(zip(info.get('preservation_items', []), results), 1):
        status = "✅" if result else "❌"
        print(f"\n  {i}. {status} {item.get('type', '未知类型/Unknown')}")
        print(f"     详情/Detail: {item.get('detail', '')[:50]}")
        print(f"     期限/Duration: {item.get('duration', '未知/Unknown')}")
        if result:
            print(f"     提醒日期/Reminder: {result['reminder_date']}（到期前30天 / 30 days before expiration）")

    print("=" * 60)
    success_count = sum(1 for r in results if r)
    total_count = len(results)
    print(f"\n成功创建 / Successfully created: {success_count}/{total_count} 个日历提醒 / calendar reminders")

    if success_count > 0:
        print("\n📅 请打开日历应用查看提醒事件 / Please open Calendar app to view reminder events")


def main():
    if len(sys.argv) < 2:
        print("用法 / Usage: python preservation.py <pdf路径/pdf_path>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    if not os.path.exists(pdf_path):
        print(f"❌ 文件不存在 / File not found: {pdf_path}")
        sys.exit(1)

    # 检查文件类型
    if not pdf_path.lower().endswith('.pdf'):
        print("⚠️ 文件不是 PDF 格式 / Not a PDF file, trying to read directly...")
        with open(pdf_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
    else:
        # 转换 PDF / Convert PDF
        md_path = convert_pdf_with_mineru(pdf_path)
        if not md_path:
            sys.exit(1)

        with open(md_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()

    print("\n🔍 正在分析文书内容 / Analyzing document content...")

    # 提取保全信息 / Extract preservation information
    info = extract_with_llm(markdown_content)
    if not info:
        print("❌ 无法提取保全信息 / Cannot extract preservation information")
        sys.exit(1)

    # 验证必要字段 / Validate required fields
    if not info.get('case_number'):
        print("⚠️ 未识别到案号 / Case number not recognized, using '未知案号/Unknown'")
        info['case_number'] = '未知案号/Unknown'

    items = info.get('preservation_items', [])
    if not items:
        print("⚠️ 未识别到保全财产信息 / No preservation items recognized")
        sys.exit(1)

    # 手写日期警告 / Handwritten date warning
    if info.get('has_handwritten_date'):
        print("\n" + "⚠️" * 30)
        print("⚠️ 警告：本文书似乎包含手写日期！/ WARNING: Document contains handwritten dates!")
        print("⚠️ 请仔细核对提取的日期与原始文书 / Please verify extracted dates against original document")
        print("⚠️" * 30 + "\n")

    print(f"\n✅ 识别到 {len(items)} 项保全财产 / Recognized {len(items)} preservation item(s)")

    # 显示提取的信息供核对 / Show extracted info for verification
    print("\n" + "=" * 60)
    print("请核对提取的信息 / Please verify extracted information:")
    print("=" * 60)
    print(f"案号/Case: {info.get('case_number')}")
    print(f"被保全人/Respondent: {info.get('respondent')}")
    for i, item in enumerate(items, 1):
        print(f"\n{i}. {item.get('type')}")
        print(f"   详情/Detail: {item.get('detail')}")
        print(f"   期限/Duration: {item.get('duration')}")
        if item.get('start_date'):
            print(f"   起始/Start: {item.get('start_date')}")
        if item.get('end_date'):
            print(f"   结束/End: {item.get('end_date')}")

    # 为每项财产创建日历提醒 / Create calendar reminders for each item
    results = []
    for item in items:
        print(f"\n📌 处理 / Processing: {item.get('type', '未知/Unknown')}")

        # 计算日期 / Calculate dates
        date_info = calculate_reminder_date(
            item.get('start_date'),
            item.get('duration_months', 12),
            item.get('end_date'),
            info.get('document_date')
        )

        if not date_info:
            print("  ⚠️ 日期计算失败，跳过 / Date calculation failed, skipping")
            results.append(None)
            continue

        print(f"  保全起始/Start: {date_info['start_date']}")
        print(f"  保全到期/End: {date_info['end_date']}")
        print(f"  提醒日期/Reminder: {date_info['reminder_date']}（提前30天 / 30 days before）")

        # 创建日历事件 / Create calendar event
        success = create_calendar_event(
            info['case_number'],
            item,
            date_info
        )

        results.append(date_info if success else None)

    # 打印汇总 / Print summary
    print_summary(info, results)


if __name__ == '__main__':
    main()
