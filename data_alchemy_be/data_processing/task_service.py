import logging
import time
from typing import Dict, Callable, Any
import pandas as pd
from .models import Dataset, Column

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
            total_rows = 0
            processed_rows = 0

            file_type = dataset.file_type
            logger.debug(f'file: {file_type}')
            chunks = None

            if file_type == 'csv':
                chunks = pd.read_csv(
                    dataset.file.path,
                    chunksize=cls.CHUNK_SIZE
                )
                logger.debug(f'chunks: {chunks}')


            first_chunk = next(chunks)
            total_rows = len(first_chunk)

            # Update initial progress
            if progress_callback:
                progress_callback(
                    progress={'processed_rows': 0, 'total_rows': total_rows},
                    stage='Analyzing column types'
                )

            time.sleep(30)

            # Process columns from first chunk
            columns_info = {}
            for pos, col_name in enumerate(first_chunk.columns):
                logger.debug(f'col_name: {col_name}, pos: {pos}')
                # Infer column type
                col_type, stats = cls._infer_column_type(first_chunk[col_name])

                # Create column record
                Column.objects.create(
                    dataset=dataset,
                    name=col_name,
                    position=pos,
                    inferred_type=col_type,
                    current_type=col_type,
                    unique_values_count=stats.get('unique_count', 0),
                    null_count =stats.get('null_count', 0),
                    sample_values =stats.get('sample_values', []),
                    statistics=stats
                )

                columns_info[col_name] = {
                    'type': col_type,
                    'stats': stats
                }

                # Update column analysis progress
                if progress_callback:
                    progress = (pos + 1) / len(first_chunk.columns) * 20
                    progress_callback(
                        progress={
                            'processed_rows': 0,
                            'total_rows': total_rows,
                            'progress': progress
                        },
                        stage=f'Analyzing column: {col_name}'
                    )
                time.sleep(30)

            # Process remaining chunks for statistics
            for chunk_num, chunk in enumerate(chunks, 1):
                # Update total rows count
                total_rows += len(chunk)
                processed_rows += len(chunk)

                # Update statistics for each column
                for col_name, info in columns_info.items():
                    column_data = chunk[col_name]
                    cls._update_column_statistics(
                        dataset.columns.get(name=col_name),
                        column_data,
                        info['type']
                    )

                # Update progress
                if progress_callback:
                    progress = 20 + (processed_rows / total_rows * 80)
                    progress_callback(
                        progress={
                            'processed_rows': processed_rows,
                            'total_rows': total_rows,
                            'progress': progress
                        },
                        stage=f'Processing batch {chunk_num}'
                    )

            # Update dataset metadata
            dataset.rows_count = total_rows
            dataset.columns_count = len(columns_info)
            dataset.save()

            return {
                'total_rows': total_rows,
                'total_columns': len(columns_info),
                'columns': columns_info
            }

        except Exception as e:
            raise Exception(f"Error processing dataset: {str(e)}")

    @staticmethod
    def _infer_column_type(series: pd.Series) -> tuple[str, Dict]:
        """Infer column type from data sample."""
        # Take a sample for type inference
        sample = series.dropna().head(1000)
        stats = {
            'null_count': int(series.isnull().sum()),
            'unique_count': int(series.nunique()),
            'sample_values': series.dropna().head(5).tolist()
        }
        logger.debug(f'stats: {stats}')

        try:
            # Try numeric conversion
            pd.to_numeric(sample)
            # Check if integers
            if all(float(x).is_integer() for x in sample):
                return 'INTEGER', stats
            return 'FLOAT', stats
        except:
            pass

        # Try datetime
        try:
            pd.to_datetime(sample)
            return 'DATETIME', stats
        except:
            pass

        # Check for boolean
        if set(sample.unique()) <= {'True', 'False', True, False, 0, 1}:
            return 'BOOLEAN', stats

        # Default to text
        return 'TEXT', stats

    @staticmethod
    def _update_column_statistics(
            column: Column,
            series: pd.Series,
            data_type: str
    ) -> None:
        """Update column statistics with new batch of data."""
        stats = column.statistics or {}

        # Update basic stats
        stats['null_count'] = stats.get('null_count', 0) + int(series.isnull().sum())
        stats['unique_count'] = len(set(stats.get('sample_values', []) + series.dropna().head(5).tolist()))

        # Update type-specific stats
        if data_type in ['INTEGER', 'FLOAT']:
            numeric_series = pd.to_numeric(series, errors='coerce')
            current_min = stats.get('min')
            current_max = stats.get('max')

            if not pd.isna(numeric_series.min()):
                stats['min'] = min(
                    numeric_series.min(),
                    current_min if current_min is not None else float('inf')
                )

            if not pd.isna(numeric_series.max()):
                stats['max'] = max(
                    numeric_series.max(),
                    current_max if current_max is not None else float('-inf')
                )

        column.statistics = stats
        column.save()