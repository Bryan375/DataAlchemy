from __future__ import absolute_import

import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from django.core.exceptions import ValidationError
from .models import Dataset
from .response import APIResponse
from .serializers import (
    DatasetCreateSerializer,
    DatasetResponseSerializer,
    DatasetListSerializer
)
from .services import DatasetService
from .validators import FileValidator


logger = logging.getLogger(__name__)

class DatasetViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing datasets. Handles validation and response formatting.
    Business logic is delegated to DatasetService.
    """
    parser_classes = (MultiPartParser,)

    def get_serializer_class(self):
        if self.action == 'create':
            return DatasetCreateSerializer
        elif self.action == 'list':
            return DatasetListSerializer
        return DatasetResponseSerializer

    def create(self, request, *args, **kwargs):
        file_validator = FileValidator(
            allowed_extensions=['csv', 'xlsx', 'xls']
        )

        try:
            if 'file' not in request.FILES:
                raise ValidationError("No file provided")

            file = request.FILES['file']

            validation_err = file_validator.validate(file)
            if validation_err:
                raise ValidationError(validation_err)

            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            logger.debug(f'validated_data: {serializer.validated_data}')

            result = DatasetService.create_dataset(
                file=file,
                validated_data=serializer.validated_data
            )

            logger.debug(f'results: {result}')

            return APIResponse.success(
                data=result,
                message="Dataset uploaded successfully. Processing started.",
                status_code=status.HTTP_201_CREATED
            )

        except ValidationError as e:
            return APIResponse.error(
                message=str(e),
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return APIResponse.error(
                message="Failed to upload dataset",
                errors={"detail": str(e)}
            )


    @action(detail=True, methods=['post'])
    def export(self, request, pk=None):
        """POST /datasets/{id}/export/ - Export dataset."""
        try:
            dataset = self.get_object()
            format = request.data.get('format', 'csv')

            # Validate export format
            if format not in ['csv', 'excel']:
                raise ValidationError("Invalid format. Use 'csv' or 'excel'.")

            result = DatasetService.start_export(dataset, format)

            return APIResponse.success(
                data=result,
                message=f"Export to {format} started"
            )

        except ValidationError as e:
            return APIResponse.error(
                message=str(e),
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return APIResponse.error(
                message="Failed to start export",
                errors={"detail": str(e)}
            )

    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        """GET /datasets/{id}/status/ - Get processing status."""
        try:
            job_id = request.query_params.get('job_id')
            logger.debug('job_id: %s', job_id)
            dataset = Dataset.objects.filter(id=pk).last()
            if not dataset:
                raise Dataset.DoesNotExist("Dataset not found")
            logger.debug(f'dataset: {dataset}')

            value = DatasetService.get_status(dataset, job_id)

            return APIResponse.success(data=value)
        except Exception as e:
            return APIResponse.error(
                message="Failed to get status",
                errors={"detail": str(e)}
            )
