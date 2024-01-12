from abc import ABC, abstractproperty, abstractmethod
from typing import Dict, List, Protocol, Tuple


class IEurostatDataset(Protocol):

    @property
    def dimension_ids(self) -> List[str]:
        ...


class Filter(ABC):

    _dataset: IEurostatDataset

    def __init__(self, dataset: IEurostatDataset):
        self._dataset = dataset
        self._dataset.add_filter(self)

    @abstractproperty
    def url_parameters(self) -> Dict[str, str]:
        raise NotImplementedError()

    @abstractmethod
    def is_dimension_filter(self) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def is_time_period_filter(self) -> bool:
        raise NotImplementedError()


class DimensionFilter(Filter):

    _dimension_values: Dict[str, List[str]]

    def __init__(self, dataset: IEurostatDataset):
        super().__init__(dataset)
        self._dimension_values = {}

    def add(self, dimension_id: str, values: List[str]):
        if dimension_id not in self._dimension_values:
            self._dimension_values[dimension_id] = []
        self._dimension_values[dimension_id].extend(values)

    def add_dimension_value(self, dimension_id: str, value: str):
        assert isinstance(dimension_id, str), "dimension_id must be a string!"
        assert isinstance(value, str), "value must be a string!"
        assert dimension_id in self._dataset.dimension_ids, \
            f"Dimension {dimension_id} must be in dataset!"

        if dimension_id not in self._dimension_values:
            self._dimension_values[dimension_id] = []
        self._dimension_values[dimension_id].append(value)

    @property
    def url_parameters(self) -> Dict[str, str]:
        return {
            f'c[{dimension_id}]': ','.join(values)
            for dimension_id, values in self._dimension_values.items()
        }

    def is_dimension_filter(self) -> bool:
        return True

    def is_time_period_filter(self) -> bool:
        return False


class TimePeriodFilter(Filter):

    class Operators:
        EQUALS: str = 'eq'
        GREATER_OR_EQUALS: str = 'ge'
        GREATER: str = 'gt'
        LOWER_OR_EQUALS: str = 'le'
        LOWER: str = 'lt'

    class OperatorStrings:
        EQUALS: str = "="
        GREATER_OR_EQUALS: str = ">="
        GREATER: str = ">"
        LOWER_OR_EQUALS: str = "<="
        LOWER: str = "<"

    OPERATOR_MAPPING: Dict[str, str] = {
        OperatorStrings.EQUALS: Operators.EQUALS,
        OperatorStrings.GREATER_OR_EQUALS: Operators.GREATER_OR_EQUALS,
        OperatorStrings.GREATER: Operators.GREATER,
        OperatorStrings.LOWER_OR_EQUALS: Operators.LOWER_OR_EQUALS,
        OperatorStrings.LOWER: Operators.LOWER
    }

    _operators_periods: List[Tuple[str, str]]

    def __init__(self, dataset: IEurostatDataset):
        super().__init__(dataset)
        self._operators_periods = []

    def add(self, operator: str, time_period: str):
        assert isinstance(operator, str), "operator must be a string!"
        assert isinstance(time_period, str), "time_period must be a string!"
        assert operator in (
            self.Operators.EQUALS, self.Operators.GREATER_OR_EQUALS,
            self.Operators.GREATER,
            self.Operators.LOWER_OR_EQUALS, self.Operators.LOWER
        ), f"Operator '{operator}' not supported!"

        self._operators_periods.append((operator, time_period))

    @property
    def url_parameters(self) -> Dict[str, str]:
        return {
            'c[TIME_PERIOD]': '+'.join(
                f"{operator}:{time_period}"
                for operator, time_period in self._operators_periods
            )
        }

    def is_dimension_filter(self) -> bool:
        return False

    def is_time_period_filter(self) -> bool:
        return True
