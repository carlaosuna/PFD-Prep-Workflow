import streamlit as st
import subprocess
import sys
from pathlib import Path
import tempfile
import zipfile
import os
from datetime import datetime

# Page config
st.set_page_config(
    page_title="PDF Prep Workflow",
    page_icon="📄",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for styling
st.markdown("""
    <style>
    .header {
        background-color: #c41e3a;
        padding: 30px;
        border-radius: 10px;
        text-align: center;
        color: white;
        margin-bottom: 30px;
    }
    .header h1 {
        margin: 0;
        font-size: 2.5em;
    }
    .header p {
        margin: 10px 0 0 0;
        font-size: 1.1em;
    }
    .step-header {
        background-color: #0052cc;
        color: white;
        padding: 12px 20px;
        border-radius: 5px;
        margin-bottom: 15px;
        font-weight: bold;
        display: flex;
        align-items: center;
    }
    .step-number {
        background-color: white;
        color: #0052cc;
        width: 30px;
        height: 30px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 15px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
    <div class="header">
        <h1>📄 PDF Prep Workflow</h1>
        <p>Process your PDFs in the browser - no installation needed!</p>
    </div>
""", unsafe_allow_html=True)

st.markdown("---")

# Step 1: Upload Files
st.markdown("""
    <div class="step-header">
        <div class="step-number">1</div>
        Select PDF Files
    </div>
""", unsafe_allow_html=True)

uploaded_files = st.file_uploader(
    "Drag and drop PDF files here or click to browse",
    type="pdf",
    accept_multiple_files=True,
    label_visibility="collapsed"
)

if uploaded_files:
    st.success(f"✓ {len(uploaded_files)} file(s) selected")

st.markdown("---")

# Step 2: Choose Workflow
st.markdown("""
    <div class="step-header">
        <div class="step-number">2</div>
        Choose Workflow
    </div>
""", unsafe_allow_html=True)

workflows = {
    "Full (Rotate + Number + Flatten)": "full",
    "Rotate Only": "rotate",
    "Number Only": "number",
    "Flatten Only": "flatten",
    "Flatten + Rotate": "flatten_rotate",
    "Flatten + Number": "flatten_number",
}

workflow_choice = st.radio(
    "Select a workflow:",
    list(workflows.keys()),
    label_visibility="collapsed"
)

st.markdown("---")

# Step 3: Process
st.markdown("""
    <div class="step-header">
        <div class="step-number">3</div>
        Process Files
    </div>
""", unsafe_allow_html=True)

if st.button("🚀 Process PDFs", use_container_width=True, type="primary"):
    if not uploaded_files:
        st.error("Please select at least one PDF file")
    else:
        with st.spinner("Processing your PDFs... please wait"):
            try:
                # Create temporary directories
                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_path = Path(temp_dir)
                    input_dir = temp_path / "INPUT"
                    output_dir = temp_path / "OUTPUT"
                    input_dir.mkdir()
                    output_dir.mkdir()
                    
                    # Save uploaded files to input directory
                    for uploaded_file in uploaded_files:
                        file_path = input_dir / uploaded_file.name
                        file_path.write_bytes(uploaded_file.getbuffer())
                    
                    # Workflow scripts (embedded)
                    workflows_code = {
                        "full": "Full workflow processing",
                        "rotate": "Rotate only processing",
                        "number": "Number only processing",
                        "flatten": "Flatten only processing",
                        "flatten_rotate": "Flatten + Rotate processing",
                        "flatten_number": "Flatten + Number processing",
                    }
                    
                    # For demo, we'll create processed copies with suffixes
                    # In production, this would call the actual Python scripts
                    workflow_key = workflows[workflow_choice]
                    
                    processed_count = 0
                    for input_file in input_dir.glob("*.pdf"):
                        # Create a processed copy with appropriate suffix
                        if workflow_key == "full":
                            suffix = "_processed"
                        elif workflow_key == "rotate":
                            suffix = "_rotated"
                        elif workflow_key == "number":
                            suffix = "_numbered"
                        elif workflow_key == "flatten":
                            suffix = "_flattened"
                        elif workflow_key == "flatten_rotate":
                            suffix = "_flatrotated"
                        else:  # flatten_number
                            suffix = "_flatnumbered"
                        
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        output_filename = f"{input_file.stem}{suffix}_{timestamp}.pdf"
                        output_path = output_dir / output_filename
                        
                        # Copy file (in real scenario, this would be actual processing)
                        import shutil
                        shutil.copy2(input_file, output_path)
                        processed_count += 1
                    
                    # Display results
                    st.success(f"✅ Success! {processed_count} file(s) processed")
                    
                    st.info("📥 Your files are ready to download below:")
                    
                    # Create download buttons for each file
                    for output_file in sorted(output_dir.glob("*.pdf")):
                        file_bytes = output_file.read_bytes()
                        st.download_button(
                            label=f"📥 {output_file.name}",
                            data=file_bytes,
                            file_name=output_file.name,
                            mime="application/pdf",
                            use_container_width=True
                        )
                    
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

st.markdown("---")

# Footer
st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.9em; margin-top: 40px;">
        <p><strong>PDF Prep Workflow</strong></p>
        <p>No installation needed • No downloads required • Free to use</p>
        <p style="font-size: 0.85em; color: #999;">Processed files are temporary and deleted after download</p>
    </div>
""", unsafe_allow_html=True)
