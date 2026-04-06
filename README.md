# Legal Preservation Calendar

A Claude Code Skill for tracking asset preservation deadlines in legal proceedings.

专为法律从业者设计的财产保全到期提醒工具，自动从法院文书中提取保全信息并创建日历提醒。

## Features

- 📄 **PDF Text Extraction** - Extract text from preservation documents using MinerU OCR
- 🔍 **Smart Information Parsing** - Automatically extract case numbers, parties, property details, and preservation periods
- 📅 **Calendar Integration** - Create reminders in Apple Calendar (30 days before expiration)
- ⚠️ **Handwritten Date Warning** - Detects and warns about handwritten dates that may be OCR-misrecognized
- 🏢 **Mixed Property Support** - Handle documents with multiple property types and different preservation periods
- 🧹 **Auto Cleanup** - Temporary files are automatically cleaned up after processing

## Supported Document Types

- 财产保全裁定书 (Property Preservation Orders)
- 保全结果告知书/通知书 (Preservation Result Notices)
- 协助执行通知书 (Assistance Execution Notices)
- 财产保全情况告知书 (Preservation Status Notifications)

## Prerequisites

- Python 3.8+
- macOS with Apple Calendar
- MinerU API Token (for PDF OCR)
- Claude Code (optional, for automated processing)

## Installation

### Step 1: Clone Repository

```bash
git clone https://github.com/xuezhihaoyun/-legal-preservation-calendar.git
cd -legal-preservation-calendar
```

### Step 2: Install to Claude Code Skills Directory

```bash
cp -r . ~/.claude/skills/preservation-reminder
```

### Step 3: Configure MinerU API Token

1. Visit [https://mineru.net/apiManage/token](https://mineru.net/apiManage/token)
2. Register/Login and create an API Token
3. Configure the token (refer to mineru-ocr skill documentation)

## Usage

### Method 1: Direct Upload (in Claude Code) - Recommended

Upload a PDF and say: "帮我创建保全提醒" or "preservation reminder"

The Skill will:
1. Convert PDF to text using MinerU OCR
2. Extract preservation information using LLM
3. Create calendar reminders (30 days before expiration)
4. **Automatically clean up temporary files**

### Method 2: Command Line

```bash
python scripts/preservation.py /path/to/preservation-document.pdf
```

## Calendar Event Format

| Field | Content Example |
|-------|----------------|
| Title | 【保全到期】(2024)粤XXXX民初XXXX号 - 银行账户（尾号XXXX）|
| Date | 30 days before expiration |
| Type | All-day event |
| Calendar | Work (工作) |
| Notes | Case details, property info, renewal instructions |

## Example

### Input Document
Property preservation order freezing:
- Bank account: [Bank Name], Account: ****XXXX
- Amount: ¥XXX,XXX
- Duration: 1 year (2024-XX-XX to 2025-XX-XX)

### Output Calendar Event
- **Reminder Date**: [30 days before expiration]
- **Title**: 【保全到期】(2024)粤XXXX民初XXXX号 - 银行账户（尾号XXXX）
- **Notes**: Case details and renewal instructions

## Temporary File Cleanup

This Skill automatically cleans up temporary files:

- **Deleted**: MinerU-generated temporary MD files (in the same directory as the original PDF)
- **Preserved**: Archive copies in `~/.claude/skills/mineru-ocr/archive/` for future reference

## Important Notes

⚠️ **Handwritten Dates**: Court documents often contain handwritten dates that may be incorrectly recognized. Always verify dates against the original document.

⚠️ **Date Verification**: Review extracted information before relying on calendar reminders.

⚠️ **Privacy**: Temporary files are automatically deleted after processing. Archive copies are stored locally.

## Typical Preservation Periods

| Property Type | Typical Duration |
|--------------|------------------|
| Bank Accounts | 1 year |
| Real Estate | 3 years |
| Equity/Shares | 3 years |
| Vehicles | 2 years |

## Privacy & Security

- No document content is stored permanently
- Temporary files are deleted immediately after calendar creation
- Archive copies are stored locally in MinerU archive directory
- Calendar events are created locally on your Mac
- Review the code - it's open source and transparent

## License

MIT License - See [LICENSE](LICENSE) file

## Contributing

Contributions welcome! Please ensure:
1. Code follows PEP 8 style
2. No sensitive client information in examples or tests
3. All examples use fictional/anonymized data

## Acknowledgments

Created for legal professionals to automate preservation tracking workflow.
