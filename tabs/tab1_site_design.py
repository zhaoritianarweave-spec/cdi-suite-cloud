import pathlib
import time
import streamlit as st
from utils import gemini_client
from utils.i18n import t, t_fmt
from utils.ui_components import section_header

DEMO_DIR = pathlib.Path(__file__).resolve().parent.parent / "assets" / "demo_photos"

def _project_types():
    return [
        t("pt_residential"),
        t("pt_townhouse"),
        t("pt_apartment"),
        t("pt_commercial"),
        t("pt_landscape"),
        t("pt_civil"),
        t("pt_mixed"),
    ]

def _design_styles():
    return [
        t("ds_modern"),
        t("ds_traditional"),
        t("ds_industrial"),
        t("ds_minimalist"),
        t("ds_sustainable"),
        t("ds_coastal"),
    ]

def _viewpoints():
    return {
        t("vp_front"): "close-up front elevation, camera at eye-level about 8 metres from the front door, tightly framed on the building facade, showing entrance detail, front door, porch, garage doors, facade materials and textures, with some foreground landscaping. Golden hour warm lighting. This is a CLOSE SHOT — do NOT show the full street or distant surroundings.",
        t("vp_aerial"): "bird's-eye aerial perspective looking down at 45 degrees from about 50 metres altitude, showing the FULL site layout including roof plan, driveway, front yard, backyard, side setbacks, landscaping, pool if any, and surrounding neighbourhood context. Wide shot.",
        t("vp_rear"): "The camera is BEHIND the house, positioned in the BACKYARD, looking TOWARD the REAR WALL of the building. Show the BACK of the house — rear sliding doors, alfresco area, deck or patio, pool if applicable, backyard lawn, rear fence and garden landscaping. The front door, front driveway and street must NOT be visible at all — they are on the opposite side of the building. This is a completely different scene from the front elevation.",
        t("vp_street"): "street-level pedestrian perspective from the footpath across the road, showing the full building in its streetscape context with neighbouring houses, street trees, footpath, fencing and letterbox. Wide contextual shot at eye level.",
    }

# Quick-pick design feature chips
def _quick_features():
    return {
        t("qf_double_garage"):      "large double garage with automatic door",
        t("qf_triple_garage"):      "oversized triple car garage",
        t("qf_luxury_landscaping"):  "premium landscaping with mature trees, hedge borders and garden lighting",
        t("qf_backyard_pool"):       "resort-style swimming pool with surrounding deck in the backyard",
        t("qf_outdoor_kitchen"):     "built-in outdoor BBQ and alfresco kitchen area",
        t("qf_large_backyard"):      "spacious rear yard with open lawn area",
        t("qf_wrap_porch"):          "wide wrap-around verandah or porch",
        t("qf_floor_glass"):         "floor-to-ceiling glass windows and curtain walls for natural light",
        t("qf_rooftop_terrace"):     "accessible rooftop terrace with lounge area",
        t("qf_gated_entry"):         "secure gated front entrance with intercom",
        t("qf_two_storey"):          "two-storey design with balcony on upper level",
        t("qf_three_storey"):        "three-storey design maximising floor area",
    }

# Fun progress messages shown during generation
PROGRESS_MESSAGES = [
    ["Calibrating aerial camera...", "Mapping roof footprint...", "Rendering full site layout..."],
    ["Generating facade geometry...", "Computing material palette...", "Simulating golden-hour lighting..."],
    ["Rendering structural envelope...", "Placing landscaping elements...", "Applying photorealistic textures..."],
    ["Scanning terrain topology...", "Analysing solar orientation...", "Finalising render pass..."],
]


# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------

def _build_anchor_prompt(
    project_type: str, styles: str, features: str, brief: str, viewpoint_desc: str,
) -> str:
    return f"""Based on this site photo, generate a high-quality photorealistic architectural rendering of a proposed {project_type}.

Design style: {styles}
Design features: {features}
Design brief: {brief}
Viewpoint: {viewpoint_desc}

Requirements for the rendering:
- Design a SPECIFIC building with clear architectural features: roof form, facade materials, window layout, entrance style
- Incorporate ALL listed design features into the building
- The aerial view must clearly show: roof plan, front yard with driveway and garage entry, backyard with pool/garden (if applicable), side setbacks, and landscaping layout
- Use realistic materials, textures, lighting and landscaping
- The building must fit the existing site conditions visible in the photo
- Professional architectural visualisation quality, suitable for client presentation

Generate ONLY the architectural rendering image."""


def _build_followup_prompt(
    project_type: str, styles: str, features: str, brief: str,
    viewpoint_desc: str, view_name: str,
) -> str:
    is_rear = "rear" in view_name.lower() or "garden" in view_name.lower()
    is_front = "front" in view_name.lower() or "elevation" in view_name.lower()

    if is_rear:
        consistency_block = """CRITICAL DESIGN CONSISTENCY — the new rendering MUST depict the IDENTICAL building from the aerial reference, viewed from GROUND LEVEL in the BACKYARD:
- MUST MATCH: exact roof form (hip/gable/flat), exact facade materials (brick/render/timber/stone), exact colour palette, exact storey count, exact window proportions and placement
- MUST MATCH: building footprint shape, wing layout, and massing as visible from above
- The camera is positioned in the BACKYARD at eye-level (~1.6m), looking at the REAR ELEVATION of the building
- Show: rear sliding doors / bifold doors, alfresco/patio area, deck, pool (if present in aerial), backyard lawn and landscaping
- The backyard layout (pool position relative to house, garden beds, fencing, paths) must be geometrically consistent with the aerial plan view
- DO NOT show the front door, front porch, driveway or street — those are on the opposite side
- Maintain the same time of day, lighting direction, and weather conditions as the aerial reference"""
    elif is_front:
        consistency_block = """CRITICAL DESIGN CONSISTENCY — the new rendering MUST depict the IDENTICAL building from the aerial reference, viewed from GROUND LEVEL at the FRONT:
- MUST MATCH: exact roof form (hip/gable/flat), exact facade materials (brick/render/timber/stone), exact colour palette, exact storey count, exact window proportions and placement
- MUST MATCH: building footprint shape, garage position (left/right/centre), and entry location as visible from above
- The camera is at eye-level (~1.6m) on the street, tightly framed on the front facade
- Show: front door, entry portico/porch, garage door(s), facade material detail, front landscaping
- The front yard layout (driveway width and position, garden beds, paths, mailbox) must be geometrically consistent with the aerial plan view
- Close-up architectural shot — do NOT show distant surroundings or full street context
- Maintain the same time of day, lighting direction, and weather conditions as the aerial reference"""
    else:
        consistency_block = """CRITICAL DESIGN CONSISTENCY — the new rendering MUST depict the IDENTICAL building from the aerial reference:
- MUST MATCH: exact roof form (hip/gable/flat), exact facade materials (brick/render/timber/stone), exact colour palette, exact storey count, exact window proportions and placement
- MUST MATCH: building footprint shape, wing layout, and massing as visible from above
- Same site layout, landscaping, driveways, pools, and features — geometrically consistent with the aerial plan
- Only the camera angle / perspective changes
- Maintain the same time of day, lighting direction, and weather conditions as the aerial reference"""

    return f"""I'm providing two images:
1. The original site photo (first image)
2. A previously generated BIRD'S-EYE / AERIAL rendering of a {project_type} design (second image) — this is the MASTER REFERENCE showing the full site layout from above

Generate a NEW rendering of the EXACT SAME BUILDING from a different angle.

New viewpoint: {viewpoint_desc}
Design style: {styles}
Design features: {features}
Design brief: {brief}

{consistency_block}

Generate ONLY the architectural rendering image. Keep every architectural detail consistent with the aerial reference rendering."""


def _get_demo_photos() -> list[pathlib.Path]:
    if DEMO_DIR.exists():
        return sorted(
            p for p in DEMO_DIR.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png"}
        )
    return []


# ---------------------------------------------------------------------------
# Video flyover
# ---------------------------------------------------------------------------

VIDEO_PROGRESS_MESSAGES = [
    "Uploading aerial reference to render farm...",
    "Constructing 3-D mesh from bird's-eye view...",
    "Computing orbital camera trajectory...",
    "Rendering cinematic fly-through frames...",
    "Synthesising ambient audio track...",
    "Compositing final 4K output...",
    "Encoding MP4 stream...",
    "Applying colour grading & lens effects...",
    "Almost there — polishing final frames...",
]


def _render_video_section():
    """Show a 'Generate Flyover Video' button and handle video generation."""
    anchor_bytes = st.session_state.get("tab1_anchor_bytes")
    if anchor_bytes is None:
        return

    st.markdown("---")
    section_header("🎬", t("t1_video_title"))
    st.caption(t("t1_video_caption"))

    gen_video = st.button(
        t("t1_video_btn"),
        type="primary",
        use_container_width=True,
        key="tab1_gen_video",
    )

    if gen_video:
        video_progress = st.empty()
        video_status = st.empty()

        def _render_video_progress(pct: int, msg: str, done: bool = False):
            bar_color = "#3FB950" if done else "#E040FB"
            icon_html = "" if done else f"""
                <div style="
                    position:absolute;
                    left:calc({pct}% - 18px); top:-14px;
                    font-size:20px;
                    transition: left 1.2s ease-in-out;
                    filter: drop-shadow(0 0 4px rgba(224,64,251,0.6));
                ">🎥</div>"""
            check_html = """
                <div style="position:absolute;right:4px;top:-16px;font-size:18px;">✅</div>""" if done else ""

            video_progress.markdown(f"""
                <div style="
                    position:relative; background:#21262D; border-radius:8px;
                    height:10px; margin:22px 0 8px 0; overflow:visible; border:1px solid #30363D;
                ">
                    <div style="
                        width:{pct}%; height:100%; border-radius:8px;
                        background:linear-gradient(90deg, {bar_color}88, {bar_color});
                        transition:width 1.2s ease-in-out;
                        box-shadow:0 0 8px {bar_color}66;
                    "></div>
                    {icon_html}{check_html}
                </div>
            """, unsafe_allow_html=True)

            if done:
                video_status.markdown(
                    "<div style='display:flex;align-items:center;gap:8px;'>"
                    f"<span style='color:#3FB950;font-weight:700;'>{t('t1_video_ready')}</span>"
                    "<span style='color:#8B949E;'>|</span>"
                    f"<span style='color:#E6EDF3;'>{t('t1_video_ready')}</span>"
                    "</div>",
                    unsafe_allow_html=True,
                )
            else:
                video_status.markdown(
                    f"<div style='display:flex;align-items:center;gap:8px;'>"
                    f"<span style='color:#CE93D8;font-weight:600;'>🎬 Rendering</span>"
                    f"<span style='color:#8B949E;'>|</span>"
                    f"<span style='color:#E6EDF3;'>{msg}</span>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

        _render_video_progress(1, VIDEO_PROGRESS_MESSAGES[0])

        msg_idx = [0]

        def _on_poll(elapsed):
            idx = min(elapsed // 12, len(VIDEO_PROGRESS_MESSAGES) - 1)
            pct = min(int((elapsed / 120) * 90) + 1, 91)
            _render_video_progress(pct, VIDEO_PROGRESS_MESSAGES[idx])

        prompt = (
            "Cinematic aerial fly-around orbit of this building. "
            "The camera smoothly orbits 360 degrees around the entire property at a low altitude, "
            "starting from the front, moving to the side, then revealing the backyard, "
            "and completing the full circle back to the front. "
            "Golden hour lighting, smooth dolly movement, architectural visualisation quality. "
            "No text overlays."
        )

        video_bytes = gemini_client.generate_flyover_video(
            prompt=prompt,
            reference_image_bytes=anchor_bytes,
            mime_type="image/png",
            duration_seconds=8,
            poll_interval=10,
            on_poll=_on_poll,
        )

        if video_bytes:
            _render_video_progress(100, "", done=True)
            st.session_state["tab1_video"] = video_bytes
        else:
            video_progress.empty()
            video_status.empty()
            st.error(t("t1_video_failed"))

    # Display previously generated video
    if "tab1_video" in st.session_state and st.session_state["tab1_video"]:
        st.video(st.session_state["tab1_video"], format="video/mp4")
        st.download_button(
            label=t("t1_video_download"),
            data=st.session_state["tab1_video"],
            file_name="design_flyover.mp4",
            mime="video/mp4",
            key="dl_video",
        )


# ---------------------------------------------------------------------------
# Render
# ---------------------------------------------------------------------------

def render():

    # --- Layout -------------------------------------------------
    col_left, col_right = st.columns([2, 3])

    image_bytes: bytes | None = None
    mime_type = "image/jpeg"

    with col_left:
        st.markdown(f"##### {t('t1_site_photo')}")
        uploaded = st.file_uploader(
            t("t1_upload"),
            type=["jpg", "jpeg", "png"],
            key="tab1_upload",
        )

        if uploaded is not None:
            image_bytes = uploaded.getvalue()
            mime_type = uploaded.type or "image/jpeg"
            st.image(image_bytes, caption="Site Input", use_container_width=True)

        # Demo photos removed — users upload their own site photos

    with col_right:
        st.markdown(f"##### {t('t1_design_params')}")

        r1c1, r1c2 = st.columns(2)
        with r1c1:
            project_type = st.selectbox(t("t1_project_type"), _project_types(), key="tab1_project_type")
        with r1c2:
            style = st.selectbox(
                t("t1_design_language"),
                _design_styles(),
                index=0,
                key="tab1_style",
            )

        # --- Quick-pick feature chips ---
        st.markdown(
            f"<span style='color:#8B949E;font-size:0.8rem;letter-spacing:0.5px;'>"
            f"{t('t1_quick_features_label')}</span>",
            unsafe_allow_html=True,
        )
        QUICK_FEATURES = _quick_features()
        selected_features = st.multiselect(
            t("t1_quick_features"),
            list(QUICK_FEATURES.keys()),
            default=[t("qf_luxury_landscaping")],
            key="tab1_features",
            label_visibility="collapsed",
        )

        # --- Rendering viewpoints ---
        VIEWPOINTS = _viewpoints()
        selected_views = st.multiselect(
            t("t1_viewpoints"),
            list(VIEWPOINTS.keys()),
            default=[t("vp_aerial"), t("vp_front")],
            key="tab1_views",
        )

        # --- Free-form design brief ---
        design_brief = st.text_area(
            t("t1_design_brief"),
            placeholder=t("t1_brief_placeholder"),
            key="tab1_brief",
            height=80,
        )

        total_images = len(selected_views)
        generate = st.button(
            t_fmt("t1_generate_btn", n=total_images),
            type="primary",
            use_container_width=True,
            disabled=image_bytes is None or total_images == 0,
        )

        if image_bytes is None:
            st.info(t("t1_upload_hint"))
        elif total_images == 0:
            st.warning(t("t1_select_viewpoint"))

    # --- Generation (chained for consistency) --------------------
    if generate and image_bytes is not None and selected_views:
        from utils.auth import get_user
        from utils.usage import check_quota, render_quota_exceeded, record_usage
        _user = get_user()
        if _user:
            _allowed, _, _ = check_quota(_user["id"])
            if not _allowed:
                render_quota_exceeded()
                st.stop()
        st.markdown("---")

        styles_str = style
        features_str = ", ".join(
            QUICK_FEATURES[f] for f in selected_features
        ) if selected_features else "standard features"
        brief_str = design_brief.strip() if design_brief.strip() else "no specific brief"

        ANCHOR_KEY = t("vp_aerial")
        ordered_views = list(selected_views)
        if ANCHOR_KEY in ordered_views:
            ordered_views.remove(ANCHOR_KEY)
            ordered_views.insert(0, ANCHOR_KEY)
        else:
            ordered_views.insert(0, ANCHOR_KEY)

        results = []
        anchor_image_bytes: bytes | None = None

        # --- Custom excavator progress bar ---
        progress_container = st.empty()
        status_text = st.empty()

        def _render_progress(pct: int, msg: str, done: bool = False):
            bar_color = "#3FB950" if done else "#0A7CFF"
            excavator_html = "" if done else f"""
                <div style="
                    position:absolute;
                    left:calc({pct}% - 18px);
                    top:-14px;
                    font-size:20px;
                    transition: left 0.8s ease-in-out;
                    filter: drop-shadow(0 0 4px rgba(10,124,255,0.6));
                ">🚜</div>"""
            check_html = f"""
                <div style="
                    position:absolute;
                    right:4px; top:-16px;
                    font-size:18px;
                ">✅</div>""" if done else ""

            progress_container.markdown(f"""
                <div style="
                    position:relative;
                    background:#21262D;
                    border-radius:8px;
                    height:10px;
                    margin:22px 0 8px 0;
                    overflow:visible;
                    border:1px solid #30363D;
                ">
                    <div style="
                        width:{pct}%;
                        height:100%;
                        border-radius:8px;
                        background: linear-gradient(90deg, {bar_color}88, {bar_color});
                        transition: width 0.8s ease-in-out;
                        box-shadow: 0 0 8px {bar_color}66;
                    "></div>
                    {excavator_html}
                    {check_html}
                </div>
            """, unsafe_allow_html=True)

            if done:
                status_text.markdown(
                    "<div style='display:flex;align-items:center;gap:8px;'>"
                    f"<span style='color:#3FB950;font-weight:700;'>{t('complete_label')}</span>"
                    "<span style='color:#8B949E;'>|</span>"
                    f"<span style='color:#E6EDF3;'>{t('complete_label')}</span>"
                    "</div>",
                    unsafe_allow_html=True,
                )
            else:
                step_num = msg.split("|")[0].strip() if "|" in msg else ""
                step_desc = msg.split("|")[1].strip() if "|" in msg else msg
                status_text.markdown(
                    f"<div style='display:flex;align-items:center;gap:8px;'>"
                    f"<span style='color:#58A6FF;font-weight:600;'>{step_num}</span>"
                    f"<span style='color:#8B949E;'>|</span>"
                    f"<span style='color:#E6EDF3;'>{step_desc}</span>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

        # Start from 1%
        _render_progress(1, f"Step 0/{len(ordered_views)}| {t('t1_progress_warmup')}")
        time.sleep(0.5)

        for i, view_name in enumerate(ordered_views):
            total = len(ordered_views)
            base_pct = int((i / total) * 90) + 1  # 1% to 91%
            step_pct_range = int(90 / total)  # % allocated to this step

            # Smooth sub-steps before API call
            msgs = PROGRESS_MESSAGES[i % len(PROGRESS_MESSAGES)]
            for j, msg in enumerate(msgs):
                sub_pct = base_pct + int((j / len(msgs)) * step_pct_range * 0.4)
                _render_progress(sub_pct, f"Step {i+1}/{total}| {msg}")
                time.sleep(0.6)

            # Show "calling API" message at ~40% of this step
            api_pct = base_pct + int(step_pct_range * 0.4)
            _render_progress(api_pct, f"Step {i+1}/{total}| Generating {view_name}...")

            vp_desc = VIEWPOINTS[view_name]

            if i == 0:
                prompt = _build_anchor_prompt(project_type, styles_str, features_str, brief_str, vp_desc)
                refs = [(image_bytes, mime_type)]
            else:
                prompt = _build_followup_prompt(project_type, styles_str, features_str, brief_str, vp_desc, view_name)
                refs = [(image_bytes, mime_type)]
                if anchor_image_bytes:
                    refs.append((anchor_image_bytes, "image/png"))

            result = gemini_client.generate_design_image(
                prompt=prompt,
                reference_images=refs,
            )

            # After API returns, jump to end of this step
            done_pct = base_pct + step_pct_range
            _render_progress(done_pct, f"Step {i+1}/{total}| {view_name} complete ✓")
            time.sleep(0.3)

            if result and result["image_bytes"]:
                if i == 0:
                    anchor_image_bytes = result["image_bytes"]
                if view_name in selected_views:
                    result["view_name"] = view_name
                    results.append(result)

        # Jump to 100%
        _render_progress(100, "", done=True)

        if results:
            st.session_state["tab1_results"] = results
            if anchor_image_bytes:
                st.session_state["tab1_anchor_bytes"] = anchor_image_bytes
            # Record usage only after successful generation
            if _user:
                record_usage(_user["id"], "site_renderer", "image-gen")
                # Save to history
                try:
                    from utils.history import save_history
                    view_names = [r.get("view_name", "View") for r in results]
                    save_history(
                        _user["id"], "site_renderer",
                        f"{st.session_state.get('tab1_project_type', 'Design')} — {st.session_state.get('tab1_style', 'Modern')}",
                        f"Generated {len(results)} renderings: {', '.join(view_names)}",
                    )
                except Exception:
                    pass
                st.rerun()
        else:
            st.error(t("generation_failed"))

    # --- Display results ----------------------------------------
    if "tab1_results" in st.session_state and st.session_state["tab1_results"]:
        st.markdown("---")
        section_header("🖼️", t("t1_results_title"))

        results = st.session_state["tab1_results"]
        cols = st.columns(min(len(results), 2))

        for i, r in enumerate(results):
            with cols[i % 2]:
                view_label = r.get("view_name", f"View {i + 1}")
                st.markdown("<div class='result-frame'>", unsafe_allow_html=True)
                st.image(
                    r["image_bytes"],
                    use_container_width=True,
                )
                st.markdown(
                    f"<div class='frame-label'>{view_label}</div></div>",
                    unsafe_allow_html=True,
                )
                if r.get("text"):
                    st.caption(r["text"])

                import re as _re
                _clean_label = _re.sub(r'^[\U0001f000-\U0001ffff\u2600-\u27bf\ufe0f\u200d]+\s*', '', view_label)
                safe_name = _clean_label.replace(" ", "_").replace("/", "_").lower()
                st.download_button(
                    label=t_fmt("t1_download", label=_clean_label),
                    data=r["image_bytes"],
                    file_name=f"design_{safe_name}.png",
                    mime="image/png",
                    key=f"dl_{i}",
                )

        # --- Download All as ZIP ---
        if len(results) > 1:
            try:
                import io, zipfile
                zip_buf = io.BytesIO()
                with zipfile.ZipFile(zip_buf, "w") as zf:
                    for i, r in enumerate(results):
                        name = r.get("view_name", f"view_{i+1}").replace(" ", "_").replace("/", "_").lower()
                        zf.writestr(f"design_{name}.png", r["image_bytes"])
                st.download_button(
                    label="Download All (.zip)" if t("log_in") != "登录" else "打包下载全部",
                    data=zip_buf.getvalue(),
                    file_name="cdi_renderings.zip",
                    mime="application/zip",
                    key="dl_all_zip",
                    use_container_width=True,
                )
            except Exception:
                pass

        # --- Flyover Video Generation --------------------------------
        _render_video_section()

        # --- Feedback ------------------------------------------------
        from utils.feedback import render_feedback
        render_feedback("site_renderer", "tab1_results")
