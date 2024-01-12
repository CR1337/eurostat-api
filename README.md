# eurostat-api

A python API to make simple Eurostat database requests.

If you use this software, please cite it using the button in the right column of the repository's main page.

# Setup

## Linux

1. Clone this repository
```bash
git clone https://github.com/CR1337/eurostat-api.git
```

2. Change directory
```bash
cd eurostat-api
```

3. Create a virtual environment
```bash
python3 -m venv .venv
```

4. Activate the virtual environment
```bash
source .venv/bin/activate
```

5. Install the requirements
```bash
pip install -r requirements.txt
```

6. Test if `example.py` works
```bash
python example.py
```

## Windows

1. Clone this repository
```bash
git clone https://github.com/CR1337/eurostat-api.git
```

2. Change directory
```bash
cd eurostat-api
```

3. Create a virtual environment
```bash
python -m venv .venv
```

4. Activate the virtual environment
```bash
.venv\Scripts\activate
```

5. Install the requirements
```bash
pip install -r requirements.txt
```

6. Test if `example.py` works
```bash
python example.py
```

# Usage

## Requesting data

Import the classes `EurostatDataset`, `DimensionFilter` and `TimePeriodFilter`.
```python
from eurostat_api.dataset import EurostatDataset
from eurostat_api.filters import DimensionFilter, TimePeriodFilter
```

Create a new `EurostatDataset` object with a dataset id and a language. The languages `de`, `en` and `fr` are supported.
```python
dataset = EurostatDataset('lfsi_emp_a', 'de')
```

Define a dimension filter and specify what values should be included.
```python
dimension_filter = DimensionFilter(dataset)

dimension_filter.add_dimension_value('age', 'Y20-64')
dimension_filter.add_dimension_value('indic_em', 'EMP_LFS')
dimension_filter.add_dimension_value('unit', 'PC_POP')

dimension_filter.add('sex', ['M', 'F'])
```

Define a time period filter and specify the time period. Possible operators are `EQUALS`, `GREATER_OR_EQUALS`, `GREATER`, `LOWER_OR_EQUALS` and `LOWER`.
```python
time_period_filter = TimePeriodFilter(dataset)

time_period_filter.add(TimePeriodFilter.Operators.GREATER_OR_EQUALS, "2022")
```

Perform the request.
```python
dataset.request_data()
```

There you have the data:
```python
print(dataset.data.dataframe)
```

```
>>>    freq indic_em sex     age    unit geo  time status observation
>>> 0     A  EMP_LFS   F  Y20-64  PC_POP  AT  2022      -        73.4
>>> 1     A  EMP_LFS   F  Y20-64  PC_POP  BE  2022      -        68.1
>>> 2     A  EMP_LFS   F  Y20-64  PC_POP  BG  2022      -        71.8
>>> 3     A  EMP_LFS   F  Y20-64  PC_POP  CH  2022      -        77.8
>>> 4     A  EMP_LFS   F  Y20-64  PC_POP  CY  2022      -        72.1
>>> ..  ...      ...  ..     ...     ...  ..   ...    ...         ...
>>> 61    A  EMP_LFS   M  Y20-64  PC_POP  RO  2022      -        77.7
>>> 62    A  EMP_LFS   M  Y20-64  PC_POP  RS  2022      -        76.2
>>> 63    A  EMP_LFS   M  Y20-64  PC_POP  SE  2022      -        85.0
>>> 64    A  EMP_LFS   M  Y20-64  PC_POP  SI  2022      -        81.2
>>> 65    A  EMP_LFS   M  Y20-64  PC_POP  SK  2022      -        80.7
>>>
>>> [66 rows x 9 columns]
```

## Metadata and structure data

### Time of last update
```python
print(dataset.data.updated)
```
```
>>> 2023-12-14 23:00:00+01:00
```

### All dimensions of the dataset
```python
print(dataset.data.dimension_ids)
```
```
>>> ['freq', 'indic_em', 'sex', 'age', 'unit', 'geo', 'time']
```

### All columns of the dataframe
```python
print(dataset.data.dataframe_columns)
```
```
>>> ['freq', 'indic_em', 'sex', 'age', 'unit', 'geo', 'time', 'status', 'observation']
```

### The amount of available values per dimension
```python
print(dataset.data.data_shape)
```
```
>>> (1, 1, 2, 1, 1, 36, 1)
```

### The meaning of the values of the dimensions (lanugae dependent)
```python
print(dataset.data.dimension_value_labels)
```
```
>>> {'freq': {'A': 'Jährlich'}, 'indic_em': {'EMP_LFS': 'Beschäftigung insgesamt (Wohnbevölkerung - AKE)'}, 'sex': {'M': 'Männer', 'F': 'Frauen'}, 'age': {'Y20-64': '20 bis 64 Jahre'}, 'unit': {'PC_POP': 'Prozent der Bevölkerung insgesamt'}, 'geo': {'EU27_2020': 'Europäische Union - 27 Länder (ab 2020)', 'EA20': 'Euroraum - 20 Länder (ab 2023)', 'BE': 'Belgien', 'BG': 'Bulgarien', 'CZ': 'Tschechien', 'DK': 'Dänemark', 'DE': 'Deutschland', 'EE': 'Estland', 'IE': 'Irland', 'EL': 'Griechenland', 'ES': 'Spanien', 'FR': 'Frankreich', 'HR': 'Kroatien', 'IT': 'Italien', 'CY': 'Zypern', 'LV': 'Lettland', 'LT': 'Litauen', 'LU': 'Luxemburg', 'HU': 'Ungarn', 'MT': 'Malta', 'NL': 'Niederlande', 'AT': 'Österreich', 'PL': 'Polen', 'PT': 'Portugal', 'RO': 'Rumänien', 'SI': 'Slowenien', 'SK': 'Slowakei', 'FI': 'Finnland', 'SE': 'Schweden', 'IS': 'Island', 'NO': 'Norwegen', 'CH': 'Schweiz', 'ME': 'Montenegro', 'MK': 'Nordmazedonien', 'RS': 'Serbien', 'TR': 'Türkei'}, 'time': {'2022': '2022'}}
```

### The selected language
```python
print(dataset.data.language)
```
```
>>> de
```

### The amount of observations (amount of rows in the dataframe)
```python
print(dataset.data.observation_count)
```
```
>>> 35952
```

### The last point in time where data is available
```python
print(dataset.data.latest_period)
```
```
>>> 2022
```

### The earliest point in time where data is available
``` python
print(dataset.data.oldest_period)
```
```
>>> 2003
```

### The meanings of the status labels (language dependent)
```python
print(dataset.data.status_labels)
```
```
>>> {'d': 'abweichende Definition (siehe Metadaten)'}
```

## Other functions

### Last point in time with specific data "fill level"

The `get_latest_time_value_with` function can be used to find the last time at which the data has at least a certain "fill level". To do this, you only need to pass the desired "fill level" and, if necessary, a restriction for the values of the dimensions. If the dimensions are not to be further restricted, it is sufficient to pass `{}`.
```python
fill_level = 0.8  # 80 % filled
time_period = dataset.data.get_latest_time_value_with(fill_level, {'sex': 'F'})
print(time_period)
```
```
>>> 2022
```

### Index dataframe

In addition to the actual DataFrame, a so-called index DataFrame can also be created. In this, the dimension values are not specified as actual values, but as indices for `dataset.data.dimension_value_labels`.
```python
print(dataset.data.index_dataframe)
```
```
>>>    freq indic_em sex age unit geo time status observation
>>> 0     0        0   1   0    0  21    0      -        73.4
>>> 1     0        0   1   0    0   2    0      -        68.1
>>> 2     0        0   1   0    0   3    0      -        71.8
>>> 3     0        0   1   0    0  31    0      -        77.8
>>> 4     0        0   1   0    0  14    0      -        72.1
>>> ..  ...      ...  ..  ..  ...  ..  ...    ...         ...
>>> 61    0        0   0   0    0  24    0      -        77.7
>>> 62    0        0   0   0    0  34    0      -        76.2
>>> 63    0        0   0   0    0  28    0      -        85.0
>>> 64    0        0   0   0    0  25    0      -        81.2
>>> 65    0        0   0   0    0  26    0      -        80.7
>>>
>>> [66 rows x 9 columns]
```

### Pivot table

A pivot table compares one dimension with another. The only meaningful combination in this case is the location and time. Such a table can be created with `get_pivot_table`. Each other dimension may only contain one value. Restrictions for the dimension values can simply be passed to the function. If no restriction is necessary, it is sufficient to pass `{}`.
```python
print(dataset.data.get_pivot_table({'sex': 'F'}))
```
```
>>> time       2022
>>> geo
>>> AT         73.4
>>> BE         68.1
>>> BG         71.8
>>> CH         77.8
>>> CY         72.1
>>> CZ         73.7
>>> DE         76.8
>>> DK         77.4
>>> EA20       69.0
>>> EE         80.4
>>> EL         55.9
>>> ES         64.1
>>> EU27_2020  69.3
>>> FI         77.8
>>> FR         71.2
>>> HR         65.0
>>> HU         75.3
>>> IE         72.6
>>> IS         82.1
>>> IT         55.0
>>> LT         78.6
>>> LU         71.5
>>> LV         75.5
>>> MT         74.1
>>> NL         79.0
>>> NO         78.0
>>> PL         70.2
>>> PT         74.3
>>> RO         59.1
>>> RS         62.3
>>> SE         79.2
>>> SI         74.3
>>> SK         72.6
```

### Status pivot table
The `get_status_pivot_table` function works in exactly the same way as `get_pivot_table`. The resulting table does not contain the data, but the status of the data.
```python
print(dataset.data.get_status_pivot_table({'sex': 'F'}))
```
```
>>> time      2022
>>> geo
>>> AT           -
>>> BE           -
>>> BG           -
>>> CH           -
>>> CY           -
>>> CZ           -
>>> DE           -
>>> DK           -
>>> EA20         -
>>> EE           -
>>> EL           -
>>> ES           d
>>> EU27_2020    -
>>> FI           -
>>> FR           d
>>> HR           -
>>> HU           -
>>> IE           -
>>> IS           -
>>> IT           -
>>> LT           -
>>> LU           -
>>> LV           -
>>> MT           -
>>> NL           -
>>> NO           -
>>> PL           -
>>> PT           -
>>> RO           -
>>> RS           -
>>> SE           -
>>> SI           -
>>> SK           -
```