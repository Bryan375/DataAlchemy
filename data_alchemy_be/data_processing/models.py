from django.db import models
from django.core.validators import FileExtensionValidator
import uuid


class Dataset(models.Model):
    """
    Model to store uploaded datasets and their processing status.
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the dataset"
    )

    name = models.CharField(
        max_length=255,
        help_text="Name of the dataset"
    )

    description = models.TextField(
        blank=True,
        help_text="Optional description of the dataset"
    )

    file = models.FileField(
        upload_to='datasets/%Y/%m/%d/',
        validators=[FileExtensionValidator(allowed_extensions=['csv', 'xlsx', 'xls'])],
        help_text="The uploaded dataset file"
    )

    file_type = models.CharField(
        max_length=10,
        choices=[('CSV', 'CSV'), ('EXCEL', 'Excel')],
        help_text="Type of the uploaded file"
    )

    rows_count = models.IntegerField(
        null=True,
        blank=True,
        help_text="Total number of rows in the dataset"
    )

    columns_count = models.IntegerField(
        null=True,
        blank=True,
        help_text="Total number of columns in the dataset"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING',
        help_text="Current processing status of the dataset"
    )

    error_message = models.TextField(
        blank=True,
        help_text="Error message if processing failed"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the dataset was uploaded"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the dataset was last updated"
    )

    processed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the dataset processing was completed"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Dataset'
        verbose_name_plural = 'Datasets'

    def __str__(self):
        return f"{self.name} ({self.status})"



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

    dataset = models.ForeignKey(
        Dataset,
        on_delete=models.CASCADE,
        related_name='columns',
        help_text="Dataset this column belongs to"
    )

    name = models.CharField(
        max_length=255,
        help_text="Current name of the column"
    )

    original_name = models.CharField(
        max_length=255,
        help_text="Original name of the column in the file"
    )

    position = models.IntegerField(
        help_text="Position of the column in the dataset"
    )

    inferred_type = models.CharField(
        max_length=20,
        choices=DATA_TYPES,
        help_text="Data type inferred by the system"
    )

    current_type = models.CharField(
        max_length=20,
        choices=DATA_TYPES,
        help_text="Current data type (may be modified by user)"
    )

    nullable = models.BooleanField(
        default=True,
        help_text="Whether the column contains null values"
    )

    unique_values_count = models.IntegerField(
        default=0,
        help_text="Number of unique values in the column"
    )

    null_count = models.IntegerField(
        default=0,
        help_text="Number of null values in the column"
    )

    sample_values = models.JSONField(
        default=list,
        help_text="Sample values from the column"
    )

    statistics = models.JSONField(
        default=dict,
        help_text="Statistical information about the column"
    )

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

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the job"
    )

    dataset = models.ForeignKey(
        Dataset,
        on_delete=models.CASCADE,
        related_name='jobs',
        help_text="Dataset being processed"
    )

    job_type = models.CharField(
        max_length=20,
        choices=JOB_TYPES,
        help_text="Type of processing job"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='QUEUED',
        help_text="Current status of the job"
    )

    celery_task_id = models.CharField(
        max_length=255,
        blank=True,
        help_text="Celery task ID for tracking"
    )

    error_message = models.TextField(
        blank=True,
        help_text="Error message if job failed"
    )

    result = models.JSONField(
        null=True,
        blank=True,
        help_text="Job result data"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the job was created"
    )

    started_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the job started processing"
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the job completed or failed"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Processing Job'
        verbose_name_plural = 'Processing Jobs'

    def __str__(self):
        return f"{self.dataset.name} - {self.job_type} ({self.status})"

    @property
    def duration(self):
        """Calculate job duration if completed."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None