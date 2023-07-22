import pandas as pd

# Your existing DataFrame
data = {
    'account': [100001, 100001, 100001, 100001, 100001, 100001, 100001, 100001, 100001, 100001, 100001, 100001, 100001],
    'URN': [1, 2, 2, 3, 5, 4, 4, 6, 7, 8, 8, 41, 42],
    'type': ['debit', 'credit', 'credit', 'credit', 'credit', 'debit', 'debit', 'debit', 'debit', 'credit', 'credit', 'debit', 'debit'],
    'section_number_FINAL': [1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4],
    'Split': ['no move', 'move', 'generated', 'no move', 'no move', 'move', 'generated', 'no move', 'no move', 'move', 'generated', 'no move', 'no move'],
    'amount2': [696, -696, -40, -25, -38, 103, 525, 240, 705, -1470, -2197, 2197, 0]
}

df = pd.DataFrame(data)

def match_urns(section_df):
    credit_rows = section_df[section_df['type'] == 'credit']
    debit_rows = section_df[section_df['type'] == 'debit']

    for index, credit_row in credit_rows.iterrows():
        urn = credit_row['URN']
        matching_debit = debit_rows[debit_rows['URN'] == urn].iloc[0]
        if credit_row['amount2'] != abs(matching_debit['amount2']):
            diff = abs(credit_row['amount2']) - abs(matching_debit['amount2'])
            section_df.loc[index, 'amount2'] -= diff
            section_df.loc[matching_debit.name, 'amount2'] += diff

# Group by account and section_number_FINAL and apply matching function to each section
df.groupby(['account', 'section_number_FINAL']).apply(match_urns)

# Generate rows for sections where amount2 doesn't sum to 0
generated_rows = df.groupby(['account', 'section_number_FINAL']).filter(lambda x: x['amount2'].sum() != 0).copy()
generated_rows['Split'] = 'generated 2'
generated_rows['amount2'] = -generated_rows['amount2']

# Concatenate the generated rows with the original DataFrame
df = pd.concat([df, generated_rows], ignore_index=True)

# Sort the DataFrame by account, section_number_FINAL, and URN
df.sort_values(['account', 'section_number_FINAL', 'URN'], inplace=True)

# Reset index to align with the length of DataFrame
df.reset_index(drop=True, inplace=True)

# Format output as a table
table = df.to_string(index=False)

# Print the final result as a table
print(table)