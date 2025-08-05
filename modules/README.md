# SCALAR Modules

This directory contains the core modules used in the SCALAR (Semantic Clustering and Labeling for Sector Classification of Crowd-Based Software Requirements) system.

## Module Overview

### `text_preprocessing.py`
- Handles text cleaning, tokenization, and normalization
- Removes stopwords, punctuation, and applies lemmatization
- Used as the first step in the processing pipeline

### `wikipedia_extractor.py`
- Extracts relevant knowledge from Wikipedia based on domain descriptions
- Identifies key terms in class descriptions and fetches related Wikipedia articles
- Creates a knowledge corpus for each domain/class

### `embedding_generator.py`
- Generates vector embeddings using pre-trained language models
- Supports multiple embedding types (sentence-bert, sentence-roberta)
- Includes fallback mechanisms when models fail to load

### `clustering.py`
- Implements clustering algorithms (KMeans, HAC, GMM, BIRCH)
- Assigns labels to clusters by comparing with Wikipedia knowledge embeddings
- Includes enhanced greedy allocation for optimal cluster-label assignment

### `visualization.py`
- Creates visualizations for clustering results
- Plots cluster distributions, similarity matrices, and cluster sizes
- Provides visual analysis tools for interpreting results

### `bertopic_interpreter.py`
- Performs topic modeling on clusters using BERTopic
- Extracts key topics and terms from each cluster
- Visualizes topic hierarchies and distributions

## Pipeline Flow

### `main.py` Pipeline:
1. **Data Loading**: Loads input data from a CSV file
2. **Wikipedia Knowledge Extraction**: Gathers domain-specific knowledge from Wikipedia
3. **Embedding Generation**: Creates embeddings for both documents and Wikipedia texts
4. **Clustering**: Performs clustering and assigns domain labels
5. **Visualization**: Generates visualizations of clustering results
6. **BERTopic Analysis**: (Optional) Performs in-depth topic analysis on each cluster

### `app.py` Pipeline:
1. **File Upload**: Accepts CSV file uploads through a web interface
2. **Parameter Configuration**: Collects user parameters for analysis
3. **Background Analysis**: Runs the analysis pipeline in a background thread
4. **Visualization Generation**: Creates interactive visualizations for the web interface
5. **Result Presentation**: Displays clustering and topic results in the web interface
6. **Result Download**: Allows downloading of analysis results in CSV and JSON formats

## Usage
These modules can be used either through the command-line interface (`main.py`) or the web application (`app.py`). Both interfaces provide access to the same underlying functionality. 