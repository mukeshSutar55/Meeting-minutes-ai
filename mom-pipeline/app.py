import os
import json
import streamlit as st
import static_ffmpeg
static_ffmpeg.add_paths()
from config.settings import settings
from main import run_pipeline
from utils.exporter import ReportExporter
from dotenv import load_dotenv
load_dotenv()  # Loads variables from .env into os.environ
st.set_page_config(
    page_title="Multilingual Voice MoM Pipeline",
    page_icon="🎙️",
    layout="wide"
)

st.title("🎙️ Voice-Based Minutes of Meeting (MoM) Pipeline")
st.caption("Supports Multilingual Audio/Video (English, Hindi, Odia) with Groq Whisper & Deepgram Speaker Diarization")

st.sidebar.header("Configuration & Setup")
st.sidebar.markdown("""
**Models Used:**
- **STT:** Groq `whisper-large-v3`
- **Diarization:** Deepgram `nova-3`
- **MoM LLM:** `openai/gpt-oss-120b`
""")

# File Uploader
uploaded_file = st.file_uploader(
    "Upload Meeting Audio/Video File",
    type=["mp3", "wav", "m4a", "flac", "mp4", "mkv", "avi", "mov"]
)

if uploaded_file is not None:
    # Save uploaded file to temporary storage
    input_file_path = os.path.join(settings.UPLOAD_DIR, uploaded_file.name)
    with open(input_file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success(f"File uploaded successfully: **{uploaded_file.name}**")
    st.audio(input_file_path)

    if st.button("🚀 Process Meeting Recording", type="primary"):
        with st.spinner("Processing audio, running speaker diarization, transcribing, and generating MoM..."):
            try:
                # Run the complete end-to-end pipeline
                result = run_pipeline(input_file_path)
                st.session_state["mom_result"] = result
                st.session_state["file_name"] = os.path.splitext(uploaded_file.name)[0]
            except Exception as e:
                st.error(f"Pipeline execution failed: {str(e)}")

# Display Pipeline Results
if "mom_result" in st.session_state:
    result = st.session_state["mom_result"]
    file_name = st.session_state["file_name"]

    st.divider()
    
    # 1. Metadata & High-Level Metrics
    meta = result.get("metadata", {})
    col1, col2, col3 = st.columns(3)
    col1.metric("Primary Language Detected", meta.get("primary_language", "N/A").upper())
    col2.metric("Total Meeting Duration", f"{meta.get('total_duration_seconds', 0)} seconds")
    col3.metric("Total Speakers", len(result.get("speaker_statistics", {})))

    tab1, tab2, tab3, tab4 = st.tabs([
        "📄 Minutes of Meeting", 
        "📊 Speaker Analytics", 
        "💬 Full Transcript", 
        "📥 Exports"
    ])

    # Tab 1: Executive Summary, Decisions, and Action Items
    with tab1:
        mom = result.get("minutes_of_meeting", {})
        
        st.subheader("Executive Summary")
        st.write(mom.get("summary", "N/A"))

        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("Key Discussion Points")
            for point in mom.get("key_discussion_points", []):
                st.markdown(f"- {point}")

        with col_b:
            st.subheader("Decisions Made")
            for decision in mom.get("decisions_made", []):
                st.markdown(f"- {decision}")

        st.subheader("Action Items")
        actions = mom.get("action_items", [])
        if actions:
            st.table(actions)
        else:
            st.info("No action items identified.")

    # Tab 2: Conversation Statistics
    with tab2:
        st.subheader("Participant Speaking Time Breakdown")
        stats = result.get("speaker_statistics", {})
        if stats:
            stats_list = [
                {
                    "Participant": speaker,
                    "Speaking Time (s)": data.get("total_speaking_time_seconds", 0),
                    "Segments Count": data.get("speaking_segments_count", 0),
                    "Talk Ratio (%)": f"{data.get('speaking_percentage', 0)}%"
                }
                for speaker, data in stats.items()
            ]
            st.dataframe(stats_list, use_container_width=True)

    # Tab 3: Speaker-Aligned Chronological Transcript
    with tab3:
        st.subheader("Chronological Meeting Transcript")
        transcript = result.get("transcript", [])
        for seg in transcript:
            st.markdown(
                f"**[{seg.get('start')}s - {seg.get('end')}s] `{seg.get('speaker')}`:** {seg.get('text')}"
            )

    # Tab 4: PDF & DOCX Export Downloads
    with tab4:
        st.subheader("Download Formatted Reports")

        pdf_path = os.path.join(settings.OUTPUT_DIR, f"{file_name}_mom.pdf")
        docx_path = os.path.join(settings.OUTPUT_DIR, f"{file_name}_mom.docx")

        # Generate exported files if they don't exist yet
        ReportExporter.to_pdf(result, pdf_path)
        ReportExporter.to_docx(result, docx_path)

        c1, c2, c3 = st.columns(3)

        with open(pdf_path, "rb") as pdf_file:
            c1.download_button(
                label="📄 Download PDF Report",
                data=pdf_file,
                file_name=f"{file_name}_MoM.pdf",
                mime="application/pdf"
            )

        with open(docx_path, "rb") as docx_file:
            c2.download_button(
                label="📝 Download Word (.docx)",
                data=docx_file,
                file_name=f"{file_name}_MoM.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

        json_str = json.dumps(result, indent=2, ensure_ascii=False)
        c3.download_button(
            label="📊 Download Raw JSON",
            data=json_str,
            file_name=f"{file_name}_MoM.json",
            mime="application/json"
        )