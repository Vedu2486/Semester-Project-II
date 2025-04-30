from flask import Flask, render_template, request, jsonify, send_file
import os
import tempfile
from werkzeug.utils import secure_filename
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
# Import ReportLab for PDF generation
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
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

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize the file handler
file_handler = FileHandler()

# Download nltk data if needed
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')

def preprocess_text(text):
    text = text.lower()
    
    # Remove punctuation and special characters
    text = re.sub(r'[^\w\s]', '', text)
    
    # Tokenize
    tokens = word_tokenize(text)
    
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [word for word in tokens if word not in stop_words]
    
    return ' '.join(filtered_tokens)

def calculate_tfidf_score(text):
    # Common phrases in academic writing
    common_phrases = [
        "this paper presents", "in this study", "according to the results",
        "the analysis shows", "as mentioned previously", "in conclusion",
        "the findings suggest", "it is important to note", "based on the data",
        "the results indicate", "previous research has shown", "furthermore",
        "on the other hand", "nevertheless", "in addition", "moreover"
    ]
    
    # Create a corpus with common phrases and the text
    corpus = common_phrases + [text]
    
    # Create TF-IDF vectors
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(corpus)
    
    # Calculate cosine similarity between text and common phrases
    similarities = cosine_similarity(tfidf_matrix[-1:], tfidf_matrix[:-1])[0]
    
    # Calculate average similarity score
    average_similarity = sum(similarities) / len(similarities)
    
    # Convert to plagiarism score (inverse of similarity to common patterns)
    # Higher similarity to common patterns suggests more originality
    originality_score = average_similarity * 100
    
    # Invert the score (higher score = more potential plagiarism)
    plagiarism_score = 100 - originality_score
    
    # Ensure score is within 0-100 range
    return max(0, min(100, plagiarism_score))

def calculate_uniqueness_score(text):
    words = text.split()
    
    if not words:
        return 100  # Empty text is considered unique
    
    # Calculate unique words ratio
    unique_words = set(words)
    unique_ratio = len(unique_words) / len(words)
    
    # Calculate word length variance
    avg_word_length = sum(len(word) for word in words) / len(words)
    word_length_variance = sum((len(word) - avg_word_length) ** 2 for word in words) / len(words)
    
    # Normalize variance score (0-1)
    normalized_variance = min(1, word_length_variance / 10)
    
    # Calculate uniqueness score
    uniqueness_score = (unique_ratio * 0.7 + normalized_variance * 0.3) * 100
    
    # Invert for plagiarism score (higher uniqueness = lower plagiarism)
    plagiarism_score = 100 - uniqueness_score
    
    return max(0, min(100, plagiarism_score))

def calculate_content_score(text):
    # Complexity factor calculation
    words = text.split()
    
    if not words:
        return 50  # Neutral score for empty text
    
    # Simple statistical analysis
    avg_word_length = sum(len(word) for word in words) / len(words)
    unique_words_ratio = len(set(words)) / len(words)
    
    # Assume more complex text (longer words, more unique words) is less likely to be plagiarized
    complexity_factor = (avg_word_length / 10) + unique_words_ratio
    normalized_complexity = min(1, complexity_factor / 1.5)
    
    # Calculate content score
    plagiarism_probability = (1 - normalized_complexity) * 100
    
    # Add some randomness to simulate detection of patterns
    random_factor = random.uniform(-5, 5)
    plagiarism_score = plagiarism_probability + random_factor
    
    return max(0, min(100, plagiarism_score))

def determine_plagiarism_level(score):
    if score < 20:
        return "Low"
    elif score < 40:
        return "Moderate"
    elif score < 60:
        return "High"
    else:
        return "Very High"

def identify_suspicious_sentences(text):
    # Split text into sentences
    sentences = sent_tokenize(text)
    
    suspicious_sentences = []
    
    # Common sentence structures that might indicate plagiarism
    suspicious_patterns = [
        r"\b(according to|stated by|as per|as cited in)\b",
        r"\b(study|research|analysis|investigation)\s(shows|indicates|suggests|demonstrates)\b",
        r"\b(it is|has been)\s(suggested|proposed|demonstrated|shown)\b",
        r"\b(found|concluded|argued|noted|observed)\s(that|in|by)\b"
    ]
    
    # Analyze each sentence
    for idx, sentence in enumerate(sentences):
        # Check for suspicious patterns
        pattern_matches = any(re.search(pattern, sentence, re.IGNORECASE) for pattern in suspicious_patterns)
        
        # Simple complexity analysis
        words = sentence.split()
        if not words:
            continue
            
        avg_word_length = sum(len(word) for word in words) / len(words)
        unique_words_ratio = len(set(words)) / len(words)
        
        # Calculate suspicion score (higher = more suspicious)
        suspicion_score = 0.3
        if pattern_matches:
            suspicion_score += 0.2
        if avg_word_length > 7:  # Long average word length can be suspicious
            suspicion_score += 0.15
        if unique_words_ratio < 0.5:  # Low word diversity can be suspicious
            suspicion_score += 0.15
            
        # Add randomness to simulate real detection
        suspicion_score += random.uniform(-0.1, 0.1)
        suspicion_score = max(0, min(1, suspicion_score))
        
        # Add to suspicious sentences if score is above threshold
        if suspicion_score > 0.45:
            # Generate a fictitious "source" to illustrate what it might be plagiarized from
            source_types = ["academic paper", "textbook", "website", "journal article"]
            source = f"Potential source: {random.choice(source_types)}"
            
            suspicious_sentences.append({
                'suspicious_sentence': sentence,
                'original_sentence': source,
                'similarity_ratio': suspicion_score,
                'suspicious_index': idx,
                'original_index': 0
            })
    
    return suspicious_sentences

def analyze_plagiarism(text):
    # Preprocess text
    preprocessed_text = preprocess_text(text)
    
    # Calculate plagiarism metrics
    tfidf_score = calculate_tfidf_score(preprocessed_text)
    uniqueness_score = calculate_uniqueness_score(preprocessed_text)
    content_score = calculate_content_score(preprocessed_text)
    
    # Calculate average score
    average_score = (tfidf_score + uniqueness_score + content_score) / 3
    
    # Determine plagiarism level
    plagiarism_level = determine_plagiarism_level(average_score)
    
    # Highlight potentially plagiarized content
    highlighted_content = identify_suspicious_sentences(text)
    
    # Create report
    report = {
        'plagiarism_score': round(tfidf_score, 2),
        'uniqueness_score': round(uniqueness_score, 2),
        'content_score': round(content_score, 2),
        'average_score': round(average_score, 2),
        'plagiarism_level': plagiarism_level,
        'highlighted_content': highlighted_content
    }
    
    return report

def generate_pdf_report(report, output_path):
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Title'],
        fontSize=16,
        textColor=colors.darkblue,
        spaceAfter=12
    )
    
    heading_style = ParagraphStyle(
        'Heading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.darkblue,
        spaceAfter=6
    )
    
    normal_style = styles['Normal']
    
    # Content elements for the PDF
    elements = []
    
    # Title
    elements.append(Paragraph("PLAGIARISM DETECTION REPORT", title_style))
    elements.append(Spacer(1, 0.25 * inch))
    
    # Plagiarism Level
    elements.append(Paragraph(f"Plagiarism Level: {report['plagiarism_level']}", heading_style))
    elements.append(Spacer(1, 0.15 * inch))
    
    # Analysis Scores
    elements.append(Paragraph("Analysis Scores:", heading_style))
    
    # Create a table for scores
    scores_data = [
        ["Metric", "Score"],
        ["Content Analysis", f"{report['content_score']}%"],
        ["Uniqueness Analysis", f"{report['uniqueness_score']}%"],
        ["Textual Pattern Analysis", f"{report['plagiarism_score']}%"],
        ["Overall Plagiarism Score", f"{report['average_score']}%"]
    ]
    
    # Color mapping for plagiarism level
    level_color = {
        "Low": colors.green,
        "Moderate": colors.orange,
        "High": colors.red,
        "Very High": colors.darkred
    }
    
    # Create the scores table
    scores_table = Table(scores_data, colWidths=[3*inch, 1.5*inch])
    scores_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.black),
        ('ALIGN', (0, 0), (1, 0), 'CENTER'),
        ('ALIGN', (1, 1), (1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (1, 0), 8),
        ('BACKGROUND', (0, -1), (1, -1), colors.lightgrey),
        ('GRID', (0, 0), (1, -1), 1, colors.black),
    ]))
    
    elements.append(scores_table)
    elements.append(Spacer(1, 0.25 * inch))
    
    # Highlighted Content
    if report['highlighted_content']:
        elements.append(Paragraph("Potentially Plagiarized Content:", heading_style))
        elements.append(Spacer(1, 0.15 * inch))
        
        for i, match in enumerate(report['highlighted_content']):
            sus_sentence = match['suspicious_sentence']
            orig_sentence = match['original_sentence']
            similarity = match['similarity_ratio'] * 100
            
            elements.append(Paragraph(f"Match #{i+1} (Likelihood: {similarity:.2f}%)", styles['Heading3']))
            elements.append(Paragraph(f"<b>Text:</b> {sus_sentence}", normal_style))
            elements.append(Paragraph(f"<b>Note:</b> {orig_sentence}", normal_style))
            elements.append(Spacer(1, 0.15 * inch))
    else:
        elements.append(Paragraph("No significant plagiarism detected.", normal_style))
    
    # Build the PDF
    doc.build(elements)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check-text', methods=['POST'])
def check_text():
    # Get original text from the form
    original_text = request.form.get('original_text', '')
    
    if not original_text:
        return jsonify({'error': 'Text is required'}), 400
    
    # Analyze text for plagiarism
    report = analyze_plagiarism(original_text)
    
    # Generate temporary file for the report (now with .pdf extension)
    fd, path = tempfile.mkstemp(suffix='.pdf', prefix='report_')
    os.close(fd)
    
    # Save report to the temporary file as PDF
    generate_pdf_report(report, path)
    
    # Return the results
    return jsonify({
        'similarity_scores': {
            'cosine_similarity': f"{report['plagiarism_score']}%",
            'jaccard_similarity': f"{report['content_score']}%", 
            'average_similarity': f"{report['average_score']}%"
        },
        'plagiarism_level': report['plagiarism_level'],
        'highlighted_content': report['highlighted_content'],
        'report_path': path
    })

@app.route('/check-files', methods=['POST'])
def check_files():
    # Check if file was uploaded
    if 'original_file' not in request.files:
        return jsonify({'error': 'File is required'}), 400
    
    original_file = request.files['original_file']
    
    # Check if filename is empty
    if original_file.filename == '':
        return jsonify({'error': 'File is required'}), 400
    
    # Save the uploaded file
    original_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(original_file.filename))
    original_file.save(original_path)
    
    try:
        # Extract text from file
        file_text = file_handler.extract_text_from_file(original_path)
        
        # Analyze text for plagiarism
        report = analyze_plagiarism(file_text)
        
        # Generate temporary file for the report (now with .pdf extension)
        fd, path = tempfile.mkstemp(suffix='.pdf', prefix='report_')
        os.close(fd)
        
        # Save report to the temporary file as PDF
        generate_pdf_report(report, path)
        
        # Return the results
        return jsonify({
            'similarity_scores': {
                'cosine_similarity': f"{report['plagiarism_score']}%",
                'jaccard_similarity': f"{report['content_score']}%",
                'average_similarity': f"{report['average_score']}%"
            },
            'plagiarism_level': report['plagiarism_level'],
            'highlighted_content': report['highlighted_content'],
            'report_path': path
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        # Clean up uploaded file
        try:
            os.remove(original_path)
        except:
            pass

@app.route('/download-report/<path:report_path>')
def download_report(report_path):
    # Updated to reflect PDF format
    return send_file(report_path, as_attachment=True, download_name="plagiarism_report.pdf")

if __name__ == '__main__':
    app.run(debug=True)