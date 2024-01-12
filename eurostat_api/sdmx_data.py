import datetime as dt
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd


class SdmxData:

    _json_data: Dict[str, Any]
    _none_value: Any
    _updated: dt.datetime
    _annotations: Dict[str, str]
    _dataframe: pd.DataFrame
    _index_dataframe: pd.DataFrame

    def __init__(self, json_data: Dict[str, Any], none_value: Any):
        self._json_data = json_data
        self._none_value = none_value
        self._updated = dt.datetime.strptime(
            self._json_data['updated'], "%Y-%m-%dT%H:%M:%S%z"
        )
        self._extract_annotations()
        self._construct_dataframe()

    def _extract_annotations(self):
        self._annotations = {
            a['type']: (
                a.get('title', None)
                or a.get('text', None)
                or a.get('date', None)
            )
            for a in self._json_data['extension']['annotation']
        }

    def _get_all_dimension_values(self) -> List[np.ndarray]:
        dimension_data = self._json_data['dimension']
        return [
            np.array([
                value for value
                in dimension_data[d_id]['category']['index'].keys()
            ])
            for d_id in self._json_data['id']
        ]

    def _get_observation_ids(self) -> np.ndarray:
        return np.array(
            list(self._json_data['value'].keys())
            + (
                list(self._json_data['status'].keys())
                if 'status' in self._json_data
                else []
            ),
            dtype=int
        )

    def _get_observation_values(
        self, observation_ids: np.ndarray
    ) -> np.ndarray:
        if 'value' not in self._json_data:
            return np.full(observation_ids.shape, self._none_value)
        return np.array([
            self._json_data['value'].get(str(obs_id), self._none_value)
            for obs_id in observation_ids
        ])

    def _get_status_values(
        self, observation_ids: np.ndarray
    ) -> np.ndarray:
        if 'status' not in self._json_data:
            return np.full(observation_ids.shape, self._none_value)
        return np.array([
            self._json_data['status'].get(str(obs_id), self._none_value)
            for obs_id in observation_ids
        ])

    def _get_dimension_indices(
        self, observation_ids: np.ndarray
    ) -> np.ndarray:
        dimension_indices = np.zeros(
            (len(observation_ids), len(self.data_shape)),
            dtype=int
        )
        for i, size in enumerate(reversed(self.data_shape)):
            observation_ids, dimension_indices[:, -i - 1] = divmod(
                observation_ids, size
            )
        return dimension_indices

    def _get_dimension_values(
        self,
        dimension_indices: np.ndarray,
        all_dimension_values: List[np.ndarray]
    ) -> np.ndarray:
        return np.array([
            specific_dimension_values[dimension_indices[:, i]]
            for i, specific_dimension_values in enumerate(
                all_dimension_values
            )
        ]).T

    def _get_dataframe_data(
        self,
        data: np.ndarray,
        status_values: np.ndarray,
        observation_values: np.ndarray
    ):
        data = np.hstack((
            data,
            status_values[:, None],
            observation_values[:, None]
        ))
        return data

    def _construct_dataframe(self):
        observation_ids = self._get_observation_ids()
        dimension_indices = self._get_dimension_indices(observation_ids)
        all_dimension_values = self._get_all_dimension_values()
        dimension_values = self._get_dimension_values(
            dimension_indices, all_dimension_values
        )
        status_values = self._get_status_values(observation_ids)
        observation_values = self._get_observation_values(observation_ids)
        dataframe_data = self._get_dataframe_data(
            dimension_values, status_values, observation_values
        )
        index_dataframe_data = self._get_dataframe_data(
            dimension_indices, status_values, observation_values
        )

        df = pd.DataFrame(
            dataframe_data, columns=self.dataframe_columns
        )
        df['status'] = df.groupby(
            [c for c in list(df.columns) if c != 'status']
        )['status'].transform(lambda x: "".join(set("".join(x))))
        df = df.drop_duplicates()
        self._dataframe = df

        df = pd.DataFrame(
            index_dataframe_data, columns=self.dataframe_columns
        )
        df['status'] = df.groupby(
            [c for c in list(df.columns) if c != 'status']
        )['status'].transform(lambda x: "".join(set("".join(x))))
        df = df.drop_duplicates()
        self._index_dataframe = df

    def _get_pivot_table(
        self, dimension_values: Dict[str, str], value_column: str
    ) -> pd.DataFrame:
        assert 'time' not in dimension_values, \
            "time must not be in dimension_values!"
        assert 'geo' not in dimension_values, \
            "geo must not be in dimension_values!"

        dimension_ids_to_drop = self.dimension_ids[:]
        dimension_ids_to_drop.remove('time')
        dimension_ids_to_drop.remove('geo')

        df = self.dataframe.copy()
        for dimension_id, value in dimension_values.items():
            df = df[df[dimension_id] == value]

        columns_to_drop = dimension_ids_to_drop + [
            'status' if value_column == 'observation' else 'observation'
        ]
        df = df.drop(columns=columns_to_drop)

        return df.pivot(
            index='geo', columns='time', values=value_column
        ).fillna(self._none_value)

    def get_pivot_table(
        self, dimension_values: Dict[str, str]
    ) -> pd.DataFrame:
        return self._get_pivot_table(dimension_values, 'observation')

    def get_status_pivot_table(
        self, dimension_values: Dict[str, str]
    ) -> pd.DataFrame:
        return self._get_pivot_table(dimension_values, 'status')

    def get_latest_time_value_with(
        self,
        fill_level: float,
        dimension_values: Dict[str, str]
    ) -> str:
        df = self._dataframe.copy()
        for dimension_id, value in dimension_values.items():
            df = df[df[dimension_id] == value]
        time_values = set(df['time'])

        max_count = 0
        for time_value in time_values:
            max_count = max(
                max_count,
                df[df['time'] == time_value]['observation'].count()
            )

        for time_value in reversed(sorted(time_values)):
            count = df[df['time'] == time_value]['observation'].count()
            if count / max_count >= fill_level:
                return time_value

        return None

    @property
    def updated(self) -> dt.datetime:
        return self._updated

    @property
    def dimension_ids(self) -> List[str]:
        return self._json_data['id']

    @property
    def dataframe_columns(self) -> List[str]:
        return self.dimension_ids + ['status', 'observation']

    @property
    def data_shape(self) -> Tuple[int]:
        return tuple(self._json_data['size'])

    @property
    def dimension_labels(self) -> Dict[str, str]:
        return {
            d_id: self._json_data['dimension'][d_id]['label']
            for d_id in self.dimension_ids
        }

    @property
    def dimension_value_labels(self) -> Dict[str, Dict[str, str]]:
        dimension_data = self._json_data['dimension']
        return {
            d_id: {
                value: dimension_data[d_id]['category']['label'][value]
                for value in dimension_data[d_id]['category']['index']
            }
            for d_id in self.dimension_ids
        }

    @property
    def language(self) -> str:
        return self._json_data['extension']['lang'].lower()

    @property
    def observation_count(self) -> int:
        return int(self._annotations['OBS_COUNT'])

    @property
    def latest_period(self) -> str:
        return self._annotations.get('OBS_PERIOD_OVERALL_LATEST', None)

    @property
    def oldest_period(self) -> str:
        return self._annotations.get('OBS_PERIOD_OVERALL_OLDEST', None)

    @property
    def status_labels(self) -> Dict[str, str]:
        if 'status' not in self._json_data:
            return {}
        return {
            status: self._json_data['extension']['status']['label'][status]
            for status in self._json_data['extension']['status']['label']
        }

    @property
    def dataframe(self) -> pd.DataFrame:
        return self._dataframe

    @property
    def index_dataframe(self) -> pd.DataFrame:
        return self._index_dataframe
