from typing import Optional, List



class FileValidator:
    """
    Validator for file uploads with size and type checking.
    """

    def __init__(
            self,
            max_size: int = 100 * 1024 * 1024,  # 100MB default
            allowed_extensions: List[str] = None,
    ):
        self.max_size = max_size
        self.allowed_extensions = allowed_extensions or ['csv', 'xlsx', 'xls']

    def validate(self, file) -> Optional[str]:
        """
        Validate file size, extension
        Returns error message if validation fails, None otherwise.
        """
        try:
            if file.size > self.max_size:
                return f"File size exceeds {self.max_size / 1024 / 1024}MB limit."

            ext = file.name.split('.')[-1].lower()
            if ext not in self.allowed_extensions:
                return (
                    f"Invalid file extension. Allowed extensions: "
                    f"{', '.join(self.allowed_extensions)}"
                )

            return None

        except Exception as e:
            return f"File validation failed: {str(e)}"


class DatasetValidator:
    """
    Validator for Dataset model with business rules.
    """

    @staticmethod
    def validate_file_content(file) -> Optional[str]:
        """
        Validate file content structure.
        Returns error message if validation fails, None otherwise.
        """
        try:
            # Read first few lines to check structure
            if file.name.endswith('.csv'):
                import csv
                reader = csv.reader(file)
                headers = next(reader)
                first_row = next(reader)

                # Validate minimum columns
                if len(headers) < 1:
                    return "File must contain at least one column"

                # Validate header names
                if not all(headers):
                    return "All columns must have names"

                # Validate no duplicate headers
                if len(headers) != len(set(headers)):
                    return "Duplicate column names found"

            elif file.name.endswith(('.xlsx', '.xls')):
                import openpyxl
                wb = openpyxl.load_workbook(file, read_only=True)
                sheet = wb.active
                headers = [cell.value for cell in sheet[1]]

                # Similar validations for Excel
                if not headers or not any(headers):
                    return "File must contain at least one column with a name"

                if len(headers) != len([h for h in headers if h]):
                    return "All columns must have names"

                if len(headers) != len(set(headers)):
                    return "Duplicate column names found"

            return None

        except Exception as e:
            return f"File content validation failed: {str(e)}"
        finally:
            file.seek(0)  # Reset file pointer

    @staticmethod
    def validate_column_names(names: List[str]) -> Optional[str]:
        """Validate column names."""
        # Check for empty names
        if not all(names):
            return "Empty column names are not allowed"

        # Check for very long names
        if any(len(name) > 100 for name in names):
            return "Column names must be less than 100 characters"

        # Check for invalid characters
        invalid_chars = set('!@#$%^&*()+={}[]|\\:;"\'<>,?/')
        if any(any(char in invalid_chars for char in name) for name in names):
            return "Column names contain invalid characters"

        return None
