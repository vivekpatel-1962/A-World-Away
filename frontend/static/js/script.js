document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const analyzeBtn = document.getElementById('analyze-btn');
    const fileInfo = document.getElementById('file-info');
    const previewContainer = document.getElementById('preview-container');
    const imagePreview = document.getElementById('image-preview');
    const manualForm = document.getElementById('manual-form');
    const resultContainer = document.getElementById('result');
    
    let selectedFile = null;
    const API_BASE_URL = 'http://localhost:3000/api';

    // Check backend health on load
    checkBackendHealth();

    // Tab Switching
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            tabBtns.forEach(b => b.classList.remove('active'));
            tabPanes.forEach(p => p.classList.remove('active'));
            
            btn.classList.add('active');
            const tabId = btn.getAttribute('data-tab');
            document.getElementById(tabId).classList.add('active');
            
            clearResults();
        });
    });

    // Drag and Drop Functionality
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.style.borderColor = '#6c63ff';
            dropZone.style.background = 'rgba(108, 99, 255, 0.1)';
        });
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.style.borderColor = 'rgba(108, 99, 255, 0.5)';
            dropZone.style.background = 'rgba(15, 14, 26, 0.3)';
        });
    });

    // File Handling
    dropZone.addEventListener('drop', handleDrop);
    dropZone.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', handleFileSelect);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    }

    function handleFileSelect(e) {
        const files = e.target.files;
        handleFiles(files);
    }

    function handleFiles(files) {
        if (files.length > 0) {
            selectedFile = files[0];
            fileInfo.textContent = selectedFile.name;
            analyzeBtn.disabled = false;
            
            const reader = new FileReader();
            reader.onload = function(e) {
                imagePreview.src = e.target.result;
                imagePreview.style.display = 'block';
                previewContainer.style.display = 'block';
            };
            reader.readAsDataURL(selectedFile);
        }
    }

    // Check Backend Health
    async function checkBackendHealth() {
        try {
            const response = await fetch(`${API_BASE_URL}/health`);
            const data = await response.json();
            if (!data.status === 'ok') {
                showResult('Warning', 'Some models or services might not be available', 'warning');
            }
        } catch (error) {
            showResult('Error', 'Could not connect to the backend server', 'error');
        }
    }

    // Analyze Image
    analyzeBtn.addEventListener('click', analyzeImage);

    async function analyzeImage() {
        if (!selectedFile) return;
        
        showLoading('Analyzing light curve...');
        
        const formData = new FormData();
        formData.append('file', selectedFile);

        try {
            const response = await fetch(`${API_BASE_URL}/predict/image`, {
                method: 'POST',
                body: formData
            });

            const result = await response.json();
            
            if (response.ok) {
                const isExoplanet = result.prediction === 1;
                const confidence = isExoplanet ? 
                    result.confidence.exoplanet.toFixed(2) : 
                    result.confidence.no_exoplanet.toFixed(2);
                
                showResult(
                    isExoplanet ? 'Exoplanet Detected!' : 'No Exoplanet Detected',
                    `Confidence: ${confidence}%`,
                    isExoplanet ? 'success' : 'info'
                );
            } else {
                throw new Error(result.error || 'Failed to analyze image');
            }
        } catch (error) {
            showResult('Error', error.message, 'error');
        }
    }

    // Manual Form Submission
    manualForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        showLoading('Analyzing features...');
        
        const formData = new FormData(manualForm);
        const data = {};
        formData.forEach((value, key) => {
            data[key] = parseFloat(value) || 0;
        });

        try {
            const response = await fetch(`${API_BASE_URL}/predict/features`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();
            
            if (response.ok) {
                showResult(
                    result.is_exoplanet ? 'Exoplanet Likely!' : 'No Clear Exoplanet',
                    `Prediction score: ${(result.prediction * 100).toFixed(2)}%`,
                    result.is_exoplanet ? 'success' : 'info'
                );
            } else {
                throw new Error(result.error || 'Failed to analyze features');
            }
        } catch (error) {
            showResult('Error', error.message, 'error');
        }
    });

    // Helper Functions
    function showLoading(message) {
        resultContainer.innerHTML = `
            <div class="loading">
                <div class="spinner"></div>
                <p>${message}</p>
            </div>
        `;
        resultContainer.style.display = 'block';
    }

    function showResult(title, message, type = 'info') {
        const icon = type === 'error' ? '❌' : type === 'success' ? '✅' : 'ℹ️';
        resultContainer.innerHTML = `
            <div class="result ${type}">
                <div class="result-icon">${icon}</div>
                <div class="result-content">
                    <h3>${title}</h3>
                    <p>${message}</p>
                </div>
            </div>
        `;
        resultContainer.style.display = 'block';
    }

    function clearResults() {
        resultContainer.style.display = 'none';
        resultContainer.innerHTML = '';
    }
});