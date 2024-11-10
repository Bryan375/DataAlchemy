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
                    time.sleep(7)

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
        type_counts = {}  # Dictionary to count occurrences of each inferred type

        # Skip if already properly typed
        if current_type != 'Text' and (is_numeric_dtype(chunk) or is_datetime64_any_dtype(chunk)):
            type_counts[str(chunk.dtype)] = 1
            return chunk, current_type

        # Try datetime
        try:
            converted = pd.to_datetime(chunk, errors='raise')
            type_counts['Datetime'] = type_counts.get('Datetime', 0) + 1
            return converted, 'Datetime'
        except (ValueError, TypeError):
            pass

        # Try boolean
        if chunk.dtype == 'object':
            unique_values = chunk.dropna().str.lower().unique()
        else:
            unique_values = chunk.dropna().unique()

        if len(unique_values) == 2:
            boolean_values = {'true', 'false', 'yes', 'no', '1', '0'}
            if set(map(str, unique_values)).issubset(boolean_values):
                def map_to_boolean(value):
                    if pd.isna(value):
                        return None
                    value_str = str(value).lower()
                    if value_str in {'true', 'yes', '1'}:
                        return True
                    return False

                type_counts['Boolean'] = type_counts.get('Boolean', 0) + 1
                return chunk.map(map_to_boolean), 'Boolean'

        # Try integer
        try:
            if chunk.dropna().apply(lambda x: str(x).isdigit()).all():
                converted = chunk.astype('Int64')
                type_counts['Integer'] = type_counts.get('Integer', 0) + 1
                return converted, 'Integer'
        except ValueError:
            pass

        # Try float
        try:
            converted = pd.to_numeric(chunk)
            type_counts['Decimal'] = type_counts.get('Decimal', 0) + 1
            return converted, 'Decimal'
        except ValueError:
            pass

        # Check for categorical
        unique_count = chunk.nunique()
        total_count = len(chunk)
        if unique_count <= 10 and unique_count < 0.2 * total_count:
            type_counts['Category'] = type_counts.get('Category', 0) + 1
            return chunk.astype('category'), 'Category'

        # Default to text if no other type was consistently inferred
        type_counts['Text'] = type_counts.get('Text', 0) + 1
        
        # Determine the most common inferred type
        if type_counts:
            inferred_type = max(type_counts.items(), key=lambda x: x[1])[0]
        else:
            inferred_type = 'Text'

        return chunk, inferred_type
