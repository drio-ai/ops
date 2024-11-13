import unittest
import base64
import json
from PDFExtractDemo.pdf_processor import PDFProcessor  # Assuming the PDFProcessor class is saved in pdf_processor.py
import os
import logging

class TestPDFProcessor(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Configure logging to output to a file with level INFO.
        logging.basicConfig(filename='PDFExtractDemo_test_log.logs',
                            level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s')
        logging.info("Starting Test Suite for PDFProcessor")

    def setUp(self):
        # Set up the PDFProcessor object and log setup completion.
        self.processor = PDFProcessor()
        self.pdf_path = '/docker-entrypoint-ddx.d/ddx_agent/resources/PDFExtractDemo/test_pdfs/drio_810_1.pdf'

        with open(self.pdf_path, 'rb') as pdf_file:
            self.encoded_pdf = base64.b64encode(pdf_file.read()).decode('utf-8')
        
        logging.info("Setup completed for test case.")

    def test_output_pdf(self):
        """Test that the output PDF JSON contains 'main_json', 'header_key', 'header_only' keys with values."""
        logging.info("Starting test: test_output_pdf")

        # Decode the base64 encoded PDF content for passing to the output_pdf function.
        decoded_pdf = base64.b64decode(self.encoded_pdf)

        # Process the PDF and get the output as a JSON string.
        json_output = self.processor.output_pdf(decoded_pdf)

        # Ensure that the function does not return None.
        self.assertIsNotNone(json_output, "output_pdf returned None")
        if json_output is not None:
            logging.info("output_pdf returned valid JSON data.")

        # Parse the JSON output.
        json_data = json.loads(json_output)

        # Check if the keys exist in the JSON and have non-empty values.
        self.assertIn("main_json", json_data, "Missing 'main_json' key in the output JSON")
        self.assertIn("header_key", json_data, "Missing 'header_key' key in the output JSON")
        self.assertIn("header_only", json_data, "Missing 'header_only' key in the output JSON")

        # Log key existence.
        logging.info("'main_json', 'header_key', and 'header_only' keys found in the JSON output.")

        # Check if the values for these keys are not empty.
        self.assertTrue(json_data["main_json"], "'main_json' key has no value")
        self.assertTrue(json_data["header_key"], "'header_key' key has no value")
        self.assertTrue(json_data["header_only"], "'header_only' key has no value")

        # Log test success if all assertions pass.
        logging.info("test_output_pdf completed successfully with all required keys present and populated.")

    @classmethod
    def tearDownClass(cls):
        logging.info("Test Suite for PDFProcessor completed.")


# Run the test
if __name__ == '__main__':
    unittest.main()
