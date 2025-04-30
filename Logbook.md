### 1. Introduction

#### Background
Academic institutions and content platforms emphasize originality, yet manual methods to detect plagiarism are tedious, inefficient, and prone to error. While commercial software solutions exist, they are often expensive and not accessible to all users. The need for an open, reliable, and user-friendly plagiarism detection tool is more pressing than ever.

This project provides a solution through a Python-based application that performs document comparison using NLP techniques and similarity metrics. It empowers users to maintain originality by validating their content effectively.

#### Problem Statement
Manual plagiarism detection is:
- Time-consuming
- Inaccurate, especially for paraphrased text
- Limited in scale when comparing multiple documents
- Unfeasible for students and institutions with restricted access to paid tools

#### Objectives
The primary goals of this project include:
- To build an automated plagiarism detection system for text documents
- To implement effective text comparison algorithms using NLP
- To allow the comparison of multiple document formats such as TXT, DOCX, and PDF
- To generate clear, readable reports indicating plagiarism percentage
- To ensure the solution is scalable, efficient, and user-friendly

#### Application
- **Academic Institutions**: For checking student assignments, research papers, and theses
- **Content Creators**: To verify the originality of their written work
- **Publishing Houses**: For ensuring the authenticity of submitted manuscripts
- **Legal Professionals**: To detect copyright infringement in documents

---

### 2. Literature Survey

#### Background
Detecting plagiarism has been a focus of both academic research and commercial application development. Multiple tools and techniques have evolved over time, each with its strengths and limitations.

#### Existing Systems
- **Turnitin**: Compares student submissions with a vast database. Subscription-based and costly.
- **Grammarly (Premium)**: Offers basic plagiarism detection but lacks depth for academic needs.
- **Open-source Methods**: Use techniques like fingerprinting, n-gram comparison, and edit distance. Often limited to plain text formats and less refined.

#### Relevant Technologies
- **Natural Language Processing (NLP)**: Preprocessing and normalizing text for better comparison
- **Cosine Similarity**: Evaluates how similar two documents are based on word vector angles
- **Levenshtein Distance**: Calculates the number of edits between strings, effective for paraphrased text
- **Jaccard Index**: Measures similarity based on token set intersection and union

#### Summary of Learnings
- Combining multiple algorithms improves detection accuracy
- Text preprocessing (tokenization, stemming, stop-word removal) enhances results
- Lightweight, offline systems are useful in low-resource environments

#### Citations
- Jurafsky, D., & Martin, J. H. *Speech and Language Processing*. Pearson
- Manning, C. D., Raghavan, P., & Schütze, H. *Introduction to Information Retrieval*. Cambridge University Press
- Scikit-learn documentation: [https://scikit-learn.org](https://scikit-learn.org)
- NLTK documentation: [https://www.nltk.org](https://www.nltk.org)
- PyPDF2: [https://github.com/py-pdf/PyPDF2](https://github.com/py-pdf/PyPDF2)
- “Levenshtein Distance Explained” – Towards Data Science, Medium
- GitHub repositories on text similarity algorithms

---

### 3. Methodology

#### Methodology / Approach
The development process was broken down into the following phases:

- **Requirement Analysis**: Identifying the need for an offline, easy-to-use tool
- **Tool and Library Selection**: Python chosen for its extensive NLP and file handling libraries
- **Text Preprocessing**: Using NLTK for tokenization, stemming, and stop-word removal
- **Similarity Calculation**:
  - Cosine Similarity
  - Levenshtein Distance
  - Jaccard Index
- **Interface Design**: A CLI or GUI for user interaction
- **Testing**: Conducted on documents of varying lengths and similarity levels

#### Hardware Requirements
- Processor: Intel Core i3 or equivalent
- Memory: 4 GB RAM
- Storage: 100 MB free space

#### Software Requirements
- OS: Windows 10+, macOS 10.15+, or Linux
- Python: Version 3.7 or later
- Libraries: NLTK, Scikit-learn, PyPDF2, python-docx
- IDE: VS Code or Jupyter Notebook
- Optional Tools: Flask, SQLite

#### Planning Milestones
- **Week 1–2**: Research and library testing
- **Week 3–4**: Development of preprocessing and similarity modules
- **Week 5–6**: Integration and testing with various document formats
- **Week 7**: Finalization and documentation

---

### 4. Implementation Details

#### Module-wise Description

- **Module 1: Plagiarism Detection with Generated Dataset**
  - Text input-based detection
  - Comparison against generated dataset
  - Output: Plagiarism percentage

- **Module 2: File Input and Report Generation**
  - Supports .txt, .pdf, and .docx files
  - Plagiarism detection for file inputs
  - Generates reports in .txt format

- **Module 3: Enhanced UI and PDF Report Generation**
  - Improved UI with better color grading
  - Plagiarism reports in .pdf format
  - More user-friendly interface

---

### 5. Results

#### Performance Metrics
- **Accuracy**: High detection for direct and partially modified content
- **Speed**: ~2 seconds for comparing 600-word documents
- **File Format Support**: Seamless handling of TXT, DOCX, and PDF
- **Reports**: Detailed similarity score and matched text highlight

#### Sample Test Outcomes
- Identical documents: 100% similarity
- Paraphrased documents: 60–75% similarity
- Unique documents: <20% similarity

#### Model Evaluation (Up to Sem-VI)
Test cases included:
- Directly copied content
- Paraphrased content with varying levels
- Minor word order and substitution changes
- File format diversity

- **Accuracy**: Averaged 92%
- **Observations**: Levenshtein Distance was highly effective for minor edits
- **Future Work**: Enhance accuracy for complex paraphrasing in Sem-VII

---

### 6. Conclusion
The developed plagiarism detection system offers a robust solution for identifying plagiarism in documents. Leveraging NLP techniques and similarity metrics, it handles direct copying and paraphrasing effectively. With multi-format support and detailed reporting, it is a valuable asset for students, educators, and content creators.

---

### 7. References
- Jurafsky, D., & Martin, J. H. *Speech and Language Processing*. Pearson
- Manning, C. D., Raghavan, P., & Schütze, H. *Introduction to Information Retrieval*. Cambridge University Press
- Scikit-learn documentation: [https://scikit-learn.org](https://scikit-learn.org)
- NLTK documentation: [https://www.nltk.org](https://www.nltk.org)
- PyPDF2: [https://github.com/py-pdf/PyPDF2](https://github.com/py-pdf/PyPDF2)
- “Levenshtein Distance Explained” – Towards Data Science, Medium
- GitHub Repositories for Text Similarity Algorithms
- Turnitin and Grammarly Official Sites

