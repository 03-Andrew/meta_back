from docx import Document
import logging
import argparse
import aspose.words as aw


# def remove_metadata_from_docx(docx_path):
#     """
#     DOCX: Clear core properties with python-docx.
#     (ﾉ´ヮ´)ﾉ*:･ﾟ✧
#     """
#     try:
#         logging.info(f"Processing DOCX: {docx_path}")
#         doc = Document(docx_path)
#         metadata_fields = [
#             'author', 'comments', 'category', 'content_status',
#             'identifier', 'keywords', 'language', 'last_modified_by',
#             'last_printed', 'revision', 'subject', 'title', 'version'
#         ]
#         for prop in metadata_fields:
#             try:
#                 setattr(doc.core_properties, prop, "")
#             except ValueError:
#                 pass
#         doc.settings.odd_and_even_pages_header_footer = False
#         doc.save(docx_path)
#         logging.info(f"Metadata removed from DOCX: {docx_path}")
#         return True
#     except Exception as e:
#         logging.exception(f"Error processing DOCX {docx_path}: {e}")
#         return False


def clean_docx_metadata(input_path, output_path):
    # Load the document
    doc = aw.Document(input_path)

    # Remove metadata
    # doc.remove_personal_information()
    doc.built_in_document_properties.clear()
    doc.custom_document_properties.clear()
    doc.accept_all_revisions()

    # Save cleaned document
    doc.save(output_path)
    print(f"Cleaned metadata and saved to: {output_path}")
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Remove metadata from a Word .docx file using Aspose.Words.")
    parser.add_argument("input", help="Path to the input .docx file")
    parser.add_argument("output", help="Path to save the cleaned .docx file")

    args = parser.parse_args()

    clean_docx_metadata(args.input, args.output)