# Provides functions to interact with the file system
import os
import ast
import math
# import keyword
import numpy as np
from tqdm import tqdm

# Fast and flexible means for data manipulation and analysis
import pandas as pd

# An interface for hashing any raw message in an encrypted format.
import hashlib as hl
from datetime import datetime


def scan_and_return_text(filename):
  '''
  To scan the input file and return the text
  '''
  with open(filename, encoding='utf8') as f:
    lines_of_code = f.readlines()

  return lines_of_code


def display_code(lines_of_code):
  '''
  To display the lines of code
  '''
  for line in lines_of_code:
    print(line, end='')


# Store the characters that constitute variable names
alphanumeric_ascii = set([chr(i) for i in range(48, 58)] + [chr(i) for i in range(65,91)] + ['_'] + [chr(i) for i in range(97,123)])


def remove_comments(lines_of_code):
  '''
  To remove the comments present in the given lines of code
  '''
  # Scan each line and remove all comments
  for i in range(len(lines_of_code)):

    # Assuming Python code
    lines_of_code[i] = lines_of_code[i].split('#')[0]

  return ' '.join(lines_of_code)


def extract_variable_names(code):
  '''
  To identify all the variable names used in the given code
  '''
  root = ast.parse(code)

  for node in ast.walk(root):

    if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
      yield node.id

    elif isinstance(node, ast.Attribute):
      yield node.attr

    elif isinstance(node, ast.FunctionDef):
      yield node.name


def get_masked_code(clean_code, variables):
  '''
  To mask all the user-defined functions and variables
  '''
  # Filter out all the non-special characters
  non_spl_chars = ''
  for c in clean_code:
    if c in alphanumeric_ascii:
      non_spl_chars += c
    else:
      non_spl_chars += ' '

  # Mask all user-defined variable names
  for v in variables:
    non_spl_chars = non_spl_chars.replace(' ' + v + ' ', ' ' + '#' * len(v) + ' ')

  # Augment the masked variables over the original code
  masked_code = ''
  for i in range(len(non_spl_chars)):
    if non_spl_chars[i] == ' ':
      masked_code += clean_code[i]
    else:
      masked_code += non_spl_chars[i]

  return masked_code.strip()


def preprocess_code(path, filename):
  '''
  To pre-process the source code read from file and return a clean masked code
  '''
  # Read the text file
  lines_of_code = scan_and_return_text(path + filename)

  # Extract all the user-defined variable names
  try:
    variables = set(list(extract_variable_names(''.join(lines_of_code))))
  except:
    variables = {}

  # Remove the comments present in code
  source_code = remove_comments(lines_of_code)

  # Remove newline characters and whitespaces from the text
  source_code = source_code.replace('\n', ' ')
  source_code = ' '.join(source_code.split())

  # Mask all user-defined variables
  masked_code = get_masked_code(' ' + source_code + ' ', variables)

  return masked_code.replace('#', '').replace(' ', '')


def derive_k_grams(clean_code, k=5):
  '''
  To derive the sequence of k-grams from the text 
  '''
  length = len(clean_code)
  k_grams = []

  for i in range(length - k + 1):
    k_grams.append(clean_code[i:i+k])

  return k_grams


def generate_hash(k_gram):
  '''
  To generate the equivalent 40-bit hexadecimal code
  '''
  encoded_text = k_gram.encode('utf-8')
  hash_value = hl.sha1(encoded_text)
  return hash_value.hexdigest()


def fetch_hash_values(k_grams):
  '''
  To return the hash values for each given k-gram
  '''
  hash_values = []

  for k_gram in k_grams:
    hash_values.append(generate_hash(k_gram))

  return hash_values


def extract_windows(hash_values, window_size):
  '''
  To extract windows of the given size
  '''
  windows = []

  for i in range(len(hash_values) - window_size + 1):
    windows.append(hash_values[i:i+window_size])

  return windows


def implement_winnowing(windows, window_size):
  '''
  To select a fingerprint from each window
  '''
  w = 0
  fingerprints = []
  window_count = len(windows)

  # Traverse through all the windows
  while w < window_count:
    min_hash_value, min_hash_value_index = windows[w][0], 0

    # For each hash value in the window
    for i in range(1, window_size):

      # Compare and store the minimum hash value
      if windows[w][i] < min_hash_value:
        min_hash_value = windows[w][i]
        min_hash_value_index = i

    fingerprints.append(min_hash_value)
    w = w + min_hash_value_index + 1

  return fingerprints


# # Trial
# hash_values = [77, 74, 42, 17, 98, 50, 17, 98, 8, 88, 67, 39, 77, 74, 42, 17, 98]
# windows = extract_windows(hash_values, 4)
# windows
# fingerprints = implement_winnowing(windows, 4)
# fingerprints


def check_for_plagiarism(filename_1, filename_2, fingerprints_1, fingerprints_2, verbose=False):
  '''
  To compare given codes for plagiarism
  '''
  # Check for blank files
  # if not fingerprints_1: print(f'{filename_1} has no fingerprints')
  # if not fingerprints_2: print(f'{filename_2} has no fingerprints')

  if not fingerprints_1 or not fingerprints_2:
    result = -1
  
  else:
    fingerprint_set_1 = set(fingerprints_1)
    fingerprint_set_2 = set(fingerprints_2)

    result = round(100 * len(fingerprint_set_1.intersection(fingerprint_set_2)) / len(fingerprint_set_1.union(fingerprint_set_2)), 2)

  if verbose:
    print('Fingerprints in 1:', len(fingerprint_set_1))
    print('Fingerprints in 2:', len(fingerprint_set_2))
    print('Common Fingerprints:', len(fingerprint_set_1.intersection(fingerprint_set_2)))
    print('Total Fingerprints:', len(fingerprint_set_1.union(fingerprint_set_2)))

  return result


def preprocess_directory(path, filenames, file_count):
  # Set the noise threshold
  k = 9

  # Preprocess each file in directory
  k_grams = {}
  max_length = 0
  hash_values = {}
  preprocessed_files = {}
  for i in range(file_count):
    preprocessed_files[filenames[i]] = preprocess_code(path, filenames[i])
    max_length = max(max_length, len(preprocessed_files[filenames[i]]))
    # print(preprocessed_files)

    # Form k-grams from the pre-processed text
    k_grams[filenames[i]] = derive_k_grams(preprocessed_files[filenames[i]], k)
    # print('k_grams', k_grams)

    # Generate hash values from the k-grams
    hash_values[filenames[i]] = fetch_hash_values(k_grams[filenames[i]])
    # print('hash_values', hash_values)

  # Set the window size
  window_size = max(1, math.floor(math.log(max_length)))
  print(f'Configuring window size to {window_size}')

  return hash_values, window_size


def extract_directory_fingerprints(filenames, file_count, hash_values, window_size):
  # Implement the Winnowing algorithm
  windows = {}
  fingerprints = {}
  for i in range(file_count):
    # Form the windows for the above hash values
    windows[filenames[i]] = extract_windows(hash_values[filenames[i]], window_size)

    # Extract the fingerprints of each code
    fingerprints[filenames[i]] = implement_winnowing(windows[filenames[i]], window_size)

  return fingerprints


def generate_file_report(specific_file, filenames, file_count, fingerprints):
  data = []

  # Compare with every potential source file
  for i in tqdm(range(file_count)):

    # Skip comparing with self
    if specific_file == filenames[i]:
      continue

    # Evaluate the files for plagiarism
    result = check_for_plagiarism(specific_file, filenames[i], fingerprints[specific_file], fingerprints[filenames[i]])

    # Store the plagiarism percentage
    data.append([specific_file, filenames[i], result])

  # Create a dataframe of acquired results
  # plagiarism_logs = pd.DataFrame(data, columns=['Submitted_Code', 'Source_Code', 'Plagiarism(%)', 'Remarks'])
  plagiarism_logs = pd.DataFrame(data, columns=['Submitted_Code', 'Source_Code', 'Plagiarism(%)'])

  # Extract the plagiarism report from the list of logs
  plagiarism_report = plagiarism_logs.sort_values(by=['Plagiarism(%)'], ascending=False).reset_index(drop=True)

  # Treat results obtained from blank files
  # plagiarism_report.loc[plagiarism_report['Submitted_Code'] in blank_files, ['Source_Code','Plagiarism(%)']] = 'NA'
  # plagiarism_report['Source_Code'] = np.where(plagiarism_report['Submitted_Code'] in blank_files, 'NA', plagiarism_report['Plagiarism(%)'])

  return plagiarism_logs, plagiarism_report


def generate_batch_report(filenames, file_count, fingerprints):
  data = []

  # For each submitted file
  for i in tqdm(range(file_count)):

    # Compare with every potential source file
    for j in range(i+1, file_count):

      # Evaluate the files for plagiarism
      result = check_for_plagiarism(filenames[i], filenames[j], fingerprints[filenames[i]], fingerprints[filenames[j]])

      # Store the plagiarism percentage
      data.append([filenames[i], filenames[j], result])
      data.append([filenames[j], filenames[i], result])

  plagiarism_logs = pd.DataFrame(data, columns=['Submitted_Code', 'Source_Code', 'Plagiarism(%)'])

  # Extract the plagiarism report from the list of logs
  plagiarism_report = plagiarism_logs.loc[plagiarism_logs.groupby(['Submitted_Code'], sort=True)['Plagiarism(%)'].idxmax()].sort_values(by=['Plagiarism(%)'], ascending=False).reset_index(drop=True)
  
  return plagiarism_logs, plagiarism_report


def batch_originality_scores(plagiarism_logs, plagiarism_report):
  '''
  To score individual submissions based on the originality of their approach
  '''
  # Calculate the mean plagiarism %age for each file
  grouped_logs = plagiarism_logs.groupby('Submitted_Code')['Plagiarism(%)'].mean()

  # Calculate the originality score for each file
  originality_df = pd.DataFrame(zip(grouped_logs.index, round((100 - grouped_logs) / 10,2)), columns=['Submitted_Code', 'Originality_Score'])

  # Update the report
  plagiarism_report = pd.merge(plagiarism_report, originality_df, left_on='Submitted_Code', right_on='Submitted_Code')

  return plagiarism_report[['Submitted_Code',	'Originality_Score', 'Source_Code',	'Plagiarism(%)']]


def fetch_insights(plagiarism_report):
  insights = {}
  insights['max'] = plagiarism_report['Plagiarism(%)'].max()
  insights['min'] = plagiarism_report['Plagiarism(%)'].min()
  insights['mean'] = round(plagiarism_report['Plagiarism(%)'].mean(), 2)
  insights['std'] = round(plagiarism_report['Plagiarism(%)'].std(), 2)
  return insights


def trigger_moss(path, specific_file=None, want_exhaustive_logs=False):
  '''
  To run MOSS for all the files present in the given path 
  '''
  # Extract all files present in the given path
  filenames = os.listdir(path)
  file_count = len(filenames)
  print(f'Received a batch of {file_count} files')

  # Preprocess each file in directory
  hash_values, window_size = preprocess_directory(path, filenames, file_count)
  # print(hash_values, window_size)

  # Implement the Winnowing algorithm
  fingerprints = extract_directory_fingerprints(filenames, file_count, hash_values, window_size)
  # print(fingerprints)

  # Perform comparison
  if specific_file:
    print('Generating plagiarism report for the chosen file')
    plagiarism_logs, plagiarism_report = generate_file_report(specific_file, filenames, file_count, fingerprints)
  else:
    print('Generating plagiarism report')
    plagiarism_logs, plagiarism_report = generate_batch_report(filenames, file_count, fingerprints)
    plagiarism_report = batch_originality_scores(plagiarism_logs, plagiarism_report)
  
  # Fetch the insights
  insights = fetch_insights(plagiarism_report)
  
  if specific_file:
    insights['originality_score'] = round((100 - plagiarism_logs[plagiarism_logs['Submitted_Code'] == specific_file]['Plagiarism(%)'].mean()) / 10, 2)

  return plagiarism_logs, plagiarism_report, insights


def fetch_group_insights(group_logs):
  '''
  To formulate insights after identifying groups
  '''
  group_insights = {}
  group_insights['total'] = group_logs.iloc[-1]['Group']
  group_insights['avg'] = round(len(group_logs) / group_insights['total'], 2)
  group_sizes = group_logs[['Group', 'Group Size']].drop_duplicates()
  group_insights['ge_2'] = (group_sizes['Group Size'] >= 2).sum()
  group_insights['ge_5'] = (group_sizes['Group Size'] >= 5).sum()
  group_insights['ge_10'] = (group_sizes['Group Size'] >= 10).sum()
  group_insights['max'] = group_sizes['Group Size'].max()
  return group_insights


def diagnose_clusters(plagiarism_report):
  '''
  To identify the groups of plagiarised submissions
  '''
  group_logs = plagiarism_report.copy()
  group_logs['Group'] = group_logs['Submitted_Code']

  for index, row in group_logs.iterrows():
    try:
      if row['Plagiarism(%)'] >= 80.0:
        source_index = group_logs[group_logs['Submitted_Code'] == row['Source_Code']].index.values[0]
        group_logs.at[index, 'Group'] = group_logs.loc[source_index]['Group']
      else:
        break
    except:
      pass

  group_logs['Group Size'] = group_logs.groupby('Group')['Group'].transform('count')
  group_logs = group_logs.sort_values(by=['Group Size', 'Plagiarism(%)'], ascending=[False, False]).reset_index(drop=True)

  group_parents = group_logs['Group'].unique()
  total_group_parents = len(group_parents)

  for i in range(total_group_parents):
    group_logs['Group'] = group_logs['Group'].replace(group_parents[i], i+1)
  
  group_logs = group_logs.sort_values(by=['Group', 'Plagiarism(%)'], ascending=[True, False]).reset_index(drop=True)
  
  # Add a column for row number
  group_logs['S/N'] = [1 + i for i in np.arange(len(group_logs))]
  
  group_insights = fetch_group_insights(group_logs)
  
  return group_logs[['S/N', 'Group', 'Submitted_Code',	'Originality_Score', 'Source_Code',	'Plagiarism(%)']], group_insights


def generate_group_report(group_logs):
    all_groups = group_logs['Group'].unique()
    group_report = pd.DataFrame(columns=['Group', 'Submission_Count', 'Maximum_Plagiarism(%)', 'Minimum_Plagiarism(%)', 'Mean_Plagiarism(%)'])
    
    for i in range(len(all_groups)):
      group_series = group_logs[group_logs['Group'] == all_groups[i]]['Plagiarism(%)']
      group_report.loc[i] = [all_groups[i], group_series.count(), group_series.max(), group_series.min(), group_series.mean()]

    return group_report





