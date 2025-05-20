import os
import subprocess
import json
import tempfile
from .base_processor import BaseProcessor
import logging

logger = logging.getLogger(__name__)

class PDFProcessor(BaseProcessor):
    """Processor for PDF files using poppler-utils"""
    
    def process(self, file_path):
        """
        Process a PDF file and extract its content
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            dict: Processed content
        """
        self.validate_file(file_path)
        
        result = {
            'content': '',
            'metadata': self.extract_metadata(file_path),
            'structure': {},
            'images': [],
            'references': []
        }
        
        # Extract text using pdftotext (from poppler-utils)
        try:
            text = self._extract_text_with_pdftotext(file_path)
            result['content'] = text
        except Exception as e:
            logger.error(f"Error extracting text from PDF {file_path}: {str(e)}")
            result['content'] = f"Error extracting text: {str(e)}"
        
        # Extract images using pdfimages (from poppler-utils)
        try:
            images = self._extract_images_with_pdfimages(file_path)
            result['images'] = images
        except Exception as e:
            logger.error(f"Error extracting images from PDF {file_path}: {str(e)}")
        
        # Extract document structure and metadata
        try:
            structure = self._extract_structure_with_pdfinfo(file_path)
            result['structure'] = structure
            # Add PDF-specific metadata
            result['metadata'].update(structure)
        except Exception as e:
            logger.error(f"Error extracting structure from PDF {file_path}: {str(e)}")
        
        return result
    
    def _extract_text_with_pdftotext(self, file_path):
        """Extract text from PDF using pdftotext"""
        with tempfile.NamedTemporaryFile(suffix='.txt') as temp_file:
            # Run pdftotext with layout preservation
            subprocess.run(
                ['pdftotext', '-layout', file_path, temp_file.name],
                check=True,
                capture_output=True
            )
            
            # Read the extracted text
            with open(temp_file.name, 'r', encoding='utf-8', errors='replace') as f:
                text = f.read()
        
        return text
    
    def _extract_images_with_pdfimages(self, file_path):
        """Extract images from PDF using pdfimages"""
        # Create temporary directory for images
        with tempfile.TemporaryDirectory() as temp_dir:
            # Run pdfimages to extract all images
            subprocess.run(
                ['pdfimages', '-j', file_path, os.path.join(temp_dir, 'img')],
                check=True,
                capture_output=True
            )
            
            # Get list of extracted images
            image_files = [f for f in os.listdir(temp_dir) if os.path.isfile(os.path.join(temp_dir, f))]
            
            # Create image metadata list
            images = []
            for img_file in image_files:
                img_path = os.path.join(temp_dir, img_file)
                # Get image size and basic info
                img_stats = os.stat(img_path)
                
                # In a real implementation, we would save these images to a permanent location
                # and return paths to them. For now, we'll just return metadata.
                images.append({
                    'filename': img_file,
                    'size': img_stats.st_size,
                    'format': os.path.splitext(img_file)[1].lower()[1:],
                })
        
        return images
    
    def _extract_structure_with_pdfinfo(self, file_path):
        """Extract document structure and metadata using pdfinfo"""
        # Run pdfinfo to get document metadata
        result = subprocess.run(
            ['pdfinfo', file_path],
            check=True,
            capture_output=True,
            text=True
        )
        
        # Parse the output
        info = {}
        for line in result.stdout.splitlines():
            if ':' in line:
                key, value = line.split(':', 1)
                info[key.strip()] = value.strip()
        
        # Extract structure information
        structure = {
            'title': info.get('Title', ''),
            'author': info.get('Author', ''),
            'creator': info.get('Creator', ''),
            'producer': info.get('Producer', ''),
            'creation_date': info.get('CreationDate', ''),
            'modification_date': info.get('ModDate', ''),
            'pages': int(info.get('Pages', 0)),
            'page_size': info.get('Page size', ''),
            'pdf_version': info.get('PDF version', '')
        }
        
        return structure
