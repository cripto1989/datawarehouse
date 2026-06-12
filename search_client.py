from abc import ABC, abstractmethod
import os

import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth


class SearchClient(ABC):

    @abstractmethod
    def build_client(self):
        pass


class OpenSearchClient(SearchClient):

    def __init__(
        self, region: str, endpoint: str, username: str, password: str, port: int = 443
    ):
        self.region = region
        self.endpoint = endpoint
        self.username = username
        self.password = password
        self.port = port

    def build_client(self):
        return OpenSearch(
            hosts=[{"host": self.endpoint, "port": self.port}],
            http_auth=(self.username, self.password),
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection,
            timeout=30,
        )

    def _get_auth(self):
        credentials = boto3.Session().get_credentials()
        return AWS4Auth(
            credentials.access_key,
            credentials.secret_key,
            self.region,
            "es",
            session_token=credentials.token,
        )
