import os
import sys
import json
import base64
import tempfile
import io
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file, make_response, session
from werkzeug.utils import secure_filename
import pandas as pd
import pickle
import threading

# Import the analysis modules
from modules.text_preprocessing import TextPreprocessor
from modules.wikipedia_extractor import WikiCorpusExtractor
from modules.embedding_generator import EmbeddingGenerator
from modules.bertopic_interpreter import BERTopicInterpreter
from modules.clustering import cluster_and_assign_labels
import modules.visualization as vis
from collections import Counter
import logging

# Configure Flask app
app = Flask(__name__, 
            static_url_path='', 
            static_folder='static',
            template_folder='templates')

app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size
app.config['SECRET_KEY'] = os.urandom(24)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Global session storage (in a real app, you'd use Flask session or a database)
session_data = {
    'uploaded_file': None,
    'class_descriptions': {},
    'parameters': {},
    'results': None
}

# Persistent file to store session data in case of server reload
SESSION_FILE = os.path.join(app.config['UPLOAD_FOLDER'], 'session_data.pkl')

# Function to save session data
def save_session():
    try:
        with open(SESSION_FILE, 'wb') as f:
            pickle.dump(session_data, f)
        logger.info("Session data saved to disk")
    except Exception as e:
        logger.error(f"Failed to save session: {str(e)}")

# Function to load session data
def load_session():
    global session_data
    try:
        if os.path.exists(SESSION_FILE):
            with open(SESSION_FILE, 'rb') as f:
                session_data = pickle.load(f)
            logger.info("Session data loaded from disk")
    except Exception as e:
        logger.error(f"Failed to load session: {str(e)}")

# Load session on startup
load_session()

# Enable CORS for all routes
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    return response

@app.route('/')
def index():
    """Render the main application page."""
    return render_template('index.html')

@app.route('/upload', methods=['POST', 'OPTIONS'])
def upload_file():
    """Handle file upload."""
    if request.method == 'OPTIONS':
        return make_response('', 200)
    
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        if file and file.filename.endswith('.csv'):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            session_data['uploaded_file'] = filepath
            # Save session after file upload
            save_session()
            logger.info(f"File uploaded successfully: {filename}")
            return jsonify({'success': True, 'filename': filename})
        else:
            return jsonify({'error': 'File must be a CSV'}), 400
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@app.route('/set-parameters', methods=['POST', 'OPTIONS'])
def set_parameters():
    """Save analysis parameters, supporting both descriptions and file uploads for class labels."""
    if request.method == 'OPTIONS':
        return make_response('', 200)
    try:
        # Accept both JSON and multipart/form-data
        if request.content_type and request.content_type.startswith('multipart/form-data'):
            form = request.form
            files = request.files
            # Parse class label data
            labels = []
            i = 0
            while True:
                name_key = f'labels[{i}][name]'
                desc_key = f'labels[{i}][description]'
                file_key = f'labels[{i}][file]'
                if name_key not in form:
                    break
                label = {
                    'name': form.get(name_key).strip(),
                    'description': form.get(desc_key, '').strip(),
                    'file': files.get(file_key)
                }
                labels.append(label)
                i += 1
        elif request.is_json:
            # Fallback for JSON (legacy)
            data = request.json
            labels = []
            for name, description in data.get('class_descriptions', {}).items():
                labels.append({'name': name, 'description': description, 'file': None})
        else:
            return jsonify({'error': 'Request must be multipart/form-data or JSON'}), 400

        if not labels or all(not l['name'] for l in labels):
            return jsonify({'error': 'No class labels provided'}), 400

        # Store parameters
        embedding_type = request.form.get('embedding_type', 'sentence-bert') if request.form else request.json.get('embedding_type', 'sentence-bert')
        clustering_method = request.form.get('clustering_method', 'kmeans') if request.form else request.json.get('clustering_method', 'kmeans')
        # Accept 'hac' and 'birch' as valid options
        if clustering_method not in ['kmeans', 'hac', 'gmm', 'birch']:
            clustering_method = 'kmeans'
        num_clusters = int(request.form.get('num_clusters', 2)) if request.form else int(request.json.get('num_clusters', 2))
        min_wiki_pages = int(request.form.get('min_wiki_pages', 3)) if request.form else int(request.json.get('min_wiki_pages', 3))
        use_bertopic = request.form.get('use_bertopic', 'true') if request.form else request.json.get('use_bertopic', True)
        if isinstance(use_bertopic, str):
            use_bertopic = use_bertopic.lower() == 'true'
        session_data['parameters'] = {
            'embedding_type': embedding_type,
            'clustering_method': clustering_method,
            'num_clusters': num_clusters,
            'min_wiki_pages': min_wiki_pages,
            'use_bertopic': use_bertopic
        }

        # Prepare class corpora: for each label, if file is present, preprocess and use as corpus; else use description
        class_corpora = {}
        class_descriptions = {}
        preprocessor = TextPreprocessor()
        for label in labels:
            label_name = label['name']
            file = label['file']
            description = label['description']
            corpus_text = None
            if file and file.filename:
                # Save file to temp, read and preprocess
                ext = os.path.splitext(file.filename)[1].lower()
                temp_path = os.path.join(app.config['UPLOAD_FOLDER'], f"label_{label_name}_{secure_filename(file.filename)}")
                file.save(temp_path)
                try:
                    if ext == '.csv':
                        df = pd.read_csv(temp_path, dtype=str).fillna("")
                        corpus_text = ' '.join(df.apply(lambda row: ' '.join(row.astype(str)), axis=1).tolist())
                    elif ext == '.json':
                        with open(temp_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        if isinstance(data, dict):
                            corpus_text = ' '.join(str(v) for v in data.values())
                        elif isinstance(data, list):
                            corpus_text = ' '.join(str(item) for item in data)
                        else:
                            corpus_text = str(data)
                    else:
                        corpus_text = file.read().decode('utf-8')
                    corpus_text = preprocessor.preprocess_text(corpus_text)
                    class_corpora[label_name] = corpus_text
                except Exception as e:
                    logger.error(f"Failed to process uploaded file for label {label_name}: {e}")
                    class_corpora[label_name] = None
            elif description:
                class_descriptions[label_name] = description
            else:
                class_descriptions[label_name] = ''  # No description or file, will use default
        session_data['class_corpora'] = class_corpora
        session_data['class_descriptions'] = class_descriptions
        save_session()
        logger.info(f"Parameters set: {session_data['parameters']}")
        logger.info(f"Class corpora: {list(class_corpora.keys())}")
        logger.info(f"Class descriptions: {session_data['class_descriptions']}")
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Parameter setup failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Parameter setup failed: {str(e)}'}), 500

# Background task for analysis to avoid timeout
def run_analysis_task():
    try:
        params = session_data['parameters']
        embedding_type = params.get('embedding_type', 'sentence-bert')
        clustering_method = params.get('clustering_method', 'kmeans')
        num_clusters = int(params.get('num_clusters', 2))
        min_wiki_pages = int(params.get('min_wiki_pages', 3))
        use_bertopic = params.get('use_bertopic', True)
        class_descriptions = session_data.get('class_descriptions', {})
        class_corpora = session_data.get('class_corpora', {})
        # Load data
        file_path = session_data['uploaded_file']
        df = pd.read_csv(file_path, dtype=str).fillna("")
        texts = df.apply(lambda row: ' '.join(row.astype(str)), axis=1).tolist()
        preprocessor = TextPreprocessor()
        processed_texts = [preprocessor.preprocess_text(text) for text in texts]
        # Prepare label corpora: use uploaded corpus if present, else Wikipedia extraction, else default
        label_corpus_texts = []
        label_names = []
        wiki_needed = {}
        for label in range(num_clusters):
            # Try to get label name from class_corpora or class_descriptions
            if class_corpora:
                # Use the order of class_corpora keys
                if label < len(class_corpora):
                    label_name = list(class_corpora.keys())[label]
                    label_names.append(label_name)
                    label_corpus_texts.append(class_corpora[label_name])
                    continue
            if class_descriptions:
                if label < len(class_descriptions):
                    label_name = list(class_descriptions.keys())[label]
                    label_names.append(label_name)
                    wiki_needed[label_name] = class_descriptions[label_name]
                    continue
            # Fallback
            label_name = f"Class {label+1}"
            label_names.append(label_name)
            wiki_needed[label_name] = ''
        # If any labels need Wikipedia extraction, do it
        wiki_embeddings = {}
        if wiki_needed:
            wiki_extractor = WikiCorpusExtractor(wiki_needed)
            wiki_extractor.max_pages_per_term = min_wiki_pages
            wiki_corpus = wiki_extractor.extract_corpus()
            for label, text in wiki_corpus.items():
                label_corpus_texts.append(text)
        # Generate embeddings for label corpora
        embedding_gen = EmbeddingGenerator(embedding_type)
        label_embeddings = embedding_gen.generate_embeddings(label_corpus_texts)
        # Generate embeddings for documents
        document_embeddings = embedding_gen.generate_embeddings(processed_texts)
        # Map label names to embeddings
        label_to_embedding = {label_names[i]: label_embeddings[i] for i in range(len(label_names))}
        # Perform clustering
        predicted_labels, cluster_labels, similarity_matrix = cluster_and_assign_labels(
            document_embeddings,
            num_clusters,
            label_to_embedding,
            label_names,
            clustering_method=clustering_method
        )
        
        # Log the number of unique clusters created
        unique_clusters = set(cluster_labels)
        logger.info(f"Clustering complete. Created {len(unique_clusters)} unique clusters.")
        
        # Generate visualizations
        visualizations = {}
        
        # Cluster visualization
        plt.figure(figsize=(10, 8))
        cluster_viz = vis.visualize_clusters(
            document_embeddings,
            predicted_labels,
            f"Document Clusters ({clustering_method.upper()})"
        )
        if cluster_viz:
            buf = io.BytesIO()
            cluster_viz.savefig(buf, format='png', bbox_inches='tight')
            buf.seek(0)
            visualizations['cluster_viz'] = base64.b64encode(buf.read()).decode('utf-8')
        
        # Similarity matrix
        if similarity_matrix is not None:
            plt.figure(figsize=(10, 8))
            # Use sorted unique cluster labels for visualization
            unique_cluster_labels = sorted(list(set(cluster_labels)))
            sim_viz = vis.plot_similarity_matrix(
                similarity_matrix,
                unique_cluster_labels,
                list(class_descriptions.keys()),
                "Cluster-Class Similarity Matrix"
            )
            if sim_viz:
                buf = io.BytesIO()
                sim_viz.savefig(buf, format='png', bbox_inches='tight')
                buf.seek(0)
                visualizations['similarity_matrix'] = base64.b64encode(buf.read()).decode('utf-8')
        
        # Cluster sizes
        plt.figure(figsize=(10, 6))
        size_viz = vis.plot_cluster_sizes(cluster_labels, "Cluster Size Distribution")
        if size_viz:
            buf = io.BytesIO()
            size_viz.savefig(buf, format='png', bbox_inches='tight')
            buf.seek(0)
            visualizations['cluster_sizes'] = base64.b64encode(buf.read()).decode('utf-8')
        
        # BERTopic analysis
        bertopic_results = {}
        if use_bertopic:
            logger.info("Running BERTopic analysis...")
            cluster_distribution = Counter(cluster_labels)
            logger.info(f"Cluster distribution: {dict(cluster_distribution)}")
            
            # Check if we have enough data for BERTopic
            small_clusters = [c for c, count in cluster_distribution.items() if count < 5]
            if small_clusters:
                logger.warning(f"Clusters {small_clusters} have fewer than 5 documents, which may cause BERTopic issues")
            
            # Create interpreter with appropriate parameters
            min_topic_size = max(3, min(5, min(cluster_distribution.values()) // 3))
            logger.info(f"Using minimum topic size of {min_topic_size}")
            
            bertopic_interpreter = BERTopicInterpreter(
                embedding_model=embedding_gen.model,
                n_gram_range=(1, 3),
                min_topic_size=min_topic_size
            )
            
            # Run analysis with progress tracking - using original texts as in main.py
            logger.info("Processing clusters with BERTopic...")
            cluster_topics = bertopic_interpreter.fit_transform_with_clusters(texts, cluster_labels)
            logger.info("BERTopic analysis complete")
            
            # Generate topic reports and visualizations
            topic_reports = []
            topic_visualizations = {}
            
            for cluster_id in sorted(set(cluster_labels)):
                logger.info(f"Generating visualizations for cluster {cluster_id}...")
                
                # Get cluster label like in main.py
                cluster_samples = [i for i, c in enumerate(cluster_labels) if c == cluster_id]
                if cluster_samples:
                    cluster_label = predicted_labels[cluster_samples[0]]
                else:
                    cluster_label = "unknown"
                
                if cluster_id in bertopic_interpreter.cluster_topics:
                    # Generate topic reports
                    for topic_id, words in bertopic_interpreter.cluster_topics[cluster_id].items():
                        if words:
                            topic_reports.append({
                                'cluster_id': int(cluster_id),
                                'cluster_label': cluster_label,  # Include cluster_label as in main.py
                                'topic_id': int(topic_id),
                                'top_terms': ", ".join([w for w, _ in words[:5]]),
                                'term_scores': dict(words[:5]),
                                'sample_count': list(cluster_labels).count(cluster_id)
                            })
                    
                    # Store topic summaries
                    topic_summaries = {}
                    for cluster_id in sorted(set(cluster_labels)):
                        topic_summaries[str(cluster_id)] = bertopic_interpreter.get_topic_summary(cluster_id)
                    
                    bertopic_results = {
                        'topic_reports': topic_reports,
                        'topic_summaries': topic_summaries,
                        'topic_visualizations': topic_visualizations
                    }
                else:
                    logger.warning(f"No topics available for cluster {cluster_id}")
            
            # Save results to dataframe
            df['predicted_label'] = predicted_labels
            df['cluster_id'] = cluster_labels
            
            # Store results
            results_file = os.path.join(app.config['UPLOAD_FOLDER'], 'results.csv')
            df.to_csv(results_file, index=False)
            
            # Prepare analysis summary
            cluster_counts = Counter(predicted_labels)
            cluster_distribution = {str(label): {'count': count, 'percentage': count/len(predicted_labels)} 
                                   for label, count in cluster_counts.most_common()}
            
            # Store results in session
            session_data['results'] = {
                'file_path': results_file,
                'cluster_distribution': cluster_distribution,
                'visualizations': visualizations,
                'bertopic_results': bertopic_results,
                'status': 'complete'
            }
            
            # Save session after analysis is complete
            save_session()
            
            logger.info("Analysis completed successfully")
    except Exception as e:
        logger.error(f"Analysis background task failed: {str(e)}")
        import traceback
        traceback.print_exc()
        session_data['results'] = {
            'status': 'error',
            'error_message': str(e)
        }
        save_session()

@app.route('/run-analysis', methods=['POST', 'OPTIONS'])
def run_analysis():
    """Run the analysis pipeline."""
    if request.method == 'OPTIONS':
        return make_response('', 200)
    try:
        if not session_data.get('uploaded_file'):
            return jsonify({'error': 'No file uploaded'}), 400
        # Accept if either class_corpora or class_descriptions is present and non-empty
        class_corpora = session_data.get('class_corpora', {})
        class_descriptions = session_data.get('class_descriptions', {})
        if (not class_corpora or len(class_corpora) == 0) and (not class_descriptions or len(class_descriptions) == 0):
            return jsonify({'error': 'No class descriptions or corpora provided'}), 400
        # Initialize results with 'in-progress' status
        session_data['results'] = {
            'status': 'in-progress',
            'message': 'Analysis is running in the background'
        }
        save_session()
        thread = threading.Thread(target=run_analysis_task)
        thread.daemon = True
        thread.start()
        return jsonify({
            'success': True, 
            'message': 'Analysis started in background. Check status with /analysis-status endpoint.'
        })
    except Exception as e:
        logger.error(f"Analysis start failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Analysis failed to start: {str(e)}'}), 500

@app.route('/analysis-status', methods=['GET', 'OPTIONS'])
def analysis_status():
    """Check the status of the analysis."""
    if request.method == 'OPTIONS':
        return make_response('', 200)
    
    try:
        # Load the latest session data from disk
        load_session()
        
        if not session_data.get('results'):
            return jsonify({'status': 'not-started'}), 200
        
        return jsonify({
            'status': session_data['results'].get('status', 'unknown'),
            'message': session_data['results'].get('message', '')
        }), 200
    except Exception as e:
        logger.error(f"Error checking analysis status: {str(e)}")
        return jsonify({'error': f'Error checking status: {str(e)}'}), 500

@app.route('/results', methods=['GET', 'OPTIONS'])
def results():
    """Get the analysis results."""
    if request.method == 'OPTIONS':
        return make_response('', 200)
    
    try:
        # Load the latest session data from disk
        load_session()
        
        if not session_data.get('results'):
            return jsonify({'error': 'No results available'}), 404
        
        if session_data['results'].get('status') == 'in-progress':
            return jsonify({
                'status': 'in-progress',
                'message': 'Analysis is still running'
            }), 202
        
        if session_data['results'].get('status') == 'error':
            return jsonify({
                'error': session_data['results'].get('error_message', 'Unknown error during analysis')
            }), 500
        
        logger.info("Returning results")
        return jsonify({'success': True, 'results': session_data['results']})
    except Exception as e:
        logger.error(f"Error retrieving results: {str(e)}")
        return jsonify({'error': f'Error retrieving results: {str(e)}'}), 500

@app.route('/download-results', methods=['GET', 'OPTIONS'])
def download_results():
    """Download the analysis results."""
    if request.method == 'OPTIONS':
        return make_response('', 200)
    
    try:
        # Load the latest session data from disk
        load_session()
        
        if not session_data.get('results') or \
           not session_data['results'].get('file_path') or \
           not os.path.exists(session_data['results']['file_path']):
            return jsonify({'error': 'No results available to download'}), 404
        
        return send_file(
            session_data['results']['file_path'],
            as_attachment=True,
            download_name='SCALAR_clustering_results.csv',
            mimetype='text/csv'
        )
    except Exception as e:
        logger.error(f"Download failed: {str(e)}")
        return jsonify({'error': f'Download failed: {str(e)}'}), 500

@app.route('/download-json', methods=['GET', 'OPTIONS'])
def download_json():
    """Download the full analysis results as JSON."""
    if request.method == 'OPTIONS':
        return make_response('', 200)
    
    try:
        # Load the latest session data from disk
        load_session()
        
        if not session_data.get('results') or session_data['results'].get('status') != 'complete':
            return jsonify({'error': 'No results available to download'}), 404
        
        # Create a copy of results without the file path
        results_copy = session_data['results'].copy()
        if 'file_path' in results_copy:
            results_copy.pop('file_path')
        
        # Convert to JSON
        json_data = json.dumps(results_copy, indent=2)
        
        # Create a BytesIO object
        json_bytes = io.BytesIO(json_data.encode())
        
        return send_file(
            json_bytes,
            as_attachment=True,
            download_name='SCALAR_clustering_results.json',
            mimetype='application/json'
        )
    except Exception as e:
        logger.error(f"JSON download failed: {str(e)}")
        return jsonify({'error': f'JSON download failed: {str(e)}'}), 500

if __name__ == '__main__':
    # Print startup message
    print("\n=== SCALAR ===")
    print("Starting application...")
    print("Once the application is running, access it at: http://localhost:5000")
    print("Press Ctrl+C to stop the server\n")
    
    # Start Flask development server
    # Disable auto-reloader to prevent session loss during long analyses
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
