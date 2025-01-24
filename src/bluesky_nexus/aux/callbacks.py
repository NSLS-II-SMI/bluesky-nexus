"""
This module is not used operationally in the bluesky_nexus package. 
This module is provided just as a tool for debug purposes.
This module provides three callback classes to write or display Bluesky documents for debugging.

Classes:
    WriteToFileCallback: Writes Bluesky documents to a file as JSON strings, one per line.
    WriteToFileFormattedCallback: Writes Bluesky documents to a file in a nicely formatted JSON array.
    WriteToTerminalCallback: Prints Bluesky documents to the terminal in a human-readable format.

Usage:
    These callbacks can be used with the Bluesky RunEngine to process, save, or display documents emitted during a run.

Example:
    from bluesky import RunEngine
    from bluesky.plans import count
    from ophyd.sim import det
    from bluesky_nexus.aux.callbacks import (
        WriteToFileCallback, 
        WriteToFileFormattedCallback,
        WriteToTerminalCallback
    )

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

    # Example 3: Display documents in the terminal
    terminal_callback = WriteToTerminalCallback()
    RE.subscribe(terminal_callback)
    RE(count([det], num=5))

Notes:
    - `WriteToFileCallback` is better suited for streaming-style writing (e.g., large data sets).
    - `WriteToFileFormattedCallback` is ideal for human-readable outputs or debugging.
    - `WriteToTerminalCallback` is primarily for debugging, printing documents as they are emitted.
"""

import json
from bluesky.callbacks import CallbackBase
from pprint import pprint

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

class WriteToTerminalCallback(CallbackBase):

    def start(self, doc):
        print("/n# I got a new 'start' document:/n")
        pprint(doc)

    def descriptor(self, doc):
        print("/n# I got a new 'descriptor' document:/n")
        pprint(doc)

    def event(self, doc):
        print("/n# I got a new 'event' document:/n")
        pprint(doc)

    def stop(self, doc):
        print("/n# I got a new 'stop' document:/n")
        pprint(doc)
        