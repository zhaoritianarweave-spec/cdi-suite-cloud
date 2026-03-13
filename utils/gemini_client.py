import streamlit as st
from google import genai
from google.genai import types


def get_api_key() -> str:
    """Return the Gemini API key from Streamlit secrets."""
    try:
        return st.secrets["GEMINI_API_KEY"]
    except (KeyError, FileNotFoundError):
        return ""


def get_client() -> genai.Client | None:
    """Get a configured Gemini client."""
    api_key = get_api_key()
    if not api_key:
        return None
    return genai.Client(api_key=api_key)


def get_model_id() -> str:
    """Get the currently selected model ID from session state."""
    return st.session_state.get("model_id", "gemini-3.1-pro-preview")


def analyse_image(prompt: str, image_bytes: bytes, mime_type: str = "image/jpeg") -> str | None:
    """Send an image + text prompt to Gemini and return the response text."""
    client = get_client()
    if client is None:
        st.error("Gemini API key not configured. Contact admin.")
        return None

    try:
        response = client.models.generate_content(
            model=get_model_id(),
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                prompt,
            ],
        )
        return response.text
    except Exception as e:
        st.error(f"Gemini API error: {e}")
        return None


def analyse_text(prompt: str) -> str | None:
    """Send a text-only prompt to Gemini and return the response text."""
    client = get_client()
    if client is None:
        st.error("Gemini API key not configured. Contact admin.")
        return None

    try:
        response = client.models.generate_content(
            model=get_model_id(),
            contents=prompt,
        )
        return response.text
    except Exception as e:
        st.error(f"Gemini API error: {e}")
        return None


IMAGE_MODEL = "gemini-3.1-flash-image-preview"
VIDEO_MODEL = "veo-3.1-fast-generate-preview"


def generate_design_image(
    prompt: str,
    reference_images: list[tuple[bytes, str]] | None = None,
) -> dict | None:
    """Generate a design rendering image using Gemini image generation."""
    client = get_client()
    if client is None:
        st.error("Gemini API key not configured. Contact admin.")
        return None

    contents = []
    if reference_images:
        for img_bytes, mime in reference_images:
            contents.append(types.Part.from_bytes(data=img_bytes, mime_type=mime))
    contents.append(prompt)

    try:
        response = client.models.generate_content(
            model=IMAGE_MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"],
            ),
        )

        result = {"text": None, "image_bytes": None}
        for part in response.parts:
            if part.text is not None:
                result["text"] = part.text
            elif part.inline_data is not None:
                result["image_bytes"] = part.inline_data.data

        if result["image_bytes"] is None:
            st.warning("Model did not return an image. It may have been filtered by safety settings.")
            if result["text"]:
                st.info(result["text"])
            return None

        return result

    except Exception as e:
        st.error(f"Image generation error: {e}")
        return None


import time as _time


def generate_flyover_video(
    prompt: str,
    reference_image_bytes: bytes,
    mime_type: str = "image/png",
    duration_seconds: int = 8,
    poll_interval: int = 10,
    on_poll: callable = None,
) -> bytes | None:
    """Generate a fly-over video using Veo 3.1 Fast with a reference image."""
    client = get_client()
    if client is None:
        st.error("Gemini API key not configured. Contact admin.")
        return None

    try:
        image_obj = types.Image(
            imageBytes=reference_image_bytes,
            mimeType=mime_type,
        )

        operation = client.models.generate_videos(
            model=VIDEO_MODEL,
            prompt=prompt,
            image=image_obj,
            config=types.GenerateVideosConfig(
                durationSeconds=duration_seconds,
            ),
        )

        elapsed = 0
        while not operation.done:
            _time.sleep(poll_interval)
            elapsed += poll_interval
            if on_poll:
                on_poll(elapsed)
            operation = client.operations.get(operation)

        generated_video = operation.response.generated_videos[0]
        client.files.download(file=generated_video.video)
        return generated_video.video.video_bytes

    except Exception as e:
        st.error(f"Video generation error: {e}")
        return None
