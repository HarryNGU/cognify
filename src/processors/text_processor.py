import os
from .base_processor import BaseProcessor
import logging

logger = logging.getLogger(__name__)

class TextProcessor(BaseProcessor):
    """Processor for text files (txt, md, rtf)"""
    
    def process(self, file_path):
        """
        Process a text file and extract its content
        
        Args:
            file_path: Path to the text file
            
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
        
        # Extract file extension
        file_extension = os.path.splitext(file_path)[1].lower()[1:]
        
        try:
            # Handle different text formats
            if file_extension == 'rtf':
                text = self._process_rtf(file_path)
            elif file_extension == 'md':
                text = self._process_markdown(file_path)
            else:  # Plain text
                text = self._process_plain_text(file_path)
                
            result['content'] = text
            
            # Basic structure extraction (paragraphs, headings)
            result['structure'] = self._extract_basic_structure(text)
            
        except Exception as e:
            logger.error(f"Error processing text file {file_path}: {str(e)}")
            result['content'] = f"Error processing text: {str(e)}"
        
        return result
    
    def _process_plain_text(self, file_path):
        """Process plain text file"""
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            return f.read()
    
    def _process_markdown(self, file_path):
        """Process markdown file"""
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            text = f.read()
            
        # In a full implementation, we might parse the markdown structure
        # For now, we'll just return the raw text
        return text
    
    def _process_rtf(self, file_path):
        """Process RTF file"""
        # In a real implementation, we would use a library like pyth or striprtf
        # For simplicity, we'll just read it as text and strip basic RTF markers
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            rtf_text = f.read()
        
        # Very basic RTF stripping (not comprehensive)
        # A real implementation would use a proper RTF parser
        text = rtf_text
        if text.startswith('{\\rtf'):
            # Strip RTF control sequences (very simplified)
            import re
            text = re.sub(r'\\[a-z]+', ' ', text)
            text = re.sub(r'\\[a-z]+\d+', ' ', text)
            text = re.sub(r'{|}', '', text)
            text = re.sub(r'\\\'[0-9a-f]{2}', '', text)
        
        return text
    
    def _extract_basic_structure(self, text):
        """Extract basic document structure from text"""
        lines = text.split('\n')
        paragraphs = []
        current_paragraph = []
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_paragraph:
                    paragraphs.append(' '.join(current_paragraph))
                    current_paragraph = []
            else:
                current_paragraph.append(line)
        
        # Add the last paragraph if there is one
        if current_paragraph:
            paragraphs.append(' '.join(current_paragraph))
        
        # Very basic heading detection
        headings = []
        for i, line in enumerate(lines):
            line = line.strip()
            # Check for markdown headings
            if line.startswith('#'):
                level = 0
                for char in line:
                    if char == '#':
                        level += 1
                    else:
                        break
                if level > 0 and level <= 6:
                    headings.append({
                        'text': line[level:].strip(),
                        'level': level,
                        'line': i
                    })
            # Check for underlined headings
            elif i < len(lines) - 1 and lines[i+1].strip() and all(c == '=' for c in lines[i+1].strip()):
                headings.append({
                    'text': line,
                    'level': 1,
                    'line': i
                })
            elif i < len(lines) - 1 and lines[i+1].strip() and all(c == '-' for c in lines[i+1].strip()):
                headings.append({
                    'text': line,
                    'level': 2,
                    'line': i
                })
        
        return {
            'paragraphs': paragraphs,
            'headings': headings,
            'total_paragraphs': len(paragraphs),
            'total_headings': len(headings)
        }
