
import json
import ast
import logging
import os
import hashlib
import re
import copy

# Set up logging
logging.basicConfig(level=logging.INFO)

class SchemaDetector:
    def __init__(self, topic, data_source):
        self.topic = topic
        self.data_source = data_source
        
        # Retrieve environment variables
        controller_url = os.getenv("CONTROLLER_BASE_URL")
        ddx_cluster_id = os.getenv("DDX_CLUSTER_ID")
        self.ddx_cluster_token = os.getenv("DDX_CLUSTER_TOKEN")
        
        # Construct the schema PUT URL
        self.schema_put_url = f"https://{controller_url}/resources/ddx-clusters/{ddx_cluster_id}/schemas"
        
        # Log the schema URL
        logging.info(f"Schema URL for controller is {self.schema_put_url}")

        # Initialize schema_map to track sent schemas using a composite key (topic + file_id)
        self.schema_map = {}

    def flat_map(self, value, spacy_output):
        # Extract a unique identifier for the decoded PDF file (e.g., file name or hash)
        file_id = self.get_file_id(value)
        
        # Generate a composite key: (topic + file_id)
        schema_key = f"{self.topic}_{file_id}"

        # Use detect_schema to generate the schema
        schema_to_post = detect_schema(value, spacy_output)
 
        # Prepare schema to be posted with data source ID
        schema_to_post_with_data_source = self.build_schema(schema_to_post)

        # Convert schema to a JSON-formatted string
        schema_string = json.dumps(schema_to_post_with_data_source, indent=4)
        logging.info("********** Schema Generated **********")
        logging.info(schema_string)
        
        # Generate a hash of the new schema
        new_schema_hash = self.hash_schema(schema_string)
        
        # Check if the schema has changed (for this topic + file_id combination)
        if self.schema_has_changed(schema_key, new_schema_hash):
            # Simulate sending schema (commented out the external exporter logic)
            #logging.info("======== Schema would be sent here ========")
            # Store the new schema hash in the map
            self.schema_map[schema_key] = new_schema_hash
        else:
            #logging.info(f"Schema for file '{file_id}' in topic '{self.topic}' has not changed. Skipping...")

        # Return the input value unmodified (or could return modified)
            return schema_string

    def build_schema(self, properties):
        # Constructs the top-level schema object
        schema = {
            "data_source_id": self.data_source,
            "schemas": [
                {
                    "name": self.topic,
                    "type": "object",
                    "properties": properties
                }
            ]
        }
        return schema

    def get_file_id(self, value):
        """Extract a unique identifier for the PDF file from the decoded output."""
        if isinstance(value, dict):
            logging.info(f"Inside get_file_id: {value.get('file_name')}")
            return value.get('file_name', 'unknown_file')
        elif isinstance(value, list):
            # Handle the case where value is a list. For example, return the first item.
            logging.info(f"Inside get_file_id with list: {value[0]['filename']}")
            return value[0]['filename'] if value else 'unknown_file'
        else:
            return 'unknown_file'

    def hash_schema(self, schema_string):
        """Generate a hash for the schema string."""
        return hashlib.md5(schema_string.encode('utf-8')).hexdigest()

    def schema_has_changed(self, schema_key, new_schema_hash):
        """Check if the schema for the topic + file_id has changed."""
        previous_schema_hash = self.schema_map.get(schema_key)
        if previous_schema_hash is None:
            #logging.info(f"No previous schema for {schema_key}, sending new schema.")
            return True
        if previous_schema_hash != new_schema_hash:
            #logging.info(f"Schema for {schema_key} has changed. Sending updated schema.")
            return True
        return False

    def extract_pdf_values(self, pdf_output):
        """
        Extract values from the PDF data in a structured way.
        """
        pdf_values = {}

        for entry in pdf_output['main_json']:
            # The second item in each entry is the dictionary containing the data
            if isinstance(entry[1], dict):
                for key, value in entry[1].items():
                    if isinstance(value, list):
                        # Convert each item to a string before joining
                        pdf_values[key] = ' '.join([str(v) if not isinstance(v, dict) else json.dumps(v) for v in value])
                    else:
                        pdf_values[key] = value
        #logging.info(f"Extracted PDF is {pdf_values}")
        return pdf_values

    def add_context_to_schema(self, spacy_output, schema, pdf_output):
        """
        Recursively add spaCy entity types as context for every field in the schema that has a 'type' defined,
        including nested lists and dictionaries, with special handling for 'ship_from' and 'ship_to' list items.
        """
        def recursively_add_context(properties, pdf_values):
            """
            Recursively iterate through properties in the schema and add context from spaCy output.
            """
            for key, field_props in properties.items():
                # Check if the current property has a 'type'
                if 'type' in field_props:
                    # Add context to the current key if it's a simple field (string, date, etc.)
                    for entity_type, entities in spacy_output['spacy_output'].items():
                        for entity in entities:
                            entity_value = entity['Entity']
                            if key in pdf_values and entity_value in pdf_values[key]:
                                field_props['context'] = entity['Type']  # Set the spaCy entity type as context

                    # Special handling for 'ship_from' and 'ship_to' - apply context to each item in the lists
                    if key in ["ship_from", "ship_to"] and field_props['type'] == 'list' and 'items' in field_props:
                        for i, item in enumerate(field_props['items']):
                            # Ensure each item is a dict, then apply context
                            if isinstance(item, dict) and 'type' in item and item['type'] == 'string':
                                for entity_type, entities in spacy_output['spacy_output'].items():
                                    for entity in entities:
                                        entity_value = entity['Entity']
                                        if entity_value in pdf_values.get(key, []):
                                            item['context'] = entity['Type']

                    # If it's a list, recursively add context to its items
                    elif field_props['type'] == 'list' and 'items' in field_props:
                        for item in field_props['items']:
                            if isinstance(item, dict):
                                recursively_add_context(item, pdf_values)

                # If it's a nested dictionary, recursively process it
                elif isinstance(field_props, dict):
                    recursively_add_context(field_props, pdf_values)

        # Extract PDF values (for comparison with spaCy output)
        pdf_values = self.extract_pdf_values(pdf_output)

        # Start the recursive process
        recursively_add_context(schema['schemas'][0]['properties'], pdf_values)

        return schema

def detect_numeric_type(value):
    """Helper function to determine if a value is numeric."""
    try:
        float(value)  # Check if the value can be converted to a float
        return True
    except (ValueError, TypeError):
        return False

# Schema detection function with context addition
def detect_schema(input_data, spacy_output):
    schema = {}
    input_data = ast.literal_eval(input_data)
    # Only consider the 'main_json' part
    main_json = input_data.get("main_json", [])

    # Keys to skip direct schema generation but still process their contents if they are lists or dicts
    keys_to_skip = {"header_items", "header", "items", "meta_header", "meta_headers", "inner", "store:","ship_to"}

    def detect_spacy_context(key, value, spacy_output):
        """
        Detect spaCy context (entity type) for the given key and value by matching it against spaCy output.
        """
        # Remove currency symbols and trailing characters for matching
        value_str = re.sub(r'[\$€£]', '', str(value).strip()).rstrip('\\')

        # Convert numeric strings to integers or floats for consistent comparison
        try:
            value_num = int(value_str) if value_str.isdigit() else float(value_str)
        except ValueError:
            value_num = value_str  # Keep as string if not numeric

        for entity in spacy_output['Extracted Entities']["entities"]:
            entity_value = re.sub(r'[\$€£]', '', entity.get('value', '').strip()).rstrip('\\')

            # Convert spaCy entity to a number if possible for consistent comparison
            try:
                entity_value_num = int(entity_value) if entity_value.isdigit() else float(entity_value)
            except ValueError:
                entity_value_num = entity_value  # Keep as string if conversion fails

            # Match either as numbers or as strings
            if entity_value_num == value_num or entity_value == value_str:
                return entity.get('entity')  # Return the matched entity type (MONEY, CARDINAL, etc.)

        return None


    def parse_item(value, key=None, spacy_output=None):
        # Determine the base type of the value
        if isinstance(value, dict):
            return {k: parse_item(v, key=k, spacy_output=spacy_output) for k, v in value.items()}
        elif isinstance(value, list):
            if value:
                item_schemas = [parse_item(v, spacy_output=spacy_output) for v in value]
                return {"type": "list", "items": item_schemas}
            return {"type": "list", "items": None}  # Empty list case
        elif isinstance(value, str):
            # Detect if it's a currency-based value or should be treated as an integer
            value_str = value.strip()
            
            # Check if the field is one of the specific keys or has a MONEY context
            if key in ['price', 'amount', 'quantity'] or detect_spacy_context(key, value, spacy_output) == 'MONEY':
                value_str = re.sub(r'[\$€£]', '', value_str)  # Remove currency symbols
                result = {"type": "int"}  # Always interpret as int
            elif re.match(r'^\d+$', value_str):  # Match only digits
                result = {"type": "int"}
            elif re.match(r'^\d+\.\d+$', value_str):  # Match decimal numbers
                result = {"type": "int"}  # Convert decimals to int as well
            else:
                result = {"type": "string"}
        elif isinstance(value, bool):
            result = {"type": "boolean"}
        else:
            result = {"type": type(value).__name__}

        # Assign context from detect_spacy_context
        if key:
            result['context'] = detect_spacy_context(key, value, spacy_output)

        return result



    def detect_schema_recursively(json_data, spacy_output):
        for item in json_data:
            if isinstance(item, list) and len(item) > 1 and isinstance(item[1], dict):
                # Process the second element of the list (handling regular fields and the items list)
                for key, value in item[1].items():
                    if key not in keys_to_skip:  # Skip specified keys for direct schema generation
                        schema[key] = parse_item(value, key=key, spacy_output=spacy_output)
                    # Special handling for 'items' key containing Line # entries
                    if key == "items":
                        for line_item in value:
                            line_number = line_item.get("Line #")
                            if line_number:
                                line_key = f"Line {line_number}"  # Create a unique key for each line
                                if line_key not in schema:
                                    schema[line_key] = {}  # Initialize schema for this line
                                # Add other fields under this line's schema
                                for field_key, field_value in line_item.items():
                                    if field_key != "Line #":  # Skip "Line #" as we use it as the key
                                        schema[line_key][field_key] = parse_item(field_value, key=field_key, spacy_output=spacy_output)
                    # Still detect the schema inside the list or dict for keys_to_skip
                    if isinstance(value, dict):
                        detect_schema_recursively([value], spacy_output)  # Process the dictionary
                    elif isinstance(value, list):
                        for sub_item in value:
                            detect_schema_recursively([sub_item], spacy_output)  # Process each item in the list
            elif isinstance(item, dict):
                for key, value in item.items():
                    if key not in schema:
                        schema[key] = parse_item(value, key=key, spacy_output=spacy_output)
                    # Still detect the schema inside the list or dict
                    if isinstance(value, dict):
                        detect_schema_recursively([value], spacy_output)
                    elif isinstance(value, list):
                        for sub_item in value:
                            detect_schema_recursively([sub_item], spacy_output)

    detect_schema_recursively(main_json, spacy_output)
    return schema


