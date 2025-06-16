import zipfile
import xml.etree.ElementTree as ET
import tempfile
import shutil
import os

class DocxMetadataHelper:
    """
    Helper class for extracting and deleting metadata
    from .docx files using ZIP + XML parsing.
    """

    # Paths inside the DOCX for each metadata part
    _parts = {
        'core': 'docProps/core.xml',
        'app': 'docProps/app.xml',
        'custom': 'docProps/custom.xml'
    }
    # Namespaces for custom property handling
    _ns_custom = 'http://schemas.openxmlformats.org/officeDocument/2006/custom-properties'
    _ns_vt = 'http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes'

    @staticmethod
    def get_metadata(file_path: str) -> dict[str, str]:
        """
        Extracts core, extended (app), and custom metadata from a .docx file
        and returns a dict mapping each property (prefixed by part) to its value.
        """
        metadata: dict[str, str] = {}

        with zipfile.ZipFile(file_path) as docx:
            for part, xml_path in DocxMetadataHelper._parts.items():
                try:
                    xml_bytes = docx.read(xml_path)
                except KeyError:
                    continue  # skip if this part isn't in the docx

                root = ET.fromstring(xml_bytes)
                if part in ('core', 'app'):
                    for elem in root:
                        tag_name = elem.tag.split('}')[-1]
                        metadata[f'{part}:{tag_name}'] = elem.text or ''
                else:  # custom properties
                    for prop in root.findall(f'.//{{{DocxMetadataHelper._ns_custom}}}property'):
                        name = prop.get('name')
                        value = ''
                        for child in prop.findall(f'./{{{DocxMetadataHelper._ns_vt}}}*'):
                            value = child.text or ''
                            break
                        metadata[f'custom:{name}'] = value

        return metadata

    @staticmethod
    def delete_metadata(file_path: str, fields_to_delete: list[str]) -> None:
        """
        Deletes specified core, app, or custom metadata fields from a .docx file.

        Parameters:
            file_path (str): Path to the original .docx file.
            fields_to_delete (list[str]): List of metadata keys to delete, formatted as
                'core:<tag>', 'app:<tag>', or 'custom:<PropertyName>'.
        """
        tmp_fd, tmp_path = tempfile.mkstemp(suffix='.docx')
        os.close(tmp_fd)

        with zipfile.ZipFile(file_path, 'r') as zin, \
             zipfile.ZipFile(tmp_path, 'w') as zout:

            for item in zin.infolist():
                data = zin.read(item.filename)

                if item.filename in DocxMetadataHelper._parts.values():
                    part_name = next(
                        key for key, val in DocxMetadataHelper._parts.items()
                        if val == item.filename
                    )
                    root = ET.fromstring(data)

                    if part_name in ('core', 'app'):
                        for child in list(root):
                            tag = child.tag.split('}')[-1]
                            key = f"{part_name}:{tag}"
                            if key in fields_to_delete:
                                root.remove(child)
                        data = ET.tostring(root, encoding='utf-8', xml_declaration=True)
                    else:  # custom
                        for prop in root.findall(f'.//{{{DocxMetadataHelper._ns_custom}}}property'):
                            name = prop.get('name')
                            key = f"custom:{name}"
                            if key in fields_to_delete:
                                root.remove(prop)
                        data = ET.tostring(root, encoding='utf-8', xml_declaration=True)

                zout.writestr(item, data)

        shutil.move(tmp_path, file_path)
