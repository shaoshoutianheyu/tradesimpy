from QuandlDataSource import QuandlDataSource
from CSVDataSource import CSVDataSource

def create_data_source(data_source):
	data_source = data_source.lower()

	if(data_source == 'quandl'):
		return QuandlDataSource()
	elif(data_source == 'csv'):
		return CSVDataSource()
	else:
		raise NotImplementedError("The data source %s is not implemented." % data_source)

def create_data_sources(data_sources):
    unique_data_sources = list(set(data_sources))

    return {ds: create_data_source(ds) for ds in unique_data_sources}
