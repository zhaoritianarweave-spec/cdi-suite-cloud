import pathlib
import time
import streamlit as st
from utils import gemini_client
from utils.ui_components import section_header

DEMO_DIR = pathlib.Path(__file__).resolve().parent.parent / "assets" / "demo_photos"

PROJECT_TYPES = [
    "Residential - House",
    "Townhouse / Duplex",
    "Apartment",
    "Commercial",
    "Landscape / Streetscape",
    "Civil Infrastructure",
    "Mixed Use",
]

DESIGN_STYLES = [
    "Modern",
    "Traditional",
    "Industrial",
    "Minimalist",
    "Sustainable",
    "Coastal",
]

VIEWPOINTS = {
    "🏠 Front Elevation": "close-up front elevation, camera at eye-level about 8 metres from the front door, tightly framed on the building facade, showing entrance detail, front door, porch, garage doors, facade materials and textures, with some foreground landscaping. Golden hour warm lighting. This is a CLOSE SHOT — do NOT show the full street or distant surroundings.",
    "🛩️ Bird's Eye / Aerial": "bird's-eye aerial perspective looking down at 45 degrees from about 50 metres altitude, showing the FULL site layout including roof plan, driveway, front yard, backyard, side setbacks, landscaping, pool if any, and surrounding neighbourhood context. Wide shot.",
    "🌳 Rear / Garden View": "The camera is BEHIND the house, positioned in the BACKYARD, looking TOWARD the REAR WALL of the building. Show the BACK of the house — rear sliding doors, alfresco area, deck or patio, pool if applicable, backyard lawn, rear fence and garden landscaping. The front door, front driveway and street must NOT be visible at all — they are on the opposite side of the building. This is a completely different scene from the front elevation.",
    "🚶 Street Level": "street-level pedestrian perspective from the footpath across the road, showing the full building in its streetscape context with neighbouring houses, street trees, footpath, fencing and letterbox. Wide contextual shot at eye level.",
}

# Quick-pick design feature chips
QUICK_FEATURES = {
    "🚗 Double Garage":      "large double garage with automatic door",
    "🚙 Triple Garage":      "oversized triple car garage",
    "🌿 Luxury Landscaping":  "premium landscaping with mature trees, hedge borders and garden lighting",
    "🏊 Backyard Pool":       "resort-style swimming pool with surrounding deck in the backyard",
    "🍖 Outdoor Kitchen":     "built-in outdoor BBQ and alfresco kitchen area",
    "🌳 Large Backyard":      "spacious rear yard with open lawn area",
    "🏡 Wrap-around Porch":   "wide wrap-around verandah or porch",
    "🪟 Floor-to-ceiling Glass": "floor-to-ceiling glass windows and curtain walls for natural light",
    "☀️ Rooftop Terrace":     "accessible rooftop terrace with lounge area",
    "🔒 Gated Entry":         "secure gated front entrance with intercom",
    "🏗️ Two Storey":          "two-storey design with balcony on upper level",
    "🏔️ Three Storey":        "three-storey design maximising floor area",
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
        consistency_block = """CRITICAL — the new rendering MUST match the SAME building visible in the aerial view, but seen from GROUND LEVEL in the BACKYARD:
- Same roof form, same facade materials, same colour palette, same number of storeys as the aerial image
- The camera is now in the BACKYARD looking at the REAR WALL of the building
- Show the BACK of the house: rear sliding doors, alfresco area, deck/patio, pool (if visible in aerial), backyard lawn
- The backyard layout (pool position, landscaping, fencing) must match what is visible in the aerial reference
- DO NOT show the front door, front porch, front driveway or street — those are on the opposite side
- This is a completely different scene from the front — only the building structure is the same"""
    elif is_front:
        consistency_block = """CRITICAL — the new rendering MUST match the SAME building visible in the aerial view, but seen from GROUND LEVEL at the FRONT:
- Same roof form, same facade materials, same colour palette, same number of storeys as the aerial image
- The camera is now at eye-level in front of the house, tightly framed on the facade
- Show the FRONT of the house: front door, porch, garage doors, facade materials
- The front yard layout (driveway, garage position, front landscaping) must match what is visible in the aerial reference
- Close-up shot — do NOT show distant surroundings or full street context"""
    else:
        consistency_block = """CRITICAL — the new rendering MUST match the SAME building visible in the aerial view:
- Same roof form, same facade materials, same colour palette, same number of storeys as the aerial image
- Same site layout, landscaping and features where visible from this angle
- Only the camera angle / perspective changes"""

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
    section_header("🎬", "Cinematic Flyover Video")
    st.caption(
        "Generate an 8-second cinematic fly-around video from the aerial rendering "
        "using the Generative Architecture Engine."
    )

    gen_video = st.button(
        "🎬 Generate Flyover Video",
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
                    "<span style='color:#3FB950;font-weight:700;'>✓ VIDEO READY</span>"
                    "<span style='color:#8B949E;'>|</span>"
                    "<span style='color:#E6EDF3;'>Cinematic flyover delivered</span>"
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
            st.error("Video generation failed. Please try again.")

    # Display previously generated video
    if "tab1_video" in st.session_state and st.session_state["tab1_video"]:
        st.video(st.session_state["tab1_video"], format="video/mp4")
        st.download_button(
            label="⬇️ Download Flyover Video",
            data=st.session_state["tab1_video"],
            file_name="design_flyover.mp4",
            mime="video/mp4",
            key="dl_video",
        )


# ---------------------------------------------------------------------------
# Render
# ---------------------------------------------------------------------------

def render():
    section_header("📐", "Site Intelligence Renderer")
    st.caption(
        "Upload a site photograph — the Generative Architecture Engine analyses existing conditions "
        "and produces multi-angle photorealistic renderings with design consistency across all viewpoints."
    )
    st.markdown("---")

    # --- Layout -------------------------------------------------
    col_left, col_right = st.columns([2, 3])

    image_bytes: bytes | None = None
    mime_type = "image/jpeg"

    with col_left:
        st.markdown("##### Site Photograph")
        uploaded = st.file_uploader(
            "Upload a site photo",
            type=["jpg", "jpeg", "png"],
            key="tab1_upload",
            label_visibility="collapsed",
        )

        if uploaded is not None:
            image_bytes = uploaded.getvalue()
            mime_type = uploaded.type or "image/jpeg"
            st.image(image_bytes, caption="Site Input", use_container_width=True)

        demo_photos = _get_demo_photos()
        if demo_photos:
            st.markdown(
                "<span style='color:#8B949E;font-size:0.8rem;'>OR SELECT A DEMO SITE</span>",
                unsafe_allow_html=True,
            )
            demo_cols = st.columns(len(demo_photos))
            for i, photo in enumerate(demo_photos):
                with demo_cols[i]:
                    if st.button(photo.stem, key=f"demo_photo_{i}", use_container_width=True):
                        st.session_state["tab1_demo_photo"] = str(photo)

            if "tab1_demo_photo" in st.session_state:
                demo_path = pathlib.Path(st.session_state["tab1_demo_photo"])
                if demo_path.exists():
                    image_bytes = demo_path.read_bytes()
                    mime_type = "image/png" if demo_path.suffix.lower() == ".png" else "image/jpeg"
                    st.image(image_bytes, caption=f"Demo — {demo_path.stem}", use_container_width=True)

    with col_right:
        st.markdown("##### Design Parameters")

        r1c1, r1c2 = st.columns(2)
        with r1c1:
            project_type = st.selectbox("Project Type", PROJECT_TYPES, key="tab1_project_type")
        with r1c2:
            style = st.selectbox(
                "Design Language",
                DESIGN_STYLES,
                index=0,
                key="tab1_style",
            )

        # --- Quick-pick feature chips ---
        st.markdown(
            "<span style='color:#8B949E;font-size:0.8rem;letter-spacing:0.5px;'>"
            "QUICK-PICK DESIGN FEATURES</span>",
            unsafe_allow_html=True,
        )
        selected_features = st.multiselect(
            "Quick Features",
            list(QUICK_FEATURES.keys()),
            default=["🌿 Luxury Landscaping"],
            key="tab1_features",
            label_visibility="collapsed",
        )

        # --- Rendering viewpoints ---
        selected_views = st.multiselect(
            "Rendering Viewpoints",
            list(VIEWPOINTS.keys()),
            default=["🛩️ Bird's Eye / Aerial", "🏠 Front Elevation"],
            key="tab1_views",
        )

        # --- Free-form design brief ---
        design_brief = st.text_area(
            "Design Brief",
            placeholder="Describe your vision... e.g., Open-plan living facing north, master suite on ground floor, seamless indoor-outdoor flow to the pool area...",
            key="tab1_brief",
            height=80,
        )

        total_images = len(selected_views)
        generate = st.button(
            f"Generate {total_images} Rendering{'s' if total_images != 1 else ''}",
            type="primary",
            use_container_width=True,
            disabled=image_bytes is None or total_images == 0,
        )

        if image_bytes is None:
            st.info("Upload a site photograph to activate the engine.")
        elif total_images == 0:
            st.warning("Select at least one viewpoint.")

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
            record_usage(_user["id"], "site_renderer", "image-gen")
        st.markdown("---")

        styles_str = style
        features_str = ", ".join(
            QUICK_FEATURES[f] for f in selected_features
        ) if selected_features else "standard features"
        brief_str = design_brief.strip() if design_brief.strip() else "no specific brief"

        ANCHOR_KEY = "🛩️ Bird's Eye / Aerial"
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
                    "<span style='color:#3FB950;font-weight:700;'>✓ COMPLETE</span>"
                    "<span style='color:#8B949E;'>|</span>"
                    "<span style='color:#E6EDF3;'>All renderings delivered</span>"
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
        _render_progress(1, f"Step 0/{len(ordered_views)}| Warming up engine...")
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
        else:
            st.error("Generation failed. Please adjust parameters and retry.")

    # --- Display results ----------------------------------------
    if "tab1_results" in st.session_state and st.session_state["tab1_results"]:
        st.markdown("---")
        section_header("🖼️", "Generated Renderings")

        results = st.session_state["tab1_results"]
        cols = st.columns(min(len(results), 2))

        for i, r in enumerate(results):
            with cols[i % 2]:
                view_label = r.get("view_name", f"View {i + 1}")
                st.image(
                    r["image_bytes"],
                    caption=view_label,
                    use_container_width=True,
                )
                if r.get("text"):
                    st.caption(r["text"])

                safe_name = view_label.replace(" ", "_").replace("/", "_").lower()
                st.download_button(
                    label=f"Download {view_label}",
                    data=r["image_bytes"],
                    file_name=f"design_{safe_name}.png",
                    mime="image/png",
                    key=f"dl_{i}",
                )

        # --- Flyover Video Generation --------------------------------
        _render_video_section()
