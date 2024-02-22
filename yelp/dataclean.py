import pandas as pd

# Load the CSV file to check its content
file_path = 'Datapath on your local repo'

# Since the delimiter used was a pipe '|', we specify it when reading the CSV
# We also assume that the first row contains incorrect headers
df = pd.read_csv(file_path, delimiter='|', header=None)

# Correcting the headers manually
correct_headers = ['business_id', 'insertedAtTimestamp', 'name', 'address', 'coordinates', 'number_of_reviews', 'rating', 'zip_code', 'cuisine']

# Assign the correct headers to the DataFrame
df.columns = correct_headers

# Remove duplicate entries based on 'business_id'
df_unique = df.drop_duplicates(subset=['business_id'])

# Save the DataFrame with unique entries back to a new CSV file
unique_file_path = '/path/to/your/new/yelp_data_unique.csv'
df_unique.to_csv(unique_file_path, index=False, sep='|')

# Inform the user of completion
print(f"Duplicates removed. The file with unique entries has been saved to {unique_file_path}")