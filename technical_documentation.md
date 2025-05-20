# Knowledge Map Program: Technical Documentation

## System Architecture

The Knowledge Map Program is built with a modular architecture that separates concerns and allows for extensibility. The system consists of the following components:

### 1. Backend (Flask Application)

The backend is responsible for:
- File upload and storage
- Content extraction from various file formats
- Knowledge extraction and analysis
- Knowledge map generation
- Learning journey creation
- API endpoints for frontend interaction

### 2. Frontend (HTML/CSS/JavaScript)

The frontend provides:
- User interface for file upload
- Interactive knowledge map visualization using D3.js
- Multiple visualization modes (Network, Hierarchy, Clusters)
- Learning journey navigation
- User preference management

### 3. Processing Pipeline

The processing pipeline consists of:
1. **File Upload**: Files are uploaded and stored with unique identifiers
2. **Content Extraction**: Specialized processors extract content from different file types
3. **Knowledge Extraction**: NLP techniques identify concepts, relationships, and patterns
4. **Knowledge Mapping**: Extracted knowledge is transformed into visual structures
5. **Learning Journey Generation**: Personalized learning paths are created based on user interaction

## Component Details

### File Processors

- **PDFProcessor**: Extracts text and images from PDF files using poppler-utils
- **TextProcessor**: Handles plain text, markdown, and RTF files
- **PresentationProcessor**: Extracts content from PowerPoint presentations
- **ImageProcessor**: Uses OCR to extract text from images
- **HTMLProcessor**: Parses HTML content to extract text and structure

### Knowledge Extraction

The `KnowledgeExtractor` class uses natural language processing to:
- Extract key concepts from text
- Identify relationships between concepts
- Generate concept hierarchies
- Create concept clusters

### Knowledge Mapping

The `KnowledgeMapper` class transforms extracted knowledge into visual structures:
- Generates nodes for concepts
- Creates links for relationships
- Calculates node positions using force-directed layout
- Organizes concepts into clusters
- Builds hierarchical structures

### Learning Journey Generation

The `LearningJourneyGenerator` creates personalized learning paths:
- Supports multiple journey types (pattern-based, hierarchical, associative)
- Adapts to user preferences and cognitive style
- Generates content for each concept in the journey
- Provides pattern insights and related concepts

## API Endpoints

- `GET /`: Main application page
- `POST /upload`: Upload learning materials
- `GET /status/<file_id>`: Check processing status
- `GET /files`: List all uploaded files
- `GET /knowledge_map/<file_id>`: Get knowledge map for a file
- `POST /learning_journey`: Generate a learning journey
- `GET /learning_journey/<journey_id>`: Get a saved learning journey
- `POST /user_preferences`: Save user preferences
- `GET /user_preferences/<user_id>`: Get saved user preferences

## Data Flow

1. User uploads learning materials through the web interface
2. Files are processed by appropriate file processors
3. Extracted content is analyzed by the knowledge extractor
4. Knowledge mapper generates visual representation
5. Frontend renders the knowledge map
6. User interacts with the map to explore concepts
7. When a node is clicked, a learning journey is generated
8. User navigates through the personalized learning journey

## Technical Requirements

- Python 3.6+
- Flask web framework
- spaCy for natural language processing
- NetworkX for graph operations
- D3.js for visualization
- Modern web browser with JavaScript enabled

## Extensibility

The system is designed to be extensible in several ways:
- New file processors can be added to support additional formats
- Alternative NLP techniques can be integrated for knowledge extraction
- Additional visualization modes can be implemented
- Learning journey generation algorithms can be enhanced or replaced
- User preference system can be extended for more personalization

## Performance Considerations

- Large files may require significant processing time
- Complex knowledge maps with many nodes may impact visualization performance
- Consider implementing background processing for production use
- Caching of processed results is recommended for repeated access
