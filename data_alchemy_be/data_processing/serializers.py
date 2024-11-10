from rest_framework import serializers
from .models import Dataset, Column, ProcessingJob, DatasetRow


class ColumnSerializer(serializers.ModelSerializer):
    """
    Serializer for Column model with type validation.
    """

    class Meta:
        model = Column
        fields = [
            'id', 'name', 'original_name', 'position',
            'inferred_type', 'current_type'
        ]
        read_only_fields = [
            'id', 'name', 'original_name', 'position','inferred_type'
        ]

    def validate_current_type(self, value):
        """Validate the current_type field."""
        valid_types = dict(Column.DATA_TYPES).keys()
        if value not in valid_types:
            raise serializers.ValidationError(
                f"Invalid type. Must be one of: {', '.join(valid_types)}"
            )
        return value


class ProcessingJobSerializer(serializers.ModelSerializer):
    """
    Serializer for ProcessingJob model.
    """

    class Meta:
        model = ProcessingJob
        fields = [
            'id', 'job_type', 'status', 'error_message', 'started_at',
            'completed_at', 'created_at'
        ]
        read_only_fields = fields


class DatasetListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for Dataset list view.
    """
    job_status = serializers.SerializerMethodField()

    class Meta:
        model = Dataset
        fields = [
            'id', 'name', 'created_at', 'job_status'
        ]

    def get_job_status(self, obj):
        latest_job = obj.jobs.first()
        if latest_job:
            return {
                'status': latest_job.status,
                'progress': latest_job.progress,
                'current_stage': latest_job.current_stage
            }
        return None


class DatasetCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for Dataset creation with file validation.
    """

    class Meta:
        model = Dataset
        fields = ['name', 'file']

    def validate_file(self, value):
        """
        Validate the uploaded file.
        Additional validation is done in the view's FileValidator.
        """
        # Determine file type
        filename = value.name.lower()
        if filename.endswith('.csv'):
            file_type = 'CSV'
        elif filename.endswith(('.xlsx', '.xls')):
            file_type = 'EXCEL'
        else:
            raise serializers.ValidationError(
                "Invalid file format. Only CSV and Excel files are supported."
            )

        # Store file_type for later use
        self.context['file_type'] = file_type
        return value

    def validate(self, data):
        """Perform additional validation if needed."""
        if not data.get('name'):
            # Use filename as name if not provided
            data['name'] = data['file'].name.rsplit('.', 1)[0]
        return data

    def create(self, validated_data):
        """Add file_type before creation."""
        validated_data['file_type'] = self.context.get('file_type', 'CSV')
        return super().create(validated_data)


class DatasetResponseSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for Dataset responses.
    """

    class Meta:
        model = Dataset
        fields = [
            'id', 'name', 'file', 'file_type', 'created_at'
        ]
        read_only_fields = fields

class DatasetColumnSerializer(serializers.ModelSerializer):
    """Serializer for column information in dataset rows view."""
    columnIndex = serializers.IntegerField(source='position')
    inferredType = serializers.CharField(source='inferred_type')
    customUserType = serializers.CharField(source='current_type')

    class Meta:
        model = Column
        fields = ['id', 'name', 'columnIndex', 'inferredType', 'customUserType']


class DatasetRowsSerializer(serializers.ModelSerializer):
    """Serializer for dataset rows with values."""
    values = serializers.SerializerMethodField()

    class Meta:
        model = DatasetRow
        fields = ['row_index', 'values']

    def get_values(self, obj):
        return {
            value.column.name: value.value
            for value in obj.values.select_related('column').all()
        }