
from bertopic import BERTopic
import pandas as pd
import numpy as np
import seaborn as sb
import spacy

# Replace 'path/to/your/model' with the actual path
merged_model = BERTopic.load("/docker-entrypoint-ddx.d/ddx_agent/resources/Merged_model_09_26_2024")
merged_model.calculate_probabilities = True

# Function to clean the text
def clean_text(text):
    # Remove unwanted characters and extra spaces
    lines = text.splitlines()
    lines = [line.strip() for line in lines if line.strip()]
    cleaned_text = " ".join(lines)
    return cleaned_text


input_text = """
Planning Schedule with Release Capacity
Seo Set Purpose Code
Ss. Acme
wa Manufacturir Mutually Defined
—_e
— Reference ID
1514893
Start Date
3/16/2024
Carrier
Code: USPN
Ship To
DC #H1A
Code: 043849
Schedule Type Schedule Qty Code Supplier Code
Planned Shipment Based Actual Discrete Quantities 434
Volex Item # Item Description | vom |
430900 3" Widget
Forecast Interval Grouping of Forecast Date Warehouse Loc:
Code Forecast Load ID
Pf 200 | | aizsizo24 |
1 1
"""
# Example documents (cleaning step added)
docs = [
    clean_text(input_text),
]

# Step 1: Transform the documents using BERTopic model
Topic1, probs1 = merged_model.transform(docs)

# Step 2: Creating a DataFrame with topic assignments and probabilities
df_probs = pd.DataFrame(probs1, columns=[f"Topic_{i+1}" for i in range(probs1.shape[1])])
df_probs['Assigned_Topic'] = Topic1

# Adding a column for Document identifiers
df_probs['Document'] = [f'Document_{i+1}' for i in range(len(Topic1))]

# Retrieve topic information (topic numbers and names)
topic_info = merged_model.get_topic_info()

topic_info_json = topic_info.to_json(orient='records', indent=4)

# Print the resulting JSON
print(topic_info_json)



