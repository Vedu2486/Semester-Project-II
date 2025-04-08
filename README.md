# AI-Based Plagiarism Checker

A sophisticated Python-based plagiarism detection system that uses Natural Language Processing (NLP) techniques to analyze text for potential plagiarism. This web application provides both text-based and file-based plagiarism checking capabilities.

## Features

- **Multiple Input Methods**:
  - Direct text input
  - File upload support (TXT, PDF, DOCX)
- **Advanced Analysis**:
  - TF-IDF based similarity detection
  - Content uniqueness scoring
  - Statistical analysis of text patterns
- **Comprehensive Reporting**:
  - Multiple similarity metrics (Cosine, Jaccard)
  - Plagiarism level assessment
  - Highlighted suspicious content
  - Downloadable detailed reports

## Technical Stack

- **Backend**: Python Flask
- **NLP Libraries**: NLTK, scikit-learn
- **File Processing**: PyPDF2, python-docx
- **Frontend**: HTML, CSS, JavaScript

## Installation

1. Clone the repository
2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Start the Flask application:
   ```bash
   python app.py
   ```
2. Open your web browser and navigate to `http://localhost:5000`
3. Choose between:
   - Text input: Paste your text directly
   - File upload: Upload a document (TXT, PDF, or DOCX)
4. View the analysis results and download the detailed report

## Supported File Formats

- Text files (.txt)
- PDF documents (.pdf)
- Microsoft Word documents (.docx)

## Limitations

- Maximum file size: 16MB
- Currently optimized for English text
- Processing time may vary based on document length

## License

This project is open-source and available under the MIT License.

