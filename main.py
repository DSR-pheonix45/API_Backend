import os
import gradio as gr
import time
import uuid
from dotenv import load_dotenv
from file_handler import FileHandler
from agent_factory import AgentFactory
from company_info import create_company_info_ui

# Load environment variables
load_dotenv()

# Store uploaded files and session data
uploaded_files = {}
session_data = {}
available_agents = ["Dabby Consultant", "Auditor Agent", "Tax Agent"]

def get_agent(session_id):
    """Get the current agent for a session"""
    if session_id not in session_data:
        session_data[session_id] = {
            "agent_name": "Dabby Consultant",
            "agent": AgentFactory.get_agent("Dabby Consultant"),
            "company_info": None
        }
    return session_data[session_id]["agent"]

def upload_file(files, chatbot, session_id):
    """Handle file uploads and automatically analyze them"""
    file_list = FileHandler.handle_uploaded_files(files, session_id, uploaded_files)
    
    # Create a message to show files were uploaded
    if files and len(files) > 0:
        file_names = ", ".join([os.path.basename(f.name) for f in files])
        message = f"Uploaded {len(files)} file(s): {file_names}"
        
        # Add to chatbot
        updated_chatbot = chatbot.copy() if chatbot else []
        updated_chatbot.append(("System", message))
        
        # Automatically analyze all uploaded files
        agent = get_agent(session_id)
        
        updated_chatbot.append(("System", "Automatically analyzing all uploaded files..."))
        
        analysis_results = []
        for file in uploaded_files[session_id]:
            try:
                file_name = file["name"]
                file_path = file["path"]
                
                # Add a message for each file analysis
                updated_chatbot.append((f"Analyzing: {file_name}", "Processing..."))
                
                # Get response from agent
                response = agent.analyze_file(file_name, file_path, session_id)
                
                # Update the last message with the actual response
                updated_chatbot[-1] = (f"Analysis of {file_name}", response)
                
                analysis_results.append({"file": file_name, "analysis": response})
            except Exception as e:
                # If there's an error, update the message accordingly
                updated_chatbot.append((f"Error analyzing {file_name}", f"Error: {str(e)}"))
        
        # Add a summary of all files if there are multiple
        if len(analysis_results) > 1:
            # Get the agent to provide a combined analysis
            combined_analysis_prompt = "Based on all the documents analyzed, provide a comprehensive summary and key insights."
            combined_analysis = agent.chat(combined_analysis_prompt, session_id)
            
            updated_chatbot.append(("Combined Analysis Summary", combined_analysis))
        
        return updated_chatbot, gr.update(value=file_list)
    
    return chatbot, gr.update(value=file_list)


def analyze_file(file_name, chatbot, session_id):
    """Analyze a selected file"""
    if not file_name or file_name.strip() == "":
        updated_chatbot = chatbot.copy() if chatbot else []
        updated_chatbot.append(("System", "No file selected. Please select a file from the list."))
        return updated_chatbot
        
    if session_id not in uploaded_files or not uploaded_files[session_id]:
        updated_chatbot = chatbot.copy() if chatbot else []
        updated_chatbot.append(("System", "No files uploaded. Please upload files first."))
        return updated_chatbot
    
    # Find the selected file in the uploaded files
    selected_file = None
    for file in uploaded_files[session_id]:
        if file["name"] == file_name:
            selected_file = file
            break
    
    if not selected_file:
        updated_chatbot = chatbot.copy() if chatbot else []
        updated_chatbot.append(("System", f"File '{file_name}' not found in uploaded files."))
        return updated_chatbot
    
    # Create a copy of the chatbot
    updated_chatbot = chatbot.copy() if chatbot else []
    
    # Add a message indicating analysis is in progress
    updated_chatbot.append((f"Analyzing file: {file_name}", "Processing..."))
    
    # Get the current agent
    agent = get_agent(session_id)
    
    # Get response from agent
    try:
        response = agent.analyze_file(file_name, selected_file["path"], session_id)
        
        # Update the last message with the actual response
        updated_chatbot[-1] = (f"Analyzing file: {file_name}", response)
    except Exception as e:
        # If there's an error, update the message accordingly
        updated_chatbot[-1] = (f"Analyzing file: {file_name}", f"Error analyzing file: {str(e)}")
    
    return updated_chatbot

def chat(message, chatbot, session_id):
    """Handle chat interactions"""
    if not message.strip():
        return chatbot
    
    # Create a copy of the chatbot
    updated_chatbot = chatbot.copy() if chatbot else []
    
    # Add to chatbot for display
    updated_chatbot.append((message, "Thinking..."))
    yield updated_chatbot
    
    # Get the current agent
    agent = get_agent(session_id)
    
    try:
        response = agent.chat(message, session_id)
        
        # Update chatbot
        updated_chatbot[-1] = (message, response)
    except Exception as e:
        # If there's an error, update the message accordingly
        updated_chatbot[-1] = (message, f"Error: {str(e)}")
    
    yield updated_chatbot

def change_agent(agent_name, session_id):
    """Change the current agent"""
    if session_id not in session_data:
        session_data[session_id] = {}
    
    session_data[session_id]["agent_name"] = agent_name
    session_data[session_id]["agent"] = AgentFactory.get_agent(agent_name)
    
    return f"Agent switched to {agent_name}"

def clear_chat(session_id):
    """Clear the chat history"""
    agent = get_agent(session_id)
    agent.clear_history(session_id)
    return []

def save_company_info(company_info, session_id):
    """Save company information to session data"""
    if session_id not in session_data:
        session_data[session_id] = {
            "agent_name": "Dabby Consultant",
            "agent": AgentFactory.get_agent("Dabby Consultant")
        }
    
    session_data[session_id]["company_info"] = company_info
    return "Company information saved successfully!"

def generate_audit_report(format_selection, chatbot, session_id):
    """Generate an audit report in the selected format"""
    if session_id not in session_data:
        updated_chatbot = chatbot.copy() if chatbot else []
        updated_chatbot.append(("System", "Session data not found. Please try again."))
        return updated_chatbot, None
    
    if session_id not in uploaded_files or not uploaded_files[session_id]:
        updated_chatbot = chatbot.copy() if chatbot else []
        updated_chatbot.append(("System", "No files uploaded. Please upload files first."))
        return updated_chatbot, None
    
    # Get the current agent
    agent = get_agent(session_id)
    
    # Check if it's an auditor agent
    if session_data[session_id]["agent_name"] != "Auditor Agent":
        updated_chatbot = chatbot.copy() if chatbot else []
        updated_chatbot.append(("System", "Please switch to the Auditor Agent to generate audit reports."))
        return updated_chatbot, None
    
    # Create a copy of the chatbot
    updated_chatbot = chatbot.copy() if chatbot else []
    
    # Add a message indicating report generation is in progress
    updated_chatbot.append(("System", f"Generating {format_selection} audit report..."))
    
    try:
        # Get document texts
        document_texts = []
        for file in uploaded_files[session_id]:
            text = FileHandler.process_file(file["path"])
            document_texts.append(text)
        
        # Map format selection to audit type
        format_to_audit_type = {
            "CARO Format": "Companies (Auditor's Report) Order",
            "SA 230 Format": "Standard on Auditing 230",
            "IndAS Format": "Indian Accounting Standards",
            "GAAP Format": "Generally Accepted Accounting Principles"
        }
        
        audit_type = format_to_audit_type.get(format_selection, "Financial Statement")
        
        # Determine appropriate framework
        framework = agent.determine_audit_framework(document_texts, audit_type)
        
        # Get company info
        company_info = session_data[session_id].get("company_info", None)
        
        # Generate the report
        report_path = agent.generate_audit_report_docx(audit_type, document_texts, framework, company_info)
        
        # Update the last message with success
        updated_chatbot[-1] = ("System", f"✅ {format_selection} audit report generated successfully!")
        
        return updated_chatbot, report_path
    except Exception as e:
        # If there's an error, update the message accordingly
        updated_chatbot[-1] = ("System", f"Error generating report: {str(e)}")
        return updated_chatbot, None

def create_ui():
    """Create the Gradio UI"""
    with gr.Blocks(title="DABBY", theme=gr.themes.Soft()) as app:
        session_id = gr.State(value=str(uuid.uuid4()))
        
        with gr.Tabs() as tabs:
            with gr.TabItem("Chat"):
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("# DABBY")
                        agent_dropdown = gr.Dropdown(
                            choices=available_agents,
                            value="Dabby Consultant",
                            label="Select Agent"
                        )
                        
                        with gr.Accordion("Workbench", open=True):
                            file_upload = gr.File(
                                file_count="multiple",
                                label="Upload Files (PDF, CSV, Excel, DOCX, TXT)"
                            )
                            file_list = gr.Dropdown(label="Uploaded Files")
                            selected_file = gr.Textbox(label="Selected File to Analyze")
                            analyze_button = gr.Button("Analyze Selected File")
                        
                        # Only show for Auditor Agent
                        with gr.Accordion("Audit Tools", open=False, visible=False) as audit_tools:
                            format_dropdown = gr.Dropdown(
                                label="Select Audit Report Format",
                                choices=["CARO Format", "SA 230 Format", "IndAS Format", "GAAP Format"],
                                value=None
                            )
                            generate_report_button = gr.Button("Generate Audit Report")
                    with gr.Column(scale=3):
                        chatbot = gr.Chatbot(height=600)
                        with gr.Row():
                            message = gr.Textbox(
                                placeholder="Ask Dabby...",
                                show_label=False
                            )
                            submit_button = gr.Button("Send")
                        
                        clear_button = gr.Button("Clear Chat")
                        
                        # Hidden component for report download
                        report_output = gr.File(label="Download Report", visible=False)
            
            with gr.TabItem("Company Information"):
                company_info_component = create_company_info_ui()
        
        # Set up event handlers
        agent_dropdown.change(
            fn=change_agent,
            inputs=[agent_dropdown, session_id],
            outputs=[gr.Textbox(visible=False)]
        ).then(
            fn=lambda agent_name: f"Ask {agent_name}...",
            inputs=[agent_dropdown],
            outputs=[message]
        ).then(
            # Show/hide audit tools based on agent selection
            fn=lambda agent_name: gr.update(visible=agent_name == "Auditor Agent"),
            inputs=[agent_dropdown],
            outputs=[audit_tools]
        )
        
        file_upload.upload(
            fn=upload_file,
            inputs=[file_upload, chatbot, session_id],
            outputs=[chatbot, file_list]
        )
        
        # In the create_ui function, replace the file_list component with:

# And update the file_list.select event handler:
        file_list.change(
            fn=lambda x: x,
            inputs=[file_list],
            outputs=[selected_file]
        )

        
        
        submit_button.click(
            fn=chat,
            inputs=[message, chatbot, session_id],
            outputs=[chatbot]
        ).then(
            fn=lambda: "",
            outputs=[message]
        )
        
        message.submit(
            fn=chat,
            inputs=[message, chatbot, session_id],
            outputs=[chatbot]
        ).then(
            fn=lambda: "",
            outputs=[message]
        )
        
        clear_button.click(
            fn=clear_chat,
            inputs=[session_id],
            outputs=[chatbot]
        )
        
        # Handle company info saving
        if hasattr(company_info_component, 'company_info'):
            company_info_component.company_info.change(
                fn=save_company_info,
                inputs=[company_info_component.company_info, session_id],
                outputs=[gr.Textbox(visible=False)]
            )
        
        # Handle audit report generation
        generate_report_button.click(
            fn=generate_audit_report,
            inputs=[format_dropdown, chatbot, session_id],
            outputs=[chatbot, report_output]
        ).then(
            fn=lambda x: gr.update(visible=x is not None),
            inputs=[report_output],
            outputs=[report_output]
        )
    
    return app

if __name__ == "__main__":
    # Get configuration from environment variables
    port = int(os.getenv('GRADIO_PORT', 7860))
    share = os.getenv('GRADIO_SHARE', 'False').lower() == 'true'
    
    app = create_ui()
    app.queue()
    app.launch(
        server_name="0.0.0.0",
        server_port=port,
        share=share
    )
