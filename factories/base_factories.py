"""
Base Factory Implementations
"""

from abc import ABC, abstractmethod
from interfaces import Processable, Parseable, Extractable, Filterable, Exportable
from components import PDFProcessor, TOCParser, ContentExtractor, NumericFilter
from validators import InputValidator
from search import TOCSearcher
from logger_config import setup_logger

logger = setup_logger(__name__)

__all__ = ['ProcessorFactory', 'StandardProcessorFactory', 'ServiceFactory', 'StandardServiceFactory']


class ProcessorFactory(ABC):
    """Abstract factory for creating processors"""
    
    @abstractmethod
    def create_pdf_processor(self, file_path: str) -> Processable:
        """Create PDF processor"""
        pass
    
    @abstractmethod
    def create_toc_parser(self, processor: Processable) -> Parseable:
        """Create TOC parser"""
        pass
    
    @abstractmethod
    def create_content_extractor(self, processor: Processable) -> Extractable:
        """Create content extractor"""
        pass
    
    @abstractmethod
    def create_filter(self) -> Filterable:
        """Create filter"""
        pass


class StandardProcessorFactory(ProcessorFactory):
    """Standard implementation of processor factory"""
    
    def create_pdf_processor(self, file_path: str) -> Processable:
        """Create standard PDF processor"""
        return PDFProcessor(file_path)
    
    def create_toc_parser(self, processor: Processable) -> Parseable:
        """Create standard TOC parser"""
        return TOCParser(processor)
    
    def create_content_extractor(self, processor: Processable) -> Extractable:
        """Create standard content extractor"""
        return ContentExtractor(processor)
    
    def create_filter(self) -> Filterable:
        """Create standard numeric filter"""
        return NumericFilter()


class ServiceFactory(ABC):
    """Abstract factory for creating services"""
    
    @abstractmethod
    def create_validator(self) -> InputValidator:
        """Create input validator"""
        pass
    
    @abstractmethod
    def create_searcher(self) -> TOCSearcher:
        """Create TOC searcher"""
        pass
    
    @abstractmethod
    def create_exporter(self) -> Exportable:
        """Create file exporter"""
        pass


class StandardServiceFactory(ServiceFactory):
    """Standard implementation of service factory"""
    
    def create_validator(self) -> InputValidator:
        """Create standard input validator"""
        return InputValidator()
    
    def create_searcher(self) -> TOCSearcher:
        """Create standard TOC searcher"""
        return TOCSearcher()
    
    def create_exporter(self) -> Exportable:
        """Create standard file exporter"""
        from exporters import FileExporter
        return FileExporter()