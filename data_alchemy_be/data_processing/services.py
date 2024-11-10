import json
import logging

from typing import Dict, Any
from django.db import transaction

from utils.redis_client import RedisClient
from .tasks.tasks import process_dataset_task
from .models import Dataset, ProcessingJob
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