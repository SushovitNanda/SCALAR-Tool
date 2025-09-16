# SCALAR: Semantic Clustering and Labeling Based Toolkit for Classification of Crowd-Based Software Requirements

## Project Overview

SCALAR is a tool for analyzing and clustering software requirements, helping researchers and developers explore and categorize crowd-based software requirements efficiently.

## Prerequisites

Before you begin, ensure you have the following installed:

### Windows
- Python 3.8 or higher
- pip (Python package manager)
- Active internet connection for Wikipedia data extraction

### Linux
- Python 3.8 or higher (`python3`)
- pip3 (Python package manager)
- Active internet connection for Wikipedia data extraction

**Installing Python on Linux:**
- **Ubuntu/Debian:** `sudo apt update && sudo apt install python3 python3-pip`
  
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
git clone https://github.com/SushovitNanda/scalar.git
cd scalar
```

### Install Dependencies

#### Windows
```cmd
pip install -r requirements.txt
```

#### Linux
```bash
# Option 1: Using the setup script (recommended)
chmod +x setup_linux.sh
./setup_linux.sh

# Option 2: Manual installation
python3 -m pip install -r requirements.txt
```

## Running the Application

### Method 1: Web Interface (Recommended)

#### Windows
You can start the application in two ways:

1. **Using Launch_app.bat (Automatic)**:
  Double-click the `Launch_app.bat` file to execute.

   This will:
   - Check system requirements
   - Check for dependencies
   - Start the Flask server
   - Open your default web browser automatically
   - Handle cleanup on exit

2. **Using app.py (Manual)**:
   ```cmd
   python app.py
   ```
   Then manually open your browser and navigate to:
   ```
   http://localhost:5000
   ```

#### Linux
You can start the application in several ways:

1. **Using setup_linux.sh (First-time setup)**:
   ```bash
   chmod +x setup_linux.sh
   ./setup_linux.sh
   ```
   This will:
   - Check system requirements
   - Check for dependencies
   - Make scripts executable
   - Optionally create a desktop shortcut
   - Provide instructions for running the application

2. **Using launch_app.sh (Automatic)**:
   ```bash
   chmod +x launch_app.sh
   ./launch_app.sh
   ```
   This will:
   - Check system requirements
   - Check for dependencies 
   - Start the Flask server
   - Open your default web browser automatically
   - Handle cleanup on exit

3. **Using app.py (Manual)**:
   ```bash
   python3 app.py
   ```
   Then manually open your browser and navigate to:
   ```
   http://localhost:5000
   ```

4. **Using launch_app.py (Cross-platform)**:
   ```bash
   python3 launch_app.py
   ```
   This works on both Windows and Linux systems.

### Method 2: Command Line Interface
For batch processing or script-based usage:

**Windows:**
```cmd
python main.py
```

**Linux:**
```bash
python3 main.py
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

## Extending the Tool: Adding More Embedding and Clustering Mechanisms

SCALAR is designed to be easily extensible, allowing users to add new embedding models and clustering algorithms. The tool already includes support for multiple methods, and adding new ones is straightforward.

### Current Supported Methods

#### Embedding Models
- **Sentence BERT**: Uses `sentence-transformers/all-MiniLM-L6-v2` (default)
- **Sentence RoBERTa**: Uses `sentence-transformers/all-distilroberta-v1`

#### Clustering Algorithms
- **K-Means**: Traditional centroid-based clustering
- **GMM (Gaussian Mixture Model)**: Probabilistic clustering
- **HAC (Hierarchical Agglomerative Clustering)**: Bottom-up hierarchical clustering (commented out)
- **BIRCH**: Memory-efficient hierarchical clustering (commented out)

### Quick Start for Extensions

**HAC and BIRCH clustering methods are already included in the module but arent implemented in the tool** and can be easily enabled or disabled by commenting/uncommenting lines in the frontend components. To modify which clustering options are available:

1. Open `src/components/ParameterForm.tsx`
2. Comment out any clustering methods you want to disable:
   ```typescript
   {/* <SelectItem value="hac">Hierarchical Clustering</SelectItem> */}
   {/* <SelectItem value="birch">BIRCH</SelectItem> */}
   ```
3. Uncomment to re-enable them

### Detailed Extension Guide

For comprehensive instructions on adding new embedding models and clustering algorithms, including:
- Step-by-step implementation guides
- Code examples for both frontend and backend modifications
- Best practices for maintaining code quality
- Complete examples (e.g., adding DBSCAN clustering)

**See the detailed documentation in [modules/README.md](modules/README.md)**

This extensible design allows researchers and developers to easily experiment with different embedding and clustering approaches for their specific use cases.

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

## Additional Documentation

- **[Linux Installation Guide](INSTALL_LINUX.md)** - Detailed instructions for Linux users
- **[Software Structure](modules/README.md)** - Information about the modules and their functionality
- **[License](LICENSE)**

## Troubleshooting

### Common Issues

#### Windows
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

#### Linux
1. **Permission Issues**:
   - Make scripts executable: `chmod +x *.sh`
   - Ensure you have write permissions in the directory
   - Run setup script as regular user (not root)

2. **Python Command Issues**:
   - Use `python3` instead of `python` if both are installed
   - Ensure Python 3.8+ is installed: `python3 --version`
   - Install pip if missing: `sudo apt install python3-pip`

3. **Dependency Problems**:
   - Run `python3 -m pip install -r requirements.txt`
   - Use virtual environment: `python3 -m venv venv && source venv/bin/activate`
   - Clear pip cache: `python3 -m pip cache purge`

4. **Browser Issues**:
   - Some Linux distributions may not have a default browser
   - Manually open: `http://localhost:5000`
   - Install a browser if needed: `sudo apt install firefox`

### Getting Help
- Check the terminal output where the Flask server is running
- Review the application logs in the terminal
- Ensure all Python dependencies are installed correctly
- Verify you're using compatible versions of Python (3.8+)
- Make sure you have an active internet connection for Wikipedia data extraction

### Quick Start Commands

#### Windows
```cmd
# Clone and setup
git clone https://github.com/SushovitNanda/scalar.git
cd scalar
pip install -r requirements.txt

# Run application
Launch_app.bat
```

#### Linux
```bash
# Clone and setup
git clone https://github.com/SushovitNanda/scalar.git
cd scalar
chmod +x setup_linux.sh
./setup_linux.sh

# Run application
./launch_app.sh
```

