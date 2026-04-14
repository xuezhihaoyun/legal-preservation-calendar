# preservation-reminder Skill 上下文

## 身份与调用规则

本 skill 用于识别财产保全文书（PDF），自动提取保全信息并在 Apple Calendar 中创建到期提醒事件。

## 核心规则

### 1. 全自动触发
当用户说出以下任一触发词，或发送保全文书 PDF 时，立即执行，**无需任何确认**：
- "保全提醒"
- "财产保全"
- "preservation reminder"
- 直接上传保全文书 PDF（财产保全裁定书、保全结果告知书、协助执行通知书、财产保全情况告知书）

### 2. 默认执行流程
1. **MinerU OCR 转换**：将 PDF 转换为 Markdown 文本。
2. **LLM 提取保全信息**：调用 Claude API（`claude-sonnet-4-6`）提取结构化 JSON 数据。
3. **计算提醒日期**：到期前 **30 天**。
4. **批量创建日历事件**：为每项保全财产分别创建独立的全天提醒事件。
5. **清理临时文件**：删除 MinerU 生成的临时 MD 文件（同目录下）。
6. **输出汇总报告**：汇报创建结果，如有手写日期则额外提醒核对。

### 3. 提取字段
- 案号（`case_number`）
- 案件名称/案由（`case_name`）
- 申请保全人（`applicant`）
- 被保全人（`respondent`）
- 保全财产列表（`preservation_items`），每项含：
  - 财产类型（`type`）：银行账户、不动产、股权、车辆、动产、其他
  - 财产详情（`detail`）
  - 保全期限（`duration`）
  - 期限月数（`duration_months`）
  - 起始日期（`start_date`，YYYY-MM-DD）
  - 结束日期（`end_date`，YYYY-MM-DD）
  - 银行账户尾号（`account_tail`）
- 文书日期（`document_date`）
- 是否有手写日期（`has_handwritten_date`）
- 法院名称（`court_name`）

### 4. 日期计算规则
- 若文书直接提供 `end_date`，以该日期为到期日。
- 若仅提供 `start_date` 和 `duration_months`，则按月推算到期日（处理日期溢出）。
- 若起始日期缺失， fallback 到 `document_date`。
- 提醒日期 = 到期日 - 30 天。

### 5. 日历事件格式规范
- **标题**：`【保全到期】案号 - 财产类型（尾号/关键标识）`
  - 银行账户优先显示尾号：`银行账户（尾号1234）`
  - 其他财产显示前 20 字符详情：`不动产（深圳市南山区...）`
- **日期**：提醒日期当天，全天事件（`allday event: true`）
- **日历**：默认"工作"
- **备注**：
  ```
  案号/Case: XXX
  财产类型/Type: XXX
  财产详情/Detail: XXX
  保全期限/Duration: XXX
  保全起始/Start: XXX
  保全到期/End: XXX

  ⚠️ 请及时向法院申请续行保全 / Please apply for renewal preservation in time
  ```

### 6. 混合保全处理
同一文书包含多种财产类型时，**每项财产分别创建独立的日历提醒**。

### 7. 手写日期警告
若 `has_handwritten_date` 为 `true`：
- 创建日历前额外打印警告信息
- 创建完成后在汇总报告中再次高亮提示用户核对日期

### 8. 临时文件清理
- 日历事件创建完成后，立即删除 MinerU 生成的 `.md` 临时文件（位于原 PDF 同目录）。
- 归档副本保留在 `~/.claude/skills/mineru-ocr/archive/`。

### 9. 异常处理
- **未识别到案号**：使用"未知案号/Unknown"作为 fallback，继续创建日历。
- **未识别到保全财产**：终止流程，报告错误。
- **日期计算失败**：跳过该项财产，继续处理其他项。
- **日历创建失败**：输出失败原因，继续处理其他项。
- **MinerU 未配置或转换失败**：报告错误，等待用户配置。

### 10. 参考文档
- 详细识别规范：`reference.md`
- 日历模板与示例：`template.md`
