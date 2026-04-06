#!/usr/bin/env python3
"""
财产保全到期提醒 - 识别 PDF 保全文书并创建日历提醒
用法: python preservation.py <pdf路径>
"""

import sys
import os
import re
import subprocess
import json
from datetime import datetime, timedelta
from pathlib import Path


def convert_pdf_with_mineru(pdf_path):
    """使用 mineru-ocr 转换 PDF 为 markdown"""
    mineru_script = Path.home() / ".claude/skills/mineru-ocr/scripts/convert.js"

    if not mineru_script.exists():
        print("❌ 未找到 mineru-ocr 脚本，请先安装 mineru-ocr skill")
        return None

    print(f"📄 正在转换 PDF: {pdf_path}")

    # 调用 mineru-ocr 转换
    result = subprocess.run(
        ["/usr/bin/osascript", "-l", "JavaScript", str(mineru_script), pdf_path],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"❌ PDF 转换失败: {result.stderr}")
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
            print("❌ 未找到转换后的 markdown 文件")
            return None

    print(f"✅ PDF 转换完成: {md_path}")
    return str(md_path)


def extract_with_llm(markdown_content):
    """使用 LLM 提取保全信息"""
    import anthropic

    client = anthropic.Anthropic()

    prompt = f"""请从以下财产保全文书中提取关键信息，以 JSON 格式返回。

文书内容：
```
{markdown_content[:15000]}
```

请提取以下信息并返回 JSON：
{{
    "case_number": "案号，如：(2024)粤0305民初1234号",
    "case_name": "案件名称/案由",
    "applicant": "申请保全人",
    "respondent": "被保全人",
    "preservation_items": [
        {{
            "type": "财产类型：银行账户/不动产/股权/车辆/动产/其他",
            "detail": "财产具体信息，如账号、开户行、房产地址、股权数额等",
            "duration": "保全期限，如：1年、2年、3年",
            "duration_months": "期限转换为月数，数字",
            "start_date": "保全起始日期，格式 YYYY-MM-DD，如未明确则留空",
            "account_tail": "如果是银行账户，提取尾号4位或关键标识"
        }}
    ],
    "document_date": "文书日期，格式 YYYY-MM-DD"
}}

注意事项：
1. 同一份文书可能有多种保全财产，每种都要单独列出
2. 银行账户通常保全1年，不动产通常3年，股权通常3年，车辆通常2年
3. 如果文书未明确起始日期，使用文书日期或留空
4. 只返回 JSON，不要其他解释文字"""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4000,
            temperature=0,
            messages=[{"role": "user", "content": prompt}]
        )

        content = response.content[0].text

        # 提取 JSON
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        else:
            print("❌ 无法解析 LLM 返回的 JSON")
            return None

    except Exception as e:
        print(f"❌ LLM 提取失败: {e}")
        return None


def calculate_reminder_date(start_date_str, duration_months, document_date_str=None):
    """计算提醒日期（到期前30天）"""
    try:
        # 解析起始日期
        if start_date_str:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        elif document_date_str:
            start_date = datetime.strptime(document_date_str, "%Y-%m-%d")
        else:
            start_date = datetime.now()

        # 计算到期日
        # 月份加法需要处理跨年
        months = int(duration_months)
        end_date = start_date

        # 加上月份
        month = start_date.month + months
        year = start_date.year + (month - 1) // 12
        month = (month - 1) % 12 + 1

        # 处理日期（如2月30日应调整为2月28/29日）
        day = min(start_date.day, [31, 29 if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])

        end_date = datetime(year, month, day)

        # 提前30天提醒
        reminder_date = end_date - timedelta(days=30)

        return {
            'start_date': start_date.strftime("%Y-%m-%d"),
            'end_date': end_date.strftime("%Y-%m-%d"),
            'reminder_date': reminder_date.strftime("%Y-%m-%d")
        }
    except Exception as e:
        print(f"⚠️ 日期计算失败: {e}")
        return None


def create_calendar_event(case_number, item, date_info, calendar_name="工作"):
    """创建苹果日历事件"""

    # 构建标题
    item_type = item.get('type', '财产')
    account_tail = item.get('account_tail', '')

    if account_tail:
        title = f"【保全到期】{case_number} - {item_type}（尾号{account_tail}）"
    else:
        detail_short = item.get('detail', '')[:20]
        title = f"【保全到期】{case_number} - {item_type}（{detail_short}）"

    # 构建备注
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

    # 解析提醒日期
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
        -- 设置提醒（提前0天，即当天提醒）
        make new display alarm at end of display alarms of theEvent with properties {{trigger interval:0}}
    end tell
end tell
'''

    result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)

    if result.returncode == 0:
        print(f"  ✅ 已创建提醒：{title}（提醒日期：{reminder_date}）")
        return True
    else:
        print(f"  ❌ 创建失败：{result.stderr}")
        return False


def print_summary(info, results):
    """打印汇总信息"""
    print("\n" + "=" * 60)
    print("📋 财产保全信息汇总")
    print("=" * 60)
    print(f"案号：{info.get('case_number', '未知')}")
    print(f"案由：{info.get('case_name', '未知')}")
    print(f"被保全人：{info.get('respondent', '未知')}")
    print(f"文书日期：{info.get('document_date', '未知')}")
    print("-" * 60)
    print("保全财产清单：")

    for i, (item, result) in enumerate(zip(info.get('preservation_items', []), results), 1):
        status = "✅" if result else "❌"
        print(f"\n  {i}. {status} {item.get('type', '未知类型')}")
        print(f"     详情：{item.get('detail', '')[:50]}")
        print(f"     期限：{item.get('duration', '未知')}")
        if result:
            print(f"     提醒日期：{result['reminder_date']}（到期前30天）")

    print("=" * 60)
    success_count = sum(1 for r in results if r)
    total_count = len(results)
    print(f"\n成功创建 {success_count}/{total_count} 个日历提醒")

    if success_count > 0:
        print("\n📅 请打开日历应用查看提醒事件")


def main():
    if len(sys.argv) < 2:
        print("用法: python preservation.py <pdf路径>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    if not os.path.exists(pdf_path):
        print(f"❌ 文件不存在: {pdf_path}")
        sys.exit(1)

    # 检查文件类型
    if not pdf_path.lower().endswith('.pdf'):
        print("⚠️ 文件不是 PDF 格式，尝试直接读取...")
        # 如果不是 PDF，尝试直接读取
        with open(pdf_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
    else:
        # 转换 PDF
        md_path = convert_pdf_with_mineru(pdf_path)
        if not md_path:
            sys.exit(1)

        with open(md_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()

    print("\n🔍 正在分析文书内容...")

    # 提取保全信息
    info = extract_with_llm(markdown_content)
    if not info:
        print("❌ 无法提取保全信息")
        sys.exit(1)

    # 验证必要字段
    if not info.get('case_number'):
        print("⚠️ 未识别到案号，将使用 '未知案号'")
        info['case_number'] = '未知案号'

    items = info.get('preservation_items', [])
    if not items:
        print("⚠️ 未识别到保全财产信息")
        sys.exit(1)

    print(f"\n✅ 识别到 {len(items)} 项保全财产")

    # 为每项财产创建日历提醒
    results = []
    for item in items:
        print(f"\n📌 处理：{item.get('type', '未知类型')}")

        # 计算日期
        date_info = calculate_reminder_date(
            item.get('start_date'),
            item.get('duration_months', 12),
            info.get('document_date')
        )

        if not date_info:
            print("  ⚠️ 日期计算失败，跳过")
            results.append(None)
            continue

        print(f"  保全起始：{date_info['start_date']}")
        print(f"  保全到期：{date_info['end_date']}")
        print(f"  提醒日期：{date_info['reminder_date']}（提前30天）")

        # 创建日历事件
        success = create_calendar_event(
            info['case_number'],
            item,
            date_info
        )

        results.append(date_info if success else None)

    # 打印汇总
    print_summary(info, results)


if __name__ == '__main__':
    main()
