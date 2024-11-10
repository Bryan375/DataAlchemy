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
    def get_status(dataset, task_id: str = None) -> Dict[str, Any]:
        """Get dataset processing status."""
        if not task_id:
            raise ValueError("No job found for dataset")

        key = f'celery-task-meta-{task_id}'
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
        
        # Handle empty series
        if series.empty:
            return True, ""
        
        # Handle all null series
        if series.isna().all():
            return True, ""
        
        # Clean the series (remove whitespace, handle empty strings)
        series = series.apply(lambda x: x.strip() if isinstance(x, str) else x)
        series = series.replace('', pd.NA)
        
        try:
            if target_type == 'Integer':
                # Remove commas from numbers (e.g., "1,000" -> "1000")
                series = series.apply(lambda x: x.replace(',', '') if isinstance(x, str) else x)
                
                # Try converting to numeric
                numeric_series = pd.to_numeric(series, errors='coerce')
                
                # Check for NaN values (conversion failures)
                if numeric_series.isna().any():
                    non_numeric = series[numeric_series.isna()].dropna().unique()
                    return False, f"Non-numeric values found: {', '.join(map(str, non_numeric[:5]))}..."
                
                # Check for decimals
                if (numeric_series.dropna() != numeric_series.dropna().astype(int)).any():
                    return False, "Some values contain decimal points"
                
                # Check for integer overflow
                if (numeric_series > 2**63 - 1).any() or (numeric_series < -2**63).any():
                    return False, "Some values are too large or small for integer type"

            elif target_type == 'Float':
                # Remove commas and handle scientific notation
                series = series.apply(lambda x: str(x).replace(',', '') if isinstance(x, (str, int, float)) else x)
                
                # Try converting to float
                numeric_series = pd.to_numeric(series, errors='coerce')
                
                # Check for NaN values (conversion failures)
                if numeric_series.isna().any():
                    non_numeric = series[numeric_series.isna()].dropna().unique()
                    return False, f"Non-numeric values found: {', '.join(map(str, non_numeric[:5]))}..."
                
                # Check for float overflow
                if (numeric_series.abs() > 1.8e308).any():
                    return False, "Some values are too large for float type"

            elif target_type == 'Datetime':
                # Try converting to datetime with various formats
                datetime_series = pd.to_datetime(series, errors='coerce')
                
                # Check for NaN values (conversion failures)
                if datetime_series.isna().any():
                    invalid_dates = series[datetime_series.isna()].dropna().unique()
                    return False, f"Invalid date values found: {', '.join(map(str, invalid_dates[:5]))}..."
                
                # Check for dates out of reasonable range (e.g., year 1000-9999)
                if (datetime_series.dt.year < 1000).any() or (datetime_series.dt.year > 9999).any():
                    return False, "Some dates are outside the supported range (year 1000-9999)"

            elif target_type == 'Boolean':
                # Define valid boolean values (case-insensitive)
                true_values = {'true', 'yes', '1', 't', 'y', 'on', 'true', 'yes'}
                false_values = {'false', 'no', '0', 'f', 'n', 'off', 'false', 'no'}
                
                # Convert to lowercase for comparison
                series = series.apply(lambda x: str(x).lower().strip() if pd.notna(x) else x)
                
                # Check for invalid values
                invalid_values = set(series.dropna().unique()) - true_values - false_values
                if invalid_values:
                    return False, f"Invalid boolean values found: {', '.join(sorted(invalid_values)[:5])}..."

            elif target_type == 'Category':
                # Remove nulls and get unique values
                unique_values = series.dropna().unique()
                total_count = len(series.dropna())
                
                # Check number of unique values
                if len(unique_values) > 100:
                    return False, f"Too many unique values for category type ({len(unique_values)} found, maximum is 100)"
                
                # Check frequency of values
                value_counts = series.value_counts()
                rare_values = value_counts[value_counts < total_count * 0.01]  # Values appearing in less than 1% of rows
                
                if not rare_values.empty:
                    return False, f"Some categories are too rare (less than 1% occurrence): {', '.join(map(str, rare_values.index[:5]))}..."

            elif target_type == 'Text':
                # Text can accept any value
                return True, ""
                
            else:
                return False, f"Unsupported target type: {target_type}"

            return True, ""

        except Exception as e:
            logger.error(f"Error validating type conversion: {str(e)}")
            return False, f"Validation error: {str(e)}"

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
