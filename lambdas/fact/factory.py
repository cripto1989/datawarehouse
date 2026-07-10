import os

from console_print_adapter import ConsolePrint
from local_print_adapter import LocalPrint
from local_storage_adapter import LocalStorageAdapter
from print_port import PrintPort
from s3_storage_adapter import S3StorageAdapter
from storage_port import StoragePort


def get_storage() -> StoragePort:
    if os.environ.get("ENV", "prod") == "prod":
        return S3StorageAdapter()
    return LocalStorageAdapter()


def get_printer() -> PrintPort:
    if os.environ.get("ENV", "prod") == "prod":
        return ConsolePrint()
    return LocalPrint()
