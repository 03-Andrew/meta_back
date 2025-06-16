import zipfile
import xml.etree.ElementTree as ET
import tempfile
import shutil
import os

def get_docx_metadata(file_path: str) -> dict[str, str]:
    """
    Extracts core, extended (app), and custom metadata from a .docx file
    and returns a dict mapping each property (prefixed by part) to its value.
    """
    metadata = {}
    ns_custom = 'http://schemas.openxmlformats.org/officeDocument/2006/custom-properties'
    ns_vt = 'http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes'

    with zipfile.ZipFile(file_path) as docx:
        parts = {
            'core': 'docProps/core.xml',
            'app': 'docProps/app.xml',
            'custom': 'docProps/custom.xml'
        }
        for part, path in parts.items():
            try:
                xml_bytes = docx.read(path)
            except KeyError:
                continue  # skip if part not present
            root = ET.fromstring(xml_bytes)

            if part in ('core', 'app'):
                for elem in root:
                    tag = elem.tag.split('}')[-1]
                    metadata[f'{part}:{tag}'] = elem.text or ''
            else:  # custom properties
                for prop in root.findall(f'.//{{{ns_custom}}}property'):
                    name = prop.get('name')
                    value = ''
                    for child in prop.findall(f'./{{{ns_vt}}}*'):
                        value = child.text or ''
                        break
                    metadata[f'custom:{name}'] = value

    return metadata


def delete_docx_metadata(file_path: str, fields_to_delete: list[str]) -> None:
    """
    Deletes specified core, app, or custom metadata fields from a .docx file.
    
    Parameters:
        file_path (str): Path to the original .docx file.
        fields_to_delete (list[str]): List of metadata keys to delete, formatted as
            'core:<tag>', 'app:<tag>', or 'custom:<PropertyName>'.
    """
    # Define paths inside DOCX for each metadata part
    parts = {
        'core': 'docProps/core.xml',
        'app': 'docProps/app.xml',
        'custom': 'docProps/custom.xml'
    }
    ns_custom = 'http://schemas.openxmlformats.org/officeDocument/2006/custom-properties'
    ns_vt = 'http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes'
    
    # Prepare a temporary file for the new .docx
    tmp_fd, tmp_path = tempfile.mkstemp(suffix='.docx')
    os.close(tmp_fd)
    
    with zipfile.ZipFile(file_path, 'r') as zin, zipfile.ZipFile(tmp_path, 'w') as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            
            # Check if current file is a metadata part we want to edit
            if item.filename in parts.values():
                part_name = [k for k,v in parts.items() if v == item.filename][0]
                root = ET.fromstring(data)
                
                if part_name in ('core', 'app'):
                    # Remove matching elements by tag
                    for child in list(root):
                        tag = child.tag.split('}')[-1]
                        key = f"{part_name}:{tag}"
                        if key in fields_to_delete:
                            root.remove(child)
                    # Serialize updated XML
                    data = ET.tostring(root, encoding='utf-8', xml_declaration=True)
                
                else:  # custom properties
                    # Remove <property> elements matching by name
                    for prop in root.findall(f'.//{{{ns_custom}}}property'):
                        name = prop.get('name')
                        key = f"custom:{name}"
                        if key in fields_to_delete:
                            root.remove(prop)
                    data = ET.tostring(root, encoding='utf-8', xml_declaration=True)
            
            # Write entry (modified or not) to new archive
            zout.writestr(item, data)
    
    # Replace original file with cleaned version
    shutil.move(tmp_path, file_path)



# Example usage:
if __name__ == "__main__":

    # to_delete = [
    #     'app:Characters', 'app:Application', 'app:DocSecurity',
    #     'app:Lines', 'app:Paragraphs', 'app:ScaleCrop',
    #     'core:title', 'core:subject', 'core:creator',
    #     'core:keywords', 'core:description',
    #     'core:lastModifiedBy', 'core:revision'
    # ]
    # delete_docx_metadata("Test1.docx", ["app:AppVersion"])

    # print("Selected metadata fields have been removed.")

    entries = get_docx_metadata("Test1.docx")
    for entry in entries.items():
        print(f"{entry}")
