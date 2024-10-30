from django.db import models
from django.core.validators import FileExtensionValidator
import uuid


class Dataset(models.Model):
    """
    Model to store uploaded datasets and their processing status.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    file = models.FileField(validators=[FileExtensionValidator(allowed_extensions=['csv', 'xlsx', 'xls'])])
    file_type = models.CharField(max_length=10, choices=[('CSV', 'CSV'), ('EXCEL', 'Excel')])
    rows_count = models.IntegerField(null=True, blank=True)
    columns_count = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Dataset'
        verbose_name_plural = 'Datasets'


class Column(models.Model):
    """
    Model to store information about each column in a dataset.
    """
    DATA_TYPES = [
        ('TEXT', 'Text'),
        ('INTEGER', 'Integer'),
        ('FLOAT', 'Float'),
        ('DATE', 'Date'),
        ('DATETIME', 'DateTime'),
        ('BOOLEAN', 'Boolean'),
        ('CATEGORY', 'Category'),
    ]

    dataset = models.ForeignKey(Dataset,on_delete=models.CASCADE, related_name='columns')
    name = models.CharField(max_length=255)
    original_name = models.CharField(max_length=255)
    position = models.IntegerField()
    inferred_type = models.CharField(max_length=20, choices=DATA_TYPES)
    current_type = models.CharField(max_length=20, choices=DATA_TYPES)
    nullable = models.BooleanField(default=True)
    unique_values_count = models.IntegerField(default=0)
    null_count = models.IntegerField(default=0)
    sample_values = models.JSONField(default=list)

    class Meta:
        ordering = ['position']
        unique_together = ['dataset', 'name']
        verbose_name = 'Column'
        verbose_name_plural = 'Columns'

    def __str__(self):
        return f"{self.dataset.name} - {self.name} ({self.current_type})"


class ProcessingJob(models.Model):
    """
    Model to track background processing jobs.
    """
    JOB_TYPES = [
        ('INFERENCE', 'Type Inference'),
        ('EXPORT', 'Data Export'),
        ('CONVERSION', 'Type Conversion'),
    ]

    STATUS_CHOICES = [
        ('QUEUED', 'Queued'),
        ('RUNNING', 'Running'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='jobs')
    job_type = models.CharField(max_length=20, choices=JOB_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='QUEUED')
    celery_task_id = models.CharField(max_length=255, blank=True)
    error_message = models.TextField(blank=True)
    result = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Processing Job'
        verbose_name_plural = 'Processing Jobs'

    def __str__(self):
        return f"{self.dataset.name} - {self.job_type} ({self.status})"
