# SCALAR: Semantic Clustering and Labeling Based Toolkit for Classification of Crowd-Based Software Requirements

## Project Overview

SCALAR is a tool for analyzing and clustering software requirements, helping researchers and developers explore and categorize crowd-based software requirements efficiently.

## Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.8 or higher
- pip (Python package manager)
- Active internet connection for Wikipedia data extraction

## Project Structure

The project consists of several key Python files:

1. **app.py**: The main Flask web application that provides the user interface and handles all web-based interactions. It manages:
   - File uploads
   - Parameter configuration
   - Analysis execution
   - Results visualization
   - Session management

2. **main.py**: A command-line interface version of the tool that allows for direct execution without the web interface. It provides:
   - Interactive command-line prompts
   - Direct parameter input
   - Batch processing capabilities
   - Console-based results output

3. **launch_app.py**: An automated launcher script that:
   - Checks system requirements
   - Installs dependencies
   - Starts the Flask server
   - Opens the web browser automatically
   - Handles error cases and cleanup

## Installation

### Clone the Repository
```bash
git clone https://github.com/SushovitNanda/sclara.git
cd sclara
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

## Running the Application

### Method 1: Web Interface (Recommended)
You can start the application in two ways:

1. **Using Launch_app.bat (Automatic)**:
  Double-click the Launch_app.bat application to execute.

   This will:
   - Check system requirements
   - Install dependencies if needed
   - Start the Flask server
   - Open your default web browser automatically
   - Handle cleanup on exit

2. **Using app.py (Manual)**:
   ```bash
   python app.py
   ```
   Then manually open your browser and navigate to:
   ```
   http://localhost:5000
   ```

### Method 2: Command Line Interface
For batch processing or script-based usage:
```bash
python main.py
```
This will prompt you for:
- Input file path
- Embedding type
- Clustering method
- Number of clusters
- BERTopic analysis preferences
- Class descriptions

## How to Use the Tool

1. **Upload Data**: Start by uploading your CSV file containing research topics.
2. **Configure Parameters**: Set embedding type, clustering method, and class definitions.
3. **Run Analysis**: Begin the analysis process and wait for the results.
4. **Explore Results**: View visualizations and download the analysis results.

## Key Features
- Wikipedia-based research topic analysis
- Configurable embedding and clustering methods
- Visualization of document clusters
- Export of analysis results
- Both web and command-line interfaces
- Automated dependency management
- Session persistence
- Error handling and logging

## Technologies Used
- Python
  - Flask for web server
  - NLTK for text preprocessing
  - Wikipedia API for data extraction
  - Sentence Transformers for embeddings
  - BERTopic for topic modeling
  - Scikit-learn for clustering
  - Matplotlib for visualizations
- HTML/CSS for the user interface

## Troubleshooting

### Common Issues
1. **Server Connection Issues**:
   - Ensure no other application is using port 5000
   - Check your firewall settings
   - Verify internet connectivity

2. **Dependency Problems**:
   - Run `pip install -r requirements.txt` again
   - Check Python version compatibility
   - Clear pip cache if needed: `pip cache purge`

3. **File Upload Issues**:
   - Ensure CSV file is properly formatted
   - Check file size (max 16MB)
   - Verify file encoding (UTF-8 recommended)

4. **Analysis Errors**:
   - Check terminal output for detailed error messages
   - Verify internet connection for Wikipedia API
   - Ensure sufficient system memory

### Getting Help
- Check the terminal output where the Flask server is running
- Review the application logs in the terminal
- Ensure all Python dependencies are installed correctly
- Verify you're using compatible versions of Python (3.8+)
- Make sure you have an active internet connection for Wikipedia data extraction
