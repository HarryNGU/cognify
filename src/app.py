import os
import json
import logging
from flask import Flask, request, jsonify, render_template, send_from_directory
import datetime
import uuid
from werkzeug.utils import secure_filename

# Import processors
from processors.pdf_processor import PDFProcessor
from processors.text_processor import TextProcessor
from processors.presentation_processor import PresentationProcessor
from processors.image_processor import ImageProcessor
from processors.html_processor import HTMLProcessor

# Import knowledge extraction and mapping
from knowledge.extractor import KnowledgeExtractor
from knowledge.mapper import KnowledgeMapper
from knowledge.journey import LearningJourneyGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='static')
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['PROCESSED_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'processed')
app.config['KNOWLEDGE_MAPS_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'knowledge_maps')
app.config['LEARNING_JOURNEYS_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'learning_journeys')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max upload size

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)
os.makedirs(app.config['KNOWLEDGE_MAPS_FOLDER'], exist_ok=True)
os.makedirs(app.config['LEARNING_JOURNEYS_FOLDER'], exist_ok=True)

# File type mapping
ALLOWED_EXTENSIONS = {
    'pdf': PDFProcessor,
    'txt': TextProcessor,
    'md': TextProcessor,
    'rtf': TextProcessor,
    'ppt': PresentationProcessor,
    'pptx': PresentationProcessor,
    'jpg': ImageProcessor,
    'jpeg': ImageProcessor,
    'png': ImageProcessor,
    'html': HTMLProcessor,
    'htm': HTMLProcessor
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    files = request.files.getlist('file')
    
    if not files or files[0].filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    upload_results = []
    
    for file in files:
        if file and allowed_file(file.filename):
            # Generate unique filename
            original_filename = secure_filename(file.filename)
            file_extension = original_filename.rsplit('.', 1)[1].lower()
            unique_id = str(uuid.uuid4())
            unique_filename = f"{unique_id}.{file_extension}"
            
            # Save uploaded file
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(file_path)
            
            # Create metadata record
            metadata = {
                'original_filename': original_filename,
                'unique_filename': unique_filename,
                'file_type': file_extension,
                'upload_time': str(datetime.datetime.now()),
                'status': 'uploaded',
                'file_size': os.path.getsize(file_path)
            }
            
            # Save metadata
            metadata_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{unique_id}.json")
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f)
            
            upload_results.append({
                'id': unique_id,
                'filename': original_filename,
                'status': 'success'
            })
            
            # Start processing in background (in production, use Celery)
            # For now, we'll process synchronously
            try:
                process_file(unique_id)
            except Exception as e:
                logger.error(f"Error processing file {unique_id}: {str(e)}")
                upload_results[-1]['status'] = 'upload_success_process_failed'
        else:
            upload_results.append({
                'filename': file.filename,
                'status': 'invalid_format'
            })
    
    return jsonify({'results': upload_results})

def process_file(file_id):
    """Process an uploaded file and extract its content"""
    # Load metadata
    metadata_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{file_id}.json")
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], metadata['unique_filename'])
    file_extension = metadata['file_type']
    
    # Update status
    metadata['status'] = 'processing'
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f)
    
    try:
        # Get appropriate processor
        processor_class = ALLOWED_EXTENSIONS[file_extension]
        processor = processor_class()
        
        # Process file
        processed_content = processor.process(file_path)
        
        # Save processed content
        processed_path = os.path.join(app.config['PROCESSED_FOLDER'], f"{file_id}.json")
        with open(processed_path, 'w') as f:
            json.dump(processed_content, f)
        
        # Update metadata
        metadata['status'] = 'processed'
        metadata['processed_path'] = processed_path
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f)
        
        # Extract knowledge
        extract_knowledge(file_id)
        
        return True
    except Exception as e:
        logger.error(f"Error processing file {file_id}: {str(e)}")
        metadata['status'] = 'processing_failed'
        metadata['error'] = str(e)
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f)
        return False

def extract_knowledge(file_id):
    """Extract knowledge from processed content"""
    # Load metadata
    metadata_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{file_id}.json")
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    
    processed_path = metadata.get('processed_path')
    
    if not processed_path or not os.path.exists(processed_path):
        logger.error(f"Processed content not found for file {file_id}")
        return False
    
    # Update status
    metadata['status'] = 'extracting_knowledge'
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f)
    
    try:
        # Load processed content
        with open(processed_path, 'r') as f:
            processed_content = json.load(f)
        
        # Extract knowledge
        extractor = KnowledgeExtractor()
        extracted_knowledge = extractor.extract_knowledge(processed_content)
        
        # Save extracted knowledge
        extracted_path = os.path.join(app.config['PROCESSED_FOLDER'], f"{file_id}_knowledge.json")
        with open(extracted_path, 'w') as f:
            json.dump(extracted_knowledge, f)
        
        # Generate knowledge map
        mapper = KnowledgeMapper()
        knowledge_map = mapper.generate_knowledge_map(extracted_knowledge)
        
        # Save knowledge map
        map_path = os.path.join(app.config['KNOWLEDGE_MAPS_FOLDER'], f"{file_id}_map.json")
        mapper.save_knowledge_map(knowledge_map, map_path)
        
        # Update metadata
        metadata['status'] = 'knowledge_extracted'
        metadata['extracted_path'] = extracted_path
        metadata['map_path'] = map_path
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f)
        
        return True
    except Exception as e:
        logger.error(f"Error extracting knowledge for file {file_id}: {str(e)}")
        metadata['status'] = 'extraction_failed'
        metadata['error'] = str(e)
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f)
        return False

@app.route('/status/<file_id>', methods=['GET'])
def get_status(file_id):
    """Get the processing status of a file"""
    metadata_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{file_id}.json")
    
    if not os.path.exists(metadata_path):
        return jsonify({'error': 'File not found'}), 404
    
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    
    return jsonify({
        'id': file_id,
        'filename': metadata['original_filename'],
        'status': metadata['status'],
        'upload_time': metadata['upload_time'],
        'error': metadata.get('error', None)
    })

@app.route('/files', methods=['GET'])
def list_files():
    """List all uploaded files and their status"""
    files = []
    
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        if filename.endswith('.json'):
            file_id = filename.rsplit('.', 1)[0]
            metadata_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            
            files.append({
                'id': file_id,
                'filename': metadata['original_filename'],
                'status': metadata['status'],
                'upload_time': metadata['upload_time']
            })
    
    return jsonify({'files': files})

@app.route('/knowledge_map/<file_id>', methods=['GET'])
def get_knowledge_map(file_id):
    """Get the knowledge map for a file"""
    metadata_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{file_id}.json")
    
    if not os.path.exists(metadata_path):
        return jsonify({'error': 'File not found'}), 404
    
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    
    map_path = metadata.get('map_path')
    
    if not map_path or not os.path.exists(map_path):
        return jsonify({'error': 'Knowledge map not found'}), 404
    
    with open(map_path, 'r') as f:
        knowledge_map = json.load(f)
    
    return jsonify(knowledge_map)

@app.route('/learning_journey', methods=['POST'])
def generate_learning_journey():
    """Generate a learning journey from a knowledge map"""
    data = request.json
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    file_id = data.get('file_id')
    start_concept = data.get('start_concept')
    user_preferences = data.get('user_preferences')
    
    if not file_id or not start_concept:
        return jsonify({'error': 'Missing required parameters'}), 400
    
    # Get knowledge map
    metadata_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{file_id}.json")
    
    if not os.path.exists(metadata_path):
        return jsonify({'error': 'File not found'}), 404
    
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    
    map_path = metadata.get('map_path')
    
    if not map_path or not os.path.exists(map_path):
        return jsonify({'error': 'Knowledge map not found'}), 404
    
    with open(map_path, 'r') as f:
        knowledge_map = json.load(f)
    
    # Generate learning journey
    journey_generator = LearningJourneyGenerator()
    journey = journey_generator.generate_journey(knowledge_map, start_concept, user_preferences)
    
    # Save journey
    journey_id = str(uuid.uuid4())
    journey_path = os.path.join(app.config['LEARNING_JOURNEYS_FOLDER'], f"{journey_id}.json")
    journey_generator.save_journey(journey, journey_path)
    
    # Return journey
    return jsonify({
        'journey_id': journey_id,
        'journey': journey
    })

@app.route('/learning_journey/<journey_id>', methods=['GET'])
def get_learning_journey(journey_id):
    """Get a saved learning journey"""
    journey_path = os.path.join(app.config['LEARNING_JOURNEYS_FOLDER'], f"{journey_id}.json")
    
    if not os.path.exists(journey_path):
        return jsonify({'error': 'Learning journey not found'}), 404
    
    with open(journey_path, 'r') as f:
        journey = json.load(f)
    
    return jsonify(journey)

@app.route('/user_preferences', methods=['POST'])
def save_user_preferences():
    """Save user preferences for personalization"""
    data = request.json
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    user_id = data.get('user_id', str(uuid.uuid4()))
    preferences = data.get('preferences', {})
    
    # Save preferences
    preferences_path = os.path.join(app.config['UPLOAD_FOLDER'], f"user_{user_id}_preferences.json")
    
    with open(preferences_path, 'w') as f:
        json.dump(preferences, f)
    
    return jsonify({
        'user_id': user_id,
        'preferences': preferences
    })

@app.route('/user_preferences/<user_id>', methods=['GET'])
def get_user_preferences(user_id):
    """Get saved user preferences"""
    preferences_path = os.path.join(app.config['UPLOAD_FOLDER'], f"user_{user_id}_preferences.json")
    
    if not os.path.exists(preferences_path):
        return jsonify({'error': 'User preferences not found'}), 404
    
    with open(preferences_path, 'r') as f:
        preferences = json.load(f)
    
    return jsonify({
        'user_id': user_id,
        'preferences': preferences
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
