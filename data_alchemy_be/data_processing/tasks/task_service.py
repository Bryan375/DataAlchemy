import logging
import time
from typing import Dict, Callable, Any, Tuple
import pandas as pd
from pandas.core.dtypes.common import is_datetime64_any_dtype, is_numeric_dtype
from data_processing.models import Dataset, Column, DatasetRow, RowValue

logger = logging.getLogger(__name__)


class DataProcessingService:
    CHUNK_SIZE = 10000

    @classmethod
    def process_dataset(
            cls,
            dataset: Dataset,
            progress_callback: Callable = None
    ) -> Dict[str, Any]:
        """
        Process dataset in chunks to handle large files efficiently.
        Uses pandas read_csv/read_excel with chunking.
        """
        try:
            if dataset.file_type == 'csv':
                df = pd.read_csv(dataset.file.path)
            elif dataset.file_type in ('xls', 'xlsx'):
                df = pd.read_excel(dataset.file.path)
            else:
                raise ValueError("Unsupported file format. Please use CSV or Excel.")

            total_columns = len(df.columns)
            total_rows = len(df)
            processed_columns = 0
            overall_progress = 0

            # Create columns first
            columns_map = {}
            for pos, col_name in enumerate(df.columns):
                column = Column.objects.create(
                    dataset=dataset,
                    name=col_name,
                    original_name=col_name,
                    position=pos,
                    inferred_type='Text',
                    current_type='Text'
                )
                columns_map[col_name] = column

            # Process data in chunks
            for start in range(0, len(df), cls.CHUNK_SIZE):
                end = min(start + cls.CHUNK_SIZE, len(df))
                chunk = df.iloc[start:end]
    
                dataset_rows = [
                    DatasetRow(
                        dataset=dataset,
                        row_index=start + idx
                    ) for idx in range(len(chunk))
                ]
                created_rows = DatasetRow.objects.bulk_create(dataset_rows)

                # Process each column for this chunk
                for column_name in df.columns:
                    column = columns_map[column_name]
                    chunk_series = chunk[column_name]
                    
                    converted_chunk, inferred_type = cls._process_column_chunk(
                        chunk_series, 
                        column.inferred_type
                    )

                    # Update column type if needed
                    if column.inferred_type != inferred_type:
                        column.inferred_type = inferred_type
                        column.current_type = inferred_type
                        column.save()

                    row_values = [
                        RowValue(
                            dataset_row=created_rows[idx],
                            column=column,
                            value=str(value) if pd.notna(value) else ''
                        ) for idx, value in enumerate(converted_chunk)
                    ]
                    
                    RowValue.objects.bulk_create(row_values, batch_size=1000)

                    # Calculate progress
                    chunk_progress = (end / total_rows) * 100
                    overall_progress = (processed_columns * 100 + chunk_progress) / total_columns

                    if progress_callback:
                        progress_callback(
                            progress={
                                'total_rows': total_rows,
                                'processed_rows': end,
                                'progress': round(overall_progress, 2),
                            },
                            stage='Processing column data'
                        )
                    processed_columns += 1

                overall_progress = (processed_columns / total_columns) * 100

                # Report completion of column
                if progress_callback:
                    progress_callback(
                        progress={
                            'total_rows': total_rows,
                            'processed_rows': total_rows,
                            'progress': round(overall_progress, 2),
                        },
                        stage='Column processing complete'
                    )


            return {
                'total_rows': total_rows,
                'total_columns': total_columns
            }

        except Exception as e:
            logger.error(f"Error processing dataset: {str(e)}")
            raise Exception(f"Error processing dataset: {str(e)}")

        
    @staticmethod
    def _process_column_chunk(chunk: pd.Series, current_type: str) -> Tuple[pd.Series, str]:
        """Process a chunk of data for a column, returning converted data and inferred type."""
        # Skip if already numeric or datetime
        if current_type != 'Text' and (is_numeric_dtype(chunk) or is_datetime64_any_dtype(chunk)):
            return chunk, current_type

        # Clean and normalize the chunk
        normalized_chunk = DataProcessingService._normalize_values(chunk)

        # Handle all null case
        if chunk.isna().all():
            return chunk, 'Text'

        # Try boolean conversion first
        if chunk.dtype == 'object':
            unique_values = normalized_chunk.dropna().unique()
            boolean_values = {'true', 'false', 'yes', 'no', '1', '0', 't', 'f', 'y', 'n'}
            if len(unique_values) <= 2 and set(map(str, unique_values)).issubset(boolean_values):
                converted = normalized_chunk.map(
                    lambda x: True if str(x).lower() in {'true', 'yes', '1', 't', 'y'}
                    else False if str(x).lower() in {'false', 'no', '0', 'f', 'n'}
                    else None
                )
                return converted, 'Boolean'

        # Try numeric conversion
        try:
            cleaned_chunk = DataProcessingService._clean_numeric_string(chunk)
            numeric_chunk = pd.to_numeric(cleaned_chunk, errors='raise')

            # Check if it should be integer
            if numeric_chunk.dropna().apply(lambda x: float(x).is_integer()).all():
                return numeric_chunk.astype('Int64'), 'Integer'
            return numeric_chunk, 'Float'
        except (ValueError, TypeError):
            pass

        # Try datetime conversion
        try:
            datetime_chunk = pd.to_datetime(chunk, errors='raise')
            return datetime_chunk, 'Datetime'
        except (ValueError, TypeError):
            pass

        # Check for categorical
        unique_count = normalized_chunk.dropna().nunique()
        total_count = len(normalized_chunk.dropna())

        if (total_count >= 30 and
                unique_count <= 10 and
                unique_count < 0.2 * total_count and
                total_count >= unique_count * 3):
            return chunk.astype('category'), 'Category'

        # Default to text
        return chunk, 'Text'

    @staticmethod
    def _normalize_values(chunk):
        """Normalize string values by stripping whitespace and converting to lowercase"""
        if chunk.dtype == 'object':
            return chunk.str.strip().str.lower()
        return chunk

    @staticmethod
    def _clean_numeric_string(chunk):
        """Clean numeric strings by removing commas"""
        if chunk.dtype == 'object':
            return chunk.str.replace(',', '')
        return chunk