"""Internationalisation helpers for CDI Suite Cloud."""

import streamlit as st

TRANSLATIONS = {
    # ── Landing page hero ──
    "hero_title": {"en": "ARCHIMIND PRO", "zh": "ARCHIMIND PRO"},
    "hero_subtitle": {"en": "Architecture & Engineering Intelligence Platform", "zh": "建筑与工程智能平台"},
    "hero_caption": {
        "en": "Photorealistic renderings · Construction drawing analysis · Contract risk review — based on Australian laws and regulations",
        "zh": "真实感渲染 · 施工图纸分析 · 合同风险审查 — 依据澳洲法律法规",
    },
    # ── Landing feature cards ──
    "feat_renderer_title": {"en": "Site Renderer", "zh": "场地渲染器"},
    "feat_renderer_desc": {
        "en": "Upload a site photo, generate multi-angle photorealistic renderings with design consistency.",
        "zh": "上传场地照片，生成多角度真实感渲染图，风格统一协调。",
    },
    "feat_analyser_title": {"en": "Drawing Analyser", "zh": "图纸分析器"},
    "feat_analyser_desc": {
        "en": "Quantity takeoff, BCA/AS compliance checks and drawing discrepancy detection, based on Australian laws and regulations.",
        "zh": "工程量提取、BCA/AS 合规检查与图纸差异检测，依据澳洲法律法规。",
    },
    "feat_contract_title": {"en": "ContractGuard", "zh": "合同卫士"},
    "feat_contract_desc": {
        "en": "Contract risk analysis based on Australian laws, regulations, NCC & Security of Payment Act.",
        "zh": "基于澳洲法律法规、NCC 与支付安全法的合同风险分析。",
    },
    "pricing_badge": {
        "en": "Currently in Beta — Free to try",
        "zh": "内测中 — 免费体验",
    },
    # ── Auth forms ──
    "log_in": {"en": "Log In", "zh": "登录"},
    "sign_up": {"en": "Sign Up", "zh": "注册"},
    "email": {"en": "Email", "zh": "邮箱"},
    "password": {"en": "Password", "zh": "密码"},
    "confirm_password": {"en": "Confirm Password", "zh": "确认密码"},
    "create_account": {"en": "Create Account", "zh": "创建账号"},
    "forgot_password": {"en": "Forgot Password?", "zh": "忘记密码？"},
    "send_reset_link": {"en": "Send Reset Link", "zh": "发送重置链接"},
    "enter_your_email": {"en": "Enter your email", "zh": "输入你的邮箱"},
    "email_placeholder": {"en": "you@company.com", "zh": "you@company.com"},
    "pw_help": {"en": "At least 6 characters", "zh": "至少6个字符"},
    # Auth messages
    "err_enter_email_pw": {"en": "Please enter email and password.", "zh": "请输入邮箱和密码。"},
    "err_fill_all": {"en": "Please fill in all fields.", "zh": "请填写所有字段。"},
    "err_pw_length": {"en": "Password must be at least 6 characters.", "zh": "密码至少需要6个字符。"},
    "err_pw_mismatch": {"en": "Passwords do not match.", "zh": "两次密码不一致。"},
    "err_invalid_login": {"en": "Invalid email or password.", "zh": "邮箱或密码错误。"},
    "err_already_registered": {"en": "This email is already registered. Please log in.", "zh": "该邮箱已注册，请直接登录。"},
    "msg_account_created": {
        "en": "Account created! Please check your email to confirm, then log in.",
        "zh": "账号创建成功！请查收确认邮件，然后登录。",
    },
    "msg_reset_sent": {"en": "Password reset email sent! Check your inbox.", "zh": "密码重置邮件已发送，请查收！"},
    "err_enter_email": {"en": "Please enter your email.", "zh": "请输入邮箱。"},
    "auth_footer": {
        "en": "ArchiMind Pro v1.0",
        "zh": "ArchiMind Pro v1.0",
    },
    # ── Header ──
    "header_title": {"en": "ARCHIMIND PRO", "zh": "ARCHIMIND PRO"},
    "header_subtitle": {"en": "Architecture · Engineering · Visualisation", "zh": "建筑 · 工程 · 可视化"},
    "header_badge": {"en": "ARCHITECTURE & ENGINEERING INTELLIGENCE", "zh": "建筑与工程智能"},
    # ── Sidebar ──
    "sidebar_brand": {"en": "ARCHIMIND PRO", "zh": "ARCHIMIND PRO"},
    "sidebar_brand_sub": {"en": "Architecture & Engineering Intelligence", "zh": "建筑与工程智能"},
    "sidebar_footer_line1": {"en": "ArchiMind Pro v1.0", "zh": "ArchiMind Pro v1.0"},
    "sidebar_footer_line2": {"en": "Architecture & Engineering Intelligence", "zh": "建筑与工程智能"},
    "plan_label": {"en": "{name} Plan", "zh": "{name} 计划"},
    "usage_label": {"en": "Usage: {used} / {limit} this month", "zh": "用量：本月 {used} / {limit}"},
    "free_quota_reached": {"en": "Free quota reached", "zh": "免费额度已用完"},
    "billing_monthly": {"en": "Monthly — A$99/mo", "zh": "月付 — A$99/月"},
    "billing_annual": {"en": "Annual — A$69/mo (save 30%)", "zh": "年付 — A$69/月（省30%）"},
    "upgrade_btn": {"en": "⚡ Upgrade to Pro — {price}", "zh": "⚡ 升级 Pro — {price}"},
    "redirecting_checkout": {"en": "Redirecting to checkout...", "zh": "正在跳转结账页面..."},
    "manage_subscription": {"en": "Manage Subscription", "zh": "管理订阅"},
    "log_out": {"en": "Log Out", "zh": "退出登录"},
    # ── App / Tabs ──
    "tab_site_renderer": {"en": "Site Renderer", "zh": "场地渲染"},
    "tab_drawing_analyser": {"en": "Drawing Analyser", "zh": "图纸分析"},
    "tab_contract_guard": {"en": "ContractGuard", "zh": "合同审查"},
    "payment_success": {"en": "Payment successful! Your plan has been upgraded.", "zh": "支付成功！您的计划已升级。"},
    "payment_fail": {
        "en": "Could not verify payment. Please contact support if your plan was not updated.",
        "zh": "无法验证支付。如果计划未更新，请联系客服。",
    },
    # ── Tab1: Site Renderer ──
    "t1_title": {"en": "Site Intelligence Renderer", "zh": "场地智能渲染器"},
    "t1_caption": {
        "en": "Upload a site photograph — ArchiMind Pro analyses existing conditions and produces multi-angle photorealistic renderings with design consistency across all viewpoints.",
        "zh": "上传场地照片 — ArchiMind Pro 分析现有条件，生成多角度真实感渲染图，所有视角保持设计一致性。",
    },
    "t1_site_photo": {"en": "Site Photograph", "zh": "场地照片"},
    "t1_upload": {"en": "Upload a site photo", "zh": "上传场地照片"},
    "t1_demo_label": {"en": "OR SELECT A DEMO SITE", "zh": "或选择示例场地"},
    "t1_design_params": {"en": "Design Parameters", "zh": "设计参数"},
    "t1_project_type": {"en": "Project Type", "zh": "项目类型"},
    "t1_design_language": {"en": "Design Language", "zh": "设计风格"},
    "t1_quick_features_label": {"en": "QUICK-PICK DESIGN FEATURES", "zh": "快速选择设计特征"},
    "t1_quick_features": {"en": "Quick Features", "zh": "快速特征"},
    "t1_viewpoints": {"en": "Rendering Viewpoints", "zh": "渲染视角"},
    "t1_design_brief": {"en": "Design Brief", "zh": "设计说明"},
    "t1_brief_placeholder": {
        "en": "Describe your vision... e.g., Open-plan living facing north, master suite on ground floor, seamless indoor-outdoor flow to the pool area...",
        "zh": "描述您的愿景... 例如：朝北的开放式起居空间，主卧套房在一楼，室内外无缝衔接至泳池区域...",
    },
    "t1_generate_btn": {"en": "Generate {n} Rendering(s)", "zh": "生成 {n} 张渲染图"},
    "t1_upload_hint": {"en": "Upload a site photograph to activate the engine.", "zh": "上传场地照片以启动引擎。"},
    "t1_select_viewpoint": {"en": "Select at least one viewpoint.", "zh": "请至少选择一个视角。"},
    "t1_results_title": {"en": "Generated Renderings", "zh": "生成的渲染图"},
    "t1_download": {"en": "Download {label}", "zh": "下载 {label}"},
    "t1_video_title": {"en": "Cinematic Flyover Video", "zh": "电影级飞越视频"},
    "t1_video_caption": {
        "en": "Generate an 8-second cinematic fly-around video from the aerial rendering using ArchiMind Pro.",
        "zh": "使用 ArchiMind Pro 从鸟瞰渲染图生成8秒电影级环绕飞越视频。",
    },
    "t1_video_btn": {"en": "🎬 Generate Flyover Video", "zh": "🎬 生成飞越视频"},
    "t1_video_ready": {"en": "✓ VIDEO READY | Cinematic flyover delivered", "zh": "✓ 视频就绪 | 电影级飞越已交付"},
    "t1_video_download": {"en": "⬇️ Download Flyover Video", "zh": "⬇️ 下载飞越视频"},
    "t1_video_failed": {"en": "Video generation failed. Please try again.", "zh": "视频生成失败，请重试。"},
    "t1_progress_warmup": {"en": "Warming up engine...", "zh": "引擎预热中..."},
    # Project types
    "pt_residential": {"en": "Residential - House", "zh": "住宅 - 独栋"},
    "pt_townhouse": {"en": "Townhouse / Duplex", "zh": "联排 / 双拼"},
    "pt_apartment": {"en": "Apartment", "zh": "公寓"},
    "pt_commercial": {"en": "Commercial", "zh": "商业"},
    "pt_landscape": {"en": "Landscape / Streetscape", "zh": "景观 / 街景"},
    "pt_civil": {"en": "Civil Infrastructure", "zh": "市政基础设施"},
    "pt_mixed": {"en": "Mixed Use", "zh": "综合体"},
    # Design styles
    "ds_modern": {"en": "Modern", "zh": "现代"},
    "ds_traditional": {"en": "Traditional", "zh": "传统"},
    "ds_industrial": {"en": "Industrial", "zh": "工业"},
    "ds_minimalist": {"en": "Minimalist", "zh": "极简"},
    "ds_sustainable": {"en": "Sustainable", "zh": "可持续"},
    "ds_coastal": {"en": "Coastal", "zh": "滨海"},
    # Viewpoints
    "vp_front": {"en": "🏠 Front Elevation", "zh": "🏠 正面立面"},
    "vp_aerial": {"en": "🛩️ Bird's Eye / Aerial", "zh": "🛩️ 鸟瞰"},
    "vp_rear": {"en": "🌳 Rear / Garden View", "zh": "🌳 后院 / 花园视角"},
    "vp_street": {"en": "🚶 Street Level", "zh": "🚶 街景视角"},
    # Quick features
    "qf_double_garage": {"en": "🚗 Double Garage", "zh": "🚗 双车库"},
    "qf_triple_garage": {"en": "🚙 Triple Garage", "zh": "🚙 三车库"},
    "qf_luxury_landscaping": {"en": "🌿 Luxury Landscaping", "zh": "🌿 豪华景观"},
    "qf_backyard_pool": {"en": "🏊 Backyard Pool", "zh": "🏊 后院泳池"},
    "qf_outdoor_kitchen": {"en": "🍖 Outdoor Kitchen", "zh": "🍖 户外厨房"},
    "qf_large_backyard": {"en": "🌳 Large Backyard", "zh": "🌳 大后院"},
    "qf_wrap_porch": {"en": "🏡 Wrap-around Porch", "zh": "🏡 环绕式门廊"},
    "qf_floor_glass": {"en": "🪟 Floor-to-ceiling Glass", "zh": "🪟 落地玻璃"},
    "qf_rooftop_terrace": {"en": "☀️ Rooftop Terrace", "zh": "☀️ 屋顶露台"},
    "qf_gated_entry": {"en": "🔒 Gated Entry", "zh": "🔒 门禁入口"},
    "qf_two_storey": {"en": "🏗️ Two Storey", "zh": "🏗️ 两层"},
    "qf_three_storey": {"en": "🏔️ Three Storey", "zh": "🏔️ 三层"},
    # ── Tab2: Drawing Analyser ──
    "t2_title": {"en": "Drawing Intelligence & Quantity Take-Off", "zh": "图纸智能分析与工程量提取"},
    "t2_caption": {
        "en": "Upload a construction drawing — ArchiMind Pro reads annotations, extracts quantities, detects discrepancies and checks compliance based on Australian laws and regulations.",
        "zh": "上传施工图纸 — ArchiMind Pro 自动读取标注、提取工程量、检测差异，依据澳洲法律法规进行合规检查。",
    },
    "t2_drawing": {"en": "Construction Drawing", "zh": "施工图纸"},
    "t2_upload": {"en": "Upload a drawing", "zh": "上传图纸"},
    "t2_demo_label": {"en": "OR SELECT A DEMO DRAWING", "zh": "或选择示例图纸"},
    "t2_analysis_params": {"en": "Analysis Parameters", "zh": "分析参数"},
    "t2_focus_label": {"en": "ANALYSIS FOCUS", "zh": "分析重点"},
    "t2_focus": {"en": "Analysis Focus", "zh": "分析重点"},
    "t2_analyse_btn": {"en": "🔬 Analyse Drawing", "zh": "🔬 分析图纸"},
    "t2_upload_hint": {"en": "Upload a construction drawing to activate the engine.", "zh": "上传施工图纸以启动引擎。"},
    "t2_select_focus": {"en": "Select at least one analysis focus.", "zh": "请至少选择一个分析重点。"},
    "t2_results_title": {"en": "Analysis Report", "zh": "分析报告"},
    "t2_tab_overview": {"en": "📋 Overview", "zh": "📋 概览"},
    "t2_tab_qto": {"en": "📊 Quantity Take-off", "zh": "📊 工程量提取"},
    "t2_tab_discrepancies": {"en": "🔍 Discrepancies", "zh": "🔍 差异检测"},
    "t2_tab_compliance": {"en": "✅ Compliance", "zh": "✅ 合规检查"},
    "t2_tab_constructability": {"en": "🏗️ Constructability", "zh": "🏗️ 可施工性"},
    "t2_tab_cost": {"en": "💰 Cost Indicators", "zh": "💰 成本指标"},
    "t2_no_qto": {"en": "No quantity data extracted.", "zh": "未提取到工程量数据。"},
    "t2_no_discrepancies": {"en": "No discrepancies detected.", "zh": "未检测到差异。"},
    "t2_no_compliance": {"en": "No compliance observations.", "zh": "无合规观察结果。"},
    "t2_no_constructability": {"en": "No constructability notes.", "zh": "无可施工性备注。"},
    "t2_no_cost": {"en": "No cost indicators generated.", "zh": "未生成成本指标。"},
    "t2_download_report": {"en": "📄 Download Full Report (.md)", "zh": "📄 下载完整报告 (.md)"},
    "t2_download_qto": {"en": "📊 Download QTO Table (.csv)", "zh": "📊 下载工程量表 (.csv)"},
    "t2_complete": {"en": "✓ ANALYSIS COMPLETE | Full report delivered", "zh": "✓ 分析完成 | 完整报告已交付"},
    # Tab2 focus options
    "af_qto": {"en": "📊 Quantity Take-off (QTO)", "zh": "📊 工程量提取 (QTO)"},
    "af_discrepancy": {"en": "🔍 Discrepancy / Error Detection", "zh": "🔍 差异 / 错误检测"},
    "af_compliance": {"en": "✅ Compliance Check (BCA/AS)", "zh": "✅ 合规检查 (BCA/AS)"},
    "af_constructability": {"en": "🏗️ Constructability Review", "zh": "🏗️ 可施工性审查"},
    "af_cost": {"en": "💰 Cost Estimation Indicators", "zh": "💰 成本估算指标"},
    # Tab2 progress
    "t2_p1": {"en": "Scanning drawing geometry...", "zh": "扫描图纸几何信息..."},
    "t2_p2": {"en": "Identifying annotation layers...", "zh": "识别标注图层..."},
    "t2_p3": {"en": "Extracting dimensions & quantities...", "zh": "提取尺寸和工程量..."},
    "t2_p4": {"en": "Cross-referencing standard symbols...", "zh": "交叉引用标准符号..."},
    "t2_p5": {"en": "Checking dimensional consistency...", "zh": "检查尺寸一致性..."},
    "t2_p6": {"en": "Evaluating compliance references...", "zh": "评估合规参考..."},
    "t2_p7": {"en": "Compiling analysis report...", "zh": "编制分析报告..."},
    # ── Tab4: ContractGuard ──
    "t4_title": {"en": "ContractGuard — Clause Risk Analyser", "zh": "合同卫士 — 条款风险分析器"},
    "t4_caption": {
        "en": "Upload a construction contract — ArchiMind Pro checks Australian legislation compliance, identifies unfair terms, benchmarks financial provisions and generates a comprehensive risk report.",
        "zh": "上传施工合同 — ArchiMind Pro 检查澳洲法律法规合规性、识别不公平条款、对标财务条款并生成综合风险报告。",
    },
    "t4_documents": {"en": "Contract Documents", "zh": "合同文件"},
    "t4_upload": {"en": "Upload contract documents", "zh": "上传合同文件"},
    "t4_demo_label": {"en": "OR SELECT A DEMO CONTRACT", "zh": "或选择示例合同"},
    "t4_scope": {"en": "Analysis Scope", "zh": "分析范围"},
    "t4_risk_categories": {"en": "Risk Categories", "zh": "风险类别"},
    "t4_risk_help": {"en": "Select which risk categories to evaluate. All selected by default.", "zh": "选择要评估的风险类别，默认全选。"},
    "t4_analyse_btn": {"en": "🛡️ Analyse Contract", "zh": "🛡️ 分析合同"},
    "t4_upload_hint": {"en": "Upload a contract document to activate the engine.", "zh": "上传合同文件以启动引擎。"},
    "t4_results_title": {"en": "Risk Assessment", "zh": "风险评估"},
    "t4_overall_risk": {"en": "Overall Risk", "zh": "综合风险"},
    "t4_high_risk": {"en": "High Risk", "zh": "高风险"},
    "t4_medium": {"en": "Medium", "zh": "中风险"},
    "t4_low_risk": {"en": "Low Risk", "zh": "低风险"},
    "t4_tab_summary": {"en": "📋 Executive Summary", "zh": "📋 执行摘要"},
    "t4_tab_findings": {"en": "🔍 Detailed Findings", "zh": "🔍 详细发现"},
    "t4_tab_risk_chart": {"en": "📊 Risk by Category", "zh": "📊 按类别风险"},
    "t4_no_findings": {"en": "No findings to display.", "zh": "暂无发现。"},
    "t4_recommendation": {"en": "Recommendation:", "zh": "建议："},
    "t4_benchmark": {"en": "Market Benchmark:", "zh": "市场基准："},
    "t4_download_report": {"en": "📄 Download Full Report (.html)", "zh": "📄 下载完整报告 (.html)"},
    "t4_download_json": {"en": "📊 Download Raw Data (.json)", "zh": "📊 下载原始数据 (.json)"},
    "t4_complete": {"en": "✓ ANALYSIS COMPLETE | Risk assessment delivered", "zh": "✓ 分析完成 | 风险评估已交付"},
    "t4_analysis_failed": {"en": "Analysis failed. Please check your document and retry.", "zh": "分析失败，请检查文件后重试。"},
    # Tab4 risk categories
    "rc_legal": {"en": "Legal Compliance", "zh": "法律合规"},
    "rc_financial": {"en": "Financial Risk", "zh": "财务风险"},
    "rc_missing": {"en": "Missing Clauses", "zh": "缺失条款"},
    "rc_unfair": {"en": "Unfair Terms", "zh": "不公平条款"},
    "rc_payment": {"en": "Payment Terms", "zh": "付款条款"},
    "rc_liability": {"en": "Liability & Insurance", "zh": "责任与保险"},
    "rc_dispute": {"en": "Dispute Resolution", "zh": "争议解决"},
    "rc_variations": {"en": "Variations & Scope", "zh": "变更与范围"},
    "rc_timeframes": {"en": "Timeframes & Delays", "zh": "工期与延误"},
    "rc_regulatory": {"en": "Regulatory", "zh": "法规监管"},
    # Tab4 progress
    "t4_p1": {"en": "Uploading contract documents...", "zh": "上传合同文件..."},
    "t4_p2": {"en": "Parsing document structure...", "zh": "解析文档结构..."},
    "t4_p3": {"en": "Identifying contract clauses...", "zh": "识别合同条款..."},
    "t4_p4": {"en": "Cross-referencing Australian legislation...", "zh": "交叉引用澳大利亚法规..."},
    "t4_p5": {"en": "Checking Security of Payment Act compliance...", "zh": "检查支付安全法合规性..."},
    "t4_p6": {"en": "Evaluating unfair contract terms...", "zh": "评估不公平合同条款..."},
    "t4_p7": {"en": "Analysing payment schedules...", "zh": "分析付款计划..."},
    "t4_p8": {"en": "Reviewing insurance & liability provisions...", "zh": "审查保险与责任条款..."},
    "t4_p9": {"en": "Benchmarking against market rates...", "zh": "对标市场费率..."},
    "t4_p10": {"en": "Compiling risk assessment report...", "zh": "编制风险评估报告..."},
    # ── Severity labels ──
    "severity_high": {"en": "HIGH RISK", "zh": "高风险"},
    "severity_medium": {"en": "MEDIUM", "zh": "中等"},
    "severity_low": {"en": "LOW", "zh": "低风险"},
    # ── Admin Panel ──
    "tab_admin": {"en": "Admin", "zh": "管理"},
    "admin_title": {"en": "User Management", "zh": "用户管理"},
    "admin_no_key": {"en": "Service role key not configured. Add SUPABASE_SERVICE_ROLE_KEY to secrets.", "zh": "未配置 service role 密钥，请在 secrets 中添加 SUPABASE_SERVICE_ROLE_KEY。"},
    "admin_no_users": {"en": "No registered users found.", "zh": "暂无注册用户。"},
    "admin_stats": {"en": "Total users: {total} · Pro users: {pro}", "zh": "总用户: {total} · Pro 用户: {pro}"},
    "admin_upgrade": {"en": "⬆️ Upgrade Pro", "zh": "⬆️ 升级 Pro"},
    "admin_downgrade": {"en": "⬇️ Downgrade", "zh": "⬇️ 降级"},
    # ── Shared ──
    "generation_failed": {"en": "Generation failed. Please adjust parameters and retry.", "zh": "生成失败，请调整参数后重试。"},
    "complete_label": {"en": "✓ COMPLETE | All renderings delivered", "zh": "✓ 完成 | 所有渲染图已交付"},
}


def get_lang() -> str:
    """Return the current language code ('en' or 'zh')."""
    return st.session_state.get("lang", "en")


def t(key: str) -> str:
    """Return the translated string for *key* in the current language."""
    entry = TRANSLATIONS.get(key)
    if entry is None:
        return key
    lang = get_lang()
    return entry.get(lang, entry.get("en", key))


def t_fmt(key: str, **kwargs) -> str:
    """Return a translated string with ``str.format(**kwargs)`` applied."""
    return t(key).format(**kwargs)
