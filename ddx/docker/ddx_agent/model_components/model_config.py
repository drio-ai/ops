# model_config.py

from model_components.models import EntityExtractor, TopicModelProcessor  # Import custom models for entity and topic extraction
from typing import Optional  # Optional type hint for model instances

# Paths for models and configuration files
ZIP_CODE_FILE_PATH: str = "/docker-entrypoint-ddx.d/ddx_agent/model_components/ZIP_Locale_Detail.xlsx"
BER_TOPIC_MODEL_PATH: str = "/docker-entrypoint-ddx.d/ddx_agent/model_components/Merged_model_09_26_2024"

# Global variables to cache model instances
_spacy_model_instance: Optional[EntityExtractor] = None  # Cache for EntityExtractor instance
_bertopic_model_instance: Optional[TopicModelProcessor] = None  # Cache for TopicModelProcessor instance

#----------------------------------------------
#           Load SpaCy Entity Model
#----------------------------------------------
def load_spacy_model() -> EntityExtractor:
    """
    Loads and returns a singleton instance of the SpaCy-based EntityExtractor.
    If the instance is already created, returns the cached instance.
    
    :return: An instance of EntityExtractor with loaded ZIP code data.
    :raises RuntimeError: If there is an error loading the SpaCy model.
    """
    global _spacy_model_instance
    if _spacy_model_instance is None:  # Check if instance is not already loaded
        try:
            _spacy_model_instance = EntityExtractor(ZIP_CODE_FILE_PATH)  # Instantiate EntityExtractor
        except Exception as e:
            raise RuntimeError(f"Error loading SpaCy model: {e}")  # Raise error if loading fails
    return _spacy_model_instance

#----------------------------------------------
#           Load BERTopic Model
#----------------------------------------------
def load_bertopic_model() -> TopicModelProcessor:
    """
    Loads and returns a singleton instance of the BERTopic-based TopicModelProcessor.
    If the instance is already created, returns the cached instance.
    
    :return: An instance of TopicModelProcessor for topic modeling.
    :raises RuntimeError: If there is an error loading the BERTopic model.
    """
    global _bertopic_model_instance
    if _bertopic_model_instance is None:  # Check if instance is not already loaded
        try:
            _bertopic_model_instance = TopicModelProcessor(BER_TOPIC_MODEL_PATH)  # Instantiate TopicModelProcessor
        except Exception as e:
            raise RuntimeError(f"Error loading BERTopic model: {e}")  # Raise error if loading fails
    return _bertopic_model_instance
