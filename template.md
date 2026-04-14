# Preservation Reminder - Template

## 日历事件模板

当识别到保全财产信息时，按以下模板为每项财产分别创建日历提醒事件。

### 事件标题
```
【保全到期】{case_number} - {财产类型}（{尾号/关键标识}）
```

#### 标题规则
- **银行账户**：优先使用 `account_tail`
  ```
  【保全到期】(2024)粤0305民初1234号 - 银行账户（尾号1234）
  ```
- **其他财产**：使用 `detail` 前 20 字符作为标识
  ```
  【保全到期】(2024)粤0305民初1234号 - 不动产（深圳市南山区科苑路...）
  ```
- **案号缺失时**：
  ```
  【保全到期】未知案号/Unknown - 银行账户（尾号1234）
  ```

### 日期
- **提醒日期**：到期前 30 天（全天事件）
- **日期格式**：`YYYY-MM-DD`

### 日历
- **默认日历**：`工作`

### 备注（Description）
```
案号/Case: {case_number}
财产类型/Type: {type}
财产详情/Detail: {detail}
保全期限/Duration: {duration}
保全起始/Start: {start_date}
保全到期/End: {end_date}

⚠️ 请及时向法院申请续行保全 / Please apply for renewal preservation in time
```

---

## 用户汇报格式模板

日历创建完成后，向用户汇报时统一使用以下格式：

```
📋 财产保全信息汇总 / Property Preservation Summary
============================================================
案号/Case: {case_number}
案由/Case Name: {case_name}
被保全人/Respondent: {respondent}
文书日期/Document Date: {document_date}
------------------------------------------------------------
保全财产清单 / Preservation Items:

  1. ✅ {财产类型}
     详情/Detail: {detail}
     期限/Duration: {duration}
     提醒日期/Reminder: {reminder_date}（到期前30天）

  2. ❌ {财产类型}
     详情/Detail: {detail}
     期限/Duration: {duration}
     提醒日期/Reminder: 创建失败

============================================================

成功创建 / Successfully created: {success_count}/{total_count} 个日历提醒

📅 请打开日历应用查看提醒事件
```

### 手写日期警告补充
若文书包含手写日期，在汇总前额外输出：
```
⚠️ 警告：本文书似乎包含手写日期！
⚠️ 请仔细核对提取的日期与原始文书
```

---

## 完整示例

**输入文书**：财产保全裁定书，(2024)粤0305民初1234号，买卖合同纠纷，被保全人：张三，银行账户 6222****1234（保全1年，2024-05-10 至 2025-05-10）

**输出日历事件**：
| 属性 | 值 |
|------|-----|
| 标题 | `【保全到期】(2024)粤0305民初1234号 - 银行账户（尾号1234）` |
| 提醒日期 | `2025-04-10` |
| 全天事件 | `是` |
| 日历 | `工作` |
| 备注 | `案号/Case: (2024)粤0305民初1234号\n财产类型/Type: 银行账户\n财产详情/Detail: 6222****1234\n保全期限/Duration: 1年\n保全起始/Start: 2024-05-10\n保全到期/End: 2025-05-10\n\n⚠️ 请及时向法院申请续行保全 / Please apply for renewal preservation in time` |
