#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec  9 14:16:39 2024

@author: taehokim
"""
######################################################
# Overview of the Code Task:
# This script gathers Google Trends data for a research project focused on police use of force incidents.
# The goal is to retrieve trends for victim names for all the incidents in a way to compare all of them in a consistent way. 
# The script processes data in batches of 4 names at a time (along with a common keyword ("Michael Brown")), collects Google Trends data, reshapes it into a
# wide format, and appends the data to a CSV file. The trends data is collected for the years 2012-2016.

# Key Steps:
# 1. Load and filter incident data to 2013-2016.
# 2. Extract and clean first and last names from the victim’s name column.
# 3. Build keyword lists for Google Trends, ensuring the inclusion of "Michael Brown" for comparison.
# 4. Collect Google Trends data for each batch of 4 names, ensuring that "Michael Brown" is included in each query.
# 5. Reshape the data and add the "Michael Brown" data as new columns for consistency.
# 6. Append the processed data to a CSV file, ensuring each batch is added incrementally.

# Libraries required for the code
import os
import pandas as pd 
import numpy as np
import random
import itertools
import unicodedata
import re
import getpass
import sys
import math 
import copy
import time
from pytrends.request import TrendReq
import plotly.express as px


# Set path to your working directory
username = getpass.getuser()
path_ = "C:/MyProjects/WebScraping/Upwork/Ahmad/Job5"
os.chdir(path_)

# Load the dataset with incidents
sample = pd.read_csv('C:/MyProjects/WebScraping/Upwork/Ahmad/Job5/MPVDatasetDownload.csv', encoding='latin1')

# Convert the date column to datetime format
sample['Date of Incident (month/day/year)'] = pd.to_datetime(sample['Date of Incident (month/day/year)'], errors='coerce')

# Filter rows between 2013 and 2016
filtered_sample = sample[(
    sample['Date of Incident (month/day/year)'].dt.year >= 2013) & 
    (sample['Date of Incident (month/day/year)'].dt.year <= 2016)
]

columns_to_keep = ["Victim's name", "Date of Incident (month/day/year)", "Agency responsible for death"]
filtered_sample = filtered_sample[columns_to_keep]

# Define a set of common suffixes
SUFFIXES = {"Jr.", "Sr.", "II", "III", "IV", "V"}

# Define a function to extract first and last names
def extract_first_last_name(full_name):
    # Split the name into parts
    parts = full_name.split()
    
    # Handle edge cases
    if len(parts) == 0:  # Empty string
        return "", ""
    elif len(parts) == 1:  # Only one part, assume it's the first name
        return parts[0], ""
    else:
        # Check if the last part is a suffix
        last_name = parts[-1]
        if last_name in SUFFIXES and len(parts) > 2:  # If there's a suffix, get the second-to-last as the last name
            last_name = parts[-2]
            first_name = parts[0]
        else:  # Otherwise, treat the last part as the last name
            first_name = parts[0]
            last_name = parts[-1]
        return first_name, last_name

# Apply the function to the "Victim's name" column
filtered_sample[['First Name', 'Last Name']] = filtered_sample["Victim's name"].apply(
    lambda x: pd.Series(extract_first_last_name(x))
)

# Sort the sample by the date of the incident
filtered_sample = filtered_sample.sort_values(by='Date of Incident (month/day/year)')

# Drop duplicates based on 'First Name' and 'Last Name', keeping the earliest occurrence
filtered_sample = filtered_sample.drop_duplicates(subset=['First Name', 'Last Name'], keep='first')

# Remove rows where 'Last Name' equals 'police' (case-insensitive)
filtered_sample = filtered_sample[~filtered_sample['Last Name'].str.lower().eq('police')]

# Initialize pytrends
pytrends = TrendReq(hl='en-US', tz=360)

# Get Google Trends for four items at a time including "Michael Brown"
for i in range(0, len(filtered_sample[0:40]), 4):
    # Create a list of the first 4 names
    kw_list = [
        f"{filtered_sample.iloc[j]['First Name']} {filtered_sample.iloc[j]['Last Name']}"
        for j in range(i, min(i+4, len(filtered_sample)))
    ]
    
    # Add "Michael Brown" to kw_list only if it isn't already present
    if "Michael Brown" not in kw_list:
        kw_list.append("Michael Brown")
    
    # Try-except block for error handling
    try:
        pytrends.build_payload(kw_list, cat=0, geo='US', timeframe='2012-01-01 2016-12-31')
        data = pytrends.interest_over_time()
    except Exception as e:
        print(f"Error with batch {i}: {e}")
        continue  # Skip this batch and move to the next
    
    # Reset the index to make 'date' a regular column
    data = data.reset_index()
    data = data.drop(columns=['isPartial'])
    
    # Reshape to long format
    long_data = data.melt(id_vars=['date'], var_name='Name', value_name='Interest')
    
    # Reshape to wide format (Name as rows, date as columns)
    wide_data = long_data.pivot(index='Name', columns='date', values='Interest')
    
    # Add the common keyword's interests over time as separate columns
    michael_brown_values = wide_data.loc["Michael Brown"]
    michael_brown_columns = michael_brown_values.rename(lambda x: f"Michael Brown - {x}")
    michael_brown_df = pd.DataFrame([michael_brown_columns] * len(wide_data), 
                                    columns=michael_brown_columns.index, 
                                    index=wide_data.index)
    
    # Concatenate the new columns to the original DataFrame
    wide_data = pd.concat([wide_data, michael_brown_df], axis=1)
    
    # Drop the "Michael Brown" row
    wide_data = wide_data.drop("Michael Brown")
    
    # Save the initial DataFrame (wide_data) to a CSV file
    output_path = "C:/MyProjects/WebScraping/Upwork/Ahmad/Job5/rawdata/GoogleTrends_MPV.csv"
    
    # For appending in future iterations:
    if i == 0:  # Write headers only for the first batch
        wide_data.to_csv(output_path, mode='w', header=True, index=True)
    else:
        wide_data.to_csv(output_path, mode='a', header=False, index=True)
    
    print(f"Processed batch {i//4 + 1}: {kw_list}")
    time.sleep(1)
