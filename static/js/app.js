
document.addEventListener('DOMContentLoaded', function() {
  // DOM elements
  const tabButtons = document.querySelectorAll('.tab-button');
  const tabContents = document.querySelectorAll('.tab-content');
  const uploadForm = document.getElementById('upload-form');
  const fileInput = document.getElementById('file-input');
  const dropZone = document.getElementById('drop-zone');
  const browseButton = document.getElementById('browse-button');
  const fileDetails = document.getElementById('file-details');
  const filename = document.getElementById('filename');
  const removeFileButton = document.getElementById('remove-file');
  const uploadButton = document.getElementById('upload-button');
  const uploadError = document.getElementById('upload-error');
  const parametersForm = document.getElementById('parameters-form');
  const backToUploadButton = document.getElementById('back-to-upload');
  const analyzeButton = document.getElementById('analyze-button');
  const numClustersSelect = document.getElementById('num-clusters');
  const backToParametersButton = document.getElementById('back-to-parameters');
  const newAnalysisButton = document.getElementById('new-analysis');
  const loadingIndicator = document.getElementById('loading-indicator');
  const resultsContent = document.getElementById('results-content');
  const resultsError = document.getElementById('results-error');
  const errorMessage = document.getElementById('error-message');
  const classDescriptionsContainer = document.getElementById('class-descriptions');
  const downloadCsvButton = document.getElementById('download-csv');
  const downloadJsonButton = document.getElementById('download-json');
  const retryButton = document.getElementById('retry-button');

  // Tab functionality
  function switchTab(tabId) {
    tabButtons.forEach(button => {
      button.classList.remove('active');
      if (button.dataset.tab === tabId) {
        button.classList.add('active');
      }
    });

    tabContents.forEach(content => {
      content.classList.remove('active');
      if (content.id === `${tabId}-tab`) {
        content.classList.add('active');
      }
    });
  }

  tabButtons.forEach(button => {
    button.addEventListener('click', function() {
      if (!this.disabled) {
        switchTab(this.dataset.tab);
      }
    });
  });

  // File upload handling
  browseButton.addEventListener('click', () => {
    fileInput.click();
  });

  fileInput.addEventListener('change', handleFileSelect);

  function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
      displayFileDetails(file);
    }
  }

  function displayFileDetails(file) {
    if (file.type !== 'text/csv' && !file.name.endsWith('.csv')) {
      showUploadError('Please select a CSV file');
      return;
    }

    uploadError.textContent = '';
    filename.textContent = file.name;
    fileDetails.classList.remove('hidden');
    uploadButton.disabled = false;
  }

  removeFileButton.addEventListener('click', () => {
    fileInput.value = '';
    fileDetails.classList.add('hidden');
    uploadButton.disabled = true;
    uploadError.textContent = '';
  });

  // Drag and drop functionality
  ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, preventDefaults, false);
  });

  function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
  }

  ['dragenter', 'dragover'].forEach(eventName => {
    dropZone.addEventListener(eventName, () => {
      dropZone.classList.add('dragover');
    }, false);
  });

  ['dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, () => {
      dropZone.classList.remove('dragover');
    }, false);
  });

  dropZone.addEventListener('drop', handleDrop, false);

  function handleDrop(e) {
    const file = e.dataTransfer.files[0];
    if (file) {
      fileInput.files = e.dataTransfer.files;
      displayFileDetails(file);
    }
  }

  function showUploadError(message) {
    uploadError.textContent = message;
    fileDetails.classList.add('hidden');
    uploadButton.disabled = true;
  }

  // Upload form submission
  uploadForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    if (!fileInput.files[0]) {
      showUploadError('Please select a file');
      return;
    }

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    try {
      uploadButton.disabled = true;
      uploadButton.textContent = 'Uploading...';
      
      const response = await fetchWithTimeout('/upload', {
        method: 'POST',
        body: formData
      }, 60000); // 60 second timeout
      
      const data = await response.json();
      
      if (data.success) {
        // Enable parameters tab
        document.querySelector('.tab-button[data-tab="parameters"]').disabled = false;
        switchTab('parameters');
        generateClassDescriptionFields(parseInt(numClustersSelect.value));
      } else {
        showUploadError(data.error || 'Error uploading file');
      }
    } catch (error) {
      console.error('Upload error:', error);
      showUploadError(error.message || 'Network error, please try again');
    } finally {
      uploadButton.disabled = false;
      uploadButton.textContent = 'Upload & Continue';
    }
  });

  // Helper function for fetch with timeout
  async function fetchWithTimeout(url, options = {}, timeout = 30000) {
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), timeout);
    
    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal
      });
      clearTimeout(id);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `Server error: ${response.status}`);
      }
      
      return response;
    } catch (error) {
      clearTimeout(id);
      if (error.name === 'AbortError') {
        throw new Error('Request timed out. The server may be processing a large dataset or is overloaded.');
      }
      throw error;
    }
  }

  // Generate class description fields
  function generateClassDescriptionFields(numClusters) {
    classDescriptionsContainer.innerHTML = '';
    
    for (let i = 0; i < numClusters; i++) {
      const fieldHTML = `
        <div class="class-description-field">
          <div class="form-row">
            <div class="form-group half">
              <label for="class-name-${i}">Class ${i+1} Name</label>
              <input type="text" id="class-name-${i}" name="class_name_${i}" required placeholder="e.g., Computer Science">
            </div>
            <div class="form-group half">
              <label for="class-desc-${i}">Class ${i+1} Description</label>
              <input type="text" id="class-desc-${i}" name="class_desc_${i}" required placeholder="e.g., Computing theory and applications">
            </div>
          </div>
        </div>
      `;
      
      classDescriptionsContainer.insertAdjacentHTML('beforeend', fieldHTML);
    }
  }

  // Update class description fields when num clusters changes
  numClustersSelect.addEventListener('change', function() {
    generateClassDescriptionFields(parseInt(this.value));
  });

  // Navigation buttons
  backToUploadButton.addEventListener('click', () => {
    switchTab('upload');
  });

  backToParametersButton.addEventListener('click', () => {
    switchTab('parameters');
  });

  // Add retry button functionality if it exists
  if (retryButton) {
    retryButton.addEventListener('click', () => {
      runAnalysis();
    });
  }

  newAnalysisButton.addEventListener('click', () => {
    // Reset all forms and switch to upload tab
    uploadForm.reset();
    parametersForm.reset();
    fileDetails.classList.add('hidden');
    uploadButton.disabled = true;
    resultsContent.classList.add('hidden');
    resultsError.classList.add('hidden');
    document.querySelector('.tab-button[data-tab="results"]').disabled = true;
    switchTab('upload');
  });

  // Parameters form submission
  parametersForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    await saveParameters();
    await runAnalysis();
  });

  async function saveParameters() {
    // Collect parameters
    const formData = new FormData(parametersForm);
    const params = {
      embedding_type: formData.get('embedding_type'),
      clustering_method: formData.get('clustering_method'),
      num_clusters: parseInt(formData.get('num_clusters')),
      min_wiki_pages: parseInt(formData.get('min_wiki_pages')),
      use_bertopic: formData.get('use_bertopic') === 'on',
      class_descriptions: {}
    };
    
    // Collect class descriptions
    const numClusters = parseInt(formData.get('num_clusters'));
    for (let i = 0; i < numClusters; i++) {
      const className = formData.get(`class_name_${i}`);
      const classDesc = formData.get(`class_desc_${i}`);
      
      if (!className || !classDesc) {
        showParametersError('Please fill in all class names and descriptions');
        return false;
      }
      
      params.class_descriptions[className] = classDesc;
    }
    
    try {
      // Save parameters
      const saveResponse = await fetchWithTimeout('/set-parameters', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(params)
      }, 30000);
      
      const saveData = await saveResponse.json();
      
      if (!saveData.success) {
        showParametersError(saveData.error || 'Error saving parameters');
        return false;
      }
      
      return true;
    } catch (error) {
      console.error('Parameters error:', error);
      showParametersError(error.message || 'Network error, please try again');
      return false;
    }
  }

  async function runAnalysis() {
    try {
      // Enable results tab and switch to it
      document.querySelector('.tab-button[data-tab="results"]').disabled = false;
      switchTab('results');
      
      // Show loading indicator
      loadingIndicator.classList.remove('hidden');
      resultsContent.classList.add('hidden');
      resultsError.classList.add('hidden');
      
      // Run analysis
      analyzeButton.disabled = true;
      analyzeButton.textContent = 'Running Analysis...';
      
      const analysisResponse = await fetchWithTimeout('/run-analysis', {
        method: 'POST'
      }, 300000); // 5 minute timeout for analysis
      
      const analysisData = await analysisResponse.json();
      
      if (analysisData.success) {
        // Fetch results
        await fetchAndDisplayResults();
      } else {
        // Show error
        resultsError.classList.remove('hidden');
        errorMessage.textContent = analysisData.error || 'Error during analysis';
      }
    } catch (error) {
      console.error('Analysis error:', error);
      resultsError.classList.remove('hidden');
      errorMessage.textContent = error.message || 'Network error, please try again';
    } finally {
      loadingIndicator.classList.add('hidden');
      analyzeButton.disabled = false;
      analyzeButton.textContent = 'Run Analysis';
    }
  }

  // Fetch and display results
  async function fetchAndDisplayResults() {
    try {
      const response = await fetchWithTimeout('/results', {}, 30000);
      const data = await response.json();
      
      if (data.success && data.results) {
        displayResults(data.results);
      } else {
        throw new Error(data.error || 'Failed to load results');
      }
    } catch (error) {
      console.error('Results error:', error);
      resultsError.classList.remove('hidden');
      errorMessage.textContent = error.message || 'Error loading results';
    }
  }

  function displayResults(results) {
    resultsContent.classList.remove('hidden');
    
    // Cluster distribution
    displayClusterDistribution(results.cluster_distribution);
    
    // Visualizations
    displayVisualizations(results.visualizations);
    
    // BERTopic results
    displayBERTopicResults(results.bertopic_results);
    
    // Set download links
    downloadCsvButton.href = '/download-results';
    downloadJsonButton.href = '/download-json';
  }

  function displayClusterDistribution(distribution) {
    const container = document.getElementById('cluster-distribution');
    
    if (!distribution || Object.keys(distribution).length === 0) {
      container.innerHTML = '<p>No cluster distribution data available</p>';
      return;
    }
    
    let tableHTML = `
      <table class="cluster-table">
        <thead>
          <tr>
            <th>Label</th>
            <th>Count</th>
            <th>Percentage</th>
          </tr>
        </thead>
        <tbody>
    `;
    
    Object.entries(distribution).forEach(([label, data]) => {
      tableHTML += `
        <tr>
          <td>${label}</td>
          <td>${data.count}</td>
          <td>${(data.percentage * 100).toFixed(1)}%</td>
        </tr>
      `;
    });
    
    tableHTML += `
        </tbody>
      </table>
    `;
    
    container.innerHTML = tableHTML;
  }

  function displayVisualizations(visualizations) {
    if (!visualizations) return;
    
    // Cluster visualization
    if (visualizations.cluster_viz) {
      const container = document.getElementById('cluster-viz-container');
      container.innerHTML = `<img src="data:image/png;base64,${visualizations.cluster_viz}" alt="Cluster Visualization">`;
    }
    
    // Similarity matrix
    if (visualizations.similarity_matrix) {
      const container = document.getElementById('similarity-matrix-container');
      container.innerHTML = `<img src="data:image/png;base64,${visualizations.similarity_matrix}" alt="Similarity Matrix">`;
    }
    
    // Cluster sizes
    if (visualizations.cluster_sizes) {
      const container = document.getElementById('cluster-sizes-container');
      container.innerHTML = `<img src="data:image/png;base64,${visualizations.cluster_sizes}" alt="Cluster Sizes">`;
    }
  }

  function displayBERTopicResults(bertopicResults) {
    const container = document.getElementById('bertopic-results');
    const summariesContainer = document.getElementById('topic-summaries');
    
    if (!bertopicResults || !bertopicResults.topic_summaries || Object.keys(bertopicResults.topic_summaries).length === 0) {
      container.classList.add('hidden');
      return;
    }
    
    container.classList.remove('hidden');
    summariesContainer.innerHTML = '';
    
    // Display topic summaries
    Object.entries(bertopicResults.topic_summaries).forEach(([clusterId, summaries]) => {
      const cardHTML = `
        <div class="topic-card">
          <h4>Cluster ${clusterId}</h4>
          <ul>
            ${summaries.map(summary => `<li>${summary}</li>`).join('')}
          </ul>
        </div>
      `;
      
      summariesContainer.insertAdjacentHTML('beforeend', cardHTML);
    });
  }

  function showParametersError(message) {
    alert(message);
  }

  // Initialize the first tab
  switchTab('upload');
});
