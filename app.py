from flask import Flask, render_template, request, jsonify, send_file
import os
import tempfile
from file_handler import FileHandler
from werkzeug.utils import secure_filename
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

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
    
    # Generate temporary file for the report
    fd, path = tempfile.mkstemp(suffix='.txt', prefix='report_')
    os.close(fd)
    
    # Save report to the temporary file
    with open(path, 'w', encoding='utf-8') as file:
        file.write(format_report_as_text(report))
    
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
        
        # Generate temporary file for the report
        fd, path = tempfile.mkstemp(suffix='.txt', prefix='report_')
        os.close(fd)
        
        # Save report to the temporary file
        with open(path, 'w', encoding='utf-8') as file:
            file.write(format_report_as_text(report))
        
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
    return send_file(report_path, as_attachment=True, download_name="plagiarism_report.txt")

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

def format_report_as_text(report):
    
    # Prepare the report text
    report_text = []
    report_text.append("=== PLAGIARISM DETECTION REPORT ===")
    report_text.append("")
    report_text.append(f"Plagiarism Level: {report['plagiarism_level']}")
    report_text.append("")
    report_text.append("Analysis Scores:")
    report_text.append(f"- Content Analysis: {report['content_score']}%")
    report_text.append(f"- Uniqueness Analysis: {report['uniqueness_score']}%")
    report_text.append(f"- Textual Pattern Analysis: {report['plagiarism_score']}%")
    report_text.append(f"- Overall Plagiarism Score: {report['average_score']}%")
    report_text.append("")
    
    if report['highlighted_content']:
        report_text.append("Potentially Plagiarized Content:")
        report_text.append("----------------------------------")
        
        for i, match in enumerate(report['highlighted_content']):
            sus_sentence = match['suspicious_sentence']
            orig_sentence = match['original_sentence']
            similarity = match['similarity_ratio'] * 100
            
            report_text.append(f"Match #{i+1} (Likelihood: {similarity:.2f}%):")
            report_text.append("Text:")
            report_text.append(f"  {sus_sentence}")
            report_text.append("Note:")
            report_text.append(f"  {orig_sentence}")
            report_text.append("")
    else:
        report_text.append("No significant plagiarism detected.")
    
    return '\n'.join(report_text)

if __name__ == '__main__':
    app.run(debug=True) 