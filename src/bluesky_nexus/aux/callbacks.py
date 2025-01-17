"""
This module is not used operatioanlly in the bluesky_nexus package. 
This module is provided just as a tool for debug purposes.
This module provides two callback classes to write Bluesky documents to a file.

Classes:
    WriteToFileCallback: Writes Bluesky documents to a file as JSON strings, one per line.
    WriteToFileFormattedCallback: Writes Bluesky documents to a file in a nicely formatted JSON array.

Usage:
    These callbacks can be used with the Bluesky RunEngine to process and save documents emitted during a run.

Example:
    from bluesky import RunEngine
    from bluesky.plans import count
    from ophyd.sim import det
    from your_module import WriteToFileCallback, WriteToFileFormattedCallback  # Replace `your_module` with the actual module name

    # Initialize the RunEngine
    RE = RunEngine({})

    # Example 1: Write documents as JSON strings, one per line
    file_callback = WriteToFileCallback("bluesky_documents.json")
    RE.subscribe(file_callback)
    RE(count([det], num=5))
    file_callback.close()  # Ensure the file is properly closed after the run

    # Example 2: Write documents in a nicely formatted JSON array
    file_formatted_callback = WriteToFileFormattedCallback("formatted_bluesky_documents.json")
    RE.subscribe(file_formatted_callback)
    RE(count([det], num=5))
    file_formatted_callback.close()  # Ensure the file is properly closed after the run

Notes:
    - The `__call__` method processes each document (`name` and `doc`) as they are emitted by the RunEngine.
    - The `close()` method must be called after the run to ensure all data is written and the file is closed.
    - The `WriteToFileCallback` class is better suited for streaming-style writing (e.g., large data sets).
    - The `WriteToFileFormattedCallback` class is ideal for human-readable outputs or debugging.

"""

import json

class WriteToFileCallback:
    def __init__(self, file_path):
        self.file_path = file_path
        self.file = open(file_path, 'w')
    
    def __call__(self, name, doc):
        # Write each document as a JSON string, one per line
        self.file.write(json.dumps({name: doc}) + '\n')
        self.file.flush()  # Ensure data is written to disk

    def close(self):
        self.file.close()

class WriteToFileFormattedCallback:
    def __init__(self, file_path):
        self.file_path = file_path
        self.file = open(file_path, 'w')
        self.documents = []  # Store all documents in a list

    def __call__(self, name, doc):
        # Append each document (as a dictionary) to the list
        self.documents.append({name: doc})

    def close(self):
        # Write all documents to the file in a nicely formatted way
        json.dump(self.documents, self.file, indent=4)  # Pretty-print with indentation
        self.file.close()
        