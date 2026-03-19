# CDI Suite Cloud — 开发任务书

## 一、项目概况

| 项目 | 信息 |
|------|------|
| **产品名称** | CDI Suite — Civil Design Intelligence Platform |
| **技术栈** | Python + Streamlit + Supabase + Google Gemini API |
| **本地版路径** | `/Users/hesiyuan/Desktop/Claude/ai-civil-design-suite/` |
| **运营版路径** | `/Users/hesiyuan/Desktop/Claude/cdi-suite-cloud/` |
| **线上地址** | `https://cdi-suite-cloud-f3svb9i29ma9kpwxgtdc6l.streamlit.app` |
| **GitHub 仓库** | `https://github.com/zhaoritianarweave-spec/cdi-suite-cloud` (Public) |
| **Supabase 项目** | (see Streamlit Cloud Secrets) |
| **当前状态** | 已上线，登录/注册/3个功能Tab均可用 |

---

## 二、产品架构

### 文件结构
```
cdi-suite-cloud/
├── app.py                          # 主入口：Auth gate → Tab 路由
├── requirements.txt                # 依赖：streamlit, google-genai, supabase, pypdf
├── supabase_schema.sql             # 数据库 schema
├── .streamlit/config.toml          # 主题配置（暗色）
├── utils/
│   ├── auth.py                     # Supabase 认证（登录/注册/登出/会话管理）
│   ├── usage.py                    # 用量追踪 & 配额控制（FREE_MONTHLY_LIMIT=5）
│   ├── gemini_client.py            # Gemini API 封装（图片/文本/视频生成）
│   └── ui_components.py            # 共享 UI（Header/Sidebar/CSS）
├── tabs/
│   ├── tab1_site_design.py         # Tab1: 场地渲染（Gemini 图片生成）
│   ├── tab2_drawing_analyser.py    # Tab2: 图纸分析（QTO/差异检测）
│   ├── tab3_construction_video.py  # Tab3: 飞越视频（Veo 3.1，暂未在运营版启用）
│   └── tab4_contract_guard.py      # Tab3: 合同审查（ContractGuard AU）
└── assets/
    ├── demo_contracts/             # 示例合同
    ├── demo_drawings/              # 示例图纸
    ├── demo_photos/                # 示例照片
    └── demo_videos/                # 示例视频
```

### 认证流程
```
用户访问 → app.py auth gate → 未登录？→ render_auth_page()（Login/Signup）
                              → 已登录？→ render_sidebar() + render_header() + 3 Tabs
```

### 用量追踪
- 数据库表：`usage_logs`（user_id, tab, model, created_at）
- 配额：FREE_MONTHLY_LIMIT = 5 次/月，按自然月重置
- 侧边栏显示："Usage: X / 5 this month"
- 超额后显示升级提示，阻止 AI 调用

### Session State 关键字段
| Key | 类型 | 用途 |
|-----|------|------|
| `user` | dict {id, email, created_at} | 当前登录用户 |
| `access_token` | str | Supabase JWT |
| `supabase_client` | Client | 复用的 Supabase 连接 |
| `model_id` | str | 当前选中的 Gemini 模型 |

### Secrets 配置（Streamlit Cloud）
```toml
GEMINI_API_KEY = "your-gemini-api-key"
SUPABASE_URL = "your-supabase-url"
SUPABASE_KEY = "your-supabase-anon-key"
STRIPE_SECRET_KEY = "your-stripe-secret-key"
STRIPE_PRO_MONTHLY_PRICE_ID = "price_xxx"
STRIPE_PRO_ANNUAL_PRICE_ID = "price_xxx"
APP_URL = "your-app-url"
```

---

## 三、已完成功能

- [x] Supabase 用户认证（邮箱注册/登录/登出）
- [x] 3 个功能 Tab（Site Renderer / Drawing Analyser / ContractGuard）
- [x] 用量追踪 & 免费配额（5次/月）
- [x] 侧边栏用量显示 + 进度条
- [x] 运营版移除了 API Key 输入框和模型选择器
- [x] Streamlit Cloud 部署上线
- [x] Supabase 数据库 schema + RLS 策略

---

## 四、待开发任务

### P0 — 变现核心（优先开发）

#### 4.1 用量计数落库 ✅ DONE
**已修复**：`record_usage()` 移至 AI 调用**成功后**才执行，避免 API 失败仍扣用量。

**验证清单**：
- [x] tab1_site_design.py：渲染成功后调用 `record_usage(user_id, "site_renderer", model)`
- [x] tab2_drawing_analyser.py：分析成功后调用 `record_usage(user_id, "drawing_analyser", model)`
- [x] tab4_contract_guard.py：审查成功后调用 `record_usage(user_id, "contract_guard", model)`
- [x] 每个 Tab 在调用前检查 `check_quota()` 并在超额时显示 `render_quota_exceeded()`

#### 4.2 Stripe 支付集成 ✅ DONE
**已实现**：完整的 Stripe Checkout 付费流程。

**实现方案**（无 Webhook，适配 Streamlit Cloud）：
1. ✅ Supabase `subscriptions` 表：user_id, plan, stripe_customer_id, stripe_subscription_id, current_period_end, status
2. ✅ `utils/stripe_client.py`：Stripe Checkout Session 创建、支付成功回调处理、订阅状态同步、Customer Portal
3. ✅ `app.py`：处理 `?payment=success&session_id=xxx` 回调参数
4. ✅ `utils/usage.py`：`check_quota()` 根据 plan 返回不同限额（free=5, pro=100, enterprise=unlimited）
5. ✅ 侧边栏显示当前 Plan badge + "Upgrade to Pro" 按钮（free 用户）/ "Manage Subscription" 链接（付费用户）

**定价方案**：
| Plan | 月费 | 年付月费 | 限额 |
|------|------|---------|------|
| Free | $0 | - | 3 次/月 |
| Pro | A$99/月 | A$69/月（年付 A$828） | 25 次/月 |
| Enterprise | Contact Sales | - | 无限制 |

**部署步骤**（需手动操作）：
1. ✅ 在 Supabase SQL Editor 执行 subscriptions 表创建语句
2. 在 [Stripe Dashboard](https://dashboard.stripe.com) 创建 Pro Product + 两个 Price：
   - Pro Monthly: A$99/month (recurring monthly)
   - Pro Annual: A$828/year (A$69/month, recurring yearly)
3. 在 Streamlit Cloud Secrets 中添加：`STRIPE_SECRET_KEY`, `STRIPE_PRO_MONTHLY_PRICE_ID`, `STRIPE_PRO_ANNUAL_PRICE_ID`
4. （可选）在 Stripe 中配置 Customer Portal（允许用户自助取消/换 plan）

#### 4.3 Supabase 邮件确认跳转修复
**已完成配置指引**：
- Supabase Dashboard → Authentication → URL Configuration
- Site URL 改为：`https://cdi-suite-cloud-f3svb9i29ma9kpwxgtdc6l.streamlit.app`

---

### P1 — 用户体验

#### 4.4 Landing Page（产品介绍页）
**当前问题**：未登录用户直接看到登录框，没有产品介绍。

**方案**：在 `auth.py` 的 `render_auth_page()` 中，登录/注册框之前添加：
- 产品标题 + 一句话价值主张
- 3 个核心功能卡片（带 icon + 简要说明）
- "Trusted by X+ professionals" 社会证明
- 登录/注册框放在下方

#### 4.5 密码重置功能
**方案**：
- 登录页添加 "Forgot Password?" 链接
- 调用 `supabase.auth.reset_password_email(email)`
- 用户点邮件链接后重置密码

#### 4.6 自定义域名
**选项**：
- Streamlit Cloud App URL 改短：如 `cdi-suite.streamlit.app`
- 或购买域名（如 `cdisuite.com.au`）绑定

#### 4.7 Tab2 图纸分析优化 ✅ DONE
- [x] 分析语句中 "90年职业生涯" 表述不当 → 已修改为 "leading Australian consulting engineering firm"
- [x] 删除图纸类型选择控件（Drawing Type selector）→ 已在之前版本删除

---

### P2 — 运营管理

#### 4.8 管理员后台
**功能**：
- 用户总数、活跃用户数、付费用户数
- 总 API 调用次数、按 Tab 分布
- 收入统计（如接入 Stripe）
- 用户列表（邮箱、注册时间、用量、Plan）

**方案**：新建 `admin.py` 页面，通过 URL 参数或特定邮箱白名单控制访问。

#### 4.9 用户反馈收集
**方案**：每次分析完成后显示 👍/👎 按钮，记录到 `feedback` 表。

#### 4.10 邮件通知
- 注册欢迎邮件
- 用量即将用尽提醒（4/5 时）
- 配额重置通知（每月1号）

---

### P3 — 产品增强

#### 4.11 分析历史记录
- 新建 `analysis_history` 表存储每次分析结果
- 用户可查看历史分析报告

#### 4.12 团队/组织功能
- 组织账号，多成员共享配额
- 管理员可添加/移除成员

#### 4.13 导出功能增强
- 合同审查报告导出 PDF
- 图纸分析报告导出 Excel
- 渲染图打包下载

---

## 五、技术注意事项

### Git 工作流
```bash
# 修改代码后推送
cd /Users/hesiyuan/Desktop/Claude/cdi-suite-cloud
git add <files>
git commit -m "描述"
git push origin main
# Streamlit Cloud 会自动检测 push 并重新部署
```

### 本地开发运行
```bash
cd /Users/hesiyuan/Desktop/Claude/cdi-suite-cloud
streamlit run app.py --server.port 8502
```

### 本地版（个人使用）
```bash
cd /Users/hesiyuan/Desktop/Claude/ai-civil-design-suite
streamlit run app.py --server.port 8501
```
本地版无需登录，API Key 在侧边栏输入，有模型选择器。

### Supabase 数据库操作
- Dashboard：https://supabase.com/dashboard （项目名 cdi-suite）
- SQL Editor 可直接执行 SQL
- 已有表：`usage_logs`（含 RLS 策略）

### 关键依赖版本
```
streamlit>=1.45.0
google-genai>=1.14.0
supabase>=2.15.0
pypdf>=5.0.0
Pillow>=11.0.0
```

---

## 六、成本预估

| 阶段 | 用户规模 | 月成本 |
|------|---------|--------|
| 冷启动 | 0-20人 | $50-100 |
| Beta | 20-100人 | $100-400 |
| 正式运营 | 100-500人 | $400-2,000 |

盈亏平衡：Pro $49/月 × 2-3个付费用户 即可覆盖冷启动成本。

---

## 七、运营策略

### 获客渠道
1. LinkedIn 建筑行业群组分享
2. 澳洲建筑行业论坛（如 BuildBlog, Architecture & Design）
3. Google Ads 投放关键词：contract review australia, construction drawing analysis
4. 免费 Demo 吸引试用 → 转付费

### 关键指标
- 注册转化率（访问→注册）
- 试用转付费率（免费→Pro）
- 月活跃用户（MAU）
- 平均用量（次/用户/月）
- Churn Rate（月流失率）
