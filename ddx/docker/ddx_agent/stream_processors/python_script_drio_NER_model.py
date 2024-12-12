import spacy
import pandas as pd

# Directory path to the model
drio_model2 = spacy.load('/docker-entrypoint-ddx.d/ddx_agent/Drio_Model/Drio_NER_model_2.0/ddx_agent/resources/Drio_Model/Drio_NER_model_2.0')
# Path to the input text file
input_file_path = '/docker-entrypoint-ddx.d/ddx_agent/resources/spacy_input.txt'

# Read the input data from the file
with open(input_file_path, 'r') as file:
    input_text = file.read()

# Create object called 'doc'
doc = drio_model2(input_text)

# Extract entities
entities = [(ent.text, ent.label_, ent.start_char, ent.end_char) for ent in doc.ents]

# Create a pandas DataFrame
df = pd.DataFrame(entities, columns=["Text", "Label", "Start", "End"])

# Export to Excel
df.to_excel("/docker-entrypoint-ddx.d/ddx_agent/resources/entities.xlsx", index=False)

print("Entities have been extracted and saved to entities.xlsx")