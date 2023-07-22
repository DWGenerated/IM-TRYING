import pandas as pd
import numpy as np


df = pd.read_csv(r'C:\Users\xxx\Desktop\transactions.csv', parse_dates=['date'], dayfirst=True)
# Load the dataset into a Pandas DataFrame
df = pd.read_csv(r'C:\Users\xxx\Desktop\transactions.csv', parse_dates=['date'], dayfirst=True)

# Step 1: Add flag and absolute value column
df['flag'] = np.where(df['amount'] >= 0, 'positive', 'negative')
df['abs_amount'] = df['amount'].abs()

# Step 2: Separate positive and negative values
positive_values = df[df['flag'] == 'positive'].copy()
negative_values = df[df['flag'] == 'negative'].copy()

# Step 3: Sort positive and negative values
positive_values.sort_values(['account', 'date'], inplace=True)
negative_values.sort_values(['account', 'date'], inplace=True)

# Step 4: Create running totals
positive_values['running_total'] = positive_values.groupby('account')['abs_amount'].cumsum()
negative_values['running_total'] = negative_values.groupby('account')['abs_amount'].cumsum()

# Step 5: Append positive and negative values to create 1 set
merged_df = pd.concat([positive_values, negative_values], ignore_index=True)

# Step 6: Sort the merged set by account number, running total, and date
merged_df.sort_values(['account', 'running_total', 'date'], inplace=True)

# Step 7: Create new running totals on the amount column
merged_df['running_balance_new_order'] = merged_df.groupby('account')['amount'].cumsum()

# Step 8: Add section number column based on the change in sign of the running balance new order value within each account
merged_df['section_number'] = merged_df.groupby('account')['running_balance_new_order'].apply(lambda x: ((x.shift(1) > 0) & (x <= 0)).cumsum())
merged_df['section_number2'] = merged_df.groupby('account')['running_balance_new_order'].apply(lambda x: ((x.shift(1) <= 0) & (x > 0)).cumsum() + 1)

# Step 9: Add section number column based on the change in sign of the running balance new order value within each account
merged_df['section_number3'] = merged_df.groupby('account')['running_balance_new_order'].apply(lambda x: ((x.shift(1) > 0) & (x <= 0)).astype(int))
merged_df['section_number4'] = merged_df.groupby('account')['running_balance_new_order'].apply(lambda x: ((x.shift(1) <= 0) & (x > 0)).astype(int))

merged_df['section_number_FINAL'] = merged_df['section_number'] + merged_df['section_number2'] - merged_df['section_number3'] - merged_df['section_number4']

# Step 10: Add "Split" flag and "value to move" column
merged_df['Split'] = np.where((merged_df['section_number3'] + merged_df['section_number4']) == 1, 'move', 'no move')
merged_df['value_to_move'] = np.where(merged_df['Split'] == 'move', merged_df['running_balance_new_order'], 0)

# Step 11: Update amount2 column based on different cases
merged_df['amount2'] = np.where(merged_df['Split'] == 'move', merged_df['amount'] - merged_df['value_to_move'], merged_df['amount'])

# Step 12: Split last entry if there is a "value to move"
split_mask = (merged_df['value_to_move'] != 0)
split_df = merged_df[split_mask].copy()
split_df['section_number_FINAL'] += 1
split_df['amount'] = 0
split_df['amount2'] = merged_df['value_to_move']
split_df['Split'] = 'generated'

# Concatenate the split_df with the original merged_df and sort again
merged_df = pd.concat([merged_df, split_df], ignore_index=True)
merged_df.sort_values(['account', 'running_total', 'date'], inplace=True)

# Reset index to align with the length of DataFrame
merged_df.reset_index(drop=True, inplace=True)



# Format output as a table
table = merged_df.to_string(index=False)

output_file_path = r'C:\Users\xxx\Desktop\output_file.csv'
merged_df.to_csv(output_file_path, index=False)
