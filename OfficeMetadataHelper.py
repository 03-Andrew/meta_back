import zipfile
import xml.etree.ElementTree as ET
import tempfile
import shutil
import os

class OfficeMetadataHelper:
    _parts = {
        'core': 'docProps/core.xml',
        'app': 'docProps/app.xml',
        'custom': 'docProps/custom.xml'
    }
    _ns_custom = 'http://schemas.openxmlformats.org/officeDocument/2006/custom-properties'
    _ns_vt = 'http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes'
    OFFICE_EXTENSIONS: set[str] = {
        # Microsoft Word
        '.docx',
        # Microsoft Excel
        '.xlsx',

    }

    @staticmethod
    def get_metadata(file_path: str) -> dict[str, str]:
        metadata = {}
        with zipfile.ZipFile(file_path) as zf:
            for part, path in OfficeMetadataHelper._parts.items():
                try:
                    xml_bytes = zf.read(path)
                except KeyError:
                    continue  # Part doesn't exist

                root = ET.fromstring(xml_bytes)

                if part in ('core', 'app'):
                    for elem in root:
                        tag_name = elem.tag.split('}')[-1]
                        metadata[f'{part}:{tag_name}'] = elem.text or ''
                else:
                    for prop in root.findall(f'.//{{{OfficeMetadataHelper._ns_custom}}}property'):
                        name = prop.get('name')
                        value = ''
                        for child in prop.findall(f'./{{{OfficeMetadataHelper._ns_vt}}}*'):
                            value = child.text or ''
                            break
                        metadata[f'custom:{name}'] = value
        return metadata

    @staticmethod
    def delete_metadata(file_path: str, fields_to_delete: list[str]) -> None:
        ext = os.path.splitext(file_path)[-1].lower()
        if ext not in OfficeMetadataHelper.OFFICE_EXTENSIONS:
            raise ValueError(f"Unsupported file type: {ext}")

        tmp_fd, tmp_path = tempfile.mkstemp(suffix=ext)
        os.close(tmp_fd)

        with zipfile.ZipFile(file_path, 'r') as zin, \
             zipfile.ZipFile(tmp_path, 'w') as zout:

            for item in zin.infolist():
                data = zin.read(item.filename)

                if item.filename in OfficeMetadataHelper._parts.values():
                    part_name = next(
                        key for key, val in OfficeMetadataHelper._parts.items()
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
                        for prop in root.findall(f'.//{{{OfficeMetadataHelper._ns_custom}}}property'):
                            name = prop.get('name')
                            key = f"custom:{name}"
                            if key in fields_to_delete:
                                root.remove(prop)
                        data = ET.tostring(root, encoding='utf-8', xml_declaration=True)

                zout.writestr(item, data)

        shutil.move(tmp_path, file_path)
