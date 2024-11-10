from celery import shared_task
from django.utils import timezone
import logging
from typing import Dict, Any
from data_processing.models import Dataset, ProcessingJob
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