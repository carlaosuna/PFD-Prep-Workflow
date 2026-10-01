import streamlit as st
from pathlib import Path
import tempfile
import shutil

# Try to import PDF processing libraries
try:
    from PyPDF2 import PdfReader, PdfWriter
    import pikepdf
    HAS_PDF_LIBS = True
except ImportError:
    HAS_PDF_LIBS = False

# Page config
st.set_page_config(
    page_title="PDF Prep Workflow",
    page_icon="📄",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS
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
        <p>Process your PDFs instantly - no installation needed!</p>
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

workflow_options = {
    "Full (Rotate + Number + Flatten)": "full",
    "Rotate Only": "rotate",
    "Number Only": "number",
    "Flatten Only": "flatten",
    "Flatten + Rotate": "flatten_rotate",
    "Flatten + Number": "flatten_number",
}

workflow_choice = st.radio(
    "Select a workflow:",
    list(workflow_options.keys()),
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
        st.error("❌ Please select at least one PDF file")
    else:
        try:
            with st.spinner("Processing your PDFs..."):
                processed_files = []
                workflow_key = workflow_options[workflow_choice]
                
                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_path = Path(temp_dir)
                    
                    for uploaded_file in uploaded_files:
                        try:
                            # Read file bytes directly
                            file_bytes = uploaded_file.read()
                            
                            # Process the file in memory when possible
                            if HAS_PDF_LIBS:
                                output_bytes = process_pdf_bytes(file_bytes, workflow_key, temp_path)
                            else:
                                output_bytes = file_bytes
                            
                            # Store with original filename
                            processed_files.append((uploaded_file.name, output_bytes))
                        
                        except Exception as e:
                            st.error(f"Error processing {uploaded_file.name}: {str(e)}")
                            continue
                
                # Display results
                if processed_files:
                    st.success(f"✅ Success! {len(processed_files)} file(s) processed")
                    st.info("📥 Download your processed files:")
                    
                    for filename, file_bytes in processed_files:
                        st.download_button(
                            label=f"📥 {filename}",
                            data=file_bytes,
                            file_name=filename,
                            mime="application/pdf",
                            use_container_width=True
                        )
                else:
                    st.error("❌ No files were successfully processed.")
        
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

def process_pdf_bytes(pdf_bytes, workflow, temp_path):
    """Process PDF from bytes and return bytes"""
    input_file = temp_path / "input.pdf"
    output_file = temp_path / "output.pdf"
    
    input_file.write_bytes(pdf_bytes)
    
    if workflow == "rotate":
        rotate_only(str(input_file), str(output_file))
    elif workflow == "number":
        number_only(str(input_file), str(output_file))
    elif workflow == "flatten":
        flatten_only(str(input_file), str(output_file))
    elif workflow == "flatten_rotate":
        flatten_then_rotate(str(input_file), str(output_file))
    elif workflow == "flatten_number":
        flatten_then_number(str(input_file), str(output_file))
    else:  # full
        full_workflow(str(input_file), str(output_file))
    
    return output_file.read_bytes()

def rotate_only(input_pdf, output_pdf):
    """Rotate landscape to portrait"""
    try:
        reader = PdfReader(input_pdf)
        writer = PdfWriter()
        
        for page in reader.pages:
            mediabox = page.mediabox
            if float(mediabox.width) > float(mediabox.height):
                page.rotate(270)
            writer.add_page(page)
        
        with open(output_pdf, 'wb') as f:
            writer.write(f)
    except:
        shutil.copy2(input_pdf, output_pdf)

def number_only(input_pdf, output_pdf):
    """Add page numbers only"""
    try:
        with pikepdf.open(input_pdf) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                page_text = f"""
BT
/F1 12 Tf
280 20 Td
({page_num}) Tj
ET
"""
                if '/Contents' not in page:
                    page['/Contents'] = pikepdf.Stream(pdf, page_text.encode('utf-8'))
                else:
                    contents = page['/Contents']
                    if isinstance(contents, pikepdf.Array):
                        new_content = pikepdf.Stream(pdf, page_text.encode('utf-8'))
                        contents.append(new_content)
                    else:
                        old_data = contents.read_bytes()
                        new_data = old_data + page_text.encode('utf-8')
                        page['/Contents'] = pikepdf.Stream(pdf, new_data)
            pdf.save(output_pdf)
    except:
        shutil.copy2(input_pdf, output_pdf)

def flatten_only(input_pdf, output_pdf):
    """Flatten layers only"""
    try:
        with pikepdf.open(input_pdf) as pdf:
            if '/OCProperties' in pdf.Root:
                del pdf.Root['/OCProperties']
            pdf.save(output_pdf)
    except:
        shutil.copy2(input_pdf, output_pdf)

def flatten_then_rotate(input_pdf, output_pdf):
    """Flatten then rotate"""
    temp_file = input_pdf.replace('.pdf', '_temp1.pdf')
    try:
        flatten_only(input_pdf, temp_file)
        rotate_only(temp_file, output_pdf)
    finally:
        if Path(temp_file).exists():
            Path(temp_file).unlink()

def flatten_then_number(input_pdf, output_pdf):
    """Flatten then add numbers"""
    temp_file = input_pdf.replace('.pdf', '_temp1.pdf')
    try:
        flatten_only(input_pdf, temp_file)
        number_only(temp_file, output_pdf)
    finally:
        if Path(temp_file).exists():
            Path(temp_file).unlink()

def full_workflow(input_pdf, output_pdf):
    """Full workflow: rotate, number, flatten"""
    temp1 = input_pdf.replace('.pdf', '_temp1.pdf')
    temp2 = input_pdf.replace('.pdf', '_temp2.pdf')
    
    try:
        rotate_only(input_pdf, temp1)
        number_only(temp1, temp2)
        flatten_only(temp2, output_pdf)
    finally:
        for temp in [temp1, temp2]:
            if Path(temp).exists():
                Path(temp).unlink()

st.markdown("---")

# Footer
st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.9em; margin-top: 40px;">
        <p><strong>PDF Prep Workflow</strong></p>
        <p>No installation • No downloads • No login • Completely free</p>
        <p style="font-size: 0.85em; color: #999;">Files keep their original names throughout</p>
    </div>
""", unsafe_allow_html=True)
