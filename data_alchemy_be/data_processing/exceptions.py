from rest_framework.exceptions import APIException
from rest_framework import status

class DataProcessingError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'An error occurred while processing the data.'
    default_code = 'data_processing_error'

class InvalidFileError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid file format or corrupted file.'
    default_code = 'invalid_file'

class ProcessingLimitExceeded(APIException):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_detail = 'Processing limit exceeded. Please try again later.'
    default_code = 'processing_limit_exceeded'

class ExportError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'An error occurred while exporting the data.'
    default_code = 'export_error'