import os
import pandas as pd
import docx
import PyPDF2
import tempfile
from pathlib import Path

class FileHandler:
    """Common file handling functionality for all agents"""
    
    @staticmethod
    def extract_text_from_pdf(file_path):
        """Extract text from PDF files."""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num in range(len(pdf_reader.pages)):
                    text += pdf_reader.pages[page_num].extract_text()
        except Exception as e:
            text = f"Error extracting PDF content: {str(e)}"
        return text

    @staticmethod
    def extract_text_from_docx(file_path):
        """Extract text from DOCX files."""
        try:
            doc = docx.Document(file_path)
            return "\n".join([paragraph.text for paragraph in doc.paragraphs])
        except Exception as e:
            return f"Error extracting DOCX content: {str(e)}"

    @staticmethod
    def extract_text_from_txt(file_path):
        """Extract text from TXT files."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            return f"Error extracting TXT content: {str(e)}"

    @staticmethod
    def extract_data_from_csv(file_path):
        """Extract data from CSV files."""
        try:
            df = pd.read_csv(file_path)
            return df.to_string()
        except Exception as e:
            return f"Error extracting CSV content: {str(e)}"

    @staticmethod
    def extract_data_from_excel(file_path):
        """Extract data from Excel files."""
        try:
            df = pd.read_excel(file_path)
            return df.to_string()
        except Exception as e:
            return f"Error extracting Excel content: {str(e)}"

    @staticmethod
    def process_file(file_path):
        """Process a file and extract its content based on file type."""
        if not os.path.exists(file_path):
            return f"File not found: {file_path}"
            
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == '.pdf':
            return FileHandler.extract_text_from_pdf(file_path)
        elif file_extension == '.docx':
            return FileHandler.extract_text_from_docx(file_path)
        elif file_extension == '.txt':
            return FileHandler.extract_text_from_txt(file_path)
        elif file_extension == '.csv':
            return FileHandler.extract_data_from_csv(file_path)
        elif file_extension in ['.xls', '.xlsx']:
            return FileHandler.extract_data_from_excel(file_path)
        else:
            return f"Unsupported file format: {file_extension}"
    
    @staticmethod
    def handle_uploaded_files(files, session_id, uploaded_files_dict):
        """Process uploaded files and store their information."""
        if session_id not in uploaded_files_dict:
            uploaded_files_dict[session_id] = []
        
        file_list = []
        for file in files:
            # Store the actual file object and its path
            file_path = file.name
            file_name = os.path.basename(file_path)
            
            # Save the file info
            uploaded_files_dict[session_id].append({
                "name": file_name,
                "path": file_path,
                "type": os.path.splitext(file_name)[1]
            })
            file_list.append(file_name)
        
        return file_list
