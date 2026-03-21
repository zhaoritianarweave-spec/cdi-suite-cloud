# ArchiMind Pro

## Project Overview
ArchiMind Pro is a Streamlit Cloud SaaS platform for the Australian construction industry. It provides 3 core features: Site Renderer (architectural visualization), Drawing Analyser (construction drawing analysis), and ContractGuard (contract risk review).

- **Live:** https://cdi-suite-cloud-f3svb9i29ma9kpwxgtdc6l.streamlit.app
- **GitHub:** https://github.com/zhaoritianarweave-spec/cdi-suite-cloud
- **Status:** Beta (live, Stripe in test mode)
- **Admin:** hsy8260@proton.me

## Tech Stack
Python + Streamlit + Supabase (Auth + PostgreSQL) + Google Gemini (3.1 Pro/Flash/Veo) + Stripe + Resend

## Key Files
- `app.py` — Main entry: auth gate → 3 feature cards → workspace below
- `tabs/tab1_site_design.py` — Site Renderer (multi-angle rendering + video)
- `tabs/tab2_drawing_analyser.py` — Drawing Analyser (QTO, compliance, cost)
- `tabs/tab4_contract_guard.py` — ContractGuard (10-category risk analysis)
- `tabs/tab_admin.py` — Admin panel (user management, upgrade/downgrade)
- `utils/i18n.py` — English/Chinese translations (267 keys)
- `utils/ui_components.py` — Shared CSS, header, sidebar
- `utils/auth.py` — Supabase auth + landing page
- `utils/gemini_client.py` — Gemini API wrapper
- `utils/stripe_client.py` — Stripe checkout + portal
- `utils/usage.py` — Quota management (Free:3, Pro:50, Max:200, Enterprise:unlimited)
- `utils/email_service.py` — Resend welcome + usage warning emails
- `utils/history.py` — Analysis history (Supabase)
- `utils/feedback.py` — User feedback (thumbs up/down)
- `supabase_schema.sql` — DB schema (usage_logs, subscriptions, feedback, analysis_history)

## Full Status Report
See `PROJECT_STATUS.md` for comprehensive development report including all completed features and pending tasks.

## Rules
- Never use "AI" in any UI-facing text
- Git user.name must be "steven" (not real name)
- Chinese and English text must be kept separate (no mixing in same string)
- Download buttons: no emoji icons, text only (e.g., "Download Aerial View")
- Brand: ArchiMind Pro, colors #0A7CFF + #00D4AA, fonts Plus Jakarta Sans / Space Grotesk / Noto Sans SC
- Secrets are in Streamlit Cloud (never commit to repo)
- Deploy: `git push origin main` → Streamlit Cloud auto-deploys in 2-3 min
- Local dev: `streamlit run app.py --server.port 8502`
