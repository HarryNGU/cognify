from abc import ABC, abstractmethod
import os
import json
import logging

logger = logging.getLogger(__name__)

class BaseProcessor(ABC):
    """Base class for all file processors"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    @abstractmethod
    def process(self, file_path):
        """
        Process a file and extract its content
        
        Args:
            file_path: Path to the file to process
            
        Returns:
            dict: Processed content with structure:
                {
                    'content': str or list,  # Extracted text content
                    'metadata': dict,        # File metadata
                    'structure': dict,       # Document structure information
                    'images': list,          # List of extracted images (if any)
                    'references': list       # List of references/citations (if any)
                }
        """
        pass
    
    def validate_file(self, file_path):
        """Validate that the file exists and is accessible"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not os.path.isfile(file_path):
            raise ValueError(f"Not a file: {file_path}")
        
        if not os.access(file_path, os.R_OK):
            raise PermissionError(f"No permission to read file: {file_path}")
    
    def extract_metadata(self, file_path):
        """Extract basic file metadata"""
        stats = os.stat(file_path)
        return {
            'file_size': stats.st_size,
            'created_time': stats.st_ctime,
            'modified_time': stats.st_mtime,
            'file_name': os.path.basename(file_path),
            'file_extension': os.path.splitext(file_path)[1].lower()[1:]
        }
