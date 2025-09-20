"""
Builder Pattern Implementation
"""

from abc import ABC, abstractmethod
from .pipeline import ProcessingPipeline

__all__ = ['ProcessingDirector', 'ProcessingBuilder', 'ConcreteProcessingBuilder']


class ProcessingBuilder(ABC):
    """Abstract builder for processing pipeline"""
    
    @abstractmethod
    def add_validation(self) -> 'ProcessingBuilder':
        pass
    
    @abstractmethod
    def add_parsing(self) -> 'ProcessingBuilder':
        pass
    
    @abstractmethod
    def add_extraction(self) -> 'ProcessingBuilder':
        pass
    
    @abstractmethod
    def add_export(self) -> 'ProcessingBuilder':
        pass
    
    @abstractmethod
    def add_preprocessing(self) -> 'ProcessingBuilder':
        pass
    
    @abstractmethod
    def add_filtering(self) -> 'ProcessingBuilder':
        pass
    
    @abstractmethod
    def add_postprocessing(self) -> 'ProcessingBuilder':
        pass
    
    @abstractmethod
    def add_validation_reports(self) -> 'ProcessingBuilder':
        pass
    
    @abstractmethod
    def build(self) -> ProcessingPipeline:
        pass


class ConcreteProcessingBuilder(ProcessingBuilder):
    """Concrete builder implementation"""
    
    def __init__(self):
        self._pipeline = ProcessingPipeline()
    
    def add_validation(self) -> 'ProcessingBuilder':
        self._pipeline.add_step("validation")
        return self
    
    def add_parsing(self) -> 'ProcessingBuilder':
        self._pipeline.add_step("parsing")
        return self
    
    def add_extraction(self) -> 'ProcessingBuilder':
        self._pipeline.add_step("extraction")
        return self
    
    def add_export(self) -> 'ProcessingBuilder':
        self._pipeline.add_step("export")
        return self
    
    def add_preprocessing(self) -> 'ProcessingBuilder':
        self._pipeline.add_step("preprocessing")
        return self
    
    def add_filtering(self) -> 'ProcessingBuilder':
        self._pipeline.add_step("filtering")
        return self
    
    def add_postprocessing(self) -> 'ProcessingBuilder':
        self._pipeline.add_step("postprocessing")
        return self
    
    def add_validation_reports(self) -> 'ProcessingBuilder':
        self._pipeline.add_step("validation_reports")
        return self
    
    def build(self) -> ProcessingPipeline:
        pipeline = self._pipeline
        self._pipeline = ProcessingPipeline()  # Reset for next build
        return pipeline


class ProcessingDirector:
    """Director for Builder Pattern"""
    
    def __init__(self, builder: ProcessingBuilder):
        self._builder = builder
    
    def construct_basic_processing(self) -> ProcessingPipeline:
        """Construct basic processing pipeline"""
        return (self._builder
                .add_validation()
                .add_parsing()
                .add_extraction()
                .add_export()
                .build())
    
    def construct_advanced_processing(self) -> ProcessingPipeline:
        """Construct advanced processing pipeline"""
        return (self._builder
                .add_validation()
                .add_preprocessing()
                .add_parsing()
                .add_filtering()
                .add_extraction()
                .add_postprocessing()
                .add_export()
                .add_validation_reports()
                .build())