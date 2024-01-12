import json
from typing import Any, Dict, List

import eurostat_api.request as request
from eurostat_api.datastructure_definition import DatastructureDefinition
from eurostat_api.filters import DimensionFilter, Filter, TimePeriodFilter
from eurostat_api.sdmx_data import SdmxData


class EurostatDataset:

    BASE_URL: str = (
        "https://ec.europa.eu/eurostat/api/dissemination/sdmx/3.0"
    )
    METADATA_BASE_URL: str = f"{BASE_URL}/structure/dataflow/ESTAT"
    DSD_BASE_URL: str = f"{BASE_URL}/structure/datastructure/ESTAT"
    DATA_BASE_URL: str = f"{BASE_URL}/data/dataflow/ESTAT"

    @classmethod
    def from_json_file(cls, json_filename: str):
        with open(json_filename, 'r') as file:
            json_data = json.load(file)
        if 'none_value' in json_data:
            dataset = cls(
                json_data['dataset'],
                json_data['language'],
                json_data['none_value']
            )
        else:
            dataset = cls(json_data['dataset'], json_data['language'])
        if 'dimension_filter' in json_data:
            dimension_filter = DimensionFilter(dataset)
            for dimension_id, values in json_data['dimension_filter'].items():
                dimension_filter.add(dimension_id, values)
            dataset.add_filter(dimension_filter)
        if 'time_period_filter' in json_data:
            time_period_filter = TimePeriodFilter(dataset)
            for operator, time_period in json_data['time_period_filter']:
                time_period_filter.add(
                    TimePeriodFilter.OPERATOR_MAPPING[operator], time_period
                )
            dataset.add_filter(time_period_filter)
        return dataset

    _dataset_id: str
    _language: str
    _none_value: Any
    _version: str
    _datastructure_definition: DatastructureDefinition
    _filters: List[Filter]
    _data: SdmxData

    def __init__(
        self, dataset_id: str, language: str, none_value: Any = "-"
    ):
        assert isinstance(dataset_id, str), "dataset_id must be a string!"

        self._dataset_id = dataset_id
        self._language = language
        self._none_value = none_value
        self._filters = []
        self._request_version()
        self._request_datastructure_definition()

    def _request_version(self):
        response = request.get(
            url=f"{self.METADATA_BASE_URL}/{self._dataset_id}/1.0",
            params={
                'compress': 'false',
                'format': 'json'
            },
            headers={
                'Accept-Language': self._language
            }
        )
        response.raise_for_status()
        data = response.json()
        self._version = data['extension']['datastructure']['version']

    def _request_datastructure_definition(self):
        response = request.get(
            url=f"{self.DSD_BASE_URL}/{self._dataset_id}/{self._version}",
            params={
                'compress': 'false'
            },
            headers={
                'Accept-Language': self._language
            }
        )
        response.raise_for_status()
        self._datastructure_definition = DatastructureDefinition(
            response.content
        )

    def _request_data(self) -> Dict[str, Any]:
        params = {
            'compress': 'false',
            'format': 'json'
        }
        for filter_ in self._filters:
            params.update(filter_.url_parameters)
        response = request.get(
            url=f"{self.DATA_BASE_URL}/{self._dataset_id}/1.0/*",
            params=params,
            headers={
                'Accept-Language': self._language
            }
        )
        response.raise_for_status()
        return response.json()

    def add_filter(self, filter_: Filter):
        self._filters.append(filter_)

    def request_data(self):
        self._data = SdmxData(self._request_data(), self._none_value)

    @property
    def dimension_ids(self) -> List[str]:
        return self._datastructure_definition.dimension_ids

    @property
    def data(self) -> SdmxData:
        return self._data

    @property
    def none_value(self) -> str:
        return self._none_value
