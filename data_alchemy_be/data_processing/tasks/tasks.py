import time

import pandas as pd
from celery import shared_task
from django.utils import timezone
import logging
from typing import Dict, Any
from data_processing.models import Dataset, ProcessingJob, Column, RowValue
from data_processing.tasks.task_service import DataProcessingService
from utils.helpers import convert_to_integer, convert_to_float, convert_to_datetime, convert_to_boolean, \
    convert_to_category

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, soft_time_limit=3600)
def process_dataset_task(self, dataset_id: str, job_id: str) -> Dict[str, Any]:
    """
    Process dataset with progress tracking.
    Soft time limit: 1 hour
    """

    dataset = Dataset.objects.filter(id=dataset_id).last()

    job = ProcessingJob.objects.filter(id=job_id).last()
    job.status = 'RUNNING'
    job.started_at = timezone.now()
    job.save()

    try:
        # Update initial status
        self.update_state(
            state='PROGRESS',
            meta={
                'progress': 0,
                'current_stage': 'Starting dataset processing',
                'processed_rows': 0,
                'total_rows': 0
            }
        )

        # Start processing
        result = DataProcessingService.process_dataset(
            dataset=dataset,
            progress_callback=lambda progress, stage: self.update_state(
                state='PROGRESS',
                meta={
                    'progress': progress['progress'],
                    'current_stage': stage,
                    'processed_rows': progress['processed_rows'],
                    'total_rows': progress['total_rows']
                }
            )
        )

        # Update job status
        job.status = 'COMPLETED'
        job.completed_at = timezone.now()
        job.result = result
        job.save()

        return {
            'status': 'success',
            'dataset_id': str(dataset.id),
            'rows_processed': result.get('total_rows', 0),
            'columns_processed': result.get('total_columns', 0)
        }

    except Exception as e:
        logger.error(f"Error processing dataset {dataset_id}: {str(e)}")
        job.status = 'FAILED'
        job.error_message = str(e)
        job.completed_at = timezone.now()
        job.save()
        raise


@shared_task(bind=True)
def convert_column_type_task(self, column_id: str, dataset_id: str, target_type: str, job_id: str) -> Dict[str, Any]:
    """
    Task to convert column values to new type
    """
    try:
        column = Column.objects.get(id=column_id, dataset_id=dataset_id)
        job = ProcessingJob.objects.get(id=job_id)

        job.status = 'RUNNING'
        job.started_at = timezone.now()
        job.save()

        # Get all values
        values = RowValue.objects.filter(column=column)
        total_values = values.count()

        if total_values == 0:
            job.status = 'COMPLETED'
            job.completed_at = timezone.now()
            job.save()
            return {
                'status': 'success',
                'message': 'No values to convert'
            }

        # Initial progress
        self.update_state(
            state='PROGRESS',
            meta={'progress': 0}
        )

        conversion_functions = {
            'Integer': convert_to_integer,
            'Float': convert_to_float,
            'Datetime': convert_to_datetime,
            'Boolean': convert_to_boolean,
            'Category': convert_to_category,
            'Text': str
        }

        # Get the appropriate conversion function
        convert_func = conversion_functions.get(target_type)
        if not convert_func:
            raise ValueError(f"Unsupported target type: {target_type}")

        # Batch processing to improve performance
        batch_size = 1000
        total_batches = (total_values + batch_size - 1) // batch_size
        
        for batch_index in range(total_batches):
            start_idx = batch_index * batch_size
            end_idx = min((batch_index + 1) * batch_size, total_values)
            
            batch_values = values[start_idx:end_idx]
            updated_values = []

            for value in batch_values:
                try:
                    converted_value = convert_func(value.value)
                    value.value = converted_value
                    updated_values.append(value)
                except Exception as e:
                    job.status = 'FAILED'
                    job.error_message = (
                        f"Error converting value '{value.value}' at row "
                        f"{value.dataset_row.row_index}: {str(e)}"
                    )
                    job.completed_at = timezone.now()
                    job.save()
                    raise

            # Bulk update the batch
            RowValue.objects.bulk_update(updated_values, ['value'])

            # Update progress
            progress = ((batch_index + 1) * batch_size / total_values) * 100
            self.update_state(
                state='PROGRESS',
                meta={'progress': min(round(progress, 2), 100)}
            )

        # Update column type
        column.current_type = target_type
        column.save()

        # Complete job
        job.status = 'COMPLETED'
        job.completed_at = timezone.now()
        job.save()

        return {
            'status': 'success',
            'message': f'Successfully converted column type to {target_type}'
        }

    except Exception as e:
        logger.error(f"Error in convert_column_type_task: {str(e)}")
        if job.status != 'FAILED':  # Only update if not already marked as failed
            job.status = 'FAILED'
            job.error_message = str(e)
            job.completed_at = timezone.now()
            job.save()
        raise