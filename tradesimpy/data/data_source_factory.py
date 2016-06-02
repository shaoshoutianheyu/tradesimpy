from QuandlDataSource import QuandlDataSource
from CSVDataSource import CSVDataSource

def create_data_source(data_source, csv_data_uri=None):
	data_source = data_source.lower()

	if(data_source == 'quandl'):
		return QuandlDataSource()
	elif(data_source == 'csv'):
		return CSVDataSource(csv_data_uri)
	else:
		raise NotImplementedError("The data source %s is not implemented." % data_source)

def create_data_sources(data_sources, csv_data_uri=None):
    unique_data_sources = list(set(data_sources))

    return {ds: create_data_source(ds, csv_data_uri) for ds in unique_data_sources}
