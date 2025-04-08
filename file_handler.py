import os
import PyPDF2
import docx

class FileHandler:
    def __init__(self):
        self.supported_extensions = ['.txt', '.pdf', '.docx']
    
    def is_supported_file(self, filename):
       
        _, ext = os.path.splitext(filename)
        return ext.lower() in self.supported_extensions
    
    def extract_text_from_file(self, file_path):
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        if ext not in self.supported_extensions:
            raise ValueError(f"Unsupported file type: {ext}")
        
        if ext == '.txt':
            return self._extract_from_txt(file_path)
        elif ext == '.pdf':
            return self._extract_from_pdf(file_path)
        elif ext == '.docx':
            return self._extract_from_docx(file_path)
    
    def _extract_from_txt(self, file_path):
        """Extract text from a txt file"""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    
    def _extract_from_pdf(self, file_path):
        """Extract text from a PDF file"""
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text()
        return text
    
    def _extract_from_docx(self, file_path):
        """Extract text from a DOCX file"""
        doc = docx.Document(file_path)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        return '\n'.join(full_text) 