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
