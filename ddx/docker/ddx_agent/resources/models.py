# Import necessary libraries
import json
import re
import pandas as pd
import logging

# Configure logging with a configurable level
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SpacyNER:
    def __init__(self, zip_code_file_path, nlp):
        # Use the spaCy model passed from agent_main.py
        self.nlp = nlp  # Correctly assign the passed spaCy model
        
        # Load the Excel file containing valid US zip codes
        self.zip_codes_df = self.load_zip_codes(zip_code_file_path)
        
        # Check if 'entity_ruler' already exists in the pipeline
        if 'entity_ruler' not in self.nlp.pipe_names:
            # Add EntityRuler for custom regex patterns to the pipeline
            self.entity_ruler = self.nlp.add_pipe("entity_ruler", before="ner")
            logging.info("Added 'entity_ruler' to the spaCy pipeline.")
        else:
            # Get the existing 'entity_ruler' from the pipeline
            self.entity_ruler = self.nlp.get_pipe("entity_ruler")
            logging.info("'entity_ruler' already exists in the spaCy pipeline.")
        
        # Context terms for improved entity detection
        self.context_terms = {
            "SSN": ["social security number", "ssn", "social security", "security number", "ss#", "SSN: "],
            "PHONE_NUMBER": ["phone number", "call", "text", "mobile", "contact", "Phone: ", "Mobile: "],
            "ADDRESS": ["address", "street", "city", "state", "zip", "Address: ", "Location: "],
            "EMAIL": ["email", "email address", "mail", "contact", "Email: ", "Mail: "],
            "ZIP_CODE": ["zip", "postal", "address", "city", "state", "Zip: ", "Postal Code: "],
            "CREDIT/DEBIT_CARD": ["credit", "card", "visa", "mastercard", "amex", "payment", "debit", "Card Number: ", "Credit Card: "],
            "ORDER_NUMBER": ["PO #", "Order Number", "Associated PO #", "PO Number", "Order #"]
        }
        
        # Optimized patterns for Spacy EntityRuler
        patterns = []
        for label, term_list in self.context_terms.items():
            for term in term_list:
                patterns.append({"label": label, "pattern": [{"LOWER": term.lower()}]})
        
        self.entity_ruler.add_patterns(patterns)
        
        # Define custom patterns for sensitive information with compiled regex
        self.custom_patterns = {
            "SSN": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
            "PHONE_NUMBER": re.compile(r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b"),
            "CREDIT/DEBIT_CARD": re.compile(r"\b(?:\d[ -]*?){13,16}\b"),
            "EMAIL": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
            "ZIP_CODE": re.compile(r"\b\d{5}(?:-\d{4})?\b"),
            "ADDRESS": re.compile(r"\d+\s+\w+(\s+\w+)*,\s+\w+(\s+\w+)*,\s*[A-Z]{2}\s*\d{5}(?:-\d{4})?")
        }

    def load_zip_codes(self, file_path):
        try:
            zip_codes_df = pd.read_excel(file_path)
            zip_codes_df['DELIVERY ZIPCODE'] = zip_codes_df['DELIVERY ZIPCODE'].astype(str).str.strip()
            return zip_codes_df
        except FileNotFoundError:
            logging.error("The Excel file with zip codes was not found.")
            return pd.DataFrame()

    def filter_entities_by_pos(self, doc, entities):
        """Filter entities based on their POS tags"""
        filtered_entities = []
        for entity in entities:
            if "start" in entity and "end" in entity:
                start, end = entity["start"], entity["end"]
                pos_tags = [token.pos_ for token in doc[start:end]]
                if any(tag in ["VERB", "ADJ"] for tag in pos_tags):
                    continue
            filtered_entities.append(entity)
        return filtered_entities

    def match_custom_patterns(self, text):
        """Match custom entities based on regex patterns"""
        entities = []
        for label, pattern in self.custom_patterns.items():
            for match in pattern.finditer(text):
                start, end = match.span()
                entities.append({
                    "entity": label,
                    "value": match.group(),
                    "start": start,
                    "end": end
                })
        return entities

    def validate_zip_codes(self, custom_entities, nest_number):
        """Validate ZIP codes against the loaded ZIP code data."""
        zip_codes_set = set()
        validated_entities = []

        for entity in custom_entities:
            if entity["entity"] == "ZIP_CODE":
                zip_value = entity["value"].strip()
                if zip_value not in zip_codes_set:
                    logging.info(f"Validating ZIP_CODE: {zip_value}")
                    zip_codes_set.add(zip_value)

                    if zip_value in self.zip_codes_df['DELIVERY ZIPCODE'].values:
                        logging.info(f"ZIP_CODE {zip_value} is valid.")
                        entity["nest_number"] = nest_number
                        validated_entities.append(entity)
                    else:
                        entity["note"] = "Invalid ZIP code"
                        entity["nest_number"] = nest_number
                        validated_entities.append(entity)
                        logging.info(f"ZIP_CODE {zip_value} is invalid.")
            else:
                entity["nest_number"] = nest_number
                validated_entities.append(entity)

        return validated_entities

    def extract_entities(self, text, nest_number):
        """Extract entities and validate ZIP codes and Order Numbers"""
        doc = self.nlp(text)
        
        seen_entities = set()
        entities = []

        # Extract entities detected by spaCy NER
        for ent in doc.ents:
            entity_tuple = (ent.label_, ent.text)
            if entity_tuple not in seen_entities:
                entities.append({
                    "entity": ent.label_, 
                    "value": ent.text, 
                    "start": ent.start_char, 
                    "end": ent.end_char,
                    "nest_number": nest_number
                })
                seen_entities.add(entity_tuple)

        # Extract order number based on context terms
        for term in self.context_terms["ORDER_NUMBER"]:
            if term in text:
                order_number = re.search(rf"{term}\s*(\d+)", text)
                if order_number:
                    order_number_value = order_number.group(1).strip()
                    entities.append({
                        "entity": "ORDER_NUMBER",
                        "value": order_number_value,
                        "start": order_number.start(),
                        "end": order_number.end(),
                        "nest_number": nest_number
                    })

        # Filter entities based on POS tags
        entities = self.filter_entities_by_pos(doc, entities)

        # Match custom entities using regex patterns
        custom_entities = self.match_custom_patterns(text)

        # Validate ZIP code entities
        validated_entities = self.validate_zip_codes(custom_entities, nest_number)

        # Append validated custom entities and avoid duplicates
        entities.extend(validated_entities)

        # Extract context for each entity
        for entity in entities:
            start, end = entity["start"], entity["end"]
            context = doc[max(0, start-15):min(len(doc), end+15)].text
            entity["context"] = context

        return {
            "doc_text": doc.text,
            "entities": [{"entity": ent["entity"], "value": ent["value"], "start": ent["start"], "end": ent["end"], "context": ent["context"], "nest_number": ent["nest_number"], **({"note": ent.get("note")} if "note" in ent else {})} for ent in entities]
        }

    def process_text(self, text, nest_number=0):
        """Process raw text input for NER and validation"""
        extracted_entities = self.extract_entities(text, nest_number)
        return {
            "Original Text": text,
            "Extracted Entities": extracted_entities
        }

    def process_file(self, file_path):
        """Process a file input (JSON or plain text)"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            return self.process_json_file(data)
        except json.JSONDecodeError:
            with open(file_path, 'r') as f:
                text = f.read()
            return self.process_text(text)

    def process_json_file(self, data, nest_number=0):
        """Process JSON file input"""
        result = []
        for i, item in enumerate(data.get("main_json", [])):
            for j, subitem in enumerate(item):
                if isinstance(subitem, dict):
                    processed_subitem = {k: self.process_json_value(v, nest_number=f"{nest_number}.{i}.{j}") for k, v in subitem.items()}
                    result.append(processed_subitem)
        return result

    def process_json_value(self, value, nest_number=""):
        """Process different JSON value types and handle ZIP code validation"""
        if isinstance(value, str):
            extracted_entities = self.extract_entities(value, nest_number)
            return {
                "Original Text": value,
                "Extracted Entities": extracted_entities
            }
        elif isinstance(value, dict):
            return {k: self.process_json_value(v, nest_number=f"{nest_number}.{k}") for k, v in value.items()}
        elif isinstance(value, list):
            return [self.process_json_value(v, nest_number=f"{nest_number}.{i}") for i, v in enumerate(value)]
        else:
            return value

    def save_output(self, result, output_file_path):
        """Save output to a JSON file"""
        with open(output_file_path, 'w') as f:
            json.dump(result, f, indent=4)




###########################


from bertopic import BERTopic
import pandas as pd
import json

class TopicModelProcessor:
    def __init__(self, model_path: str):
        """
        Initialize the TopicModelProcessor with the path to the BERTopic model.
        """
        self.model_path = model_path
        self.merged_model = BERTopic.load(self.model_path)
        self.merged_model.calculate_probabilities = True

    def clean_text(self, text: str) -> str:
        """
        Clean and format the input text by removing unwanted characters and extra spaces.
        """
        lines = text.splitlines()
        lines = [line.strip() for line in lines if line.strip()]
        cleaned_text = " ".join(lines)
        return cleaned_text

    def process_text(self, text: str, filename: str) -> str:
        """
        Process the given text, get topics and their probabilities, and return the output as a JSON string.
        
        :param text: The input text to process.
        :param filename: The name of the file associated with the document.
        :return: A JSON string with topic information and probabilities.
        """
        # Clean and format the input text
        cleaned_text = self.clean_text(text)

        # Get the topic information from the model
        topic_info = self.merged_model.get_topic_info()

        # Convert the topic_info dataframe to a JSON-like format
        test_json = topic_info.to_json(orient="records", indent=4)

        # Perform topic modeling on the cleaned text
        topics, probs = self.merged_model.transform([cleaned_text])

        # Convert numpy float32 to Python float for compatibility with JSON serialization
        probs = probs.astype(float)

        # Create a dictionary mapping each topic number to its probability
        topic_probabilities = {}
        for i, prob in enumerate(probs[0]):
            topic_probabilities[f"Topic_{i+1}"] = prob

        # Combine the topic probabilities with the test_json (topic info)
        combined_output = {
            "Topic_Info": json.loads(test_json),  # Convert test_json (already in JSON string format) to Python object
            f"{filename}_Topic_Probabilities": topic_probabilities
        }

        # Convert the final combined output to JSON format
        combined_output_json = json.dumps(combined_output, indent=4)

        return combined_output_json








# Example usage
if __name__ == "__main__":
    zip_code_file = "/docker-entrypoint-ddx.d/ddx_agent/resources/ZIP_Locale_Detail.xlsx"
    ner = SpacyNER(zip_code_file)
    
    input_text = """acme@drio.ai, mobile: 6693225487, SSN: 124-55-8974,
    visa : 1458-9989-6287-6582,
    Acme Inc,
    Adress: 54 Clydelle ave San Jose 95124, CA
    The order was placed under PO # 12345, and the billing address is 456 Elm St, New York, NY 10001.
    The customer phone number is 555-678-9101."""

    result = ner.process_text(input_text)
    print(json.dumps(result, indent=4))