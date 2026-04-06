---
name: legal-preservation-calendar
description: Asset Preservation Reminder for Legal Proceedings. Upload PDF documents of property preservation (court orders, preservation result notices, or assistance execution notices), automatically extract preservation information (case number, property type, account/details, preservation duration), and create calendar reminders in Apple Calendar (30 days before expiration). Trigger words: "保全提醒", "财产保全", "preservation reminder", "legal preservation".
version: 1.0.0
author: 叶律师
license: MIT
---

# Legal Preservation Calendar

A Claude Code Skill for tracking asset preservation deadlines in legal proceedings.

上传财产保全文书 PDF，自动识别保全信息并按财产类型分别创建到期提醒日历。

## Features / 功能

1. **PDF Text Extraction** - Extract text from preservation documents using MinerU OCR
2. **Information Parsing** - Automatically extract:
   - Case number / 案号
   - Parties (applicant/respondent) / 当事人
   - Property type / 财产类型 (bank account银行账户, real estate不动产, equity股权, vehicle车辆, etc.)
   - Property details / 财产详情 (account number, address, equity amount)
   - Preservation duration / 保全期限
   - Start and end dates / 起止日期
3. **Smart Calculation** - Calculate reminder dates (30 days before expiration) / 提前30天创建提醒
4. **Calendar Integration** - Batch create events in Apple Calendar / 在苹果日历中批量创建提醒事件

## Supported Document Types / 支持文书类型

- Property Preservation Orders (财产保全裁定书)
- Preservation Result Notices (保全结果告知书/通知书)
- Assistance Execution Notices (协助执行通知书)
- Preservation Status Notifications (财产保全情况告知书)

## Installation / 安装

```bash
# Clone the repository
git clone https://github.com/xuezhihaoyun/-legal-preservation-calendar.git

# Copy to Claude Code skills directory
cp -r legal-preservation-calendar ~/.claude/skills/preservation-reminder
```

## Usage / 使用方法

### Method 1: Direct PDF Upload / 直接上传
Upload a PDF file and say: "帮我创建保全提醒" or "preservation reminder"

### Method 2: Specify Path / 指定路径
Say: "帮我创建保全提醒，文件在 /path/to/document.pdf"

### Method 3: Automatic Execution / 自动执行
AI automatically processes and creates reminders, then cleans up temporary files.

## Calendar Event Format / 日历事件格式

| Field | Content |
|-------|---------|
| Title / 标题 | 【保全到期】Case Number - Property Type (Identifier) |
| Date / 日期 | 30 days before expiration (到期前30天) |
| All Day / 全天 | Yes |
| Calendar / 日历 | "工作" (Work) |
| Notes / 备注 | Full case info, property details, renewal reminder |

## Handling Mixed Preservation Types / 混合保全处理

When a document contains properties with different preservation periods:
- Bank accounts / 银行账户: typically 1 year / 通常1年
- Real estate / 不动产: typically 3 years / 通常3年
- Equity / 股权: typically 3 years / 通常3年
- Vehicles / 车辆: typically 2 years / 通常2年

Each property gets its own calendar reminder / 各财产分别创建提醒。

## Temporary File Cleanup Rules / 临时文件清理规则

**Standard Workflow / 标准操作流程**:
- MinerU-generated temporary MD files (in the same directory as the original PDF) **must be deleted immediately after calendar events are created** / MinerU 转换生成的临时 MD 文件（位于原 PDF 同目录）**必须在日历事件创建完成后立即删除**
- Archive copies are preserved in `~/.claude/skills/mineru-ocr/archive/` for future reference / 归档副本保留在 `~/.claude/skills/mineru-ocr/archive/` 目录，如需查阅可调取
- Only temporary working files are deleted; archives and history are preserved / 仅删除临时工作文件，不清除归档和历史记录

## Important Notes / 注意事项

⚠️ **Handwritten Dates**: Court documents often contain handwritten dates that may be incorrectly recognized by OCR. Always verify dates against the original document. / 法院文书中的手写日期可能被OCR错误识别，请与原件核对。

⚠️ **Date Verification**: The Skill will display extracted information for verification before creating calendar events. / 创建日历事件前会显示提取的信息供核对。

⚠️ **MinerU API Token**: Need to configure MinerU API Token in advance (refer to mineru-ocr skill). / 需要提前配置 MinerU API Token。

## Requirements / 环境要求

- Python 3.8+
- macOS with Apple Calendar

## License / 许可

MIT License - See LICENSE file for details
