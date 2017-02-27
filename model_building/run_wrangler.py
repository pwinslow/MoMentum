'''
This file runs all the methods in the wrangler class to load and clean the
data before extracting numerical features. It then filters outliers and
rescales features. Since the total raw data is only ~150MB, after each
processing step the data is saved to a PostgresSQL database in an attempt
at basic fault tolerance for each of the methods.
'''

from wrangler import Wrangler

# Create wrangler instance
wrangler = Wrangler()

# Load data
df = wrangler.load_from_csv("../data/api_data/")

# Clean data
df = wrangler.drop_nulls_and_duplicates(df)
wrangler.save_to_db(df, "raw_data")

# Extract numerical features from raw data
df = wrangler.reformat_df(df)
wrangler.save_to_db(df, "reformatted_data")

# Filter outliers
df = wrangler.filter_outliers(df)
wrangler.save_to_db(df, "filtered_outlier_data")

# Rescale numerical features
df, norm_dict = wrangler.feature_scaling(df, "max")
wrangler.save_to_db(df, "rescaled_data")
