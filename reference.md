# Preservation Reminder - Reference

## 1. 触发条件

当用户说出以下任一触发词，或发送保全文书 PDF 时，立即全自动执行：
- "保全提醒"
- "财产保全"
- "preservation reminder"
- 直接上传保全文书 PDF

## 2. OCR 引擎选择

- **默认**：MinerU（云端 API，需提前配置 Token）
- **PDF 处理**：通过 `osascript` 调用 `mineru-ocr/scripts/convert.js` 转换为 Markdown
- **临时文件**：生成的 `.md` 文件位于原 PDF 同目录，处理完成后立即删除

## 3. 信息提取规则

### 3.1 LLM 提取方式
使用 Claude API（`claude-sonnet-4-6`）对 Markdown 内容进行结构化提取，返回固定 JSON 格式。

### 3.2 JSON 字段定义
| 字段 | 类型 | 说明 |
|------|------|------|
| `case_number` | string | 案号，如：(2024)粤0305民初1234号 |
| `case_name` | string | 案件名称/案由 |
| `applicant` | string | 申请保全人 |
| `respondent` | string | 被保全人 |
| `preservation_items` | array | 财产列表，每项一个对象 |
| `preservation_items[].type` | string | 财产类型：银行账户、不动产、股权、车辆、动产、其他 |
| `preservation_items[].detail` | string | 财产具体信息 |
| `preservation_items[].duration` | string | 保全期限，如：1年、2年、3年 |
| `preservation_items[].duration_months` | number/string | 期限对应的月数 |
| `preservation_items[].start_date` | string | 起始日期（YYYY-MM-DD），未明确可留空 |
| `preservation_items[].end_date` | string | 结束日期（YYYY-MM-DD），未明确可留空 |
| `preservation_items[].account_tail` | string | 银行账户尾号（4位或关键标识） |
| `document_date` | string | 文书日期（YYYY-MM-DD） |
| `has_handwritten_date` | boolean | 文书是否包含手写日期 |
| `court_name` | string | 法院名称 |

### 3.3 默认期限速查表
| 财产类型 | 通常期限 |
|----------|----------|
| 银行账户 | 1 年 |
| 不动产 | 3 年 |
| 股权 | 3 年 |
| 车辆 | 2 年 |
| 动产 | 视文书而定 |

### 3.4 LLM Prompt 约束
- 同一份文书中的多种财产必须分别列出。
- 必须检查日期是否为手写或 OCR 错误。
- 仅返回 JSON，不输出解释文字。

## 4. 日期计算规则

### 4.1 到期日计算优先级
1. **最高优先**：直接使用 `end_date`（文书已明确到期日）。
2. **次优先**：`start_date` + `duration_months` 推算。
3. **Fallback**：`document_date` + `duration_months` 推算。
4. **最后手段**：当前系统日期 + `duration_months` 推算。

### 4.2 日期溢出处理
按月推算时，若目标月份不存在对应日期（如 1月31日 + 1个月），取该月最后一天（2月28/29日）。

### 4.3 提醒日期
```
reminder_date = end_date - 30 days
```

## 5. 日历创建规则

- **目标日历**：默认"工作"日历（`calendar_name="工作"`）。
- **事件类型**：全天事件（`allday event: true`）。
- **提醒设置**：创建当天触发 display alarm（`trigger interval: 0`）。
- **批量创建**：每项保全财产独立创建一个日历事件。

## 6. 临时文件清理规则

- **删除对象**：MinerU 生成的 `.md` 临时文件（位于原 PDF 同目录）。
- **删除时机**：日历事件创建完成后立即执行。
- **保留对象**：`~/.claude/skills/mineru-ocr/archive/` 下的归档副本。

## 7. 异常处理

| 异常场景 | 处理方式 |
|----------|----------|
| MinerU 未配置 | 报告错误，提示安装/配置 mineru-ocr skill。 |
| PDF 转换失败 | 报告失败原因，终止流程。 |
| LLM 提取失败 | 报告失败原因，终止流程。 |
| 未识别到案号 | 使用 fallback "未知案号/Unknown"，继续创建日历。 |
| 未识别到保全财产 | 终止流程，报告错误。 |
| 某项日期计算失败 | 跳过该项，继续处理其他财产。 |
| 某项日历创建失败 | 报告失败原因，继续处理其他财产。 |

## 8. 输出要求

- 控制台打印提取信息供核对。
- 手写日期时打印高亮警告。
- 为每项财产打印处理进度（起始、到期、提醒日期）。
- 最终输出汇总报告（成功数/总数、财产清单、提醒日期）。
