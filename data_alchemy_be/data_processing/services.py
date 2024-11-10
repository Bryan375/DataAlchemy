import json
import logging

from typing import Dict, Any, Tuple

import pandas as pd
from django.db import transaction

from utils.redis_client import RedisClient
from .tasks.tasks import process_dataset_task, convert_column_type_task
from .models import Dataset, ProcessingJob, RowValue, Column

logger = logging.getLogger(__name__)

class DatasetService:
    @staticmethod
    @transaction.atomic
    def create_dataset(file, validated_data: Dict) -> Dict[str, Any]:
        file_type = file.name.split('.')[-1].lower()
        dataset = Dataset.objects.create(
            file_type=file_type,
            **validated_data
        )

        job = ProcessingJob.objects.create(
            dataset=dataset,
            job_type='INFERENCE',
            status='QUEUED'
        )

        task = process_dataset_task.delay(str(dataset.id), str(job.id))

        job.celery_task_id = task.id
        job.save()

        return {
            'datasetId': dataset.id,
            'taskId': task.id
        }

    @staticmethod
    def get_status(dataset, job_id: str = None) -> Dict[str, Any]:
        """Get dataset processing status."""
        job_id = job_id or dataset.jobs.first().id
        if not job_id:
            raise ValueError("No job found for dataset")

        key = f'celery-task-meta-{job_id}'
        value = RedisClient().get(key)

        if value:
            result = json.loads(value.decode())
            return {
                'status': result.get('status'),
                'progress': result.get('result', {}).get('progress', 0),
            }

        return {}

class ColumnService:
    @staticmethod
    def validate_type_conversion(column: Column, target_type: str) -> Tuple[bool, str]:
        """
        Validate if column data can be converted to target type.
        Returns (can_convert, error_message)
        """
        # Get all values for the column
        values = RowValue.objects.filter(
            column=column
        ).values_list('value', flat=True)

        # Convert to pandas series for easier validation
        series = pd.Series(values)

        try:
            if target_type == 'Integer':
                # Try converting to integer
                series = pd.to_numeric(series, downcast='integer')
                if series.apply(lambda x: x != int(x)).any():
                    return False, "Some values contain decimal points"

            elif target_type == 'Float':
                # Try converting to float
                pd.to_numeric(series)

            elif target_type == 'Datetime':
                # Try converting to datetime
                pd.to_datetime(series)

            elif target_type == 'Boolean':
                # Check if values are boolean-like
                valid_values = {'true', 'false', '1', '0', 'yes', 'no'}
                invalid_values = set(series.str.lower()) - valid_values
                if invalid_values:
                    return False, f"Invalid boolean values found: {invalid_values}"

            elif target_type == 'Category':
                # Check if unique values are within reasonable limit
                if series.nunique() > 100:
                    return False, "Too many unique values for category type"

            return True, ""

        except Exception as e:
            return False, str(e)

    @staticmethod
    @transaction.atomic
    def update_column_type(dataset_id: int, column_id: int, target_type: str) -> Dict[str, Any]:
        # Create processing job for conversion
        job = ProcessingJob.objects.create(
            dataset_id=dataset_id,
            job_type='CONVERSION',
            status='QUEUED'
        )

        # Start conversion task
        task = convert_column_type_task.delay(
            column_id=column_id,
            dataset_id=dataset_id,
            target_type=target_type,
            job_id=str(job.id)
        )

        job.celery_task_id = task.id
        job.save()

        return {
            'datasetId': dataset_id,
            'taskId': task.id
        }
