# ArchiMind Pro — 项目开发情况报告

> 截止日期：2026年3月20日

---

## 一、项目概况

| 项目 | 信息 |
|------|------|
| **产品名称** | ArchiMind Pro（原 CDI Suite） |
| **定位** | 澳大利亚建筑与工程智能平台 |
| **技术栈** | Python + Streamlit + Supabase + Google Gemini + Stripe + Resend |
| **线上地址** | `https://cdi-suite-cloud-f3svb9i29ma9kpwxgtdc6l.streamlit.app` |
| **GitHub** | `https://github.com/zhaoritianarweave-spec/cdi-suite-cloud`（Public） |
| **代码规模** | ~4,300 行 Python，39+ commits |
| **当前状态** | **已上线运营，Beta 阶段** |

---

## 二、三大核心功能

### 1. Site Renderer（场地渲染器）— `tabs/tab1_site_design.py`（593行）
- 上传场地照片 → Gemini 生成多角度真实感建筑渲染图
- 支持 7 种项目类型（住宅/联排/公寓/商业/景观/市政/综合）
- 支持 6 种设计风格 + 12 种快捷特征选择
- 4 个视角（正面立面/鸟瞰/后院/街景），视角间保持设计一致性
- 环绕动画视频生成（Walkthrough Video）
- 渲染图单张下载 + ZIP 打包下载

### 2. Drawing Analyser（图纸分析器）— `tabs/tab2_drawing_analyser.py`（571行）
- 上传施工图纸（PDF/PNG）→ Gemini 智能分析
- 5 大分析维度：工程量提取(QTO)、差异检测、BCA/AS合规检查、可施工性审查、成本指标
- 结构化报告输出（概览/QTO表/差异/合规/可施工性/成本）
- 支持导出 Excel QTO 表 + Markdown 报告

### 3. ContractGuard（合同卫士）— `tabs/tab4_contract_guard.py`（836行）
- 上传施工合同（PDF/DOCX）→ 澳洲法律合规风险分析
- 10 类风险评估：法律合规、财务风险、缺失条款、不公平条款、付款条款、责任保险、争议解决、变更范围、工期延误、法规监管
- 三级风险标记（HIGH/MEDIUM/LOW）
- 基于 NCC、Security of Payment Act 等澳洲法规
- 导出 HTML 报告 + JSON 数据

---

## 三、已完成功能清单

### 认证与用户系统
- [x] Supabase 邮箱/密码注册、登录、登出
- [x] 会话持久化（access_token + session state）
- [x] Landing Page 产品介绍页（hero图 + 3功能卡片 + 登录框）
- [x] 管理员面板（仅 hsy8260@proton.me 可见，侧边栏 expander）
- [x] 用户管理：查看所有用户、升级/降级 Pro 计划

### 国际化
- [x] 中英文双语切换（286行翻译，覆盖全部 UI 文案）
- [x] 侧边栏语言选择器
- [x] Landing Page 语言切换

### 付费系统（Stripe）
- [x] Stripe Checkout 集成（测试模式 ✅，正式模式待切换）
- [x] Pro 月付 A$99 / 年付 A$69/月（A$828/年）
- [x] 支付成功回调 → 自动升级计划
- [x] Customer Portal（用户自助管理订阅）
- [x] 侧边栏显示 Plan 徽章 + 升级/管理按钮

### 用量与配额
- [x] API 调用计数落库（usage_logs 表）
- [x] 配额系统：Free 3次/月、Pro 25次/月、Enterprise 无限
- [x] 侧边栏用量显示 + 自定义 HTML 进度条
- [x] 超额阻断 + 升级提示
- [x] 调用成功后 `st.rerun()` 同步计数

### 邮件通知（Resend）
- [x] 注册欢迎邮件
- [x] 用量告警邮件（达到 80% 时触发）

### 数据存储
- [x] 分析历史记录（analysis_history 表 + 侧边栏展示）
- [x] 用户反馈收集（feedback 表，分析后 👍/👎）

### UI/UX
- [x] 深色主题 + 蓝图网格背景
- [x] Premium 字体（Plus Jakarta Sans + Space Grotesk + Noto Sans SC）
- [x] 卡片式模块导航（3功能卡片 + 下方工作区）
- [x] 欢迎栏（问候语 + 🗓️ 澳洲时间日历）
- [x] 渐变色品牌文字、按钮悬停效果、磨砂玻璃风格
- [x] 文件上传区虚线边框美化
- [x] 下载按钮统一样式（无 emoji）

### 导出功能
- [x] 渲染图 PNG 单张下载 + ZIP 打包
- [x] QTO 工程量表 Excel 导出
- [x] 图纸分析 Markdown 报告下载
- [x] 合同报告 HTML 导出 + JSON 数据导出

---

## 四、待完善功能

### P0 — 变现关键（优先级最高）

| 任务 | 状态 | 说明 |
|------|------|------|
| **Stripe 切换正式模式** | ⚠️ 待操作 | 目前使用 test key（sk_test_），需要在 Stripe Dashboard 切换到 live key（sk_live_），更新 Streamlit Cloud Secrets 中的 STRIPE_SECRET_KEY、STRIPE_PRO_MONTHLY_PRICE_ID、STRIPE_PRO_ANNUAL_PRICE_ID |
| **自定义域名** | ⚠️ 待购买 | 建议购买 `archimindpro.com.au` 或类似域名，通过 Cloudflare DNS 绑定到 Streamlit Cloud |

### P1 — 用户体验

| 任务 | 状态 | 说明 |
|------|------|------|
| **密码重置 UI** | ⚠️ 待开发 | Supabase 后端已支持 `reset_password_email()`，需在登录页 "Forgot Password?" 添加 UI 流程 |
| **渲染视角一致性优化** | 🔄 持续优化 | Prompt 已细化（材料/几何/光照匹配），但 Gemini 生成的不同视角仍可能存在差异，需持续调优 |
| **错误处理增强** | ⚠️ 待优化 | API 调用失败时的用户提示可更友好；可考虑接入 Sentry 做异常监控 |

### P2 — 功能扩展

| 任务 | 状态 | 说明 |
|------|------|------|
| **Tab3 施工视频** | ❌ 未开发 | `tab3_construction_video.py` 仅 11 行占位代码，需接入 Veo 3.1 API 实现施工过程动画 |
| **团队/组织功能** | ❌ 未开发 | 多用户组织账号、共享配额、成员管理 |
| **导出 PDF 报告** | ⚠️ 部分完成 | 合同报告支持 HTML，图纸报告支持 MD/Excel；可增加统一 PDF 格式导出 |
| **移动端适配** | ⚠️ 待测试 | Streamlit 响应式布局基础上，手机/平板端可能需要额外适配 |

### P3 — 运营与增长

| 任务 | 状态 | 说明 |
|------|------|------|
| **数据分析仪表盘** | ❌ 未开发 | 注册转化率、试用→付费转化率、MAU、留存率等关键指标 |
| **Stripe Webhook** | ❌ 未接入 | Streamlit Cloud 不支持 webhook endpoint，目前用轮询方式同步订阅状态；如迁移到其他平台可接入 |
| **SEO / Google Ads** | ❌ 未启动 | 关键词：contract review australia, construction drawing analysis |
| **更多语言** | ❌ 未计划 | 当前仅中英文，可扩展日语、西班牙语等 |

---

## 五、技术架构

### 数据库（Supabase PostgreSQL）

| 表名 | 用途 | RLS |
|------|------|-----|
| `usage_logs` | API 调用记录 | 用户仅读写自己的 |
| `subscriptions` | 订阅计划 & Stripe 信息 | 用户读自己的，service_role 管全部 |
| `feedback` | 用户反馈（👍/👎） | 用户仅插入自己的 |
| `analysis_history` | 分析历史记录 | 用户仅读写自己的 |

### Secrets 配置（Streamlit Cloud）

```
GEMINI_API_KEY          — Google Gemini API 密钥
SUPABASE_URL            — Supabase 项目 URL
SUPABASE_KEY            — Supabase anon key
SUPABASE_SERVICE_ROLE_KEY — Supabase 管理员密钥（admin 面板用）
STRIPE_SECRET_KEY       — Stripe API 密钥（当前为 test key）
STRIPE_PRO_MONTHLY_PRICE_ID — Stripe 月付价格 ID
STRIPE_PRO_ANNUAL_PRICE_ID  — Stripe 年付价格 ID
APP_URL                 — 应用 URL（支付回调用）
RESEND_API_KEY          — Resend 邮件 API 密钥
```

### 文件结构

```
cdi-suite-cloud/
├── app.py                              # 主入口：Auth gate → 卡片导航 → 工作区
├── requirements.txt                    # 依赖
├── supabase_schema.sql                 # 数据库 schema
├── .streamlit/config.toml              # 主题配置（暗色）
├── assets/
│   ├── ui/                             # Landing Page 图片（hero + 3功能卡片）
│   ├── demo_drawings/                  # 示例图纸
│   └── demo_contracts/                 # 示例合同
├── tabs/
│   ├── tab1_site_design.py             # 场地渲染器（593行）
│   ├── tab2_drawing_analyser.py        # 图纸分析器（571行）
│   ├── tab3_construction_video.py      # 施工视频（占位，11行）
│   ├── tab4_contract_guard.py          # 合同卫士（836行）
│   └── tab_admin.py                    # 管理员面板（184行）
└── utils/
    ├── auth.py                         # 认证（238行）
    ├── gemini_client.py                # Gemini API 封装（161行）
    ├── stripe_client.py                # Stripe 支付（358行）
    ├── usage.py                        # 配额管理（132行）
    ├── i18n.py                         # 国际化（286行）
    ├── ui_components.py                # UI 组件 & CSS（522行）
    ├── email_service.py                # 邮件通知（150行）
    ├── history.py                      # 历史记录（76行）
    └── feedback.py                     # 反馈收集（74行）
```

### 定价方案

| Plan | 月费 | 年付月费 | 限额 |
|------|------|---------|------|
| Free | $0 | - | 3 次/月 |
| Pro | A$99/月 | A$69/月（年付 A$828） | 25 次/月 |
| Enterprise | 面议 | - | 无限制 |

---

## 六、部署与开发

### 线上部署
- Streamlit Cloud 自动部署：push 到 `main` 分支 → 2-3 分钟自动更新
- 无需手动操作

### 本地开发
```bash
cd /Users/hesiyuan/Desktop/Claude/cdi-suite-cloud
streamlit run app.py --server.port 8502
```

### Git 提交规范
```bash
git add <files>
git commit -m "描述"
git push origin main
```
- Git 用户名：steven（非真名）
- Co-Author: Claude Opus 4.6

---

## 七、品牌信息

| 项目 | 内容 |
|------|------|
| **品牌名** | ArchiMind Pro |
| **英文 slogan** | Architecture & Engineering Intelligence |
| **中文 slogan** | 建筑与工程智能 |
| **主题色** | #0A7CFF（蓝）+ #00D4AA（青绿）|
| **背景色** | #0E1117（深灰）|
| **字体** | Plus Jakarta Sans / Space Grotesk / Noto Sans SC |
| **管理员邮箱** | hsy8260@proton.me |
| **目标市场** | 澳大利亚建筑与工程行业 |

---

## 八、下一步行动建议

1. **切换 Stripe 正式密钥** — 开始正式收费
2. **购买域名** — `archimindpro.com.au` 或类似
3. **持续优化渲染一致性** — 调优 Gemini prompt
4. **开发密码重置 UI** — 完善认证体验
5. **接入更多用户** — 发放 Beta 邀请码，收集反馈
6. **考虑 Tab3 施工视频** — 等 Veo 3.1 API 稳定后接入
