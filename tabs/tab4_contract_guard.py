"""Tab 4: ContractGuard — Clause Risk Analyser.

Ported from the standalone ContractGuard AU Next.js application.
Uses Gemini Pro with structured JSON output for Australian
construction contract risk analysis.
"""

import json
import pathlib
import time
import io
import base64
import streamlit as st
from utils import gemini_client
from utils.ui_components import section_header
from utils.i18n import t, t_fmt

DEMO_DIR = pathlib.Path(__file__).resolve().parent.parent / "assets" / "demo_contracts"

# ---------------------------------------------------------------------------
# Finding categories & severity (mirrored from the original TS types)
# ---------------------------------------------------------------------------

def _category_labels():
    return {
        "legal_compliance": t("rc_legal"),
        "financial_risk": t("rc_financial"),
        "missing_clauses": t("rc_missing"),
        "unfair_terms": t("rc_unfair"),
        "payment_terms": t("rc_payment"),
        "liability_insurance": t("rc_liability"),
        "dispute_resolution": t("rc_dispute"),
        "variations_scope": t("rc_variations"),
        "timeframes_delays": t("rc_timeframes"),
        "regulatory": t("rc_regulatory"),
    }


def _severity_config():
    return {
        "high": {"color": "#DC2626", "bg": "#FEF2F2", "label": t("severity_high"), "emoji": "🔴"},
        "medium": {"color": "#D97706", "bg": "#FFFBEB", "label": t("severity_medium"), "emoji": "🟡"},
        "low": {"color": "#2563EB", "bg": "#EFF6FF", "label": t("severity_low"), "emoji": "🟢"},
    }


def _progress_messages():
    return [
        t("t4_p1"),
        t("t4_p2"),
        t("t4_p3"),
        t("t4_p4"),
        t("t4_p5"),
        t("t4_p6"),
        t("t4_p7"),
        t("t4_p8"),
        t("t4_p9"),
        t("t4_p10"),
    ]

# ---------------------------------------------------------------------------
# Prompts (ported from risk-analysis.ts and system-prompt.ts)
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are a senior Australian construction law consultant and quantity surveyor with 20+ years of experience across residential and commercial construction projects. You provide expert contract risk analysis.

YOUR KNOWLEDGE BASE:

## AUSTRALIAN LEGISLATION
- Home Building Act 1989 (NSW): licensing requirements, statutory warranties (6-year structural/2-year non-structural from completion), deposit caps (10% of contract price), mandatory written contracts for work >$5,000, cooling-off period requirements, progress payment schedules
- Building and Construction Industry Security of Payment Act 1999 (NSW): progress payment entitlements, payment claim procedures, 10-business-day response deadline for payment schedules, adjudication rights, retention money trust account requirements
- Design and Building Practitioners Act 2020 (NSW): regulated design requirements, compliance declarations
- Australian Consumer Law (Schedule 2, Competition and Consumer Act 2010): unfair contract terms provisions, consumer guarantees for services, misleading conduct
- Work Health and Safety Act 2011: principal contractor duties, WHS management plans, safe work method statements
- Environmental Planning and Assessment Act 1979 (NSW): development consent conditions, complying development

## STANDARD FORM CONTRACTS
- AS 2124-1992: tends to favour the Principal; EOT under clause 35.5(a), payment claims under clause 42
- AS 4000-1997: more balanced allocation of risk; delay damages under clause 34.9, tiered dispute resolution
- HIA contracts: Housing Industry Association standard forms for residential work
- MBA contracts: Master Builders Association standard forms
- ABIC contracts: Australian Building Industry Contracts

## MARKET RATES (2024-2025 AUD, Sydney Metropolitan Area)
- Structural concrete: $350-500/m3 supply and pour
- Structural steel: $5,000-8,000/tonne fabricated and erected
- Standard brickwork: $80-120/m2 laid
- Electrical rough-in (residential): $8,000-15,000 per dwelling
- Plumbing rough-in (residential): $10,000-18,000 per dwelling
- Builder's margin: 15-25% (residential), 5-15% (commercial)
- Liquidated damages: 0.05-0.1% of contract value per day typical

You respond ONLY in valid JSON format as specified in the user prompt. Be thorough, precise, and cite specific legislation sections."""

RISK_ANALYSIS_PROMPT = """Analyze the provided Australian construction contract document(s) thoroughly. Return a comprehensive risk analysis in the following JSON structure:

{
  "summary": {
    "overallRiskLevel": "high" | "medium" | "low",
    "totalFindings": <number>,
    "highRiskCount": <number>,
    "mediumRiskCount": <number>,
    "lowRiskCount": <number>,
    "executiveSummary": "<2-3 paragraphs summarizing key risks and overall assessment>",
    "contractType": "<identified contract type, e.g. AS 4000, HIA Lump Sum, Custom>",
    "estimatedContractValue": "<if identifiable from the documents>"
  },
  "findings": [
    {
      "id": "<unique id like F001>",
      "category": "<one of: legal_compliance, financial_risk, missing_clauses, unfair_terms, payment_terms, liability_insurance, dispute_resolution, variations_scope, timeframes_delays, regulatory>",
      "severity": "high" | "medium" | "low",
      "title": "<concise finding title>",
      "description": "<detailed explanation of the issue found>",
      "recommendation": "<specific professional guidance on how to address this>",
      "legalReference": "<relevant legislation section or standard clause>",
      "affectedParties": ["<who is affected, e.g. Owner, Builder, Subcontractor>"],
      "documentReference": {
        "fileName": "<source document name>",
        "section": "<contract clause number if identifiable>"
      },
      "marketBenchmark": {
        "item": "<construction item>",
        "contractRate": "<rate stated in contract>",
        "marketRate": "<expected market rate range>",
        "variance": "<percentage or dollar variance>"
      }
    }
  ]
}

NOTE: The "marketBenchmark" field should ONLY be included for findings in the "financial_risk" category where a price comparison is relevant. For other categories, omit this field entirely.

## ANALYSIS CHECKLIST:

### 1. LEGAL COMPLIANCE
- Deposit within 10% statutory limit? (HBA s.8)
- Statutory warranties included? (HBA s.18B)
- Home warranty insurance for residential >$20,000? (HBA s.92)
- Cooling-off period included?

### 2. PAYMENT TERMS
- Progress payment schedule aligned with SoPA?
- Response timeline within 10 business days?
- Retention amounts reasonable?

### 3. UNFAIR CONTRACT TERMS
- One-sided termination rights?
- Unreasonable penalty clauses?
- Disproportionate indemnities?

### 4. MISSING CLAUSES
- Dispute resolution mechanism?
- Variation procedure?
- Defects liability period?
- Force majeure provisions?

### 5. FINANCIAL RISK
- Compare rates against market benchmarks
- Front-loading of payment schedule?
- Contingency provisions?

### 6. LIABILITY AND INSURANCE
- Public liability insurance? (min $10M-$20M)
- Workers compensation?
- Contract works insurance?

### 7. TIMEFRAMES AND DELAYS
- Completion date specified?
- Extension of time provisions?
- Liquidated damages rate?

### 8. VARIATIONS AND SCOPE
- Variation procedure and pricing?
- Scope clearly defined?

### 9. DISPUTE RESOLUTION
- Tiered process?
- Security of Payment adjudication preserved?

### 10. REGULATORY COMPLIANCE
- NCC/BCA compliance?
- WHS management plan?

Severity Guidelines:
- HIGH: Legal non-compliance, missing mandatory provisions, significant financial exposure (>10% variance)
- MEDIUM: Departures from best practice, moderate financial risk (5-10% variance)
- LOW: Minor improvements recommended, industry standard but not optimal

LANGUAGE INSTRUCTION:
Write all analysis output in English. Use professional, authoritative language suitable for an Australian construction law advisory report."""


# ---------------------------------------------------------------------------
# Document extraction helpers
# ---------------------------------------------------------------------------

def _extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract text from a .docx file.

    Tries python-docx first; falls back to stdlib zipfile + XML parsing
    so it works even when python-docx is not installed.
    """
    try:
        import docx
        doc = docx.Document(io.BytesIO(file_bytes))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n".join(paragraphs)
    except ImportError:
        pass

    # Fallback: .docx is a ZIP containing word/document.xml
    import zipfile
    import xml.etree.ElementTree as ET

    with zipfile.ZipFile(io.BytesIO(file_bytes)) as zf:
        xml_content = zf.read("word/document.xml")
    root = ET.fromstring(xml_content)
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    paragraphs = []
    for p in root.iter(f"{{{ns['w']}}}p"):
        texts = [node.text for node in p.iter(f"{{{ns['w']}}}t") if node.text]
        if texts:
            paragraphs.append("".join(texts))
    return "\n".join(paragraphs)


def _extract_text_from_pdf(file_bytes: bytes) -> str | None:
    """Extract text from a PDF. Returns None if text extraction fails (scanned PDF)."""
    try:
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(file_bytes))
        text_parts = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
        return "\n\n".join(text_parts) if text_parts else None
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Gemini analysis call
# ---------------------------------------------------------------------------

def _analyse_contract(
    documents: list[dict],
) -> dict | None:
    """Call Gemini Pro with contract documents and return structured JSON result.

    Each document dict has: name, text (extracted text), bytes (raw), mime_type.
    """
    client = gemini_client.get_client()
    if client is None:
        st.error("Please enter your Gemini API key in the sidebar.")
        return None

    from google.genai import types

    # Build multimodal content parts
    parts = []
    for doc in documents:
        if doc.get("text"):
            parts.append(types.Part.from_text(text=f"[Document: {doc['name']}]\n\n{doc['text']}"))
        elif doc.get("bytes") and doc.get("mime_type"):
            # Only send raw bytes for types Gemini supports (PDF, images)
            supported_binary = {"application/pdf", "image/jpeg", "image/png", "image/webp"}
            if doc["mime_type"] in supported_binary:
                parts.append(types.Part.from_bytes(data=doc["bytes"], mime_type=doc["mime_type"]))
            else:
                st.warning(f"⚠️ Could not extract text from {doc['name']} and file type is not supported for direct upload.")

    parts.append(types.Part.from_text(text=RISK_ANALYSIS_PROMPT))

    try:
        response = client.models.generate_content(
            model=gemini_client.get_model_id(),
            contents=parts,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.2,
                thinking_config=types.ThinkingConfig(
                    thinking_budget=8000,
                ),
            ),
        )

        response_text = response.text or ""
        # Strip markdown code fences if present
        json_str = response_text.strip()
        if json_str.startswith("```"):
            json_str = json_str.split("\n", 1)[1] if "\n" in json_str else json_str[3:]
        if json_str.endswith("```"):
            json_str = json_str[:-3]
        json_str = json_str.strip()

        # With thinking mode, response may contain extra text around JSON
        # Try to extract JSON object if direct parse fails
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            # Find the first { and last } to extract JSON
            start = json_str.find("{")
            end = json_str.rfind("}")
            if start != -1 and end != -1:
                return json.loads(json_str[start:end + 1])
            raise

    except json.JSONDecodeError as e:
        st.error(f"Failed to parse analysis response: {e}")
        return None
    except Exception as e:
        st.error(f"Contract analysis error: {e}")
        return None


# ---------------------------------------------------------------------------
# HTML report generator (ported from generator.ts)
# ---------------------------------------------------------------------------

def _generate_report_html(result: dict) -> str:
    """Generate a downloadable HTML report from the analysis result."""
    summary = result.get("summary", {})
    findings = result.get("findings", [])
    sev_cfg = _severity_config()
    cat_labels = _category_labels()
    sev = sev_cfg.get(summary.get("overallRiskLevel", "medium"), sev_cfg["medium"])

    # Group findings by category
    grouped: dict[str, list] = {}
    for f in findings:
        cat = f.get("category", "other")
        grouped.setdefault(cat, []).append(f)

    findings_html = ""
    for cat, cat_findings in grouped.items():
        cat_label = cat_labels.get(cat, cat.replace("_", " ").title())
        findings_html += f'<h2 style="font-size:20px;color:#1e293b;margin:32px 0 16px;padding-bottom:8px;border-bottom:2px solid #e2e8f0;">{cat_label} ({len(cat_findings)})</h2>'
        for f in cat_findings:
            fs = sev_cfg.get(f.get("severity", "low"), sev_cfg["low"])
            findings_html += f'''
            <div style="border:1px solid #e2e8f0;border-radius:8px;margin-bottom:16px;overflow:hidden;">
              <div style="padding:16px;border-bottom:1px solid #e2e8f0;display:flex;align-items:center;gap:12px;">
                <span style="background:{fs['bg']};color:{fs['color']};padding:2px 10px;border-radius:12px;font-size:12px;font-weight:700;">{fs['label']}</span>
                <span style="color:#64748b;font-size:12px;">{cat_label}</span>
              </div>
              <div style="padding:16px;">
                <h3 style="margin:0 0 8px;font-size:16px;color:#1e293b;">{f.get("title","")}</h3>
                <p style="margin:0 0 12px;color:#475569;font-size:14px;line-height:1.6;">{f.get("description","")}</p>
                <div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:6px;padding:12px;margin-bottom:8px;">
                  <strong style="color:#166534;font-size:13px;">Recommendation:</strong>
                  <p style="margin:4px 0 0;color:#166534;font-size:13px;line-height:1.5;">{f.get("recommendation","")}</p>
                </div>'''
            if f.get("legalReference"):
                findings_html += f'<p style="margin:4px 0 0;color:#6366f1;font-size:12px;">&#128214; {f["legalReference"]}</p>'
            if f.get("affectedParties"):
                findings_html += f'<p style="margin:4px 0 0;color:#7c3aed;font-size:12px;">&#128101; <strong>Affected:</strong> {", ".join(f["affectedParties"])}</p>'
            if f.get("documentReference"):
                ref = f["documentReference"]
                ref_text = ref.get("fileName", "")
                if ref.get("section"):
                    ref_text += f" — Section: {ref['section']}"
                findings_html += f'<p style="margin:4px 0 0;color:#64748b;font-size:12px;">&#128196; {ref_text}</p>'
            findings_html += '</div></div>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>Contract Risk Analysis — ContractGuard AU</title>
<style>*{{box-sizing:border-box;margin:0;padding:0}}body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;color:#1e293b;background:#fff}}@media print{{body{{font-size:11px}}.no-print{{display:none}}}}</style>
</head><body>
<div style="max-width:800px;margin:0 auto;padding:40px 24px;">
  <div style="text-align:center;padding:48px 0;border-bottom:3px solid #2563eb;margin-bottom:32px;">
    <span style="font-size:24px;font-weight:800;">&#128737; ContractGuard AU</span>
    <h1 style="font-size:28px;margin:16px 0 8px;">Construction Contract Risk Analysis Report</h1>
  </div>
  <div style="background:#f8fafc;border-radius:12px;padding:24px;margin-bottom:32px;">
    <h2 style="font-size:18px;margin-bottom:16px;">Executive Summary</h2>
    <div style="display:flex;gap:16px;margin-bottom:16px;flex-wrap:wrap;">
      <div style="background:{sev['bg']};border-radius:8px;padding:12px 20px;text-align:center;">
        <div style="color:{sev['color']};font-size:24px;font-weight:800;">{sev['label']}</div>
        <div style="color:#64748b;font-size:12px;margin-top:4px;">Overall Risk</div>
      </div>
      <div style="background:#fef2f2;border-radius:8px;padding:12px 20px;text-align:center;">
        <div style="color:#dc2626;font-size:24px;font-weight:800;">{summary.get("highRiskCount",0)}</div>
        <div style="color:#64748b;font-size:12px;margin-top:4px;">High</div>
      </div>
      <div style="background:#fffbeb;border-radius:8px;padding:12px 20px;text-align:center;">
        <div style="color:#d97706;font-size:24px;font-weight:800;">{summary.get("mediumRiskCount",0)}</div>
        <div style="color:#64748b;font-size:12px;margin-top:4px;">Medium</div>
      </div>
      <div style="background:#eff6ff;border-radius:8px;padding:12px 20px;text-align:center;">
        <div style="color:#2563eb;font-size:24px;font-weight:800;">{summary.get("lowRiskCount",0)}</div>
        <div style="color:#64748b;font-size:12px;margin-top:4px;">Low</div>
      </div>
    </div>
    {"<p style='color:#64748b;font-size:13px;margin-bottom:4px;'><strong>Contract Type:</strong> " + summary["contractType"] + "</p>" if summary.get("contractType") else ""}
    {"<p style='color:#64748b;font-size:13px;margin-bottom:12px;'><strong>Estimated Value:</strong> " + summary["estimatedContractValue"] + "</p>" if summary.get("estimatedContractValue") else ""}
    <p style="color:#475569;font-size:14px;line-height:1.7;white-space:pre-line;">{summary.get("executiveSummary","")}</p>
  </div>
  <div><h2 style="font-size:22px;margin-bottom:4px;">Detailed Findings</h2>
    <p style="color:#64748b;font-size:14px;margin-bottom:24px;">{summary.get("totalFindings",0)} findings identified</p>
    {findings_html}
  </div>
  <div style="margin-top:48px;padding:24px;background:#f8fafc;border-radius:8px;border:1px solid #e2e8f0;">
    <p style="color:#94a3b8;font-size:11px;line-height:1.6;text-align:center;">
      Disclaimer: This report was produced by the ContractGuard AU Intelligent Compliance Engine. Analysis is for professional reference only and does not constitute legal advice. Please consult a licensed Australian construction lawyer for specific legal matters.
    </p>
  </div>
</div></body></html>"""


# ---------------------------------------------------------------------------
# Demo helpers
# ---------------------------------------------------------------------------

def _get_demo_contracts() -> list[pathlib.Path]:
    if DEMO_DIR.exists():
        return sorted(
            p for p in DEMO_DIR.iterdir()
            if p.suffix.lower() in {".docx", ".doc", ".pdf", ".jpg", ".jpeg", ".png"}
        )
    return []


# ---------------------------------------------------------------------------
# Progress bar (red/shield theme)
# ---------------------------------------------------------------------------

def _render_progress(container, status_el, pct: int, msg: str, done: bool = False):
    bar_color = "#3FB950" if done else "#DC2626"
    icon_html = "" if done else f"""
        <div style="
            position:absolute;
            left:calc({pct}% - 18px); top:-14px;
            font-size:20px;
            transition: left 0.8s ease-in-out;
            filter: drop-shadow(0 0 4px rgba(220,38,38,0.6));
        ">🛡️</div>"""
    check_html = '<div style="position:absolute;right:4px;top:-16px;font-size:18px;">✅</div>' if done else ""

    container.markdown(f"""
        <div style="
            position:relative; background:#21262D; border-radius:8px;
            height:10px; margin:22px 0 8px 0; overflow:visible; border:1px solid #30363D;
        ">
            <div style="
                width:{pct}%; height:100%; border-radius:8px;
                background:linear-gradient(90deg, {bar_color}88, {bar_color});
                transition:width 0.8s ease-in-out;
                box-shadow:0 0 8px {bar_color}66;
            "></div>
            {icon_html}{check_html}
        </div>
    """, unsafe_allow_html=True)

    if done:
        status_el.markdown(
            f"<div style='display:flex;align-items:center;gap:8px;'>"
            f"<span style='color:#3FB950;font-weight:700;'>{t('t4_complete')}</span>"
            f"</div>",
            unsafe_allow_html=True,
        )
    else:
        status_el.markdown(
            f"<div style='display:flex;align-items:center;gap:8px;'>"
            f"<span style='color:#DC2626;font-weight:600;'>🛡️ Scanning</span>"
            f"<span style='color:#8B949E;'>|</span>"
            f"<span style='color:#E6EDF3;'>{msg}</span>"
            f"</div>",
            unsafe_allow_html=True,
        )


# ---------------------------------------------------------------------------
# Render
# ---------------------------------------------------------------------------

def render():
    import pathlib as _pl
    _assets = _pl.Path(__file__).resolve().parent.parent / "assets" / "ui"
    _img_col, _txt_col = st.columns([1, 4])
    with _img_col:
        _img_path = _assets / "contract_guard.png"
        if _img_path.exists():
            st.image(str(_img_path), width=120)
    with _txt_col:
        section_header("📜", t("t4_title"))
        st.caption(t("t4_caption"))
    st.markdown("---")

    # --- Layout ------------------------------------------------
    col_left, col_right = st.columns([2, 3])

    doc_data: list[dict] | None = None

    with col_left:
        st.markdown(f"##### {t('t4_documents')}")
        uploaded_files = st.file_uploader(
            t("t4_upload"),
            type=["pdf", "docx", "doc", "jpg", "jpeg", "png"],
            accept_multiple_files=True,
            key="tab4_upload",
            label_visibility="collapsed",
        )

        if uploaded_files:
            doc_data = []
            for f in uploaded_files:
                raw = f.getvalue()
                name = f.name or "document"
                ext = pathlib.Path(name).suffix.lower()

                extracted_text = None
                mime = f.type or "application/octet-stream"

                if ext in (".docx", ".doc"):
                    try:
                        extracted_text = _extract_text_from_docx(raw)
                    except Exception as e:
                        st.warning(f"Could not parse {name}: {e}")
                elif ext == ".pdf":
                    extracted_text = _extract_text_from_pdf(raw)

                doc_data.append({
                    "name": name,
                    "text": extracted_text,
                    "bytes": raw,
                    "mime_type": mime,
                    "size": len(raw),
                })
                st.markdown(
                    f"<div style='padding:6px 12px;background:#161B22;border-radius:6px;"
                    f"border:1px solid #30363D;margin-bottom:4px;font-size:0.85rem;'>"
                    f"📄 {name} <span style='color:#8B949E;'>({len(raw)/1024:.0f} KB)</span>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

        # Demo contracts
        demos = _get_demo_contracts()
        if demos:
            st.markdown(
                f"<span style='color:#8B949E;font-size:0.8rem;'>{t('t4_demo_label')}</span>",
                unsafe_allow_html=True,
            )
            demo_cols = st.columns(min(len(demos), 2))
            for i, demo in enumerate(demos):
                with demo_cols[i % 2]:
                    label = demo.stem.replace("_", " ").title()
                    if st.button(label, key=f"demo_contract_{i}", use_container_width=True):
                        st.session_state["tab4_demo_contract"] = str(demo)

            if "tab4_demo_contract" in st.session_state and doc_data is None:
                demo_path = pathlib.Path(st.session_state["tab4_demo_contract"])
                if demo_path.exists():
                    raw = demo_path.read_bytes()
                    ext = demo_path.suffix.lower()
                    extracted_text = None
                    mime = "application/pdf"

                    if ext in (".docx", ".doc"):
                        mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        try:
                            extracted_text = _extract_text_from_docx(raw)
                        except Exception:
                            pass
                    elif ext == ".pdf":
                        extracted_text = _extract_text_from_pdf(raw)

                    doc_data = [{
                        "name": demo_path.name,
                        "text": extracted_text,
                        "bytes": raw,
                        "mime_type": mime,
                        "size": len(raw),
                    }]
                    st.markdown(
                        f"<div style='padding:6px 12px;background:#161B22;border-radius:6px;"
                        f"border:1px solid #30363D;margin-bottom:4px;font-size:0.85rem;'>"
                        f"📄 Demo — {demo_path.stem}"
                        f"</div>",
                        unsafe_allow_html=True,
                    )

    with col_right:
        st.markdown(f"##### {t('t4_scope')}")

        focus_options = list(_category_labels().values())
        selected_focus = st.multiselect(
            t("t4_risk_categories"),
            focus_options,
            default=focus_options[:5],
            key="tab4_focus",
            help=t("t4_risk_help"),
        )

        analyse = st.button(
            t("t4_analyse_btn"),
            type="primary",
            use_container_width=True,
            disabled=doc_data is None,
        )

        if doc_data is None:
            st.info(t("t4_upload_hint"))

    # --- Analysis execution ------------------------------------
    if analyse and doc_data:
        from utils.auth import get_user
        from utils.usage import check_quota, render_quota_exceeded, record_usage
        _user = get_user()
        if _user:
            _allowed, _, _ = check_quota(_user["id"])
            if not _allowed:
                render_quota_exceeded()
                st.stop()
        st.markdown("---")

        progress_container = st.empty()
        status_text = st.empty()

        # Animate progress
        prog_msgs = _progress_messages()
        _render_progress(progress_container, status_text, 1, prog_msgs[0])
        time.sleep(0.3)

        for i, msg in enumerate(prog_msgs):
            pct = int(((i + 1) / len(prog_msgs)) * 60) + 1
            _render_progress(progress_container, status_text, pct, msg)
            time.sleep(0.4)

        _render_progress(progress_container, status_text, 65, "Waiting for Generative Architecture Engine response...")

        result = _analyse_contract(doc_data)

        if result and "summary" in result:
            _render_progress(progress_container, status_text, 100, "", done=True)
            st.session_state["tab4_results"] = result
            # Record usage only after successful analysis
            if _user:
                record_usage(_user["id"], "contract_guard", gemini_client.get_model_id())
                # Save to history
                try:
                    from utils.history import save_history
                    risk_level = result.get("summary", {}).get("overallRiskLevel", "unknown")
                    findings_count = len(result.get("findings", []))
                    save_history(
                        _user["id"], "contract_guard",
                        f"Contract Analysis — {risk_level.upper()} risk",
                        f"Found {findings_count} findings. Overall risk: {risk_level}",
                        result,
                    )
                except Exception:
                    pass
                st.rerun()
        else:
            progress_container.empty()
            status_text.empty()
            st.error(t("t4_analysis_failed"))

    # --- Display results ---------------------------------------
    if "tab4_results" in st.session_state and st.session_state["tab4_results"]:
        result = st.session_state["tab4_results"]
        summary = result.get("summary", {})
        findings = result.get("findings", [])

        st.markdown("---")

        # --- Risk summary metrics ---
        section_header("🛡️", t("t4_results_title"))

        overall_sev = _severity_config().get(summary.get("overallRiskLevel", "medium"), _severity_config()["medium"])

        metric_cols = st.columns(4)
        with metric_cols[0]:
            st.markdown(
                f"<div style='text-align:center;padding:16px;background:{overall_sev['bg']}22;"
                f"border-radius:10px;border:1px solid {overall_sev['color']}44;'>"
                f"<div style='color:{overall_sev['color']};font-size:1.4rem;font-weight:800;'>"
                f"{overall_sev['label']}</div>"
                f"<div style='color:#8B949E;font-size:0.75rem;margin-top:4px;'>{t('t4_overall_risk')}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )
        with metric_cols[1]:
            st.markdown(
                f"<div style='text-align:center;padding:16px;background:#DC262622;"
                f"border-radius:10px;border:1px solid #DC262644;'>"
                f"<div style='color:#DC2626;font-size:1.4rem;font-weight:800;'>"
                f"{summary.get('highRiskCount', 0)}</div>"
                f"<div style='color:#8B949E;font-size:0.75rem;margin-top:4px;'>{t('t4_high_risk')}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )
        with metric_cols[2]:
            st.markdown(
                f"<div style='text-align:center;padding:16px;background:#D9770622;"
                f"border-radius:10px;border:1px solid #D9770644;'>"
                f"<div style='color:#D97706;font-size:1.4rem;font-weight:800;'>"
                f"{summary.get('mediumRiskCount', 0)}</div>"
                f"<div style='color:#8B949E;font-size:0.75rem;margin-top:4px;'>{t('t4_medium')}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )
        with metric_cols[3]:
            st.markdown(
                f"<div style='text-align:center;padding:16px;background:#2563EB22;"
                f"border-radius:10px;border:1px solid #2563EB44;'>"
                f"<div style='color:#2563EB;font-size:1.4rem;font-weight:800;'>"
                f"{summary.get('lowRiskCount', 0)}</div>"
                f"<div style='color:#8B949E;font-size:0.75rem;margin-top:4px;'>{t('t4_low_risk')}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

        # Contract type & value
        info_parts = []
        if summary.get("contractType"):
            info_parts.append(f"**Contract Type:** {summary['contractType']}")
        if summary.get("estimatedContractValue"):
            info_parts.append(f"**Estimated Value:** {summary['estimatedContractValue']}")
        if info_parts:
            st.markdown(" &nbsp;|&nbsp; ".join(info_parts))

        # --- Sub-tabs for report sections ---
        tab_labels = [t("t4_tab_summary"), t("t4_tab_findings"), t("t4_tab_risk_chart")]
        result_tabs = st.tabs(tab_labels)

        # Executive Summary tab
        with result_tabs[0]:
            st.markdown(summary.get("executiveSummary", "No summary available."))

        # Detailed Findings tab
        with result_tabs[1]:
            if not findings:
                st.info(t("t4_no_findings"))
            else:
                for f in findings:
                    fs = _severity_config().get(f.get("severity", "low"), _severity_config()["low"])
                    cat_label = _category_labels().get(f.get("category", ""), f.get("category", ""))

                    with st.expander(
                        f"{fs['emoji']} **{f.get('title', 'Finding')}** — {cat_label}",
                        expanded=f.get("severity") == "high",
                    ):
                        st.markdown(f.get("description", ""))
                        st.markdown("---")
                        st.markdown(f"**{t('t4_recommendation')}** {f.get('recommendation', '')}")

                        detail_cols = st.columns(3)
                        with detail_cols[0]:
                            if f.get("legalReference"):
                                st.markdown(f"📖 {f['legalReference']}")
                        with detail_cols[1]:
                            if f.get("affectedParties"):
                                st.markdown(f"👥 {', '.join(f['affectedParties'])}")
                        with detail_cols[2]:
                            ref = f.get("documentReference", {})
                            if ref:
                                ref_text = ref.get("fileName", "")
                                if ref.get("section"):
                                    ref_text += f" — §{ref['section']}"
                                if ref_text:
                                    st.markdown(f"📄 {ref_text}")

                        # Market benchmark table
                        if f.get("marketBenchmark"):
                            mb = f["marketBenchmark"]
                            st.markdown(f"**{t('t4_benchmark')}**")
                            bm_data = {
                                "": ["Contract Rate", "Market Rate", "Variance"],
                                mb.get("item", "Item"): [
                                    mb.get("contractRate", ""),
                                    mb.get("marketRate", ""),
                                    mb.get("variance", ""),
                                ],
                            }
                            st.table(bm_data)

        # Risk by Category tab
        with result_tabs[2]:
            grouped: dict[str, list] = {}
            for f in findings:
                cat = f.get("category", "other")
                grouped.setdefault(cat, []).append(f)

            for cat, cat_findings in grouped.items():
                cat_label = _category_labels().get(cat, cat.replace("_", " ").title())
                severity_counts = {"high": 0, "medium": 0, "low": 0}
                for f in cat_findings:
                    sev_key = f.get("severity", "low")
                    severity_counts[sev_key] = severity_counts.get(sev_key, 0) + 1

                badge_html = ""
                if severity_counts["high"] > 0:
                    badge_html += f'<span style="background:#DC262633;color:#DC2626;padding:2px 8px;border-radius:10px;font-size:0.75rem;font-weight:600;margin-right:4px;">🔴 {severity_counts["high"]}</span>'
                if severity_counts["medium"] > 0:
                    badge_html += f'<span style="background:#D9770633;color:#D97706;padding:2px 8px;border-radius:10px;font-size:0.75rem;font-weight:600;margin-right:4px;">🟡 {severity_counts["medium"]}</span>'
                if severity_counts["low"] > 0:
                    badge_html += f'<span style="background:#2563EB33;color:#2563EB;padding:2px 8px;border-radius:10px;font-size:0.75rem;font-weight:600;margin-right:4px;">🟢 {severity_counts["low"]}</span>'

                st.markdown(
                    f"<div style='display:flex;align-items:center;gap:8px;padding:8px 0;'>"
                    f"<strong style='color:#E6EDF3;'>{cat_label}</strong>"
                    f"<span style='color:#8B949E;'>({len(cat_findings)})</span>"
                    f"{badge_html}"
                    f"</div>",
                    unsafe_allow_html=True,
                )
                for f in cat_findings:
                    fs = _severity_config().get(f.get("severity", "low"), _severity_config()["low"])
                    st.markdown(
                        f"<div style='padding:6px 12px 6px 20px;border-left:3px solid {fs['color']};"
                        f"margin:4px 0 4px 8px;font-size:0.9rem;'>"
                        f"<span style='color:{fs['color']};font-weight:600;'>{f.get('title','')}</span>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )

        # --- Downloads ---
        st.markdown("---")
        dl_cols = st.columns(2)
        with dl_cols[0]:
            html_report = _generate_report_html(result)
            st.download_button(
                label=t("t4_download_report"),
                data=html_report,
                file_name="contractguard_risk_report.html",
                mime="text/html",
                key="dl_tab4_html",
                use_container_width=True,
            )
        with dl_cols[1]:
            json_data = json.dumps(result, indent=2, ensure_ascii=False)
            st.download_button(
                label=t("t4_download_json"),
                data=json_data,
                file_name="contractguard_analysis.json",
                mime="application/json",
                key="dl_tab4_json",
                use_container_width=True,
            )

        # --- Feedback ------------------------------------------------
        from utils.feedback import render_feedback
        render_feedback("contract_guard", "tab4_results")
