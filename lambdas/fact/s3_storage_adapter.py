import awswrangler as wr
import pandas as pd
from storage_port import StoragePort


class S3StorageAdapter(StoragePort):
    def read_json(self, path: str) -> pd.DataFrame:
        return wr.s3.read_json(path, lines=True)

    def read_parquet(self, path: str) -> pd.DataFrame:
        return wr.s3.read_parquet(path)

    def write_parquet(self, df: pd.DataFrame, path: str):
        wr.s3.to_parquet(
            df=df,
            path=path,
            dataset=True,
            mode="overwrite_partitions",
            # TODO Enabling these two values allow sync our database/table, it requires the right permissions.
            # database="default",
            # table="thf_events",
            partition_cols=["machine_id", "year", "month", "day"],
        )
        pass
