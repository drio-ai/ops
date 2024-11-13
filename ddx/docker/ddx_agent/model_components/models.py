import json  # JSON handling for input/output processing
import re  # Regular expressions for pattern matching
import spacy  # NLP library for entity recognition
from spacy.pipeline import EntityRuler  # Pipeline component for custom entity rules
import pandas as pd  # Data handling for ZIP codes
import logging  # Logging for tracking events and errors
from bertopic import BERTopic  # Topic modeling
from typing import Dict, Optional, List, Any  # Type annotations
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


#----------------------------------------------
#        Entity Extraction Component
#----------------------------------------------
class EntityExtractor:
    def __init__(self, zip_code_file_path: str) -> None:
        """
        Initializes the EntityExtractor with a ZIP code file and SpaCy model.
        :param zip_code_file_path: Path to the Excel file containing valid ZIP codes.
        """
        # Load the SpaCy model and define custom regex patterns and context terms
        self.nlp = spacy.load("en_core_web_trf")
        self.custom_patterns: Dict[str, re.Pattern] = {
            "SSN": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
            "PHONE_NUMBER": re.compile(r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b"),
            "CREDIT/DEBIT_CARD": re.compile(r"\b(?:\d[ -]*?){13,16}\b"),
            "EMAIL": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
            "ZIP_CODE": re.compile(r"\b\d{5}(?:-\d{4})?\b"),
            "ADDRESS": re.compile(r"\d+\s+\w+(\s+\w+)*,\s+\w+(\s+\w+)*,\s*[A-Z]{2}\s*\d{5}(?:-\d{4})?")
        }
        
        self.context_terms: Dict[str, List[str]] = {
            "SSN": ["social security number", "ssn", "security number"],
            "PHONE_NUMBER": ["phone", "mobile", "contact"],
            "ADDRESS": ["address", "street", "city", "state", "zip"],
            "EMAIL": ["email", "mail"],
            "ZIP_CODE": ["zip", "postal"],
            "CREDIT/DEBIT_CARD": ["credit card", "debit card", "card number"],
            "ORDER_NUMBER": ["PO #", "Order Number", "Associated PO #"]
        }
        
        # Load ZIP codes from the specified Excel file
        self.zip_codes_df: pd.DataFrame = self.load_zip_codes(zip_code_file_path)
        
        # Add EntityRuler for context terms
        entity_ruler: EntityRuler = self.nlp.add_pipe("entity_ruler", before="ner")
        patterns = [{"label": label, "pattern": [{"LOWER": term.lower()}]} 
                    for label, terms in self.context_terms.items() for term in terms]
        entity_ruler.add_patterns(patterns)

    def load_zip_codes(self, file_path: str) -> pd.DataFrame:
        """
        Loads ZIP codes from an Excel file.
        :param file_path: Path to the Excel file.
        :return: DataFrame with ZIP codes if found, else an empty DataFrame.
        """
        try:
            zip_codes_df = pd.read_excel(file_path)
            zip_codes_df['DELIVERY ZIPCODE'] = zip_codes_df['DELIVERY ZIPCODE'].astype(str).str.strip()
            return zip_codes_df
        except FileNotFoundError:
            logging.error("Excel file for ZIP codes not found.")
            return pd.DataFrame()

    def match_custom_patterns(self, text: str) -> List[Dict[str, Any]]:
        """
        Matches custom patterns (e.g., SSN, phone) in the text.
        :param text: Input text to search.
        :return: List of entities matching custom patterns.
        """
        entities = []
        for label, pattern in self.custom_patterns.items():
            for match in pattern.finditer(text):
                start, end = match.span()
                entities.append({"entity": label, "value": match.group(), "start": start, "end": end})
        return entities

    def validate_zip_codes(self, entities: List[Dict[str, Any]], nest_number: str) -> List[Dict[str, Any]]:
        """
        Validates ZIP code entities against the ZIP codes in the loaded Excel file.
        :param entities: List of entities to validate.
        :param nest_number: Nesting identifier for entities.
        :return: List of validated entities with possible invalidation notes.
        """
        validated_entities = []
        for entity in entities:
            if entity["entity"] == "ZIP_CODE" and entity["value"] not in self.zip_codes_df['DELIVERY ZIPCODE'].values:
                entity["note"] = "Invalid ZIP code"
            entity["nest_number"] = nest_number
            validated_entities.append(entity)
        return validated_entities

    def extract_entities(self, text: str, nest_number: str) -> Dict[str, Any]:
        """
        Extracts entities from the text using SpaCy and custom patterns.
        :param text: Input text to extract entities from.
        :param nest_number: Identifier for nested entities.
        :return: Dictionary with extracted entities and context.
        """
        doc = self.nlp(text)
        entities = [{"entity": ent.label_, "value": ent.text, "start": ent.start_char, "end": ent.end_char, "nest_number": nest_number} 
                    for ent in doc.ents]
        custom_entities = self.match_custom_patterns(text)
        entities.extend(self.validate_zip_codes(custom_entities, nest_number))
        for entity in entities:
            start, end = entity["start"], entity["end"]
            entity["context"] = doc[max(0, start-15):min(len(doc), end+15)].text
        return {"doc_text": doc.text, "entities": entities}

    def process_json_data(self, json_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Processes JSON data to extract entities.
        :param json_data: JSON data with text to process.
        :return: List of processed entities.
        """
        return self.process_json_file(json_data)

    def process_json_file(self, data: Dict[str, Any], nest_number: int = 0) -> List[Dict[str, Any]]:
        """
        Processes JSON file to extract entities recursively.
        :param data: JSON data containing text to process.
        :param nest_number: Identifier for nested items.
        :return: List of extracted entities.
        """
        result = []
        for i, item in enumerate(data.get("main_json", [])):
            processed_item = self.process_json_value(item, nest_number=f"{nest_number}.{i}")
            result.append(processed_item)
        return result

    def process_json_value(self, value: Any, nest_number: str = "") -> Any:
        """
        Recursively processes each JSON value to extract entities.
        :param value: JSON value to process.
        :param nest_number: Identifier for nested items.
        :return: Extracted entities or original value.
        """
        if isinstance(value, str):
            return self.extract_entities(value, nest_number)
        elif isinstance(value, dict):
            return {k: self.process_json_value(v, f"{nest_number}.{k}") for k, v in value.items()}
        elif isinstance(value, list):
            return [self.process_json_value(v, f"{nest_number}.{i}") for i, v in enumerate(value)]
        return value

    def save_output(self, result: Any, output_file_path: str) -> None:
        """
        Saves extracted entities to a JSON file.
        :param result: Data to save.
        :param output_file_path: Path for output JSON file.
        """
        with open(output_file_path, 'w') as f:
            json.dump(result, f, indent=4)


#----------------------------------------------
#        Topic Modeling Component
#----------------------------------------------
class TopicModelProcessor:
    def __init__(self, model_path: str) -> None:
        """
        Initialize the TopicModelProcessor with the path to the BERTopic model.
        :param model_path: Path to the pre-trained BERTopic model.
        """
        self.model_path: str = model_path
        self.merged_model: BERTopic = BERTopic.load(self.model_path)
        self.merged_model.calculate_probabilities = True

    def clean_text(self, text: str) -> str:
        """
        Clean and format the input text by removing unwanted characters and extra spaces.
        :param text: The input text to clean.
        :return: Cleaned text string.
        """
        lines: List[str] = text.splitlines()
        lines = [line.strip() for line in lines if line.strip()]
        cleaned_text: str = " ".join(lines)
        return cleaned_text

    def process_text(self, text: str, filename: str) -> str:
        """
        Process the given text, get topics and their probabilities, and return the output as a JSON string.
        
        :param text: The input text to process.
        :param filename: The name of the file associated with the document.
        :return: A JSON string with topic information and probabilities.
        """
        # Clean and format the input text
        cleaned_text: str = self.clean_text(text)

        # Get the topic information from the model
        topic_info: pd.DataFrame = self.merged_model.get_topic_info()

        # Convert the topic_info dataframe to a JSON-like format
        test_json: str = topic_info.to_json(orient="records", indent=4)

        # Perform topic modeling on the cleaned text
        topics, probs = self.merged_model.transform([cleaned_text])

        # Convert numpy float32 to Python float for compatibility with JSON serialization
        probs = probs.astype(float)

        # Create a dictionary mapping each topic number to its probability
        topic_probabilities: Dict[str, float] = {}
        for i, prob in enumerate(probs[0]):
            topic_probabilities[f"Topic_{i+1}"] = prob

        # Combine the topic probabilities with the test_json (topic info)
        combined_output: Dict[str, Any] = {
            "Topic_Info": json.loads(test_json),  # Convert test_json (already in JSON string format) to Python object
            f"{filename}_Topic_Probabilities": topic_probabilities
        }

        # Convert the final combined output to JSON format
        combined_output_json: str = json.dumps(combined_output, indent=4)

        return combined_output_json


#----------------------------------------------
#        Example Usage in Main
#----------------------------------------------
if __name__ == "__main__":
    # Specify paths
    zip_code_file_path: str = "/docker-entrypoint-ddx.d/ddx_agent/model_components/ZIP_Locale_Detail.xlsx"
    bertopic_model_path: str = "/docker-entrypoint-ddx.d/ddx_agent/model_components/Merged_model_09_26_2024"  # Update with actual path

    # Sample input JSON data
    json_data: Dict[str, Any] = {
        "main_json": [
            [
                "text",
                {
                    "ship_to": [
                        "acme@drio.ai, mobile: 6693225487, SSN: 124-55-8974",
                        "visa : 1458-9989-6287-6582",
                        "Acme Inc, ",
                        "54 Clydelle ave San Jose 95124 CA",
                        "Code Type: Assigned by Buyer or Buyer's Agent",
                        "Code : 54325"
                    ],
                    "store:": ["Store #: 54325"],
                    "reference_id": "order_12345",
                    "header_items": ["Original", "New Order", "Order_12345", "5/1/2024"],
                    "header": "Purchase Order",
                    "ship_from": ["Acme Inc", "Code Type: Assigned by Buyer or Buyer's Agent", "Code : 54325"],
                    "distribution_center:": ["DC #: 54325"]
                }
            ]
        ]
    }

    # Initialize the EntityExtractor and TopicModelProcessor
    entity_extractor: EntityExtractor = EntityExtractor(zip_code_file_path)
    topic_model_processor: TopicModelProcessor = TopicModelProcessor(bertopic_model_path)

    # Process entities
    entity_result: List[Dict[str, Any]] = entity_extractor.process_json_data(json_data)
    print(json.dumps(entity_result, indent=4))

    # Example text processing for topic modeling
    input_text: str = """
    reference_id inv00000156 header_items INV00000156 5/1/2024 header Invoice ship_to Acme Inc 123 Main Street Springfield, IL 62701 USA Code 54325 items PO # 2024050 Ship Date 5/08/2024 Vendor # 98098 meta_headers Total $309.75 shipping_cost 50 other_charge_amount 10 other_charge_description Handling fee items Line # #1 Buyer's Part # 043678 Vendor Item # 726683 Description Grainger PO # 0789545 
    """
    filename: str = "sample_document"
    topic_result: str = topic_model_processor.process_text(input_text, filename)
    print(topic_result)
