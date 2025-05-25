import aspose.words as aw

# Load the document
doc = aw.Document("uploads/cleaned___cleaned_12-Muscoluskeletal-System Worksheet (1)_c88004a3.docx")

print("1. Document name: 0", doc.original_file_name)
print("2. Built-in Properties")
            
for prop in doc.built_in_document_properties :
    print("0 : 1", prop.name, prop.value)

print("3. Custom Properties")
            
for prop in doc.custom_document_properties :
    print("0 : 1", prop.name, prop.value)


builtInProps = doc.built_in_document_properties
builtInProps.clear()

customProps = doc.custom_document_properties
customProps.clear()

print("4. Built-in Properties Cleared")
for prop in doc.built_in_document_properties:
    print("0 : 1", prop.name, prop.value)

print("4. Custom Properties Cleared")

for prop in doc.custom_document_properties:
    print("0 : 1", prop.name, prop.value)

print("5. Document saved as testDocx2.docx")
doc.save(f"uploads/cleaned___cleaned_12-Muscoluskeletal-System Worksheet (1)_c88004a3.docx")
