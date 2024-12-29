from pytrends.request import TrendReq
import random, time

# Initialize pytrends
pytrends = TrendReq(hl='en-US', tz=360)

# Define the keyword list
keyword = ['Abel Gurrola', 'Andrew Closson', 'Andrew Layton', 'Mark Chavez', 'Michael Brown']



# Get interest over time
retries = 5
backoff_factor = 1
for attempt in range(retries):
    try:
        pytrends.build_payload(keyword, cat=0, geo='US', timeframe='2012-01-01 2016-12-31')
        interest_over_time_df = pytrends.interest_over_time()
        interest_over_time_df = interest_over_time_df.drop(columns = ['isPartial'])
        break
    except Exception as e:
        if attempt < retries - 1:
            wait_time = (2 ** attempt) * backoff_factor + random.uniform(0,1)
            time.sleep(wait_time)
        else:
            print(f'Failed after {retries} attempts.')
            interest_over_time_df = None
            interest_over_time_df = interest_over_time_df.drop(columns = ['isPartial'])
            break

# Print the values
df_transposed = interest_over_time_df.transpose()
df_transposed.columns.name = 'Names'
print(df_transposed)
