"""

This file sets up the data regarding the consumables that may be used in the course of an appointment.

The file is provided by Mathias Arnold and derives from the EHP work.

"""

import pandas as pd
import numpy as np

# EHP Consumables list
workingfile = '/Users/tbh03/Dropbox (SPH Imperial College)/Thanzi la Onse Theme 1 SHARE/05 - Resources/\
Module-healthsystem/From Matthias Arnold/ORIGINAL_Intervention input.xlsx'

# OUTPUT RESOURCE_FILES TO:
resourcefilepath = '/Users/tbh03/PycharmProjects/TLOmodel/resources/'

# ----------
# ----------
# ----------
# ----------

wb_import = pd.read_excel(workingfile, sheet_name='Intervention input costs', header=None)

# Drop the top row and first column as these were blank

wb = wb_import.drop(columns=0)
wb = wb.iloc[1:, :]

# Fill forward the first column to reflect that these are relating to multiple of the rows
wb.loc[:, 1] = wb.loc[:, 1].fillna(method='bfill')

# Remove any row that says "Total Cost"
wb = wb.drop(wb.index[wb.loc[:, 2] == 'Total cost'])

# get the header rows and forward fill these so that they relate to each row
hr = wb.index[wb.loc[:, 2].isna()]
wb.loc[:, 'Cat'] = None
wb.loc[hr, 'Cat'] = wb.loc[hr, 1]
wb.loc[:, 'Cat'] = wb.loc[:, 'Cat'].fillna(method='ffill')
wb = wb.drop(hr)

# Make the top row into columns names and delete repeats of this header
wb.columns = wb.iloc[0]
wb = wb.drop(wb.index[0])
wb = wb.reset_index(drop=True)
wb = wb.rename(columns={'Maternal/Newborn and Reproductive Health': 'Cat'})

# ------------
# Find rows with any na's
X = wb[wb['Units per case'].isnull()]

# For all matenral, the na's are just headers, so delete those rows
to_drop = X.index[X['Cat'] == 'Maternal/Newborn and Reproductive Health']
wb = wb.drop(to_drop)

# For HIV (condoms), it is to do with different risk groups, so drop the headers
to_drop = X.index[X['Cat'] == 'HIV/AIDS']
wb = wb.drop(to_drop)

# For PMTCT, it is to do with different headers, do drop these
to_drop = X.index[X['Cat'] == 'PMTCT']
wb = wb.drop(to_drop)

# For Zinc, it is to do with different doses according to age of child:
# Make two seperate packages
wb.at[403, 'Intervention'] = \
    wb.at[403, 'Intervention'] + ' for ' + wb.at[402, 'Drug/Supply Inputs']
wb.at[403, 'Proportion of patients receiving this input'] = 100

wb.at[405, 'Intervention'] = \
    wb.at[405, 'Intervention'] + ' for ' + wb.at[404, 'Drug/Supply Inputs']
wb.at[405, 'Proportion of patients receiving this input'] = 100

wb = wb.drop([402, 404])

# For Deworming children it is to with different does according to age of child:
wb.at[553, 'Intervention'] = \
    wb.at[553, 'Intervention'] + ' for ' + wb.at[552, 'Drug/Supply Inputs']
wb.at[553, 'Proportion of patients receiving this input'] = 100

wb.at[554, 'Intervention'] = \
    wb.at[555, 'Intervention'] + ' for ' + wb.at[554, 'Drug/Supply Inputs']
wb.at[554, 'Proportion of patients receiving this input'] = 100

wb = wb.drop([552, 554])

# For treatment with cerbeovascular disease it it to do with whether or not the patient has diabetes
# so make another package
block = wb.loc[wb['Intervention'] == 'Treatment for those with cerebrovascular disease and post-stroke'].copy()

# make a non-diabetes version (everyone just get routine test)
block_no_diabetes = block.drop([564, 565, 566])
block_no_diabetes.loc[567, 'Proportion of patients receiving this input'] = 100
block_no_diabetes.loc[:, 'Intervention'] = block.at[559, 'Intervention'] + '_ No Diabetes'

# make a diabetes version (no routine glucose test but everyone gets full test)
block_diabetes = block.drop([564, 567])
block_diabetes.loc[565, 'Proportion of patients receiving this input'] = 100
block_diabetes.loc[:, 'Intervention'] = block.at[559, 'Intervention'] + '_ With Diabetes'

wb = wb.drop(block.index)
wb = pd.concat([wb, block_no_diabetes, block_no_diabetes], ignore_index=True)

# Confirm that that there are no na's
assert len(wb[wb['Units per case'].isnull()]) == 0
# ------------

# rationalise the columns and the names
wb.loc[:, 'Expected_Units_Per_Case'] = (wb.loc[:, 'Proportion of patients receiving this input'] / 100) * \
                                       wb.loc[:, 'Number of units'] * \
                                       wb.loc[:, 'Times per day'] * \
                                       wb.loc[:, 'Days per case']

wb.loc[:, 'Unit_Cost'] = wb.loc[:, 'Unit cost (MWK) (2010)']

wb.loc[:, 'Expected_Cost_Per_Case'] = wb.loc[:, 'Expected_Units_Per_Case'] * wb.loc[:, 'Unit_Cost']

wb = wb.rename(columns={'Drug/Supply Inputs': 'Items',
                        'Intervention': 'Intervention_Pkg',
                        'Cat': 'Intervention_Cat'})

wb = wb.loc[:, ['Intervention_Cat',
                'Intervention_Pkg',
                'Items',
                'Expected_Units_Per_Case',
                'Unit_Cost'
                ]]

# Assign a unique package code
unique_intvs = pd.unique(wb['Intervention_Pkg'])
intv_codes = pd.DataFrame({'Intervention_Pkg': unique_intvs,
                           'Intervention_Pkg_Code': np.arange(0, len(unique_intvs))})

wb = wb.merge(intv_codes, on='Intervention_Pkg', how='left', indicator=True)
assert (wb['_merge'] == 'both').all()
wb = wb.drop(columns='_merge')

# Assign a unique code for each individual consumable item
unique_items = pd.unique(wb['Items'])
item_codes = pd.DataFrame({'Items': unique_items,
                           'Item_Code': np.arange(0, len(unique_items))})
wb = wb.merge(item_codes, on='Items', how='left', indicator=True)
assert (wb['_merge'] == 'both').all()
wb = wb.drop(columns='_merge')

# Reorder columns to be nice:
wb = wb[['Intervention_Cat',
         'Intervention_Pkg',
         'Intervention_Pkg_Code',
         'Items',
         'Item_Code',
         'Expected_Units_Per_Case',
         'Unit_Cost']]

assert not pd.isnull(wb).any().any()

# ----------
# Now looking at the OneHealth file (29-5-19 Slack Msg from Tara: this comes from Palladium Grp originally)
# This file should be the essentially the same as the file that has been imported already but with some
# crucial additions - things that were omitted from the EHP list Matthias provided.

onehealthfile = workingfile = '/Users/tbh03/Dropbox (SPH Imperial College)/Thanzi la Onse Theme 1 SHARE/07 - Data/\
OneHealth projection files/OneHealth commodities.xlsx'

oh = pd.read_excel(workingfile, sheet='consumables')
oh.columns = oh.loc[0]
oh = oh.drop(index=0)
# take only the values for 2010 as the values are the same in all the years
oh = oh[['Drug or supply', 2010.0]].rename(columns={'Drug or supply': 'Items', 2010.0: 'Unit_Cost'})

# compare the list of unique consumbale items in the one health sheet with the original file
list_of_consumables_oh = pd.DataFrame({'Items': pd.unique(oh['Items'])})
list_of_consumables_orig = pd.DataFrame({'Items': pd.unique(wb['Items'])})
comparison = pd.DataFrame(list_of_consumables_orig).merge(list_of_consumables_oh,
                                                          on='Items',
                                                          indicator=True,
                                                          how='outer')

# get the ones which are only in the one health dataset
only_in_oh = comparison.loc[comparison['_merge'] == 'right_only', 'Items'].reset_index(drop=True)

# merge in Unit_Cost for the combined joint set
only_in_oh = pd.DataFrame({'Items': only_in_oh}).merge(oh, on='Items', how='left')
only_in_oh = only_in_oh.drop_duplicates()  # drop duplicates caused by the merge

# Append these records to the end of the wb dataframe (the resource file)
# They fall into a "misceallanerous" package code. But at least they can still be accessed by the disease modules

# Add columns so that the only-in-oh dataframe can be appended to the wb

only_in_oh['Intervention_Cat'] = 'Imported From One Health'
only_in_oh['Intervention_Pkg'] = 'Misc'
only_in_oh['Intervention_Pkg_Code'] = -99
only_in_oh['Item_Code'] = np.arange(1000, 1000 + len(only_in_oh))
only_in_oh['Expected_Units_Per_Case'] = 1.0

assert set(only_in_oh.columns) == set(wb.columns)

# Add these to the overall dataframe: now complte listing of consumables
cons = pd.concat([wb, only_in_oh], axis=0, ignore_index=True, sort=False)

# --------------
# Notes:
# These is some duplication/overlap between the file from EHP (Matthias Arnold provided) and the OneHealth file.
# Also, these have not been cross-checked against the Malawi treatment guidelines or 'sense-checked'
# --------------


# Finally augment the file to indicate the availability of each items according to Facility_Level
# Columns will be created indicating availability at each Facility_Level
# 0: not available
# 1: always available
# (0.0, 1.0): available with this probability [this is representing stock-outs]

# As we do not know anything about this yet, for now follow a simple rule.
# This should be much better informed

cons['Available_Facility_Level_0'] = 0.85
cons['Available_Facility_Level_1'] = 0.90
cons['Available_Facility_Level_2'] = 0.95
cons['Available_Facility_Level_3'] = 0.99

# Save:
cons.to_csv(resourcefilepath + 'ResourceFile_Consumables.csv')
