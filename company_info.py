import gradio as gr
import base64
from PIL import Image
import io

def create_company_info_ui():
    """Create the company information UI component"""
    with gr.Blocks() as company_info_ui:
        gr.Markdown("# Company Information (KYC)")
        gr.Markdown("Please provide the following information about the company being audited.")
                
        company_info = gr.State({})
                
        with gr.Row():
            with gr.Column():
                company_name = gr.Textbox(label="Company Name", placeholder="Enter the company's legal name")
                company_id = gr.Textbox(label="Company Registration/CIN", placeholder="Enter company registration number")
                gst_id = gr.Textbox(label="GST Number", placeholder="Enter GST registration number")
                pan_number = gr.Textbox(label="PAN Number", placeholder="Enter company PAN")
                address = gr.Textbox(label="Registered Address", placeholder="Enter registered company address", lines=3)
                        
            with gr.Column():
                industry = gr.Dropdown(
                    label="Industry Sector",
                    choices=["Manufacturing", "Services", "Retail", "Technology", "Banking & Finance", "Healthcare", "Other"]
                )
                fiscal_year = gr.Textbox(label="Fiscal Year", placeholder="e.g., 2024-2025")
                                
                # Add materiality thresholds - fixed to remove placeholder
                gr.Markdown("### Materiality Thresholds")
                overall_materiality = gr.Number(label="Overall Materiality (₹)")
                performance_materiality = gr.Number(label="Performance Materiality (₹)")
                trivial_threshold = gr.Number(label="Trivial Threshold (₹)")
                
        gr.Markdown("### Auditor Information")
        with gr.Row():
            with gr.Column():
                ca_name = gr.Textbox(label="CA Name", placeholder="Enter CA's full name")
                ca_id = gr.Textbox(label="CA Membership Number", placeholder="Enter CA membership number")
                ca_firm = gr.Textbox(label="Firm Name", placeholder="Enter CA firm name")
                        
            with gr.Column():
                digital_signature = gr.File(label="Upload Digital Signature (Image)", file_types=["image"])
                signature_preview = gr.Image(label="Signature Preview", visible=False)
                
        with gr.Row():
            save_button = gr.Button("Save Company Information", variant="primary")
            skip_button = gr.Button("Skip for Now", variant="secondary")
                    
        # Status message
        status_msg = gr.Markdown("", visible=False)
                
        # Function to preview signature
        def preview_signature(file):
            if file is None:
                return None, gr.update(visible=False)
            try:
                img = Image.open(file.name)
                return img, gr.update(visible=True)
            except Exception as e:
                return None, gr.update(visible=False)
                
        digital_signature.change(
            preview_signature,
            inputs=[digital_signature],
            outputs=[signature_preview, signature_preview]
        )
                
        # Function to save company info
        def save_company_details(company_name, company_id, gst_id, pan_number, address, industry, fiscal_year,
                                overall_materiality, performance_materiality, trivial_threshold,
                                ca_name, ca_id, ca_firm, digital_signature):
            company_info = {
                "company_name": company_name,
                "company_id": company_id,
                "gst_id": gst_id,
                "pan_number": pan_number,
                "address": address,
                "industry": industry,
                "fiscal_year": fiscal_year,
                "overall_materiality": overall_materiality,
                "performance_materiality": performance_materiality,
                "trivial_threshold": trivial_threshold,
                "ca_name": ca_name,
                "ca_id": ca_id,
                "ca_firm": ca_firm,
                "has_digital_signature": digital_signature is not None
            }
                        
            # Convert signature to base64 if provided
            if digital_signature:
                try:
                    with open(digital_signature.name, "rb") as img_file:
                        img_data = img_file.read()
                        company_info["digital_signature"] = base64.b64encode(img_data).decode('utf-8')
                except Exception as e:
                    print(f"Error processing signature: {str(e)}")
                        
            return company_info, gr.update(value="✅ Company information saved successfully!", visible=True)
                
        save_button.click(
            save_company_details,
            inputs=[company_name, company_id, gst_id, pan_number, address, industry, fiscal_year,
                   overall_materiality, performance_materiality, trivial_threshold,
                   ca_name, ca_id, ca_firm, digital_signature],
            outputs=[company_info, status_msg]
        )
                
        # Function to skip company info
        def skip_company_info():
            return {"skipped": True}, gr.update(value="⚠️ Company information skipped.", visible=True)
                
        skip_button.click(
            skip_company_info,
            inputs=[],
            outputs=[company_info, status_msg]
        )
        
        return company_info_ui
