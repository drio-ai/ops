# DDXAgent Python Script Summary

This Python script defines a class `DDXAgent` that handles various tasks for a DDX (Data Distribution Exchange) system, including anomaly detection, entity extraction, BERTopic processing, and Kafka/JMX metric collection.

## Key Features

1. **Initialization**:
   - The `DDXAgent` class registers the DDX instance, retrieves configurations from the backend, and logs the initialization process.

2. **WebSocket Client**:
   - The agent connects to a WebSocket endpoint for real-time communication with the backend.

3. **Task Execution**:
   - Periodically performs tasks such as:
     - **Anomaly Detection**
     - **Entity Extraction** from PDFs using the `spaCy` library.
     - **BERTopic Processing** for topic modeling and analysis.

4. **Metrics Collection**:
   - Collects Kafka producer, consumer, and broker metrics using JMX queries.
   - Formats the collected metrics into nested JSON structures for easier processing.

5. **Asynchronous Task Management**:
   - Uses `asyncio` to run tasks concurrently, including:
     - Continuous metric collection.
     - Periodic execution of tasks like anomaly detection, entity extraction, and topic processing.

6. **Graceful Shutdown**:
   - Implements signal handling to ensure the agent shuts down cleanly upon receiving termination signals (SIGINT, SIGTERM).

## Execution Flow

The script starts by creating an instance of `DDXAgent` and runs its asynchronous tasks using `asyncio.run()`. The agent performs its operations in an asynchronous loop until stopped or interrupted.

