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

    class Meta:
        ordering = ['position']
        unique_together = ['dataset', 'name']


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

class DatasetRow(models.Model):
    """
    Model to store information about each row in the dataset.
    """
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='rows')
    row_index = models.IntegerField()  # Index of the row in the original file
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['row_index']
        unique_together = ['dataset', 'row_index']


class RowValue(models.Model):
    """
    Model to store individual values for each cell in a row of the dataset.
    """
    dataset_row = models.ForeignKey(DatasetRow, on_delete=models.CASCADE, related_name='values')
    column = models.ForeignKey(Column, on_delete=models.CASCADE, related_name='row_values')
    value = models.TextField()  # Store the value as text for flexibility across data types


