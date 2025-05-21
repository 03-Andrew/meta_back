import os
import docx
from pprint import pprint

path = 'PDFs'
os.chdir(path)

fname = 'testDocx.docx'
doc = docx.Document(fname)

prop = doc.core_properties
            
metadata = {}
for d in dir(prop):
    if not d.startswith('_'):
        value = getattr(prop, d)
        if value is not None:  # Only include non-None values
            metadata[d] = value

print("\n=== Document Metadata ===")
print("-" * 50)
for key, value in sorted(metadata.items()):
    print(f"{key.replace('_', ' ').title():25}: {value}")
print("-" * 50)