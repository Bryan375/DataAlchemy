from __future__ import absolute_import

import logging

from django.core.paginator import Paginator
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from django.core.exceptions import ValidationError
from .models import Dataset
from .response import APIResponse
from .serializers import (
    DatasetCreateSerializer,
    DatasetResponseSerializer,
    DatasetRowsSerializer,
    DatasetColumnSerializer
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

            result = DatasetService.create_dataset(
                file=file,
                validated_data=serializer.validated_data
            )

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

    def retrieve(self, request, *args, **kwargs):
        try:
            pk = kwargs.get('pk')
            dataset = Dataset.objects.filter(id=pk).last()

            # Get pagination parameters
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 20))

            # Get columns
            columns = dataset.columns.all().order_by('position')
            columns_data = DatasetColumnSerializer(columns, many=True).data

            # Get rows with pagination
            queryset = dataset.rows.all().prefetch_related(
                'values',
                'values__column'
            ).order_by('row_index')

            paginator = Paginator(queryset, page_size)
            current_page = paginator.page(page)

            # Serialize rows
            rows_data = DatasetRowsSerializer(current_page.object_list, many=True).data

            # Get dataset basic info
            dataset_data = DatasetResponseSerializer(dataset).data

            # Combine all data
            response_data = {
                "results": {
                    "dataset": dataset_data,
                    "columns": columns_data,
                    "rows": [row['values'] for row in rows_data]
                },
                "count": paginator.count,
                "next": page + 1 if current_page.has_next() else None,
                "previous": page - 1 if current_page.has_previous() else None,
                "current_page": page,
                "total_pages": paginator.num_pages,
                "page_size": page_size
            }

            return APIResponse.paginated_response(
                data=response_data,
                message="Dataset retrieved successfully"
            )

        except Exception as e:
            logger.error(f"Error retrieving dataset: {str(e)}")
            return APIResponse.error(
                message="Failed to retrieve dataset",
                errors={"detail": str(e)}
            )

    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        try:
            job_id = request.query_params.get('job_id')
            dataset = Dataset.objects.filter(id=pk).last()
            if not dataset:
                raise Dataset.DoesNotExist("Dataset not found")

            value = DatasetService.get_status(dataset, job_id)

            return APIResponse.success(data=value)
        except Exception as e:
            return APIResponse.error(
                message="Failed to get status",
                errors={"detail": str(e)}
            )

class ColumnViewSet(viewsets.ViewSet):
    pass

