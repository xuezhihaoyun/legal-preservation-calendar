# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

## [1.1.0] - 2026-04-14

### Added
- 新增全自动触发规则，支持发送保全文书 PDF 时直接调用 skill，无需额外口令确认。
- 新增 `claude.md`：skill 级别上下文规则，明确触发条件、执行流程、日历格式规范及异常处理。
- 新增 `reference.md`：详细的识别规范，涵盖 OCR 引擎选择、LLM JSON 字段定义、日期计算规则、临时文件清理规则及异常处理。
- 新增 `template.md`：日历输出模板与标准化用户汇报格式模板。
- 新增 `CHANGELOG.md`：记录版本更迭。

### Changed
- 更新 `SKILL.md` 中的描述（v1.0.0 已存在，本次在文档层面做了规则下沉）。

## [1.0.0] - 2025-04-06

### Added
- 初始版本发布。
- 支持使用 MinerU OCR 识别财产保全文书 PDF 并转换为 Markdown。
- 调用 Claude API（`claude-sonnet-4-6`）自动提取案号、案由、当事人、保全财产列表、期限、日期等结构化信息。
- 自动计算到期前 30 天的提醒日期。
- 在 Apple Calendar "工作"日历中为每项保全财产批量创建独立的全天提醒事件。
- 支持财产保全裁定书、保全结果告知书、协助执行通知书、财产保全情况告知书等多种文书类型。
- 添加手写日期警告和汇总报告输出。
- 添加 `SKILL.md`、`README.md`、`LICENSE` 和主脚本 `scripts/preservation.py`。
