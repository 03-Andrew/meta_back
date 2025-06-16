from ExcelHelper import ExcelMetadataHelper

if __name__ == "__main__":
    # Example usage of the ExcelMetadataHelper class
    # Replace 'test.xlsx' with the path to your Excel file
    meta = ExcelMetadataHelper.get_metadata('test1.xlsx')
    print(meta)

    # To delete specific metadata fields, uncomment the following lines
    fields_to_delete = ["core:lastModifiedBy"]

    ExcelMetadataHelper.delete_metadata('test1.xlsx', fields_to_delete)
    print("Selected metadata fields have been removed.")

    meta_after_deletion = ExcelMetadataHelper.get_metadata('test1.xlsx')
    print(meta_after_deletion)