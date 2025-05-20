import os
import subprocess
import tempfile
from .base_processor import BaseProcessor
import logging

logger = logging.getLogger(__name__)

class ImageProcessor(BaseProcessor):
    """Processor for image files with text content (jpg, jpeg, png)"""
    
    def process(self, file_path):
        """
        Process an image file and extract any text content using OCR
        
        Args:
            file_path: Path to the image file
            
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
        
        try:
            # Extract image metadata
            image_info = self._extract_image_info(file_path)
            result['metadata'].update(image_info)
            
            # Add the image itself to the images list
            result['images'].append({
                'filename': os.path.basename(file_path),
                'path': file_path,
                'width': image_info.get('width', 0),
                'height': image_info.get('height', 0),
                'format': image_info.get('format', '')
            })
            
            # Extract text using OCR if available
            text = self._extract_text_with_ocr(file_path)
            if text:
                result['content'] = text
            else:
                result['content'] = "[Image without extractable text]"
                
        except Exception as e:
            logger.error(f"Error processing image file {file_path}: {str(e)}")
            result['content'] = f"Error processing image: {str(e)}"
        
        return result
    
    def _extract_image_info(self, file_path):
        """Extract basic information about the image"""
        # In a real implementation, we would use PIL or another image library
        # For this prototype, we'll use a simplified approach with file command
        
        try:
            # Use 'file' command to get basic image info
            result = subprocess.run(
                ['file', file_path],
                check=True,
                capture_output=True,
                text=True
            )
            
            info = result.stdout
            
            # Very basic parsing of the file command output
            image_info = {
                'format': os.path.splitext(file_path)[1].lower()[1:],
            }
            
            # Try to extract dimensions if available
            import re
            dimensions_match = re.search(r'(\d+)\s*x\s*(\d+)', info)
            if dimensions_match:
                image_info['width'] = int(dimensions_match.group(1))
                image_info['height'] = int(dimensions_match.group(2))
            
            return image_info
            
        except Exception as e:
            logger.warning(f"Could not extract image info for {file_path}: {str(e)}")
            return {
                'format': os.path.splitext(file_path)[1].lower()[1:],
            }
    
    def _extract_text_with_ocr(self, file_path):
        """Extract text from image using OCR (if available)"""
        # In a real implementation, we would use Tesseract OCR
        # For this prototype, we'll check if tesseract is installed and use it if available
        
        try:
            # Check if tesseract is installed
            subprocess.run(
                ['which', 'tesseract'],
                check=True,
                capture_output=True
            )
            
            # If we get here, tesseract is installed
            with tempfile.NamedTemporaryFile(suffix='.txt') as temp_file:
                # Run tesseract OCR
                subprocess.run(
                    ['tesseract', file_path, temp_file.name.replace('.txt', '')],
                    check=True,
                    capture_output=True
                )
                
                # Read the extracted text
                with open(temp_file.name, 'r', encoding='utf-8', errors='replace') as f:
                    text = f.read()
                
                return text.strip()
                
        except subprocess.CalledProcessError:
            # Tesseract not installed or other error
            logger.warning(f"Tesseract OCR not available for {file_path}")
            return "To extract text from images, please install Tesseract OCR."
        
        except Exception as e:
            logger.warning(f"OCR failed for {file_path}: {str(e)}")
            return ""
