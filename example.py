# For an explanation see the README.md file.

# ## Requesting data

from eurostat_api.dataset import EurostatDataset
from eurostat_api.filters import TimePeriodFilter, DimensionFilter

dataset = EurostatDataset('lfsi_emp_a', 'de')

dimension_filter = DimensionFilter(dataset)
dimension_filter.add_dimension_value('age', 'Y20-64')
dimension_filter.add_dimension_value('indic_em', 'EMP_LFS')
dimension_filter.add_dimension_value('unit', 'PC_POP')
dimension_filter.add('sex', ['M', 'F'])

time_period_filter = TimePeriodFilter(dataset)
time_period_filter.add(TimePeriodFilter.Operators.GREATER_OR_EQUALS, "2022")

dataset.request_data()

print(dataset.data.dataframe)

# ## Metadata and structure data

print(dataset.data.updated)
print(dataset.data.dimension_ids)
print(dataset.data.dataframe_columns)
print(dataset.data.data_shape)
print(dataset.data.dimension_value_labels)
print(dataset.data.language)
print(dataset.data.observation_count)
print(dataset.data.latest_period)
print(dataset.data.oldest_period)
print(dataset.data.status_labels)

# ## Other functions

# ### Last point in time with specific data "fill level"
fill_level = 0.8  # 80 % filled
time_period = dataset.data.get_latest_time_value_with(fill_level, {'sex': 'F'})
print(time_period)

# ### Index dataframe
print(dataset.data.index_dataframe)

# ### Pivot table
print(dataset.data.get_pivot_table({'sex': 'F'}))

# ### Status pivot table
print(dataset.data.get_status_pivot_table({'sex': 'F'}))
