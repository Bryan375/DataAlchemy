import time

import pandas as pd
from celery import shared_task
from django.utils import timezone
import logging
from typing import Dict, Any
from data_processing.models import Dataset, ProcessingJob, Column, RowValue
from data_processing.tasks.task_service import DataProcessingService

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

        self.update_state(
            state='PROGRESS',
            meta={'progress': 0}
        )

        for i, value in enumerate(values):
            # Convert value based on target type
            try:
                if target_type == 'Integer':
                    converted_value = int(float(value.value)) if value.value else ''
                elif target_type == 'Float':
                    converted_value = float(value.value) if value.value else ''
                elif target_type == 'Datetime':
                    converted_value = pd.to_datetime(value.value) if value.value else ''
                elif target_type == 'Boolean':
                    converted_value = value.value.lower() in {'true', 'yes', '1'} if value.value else ''
                else:
                    converted_value = value.value

                value.value = str(converted_value)
                value.save()

            except Exception as e:
                job.status = 'FAILED'
                job.error_message = f"Error converting value at row {value.dataset_row.row_index}: {str(e)}"
                job.completed_at = timezone.now()
                job.save()
                raise

            # Update progress
            progress_interval = max(1, total_values // 20)  # At least 1, or every 5% for larger datasets

            if (i + 1) % progress_interval == 0 or (i + 1) == total_values:
                progress = ((i + 1) / total_values) * 100
                self.update_state(
                    state='PROGRESS',
                    meta={'progress': round(progress, 2)}
                )
            time.sleep(10)

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
        raise