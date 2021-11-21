import re
import pandas as pd
from pathlib import Path
from datetime import datetime

DATA_BASE_DIR = 'data'

FILE_PATTERN = 'growbox_data_(sensor|fake)_(?P<date>\d{8})-(?P<hour>\d{1,2})\.csv'

def get_data(data_dir, start=None, end=None):
	data_dir = Path(DATA_BASE_DIR) / data_dir
	all_files =data_dir.glob('*.csv')
	# Get files that fall within the date range
	# files_in_range = []
	# for file in Path(data_dir).glob('*.csv'):
	# 	match = re.match(FILE_PATTERN, file.name)
	# 	date = match['date']
	# 	hour = match['hour']
	# 	file_start = datetime(
	# 		year=int(date[:4]),
	# 		month=int(date[4:6]),
	# 		day=int(date[6:]),
	# 		hour=int(hour)
	# 	)
	# 	condition = start is not None
	# 	if start is not None and file_start >= start:
	dfs = [pd.read_csv(f) for f in all_files if re.match(FILE_PATTERN, f.name)]
	return pd.concat(dfs).sort_values(by='time')