# Legal Preservation Calendar

A Claude Code Skill for tracking asset preservation deadlines in legal proceedings.

专为法律从业者设计的财产保全到期提醒工具，自动从法院文书中提取保全信息并创建日历提醒。

## Features

- 📄 **PDF Text Extraction** - Extract text from preservation documents
- 🔍 **Smart Information Parsing** - Automatically extract case numbers, parties, property details, and preservation periods
- 📅 **Calendar Integration** - Create reminders in Apple Calendar (30 days before expiration)
- ⚠️ **Handwritten Date Warning** - Detects and warns about handwritten dates that may be OCR-misrecognized
- 🏢 **Mixed Property Support** - Handle documents with multiple property types and different preservation periods

## Supported Document Types

- 财产保全裁定书 (Property Preservation Orders)
- 保全结果告知书/通知书 (Preservation Result Notices)
- 协助执行通知书 (Assistance Execution Notices)
- 财产保全情况告知书 (Preservation Status Notifications)

## Installation

### Prerequisites

- Python 3.8+
- macOS with Apple Calendar
- Claude Code (optional, for LLM extraction)

### Install Dependencies

```bash
pip install pdfplumber anthropic
```

### Install Skill

```bash
# Clone repository
git clone https://github.com/yourusername/legal-preservation-calendar.git

# Copy to Claude Code skills directory
cp -r legal-preservation-calendar ~/.claude/skills/
```

## Usage

### Method 1: Direct Upload (in Claude Code)
Upload a PDF and say: "帮我创建保全提醒" or "preservation reminder"

### Method 2: Command Line

```bash
python scripts/preservation.py /path/to/preservation-document.pdf
```

## Calendar Event Format

| Field | Content Example |
|-------|----------------|
| Title | 【保全到期】(2024)粤0305民初1234号 - 银行账户（尾号8888）|
| Date | 30 days before expiration |
| Type | All-day event |
| Calendar | Work |
| Notes | Full case info, property details, renewal reminder |

## Example

### Input Document
Property preservation order freezing:
- Bank account: XXX Bank, Account: ****1234
- Amount: ¥1,000,000
- Duration: 1 year (2024-01-15 to 2025-01-14)

### Output Calendar Event
- **Reminder Date**: 2024-12-16 (30 days before expiration)
- **Title**: 【保全到期】(2024)粤0305民初1234号 - 银行账户（尾号1234）
- **Notes**: Case details and renewal instructions

## Important Notes

⚠️ **Handwritten Dates**: Court documents often contain handwritten dates that may be incorrectly recognized. Always verify dates against the original document.

⚠️ **Date Verification**: Review extracted information before relying on calendar reminders.

## Typical Preservation Periods

| Property Type | Typical Duration |
|--------------|------------------|
| Bank Accounts | 1 year |
| Real Estate | 3 years |
| Equity/Shares | 3 years |
| Vehicles | 2 years |

## Privacy & Security

- No document content is stored or transmitted to external servers (except Claude API for text extraction)
- Calendar events are created locally on your Mac
- Review the code - it's open source and transparent

## License

MIT License - See [LICENSE](LICENSE) file

## Contributing

Contributions welcome! Please ensure:
1. Code follows PEP 8 style
2. No sensitive client information in examples or tests
3. All examples use fictional data

## Author

Created for legal professionals to automate preservation tracking workflow.
