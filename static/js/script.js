document.addEventListener('DOMContentLoaded', function() {
    // Form submission for text input
    const textForm = document.getElementById('text-form');
    textForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(textForm);
        submitTextForm(formData);
    });

    // Form submission for file upload
    const fileForm = document.getElementById('file-form');
    fileForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(fileForm);
        submitFileForm(formData);
    });

    // Download report button
    const downloadReportBtn = document.getElementById('download-report-btn');
    downloadReportBtn.addEventListener('click', function(e) {
        e.preventDefault();
        if (this.getAttribute('href') !== '#') {
            window.location.href = this.getAttribute('href');
        }
    });
});

/**
 * Submit text form for plagiarism check
 */
function submitTextForm(formData) {
    // Show loading spinner
    const spinner = document.getElementById('text-spinner');
    spinner.classList.remove('d-none');
    
    // Disable submit button
    const submitBtn = document.getElementById('check-text-btn');
    submitBtn.disabled = true;

    fetch('/check-text', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        // Hide loading spinner
        spinner.classList.add('d-none');
        submitBtn.disabled = false;
        
        // Display results
        displayResults(data);
    })
    .catch(error => {
        // Hide loading spinner
        spinner.classList.add('d-none');
        submitBtn.disabled = false;
        
        // Show error
        alert('Error: ' + error.message);
    });
}

/**
 * Submit file form for plagiarism check
 */
function submitFileForm(formData) {
    // Show loading spinner
    const spinner = document.getElementById('file-spinner');
    spinner.classList.remove('d-none');
    
    // Disable submit button
    const submitBtn = document.getElementById('check-file-btn');
    submitBtn.disabled = true;

    fetch('/check-files', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        // Hide loading spinner
        spinner.classList.add('d-none');
        submitBtn.disabled = false;
        
        // Display results
        displayResults(data);
    })
    .catch(error => {
        // Hide loading spinner
        spinner.classList.add('d-none');
        submitBtn.disabled = false;
        
        // Show error
        alert('Error: ' + error.message);
    });
}

/**
 * Display plagiarism check results
 */
function displayResults(data) {
    // Show results card
    const resultsCard = document.getElementById('results-card');
    resultsCard.classList.remove('d-none');
    
    // Update similarity scores
    document.getElementById('average-similarity').textContent = data.similarity_scores.average_similarity;
    
    // Update plagiarism level
    const plagiarismLevel = document.getElementById('plagiarism-level');
    plagiarismLevel.textContent = data.plagiarism_level;
    
    // Update badge color based on plagiarism level
    plagiarismLevel.className = 'badge';
    switch (data.plagiarism_level) {
        case 'Low':
            plagiarismLevel.classList.add('bg-success');
            break;
        case 'Moderate':
            plagiarismLevel.classList.add('bg-warning');
            break;
        case 'High':
            plagiarismLevel.classList.add('bg-danger');
            break;
        case 'Very High':
            plagiarismLevel.classList.add('bg-dark');
            break;
    }
    
    // Set download report link
    document.getElementById('download-report-btn').setAttribute('href', '/download-report/' + encodeURIComponent(data.report_path));
    
    // Create charts
    createGaugeChart(parseFloat(data.similarity_scores.average_similarity));
    createSimilarityChart(data.similarity_scores);
    
    // Display matched content
    displayMatchedContent(data.highlighted_content);
    
    // Scroll to results
    resultsCard.scrollIntoView({ behavior: 'smooth' });
}

/**
 * Create gauge chart for similarity score
 */
function createGaugeChart(averageScore) {
    // Parse percentage value
    let score = averageScore;
    if (typeof averageScore === 'string') {
        score = parseFloat(averageScore.replace('%', ''));
    }
    
    // Destroy existing chart if it exists
    const gaugeCanvas = document.getElementById('similarity-gauge');
    if (gaugeCanvas._chart) {
        gaugeCanvas._chart.destroy();
    }
    
    // Create new chart
    const gaugeChart = new Chart(gaugeCanvas, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [score, 100 - score],
                backgroundColor: [getColorForScore(score), '#e9ecef'],
                borderWidth: 0
            }]
        },
        options: {
            cutout: '80%',
            circumference: 180,
            rotation: 270,
            plugins: {
                tooltip: {
                    enabled: false
                },
                legend: {
                    display: false
                }
            },
            responsive: true,
            maintainAspectRatio: true,
            aspectRatio: 2
        }
    });
    
    // Save chart instance
    gaugeCanvas._chart = gaugeChart;
}

/**
 * Create similarity metrics chart
 */
function createSimilarityChart(similarityScores) {
    // Parse percentage values
    let cosineScore = parseFloat(similarityScores.cosine_similarity.replace('%', ''));
    let jaccardScore = parseFloat(similarityScores.jaccard_similarity.replace('%', ''));
    
    // Destroy existing chart if it exists
    const chartCanvas = document.getElementById('similarity-chart');
    if (chartCanvas._chart) {
        chartCanvas._chart.destroy();
    }
    
    // Create new chart
    const metricsChart = new Chart(chartCanvas, {
        type: 'bar',
        data: {
            labels: ['Pattern Analysis', 'Content Analysis'],
            datasets: [{
                label: 'Plagiarism Score (%)',
                data: [cosineScore, jaccardScore],
                backgroundColor: [
                    'rgba(54, 162, 235, 0.7)',
                    'rgba(255, 159, 64, 0.7)'
                ],
                borderColor: [
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 159, 64, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
    
    // Save chart instance
    chartCanvas._chart = metricsChart;
}

/**
 * Display matched content from the report
 */
function displayMatchedContent(highlightedContent) {
    const matchesContainer = document.getElementById('matches-container');
    matchesContainer.innerHTML = '';
    
    if (!highlightedContent || highlightedContent.length === 0) {
        matchesContainer.innerHTML = '<p class="text-center">No significant potential plagiarism detected.</p>';
        return;
    }
    
    // Create elements for each match
    highlightedContent.forEach((match, index) => {
        const matchItem = document.createElement('div');
        matchItem.className = 'match-item';
        
        const similarityPercentage = (match.similarity_ratio * 100).toFixed(2);
        
        matchItem.innerHTML = `
            <div>
                <h6>Potential Plagiarism #${index + 1} <span class="match-percentage">(${similarityPercentage}% likelihood)</span></h6>
                <div class="row">
                    <div class="col-md-12">
                        <p><strong>Suspicious Text:</strong></p>
                        <div class="match-text">${match.suspicious_sentence}</div>
                        <p class="mt-2"><strong>Note:</strong></p>
                        <div class="match-text" style="border-left-color: #6c757d;">${match.original_sentence}</div>
                    </div>
                </div>
            </div>
        `;
        
        matchesContainer.appendChild(matchItem);
    });
}

/**
 * Get color based on similarity score
 */
function getColorForScore(score) {
    if (score < 20) {
        return '#198754'; // Success/Green for low plagiarism
    } else if (score < 40) {
        return '#ffc107'; // Warning/Yellow for moderate plagiarism
    } else if (score < 60) {
        return '#dc3545'; // Danger/Red for high plagiarism
    } else {
        return '#6c757d'; // Dark/Gray for very high plagiarism
    }
} 