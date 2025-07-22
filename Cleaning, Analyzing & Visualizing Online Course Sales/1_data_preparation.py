import datetime
from datetime import time, timedelta
import pickle
import re
import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

warnings.filterwarnings('ignore')

"""# Auxiliary functions"""

class InfoDataSet:
    def __init__(self, name, data):
        self.name = name
        self.data = data

    def pivot_info(self): # summary descriptive dataset table
        print('Name of the data: ', self.name)

        type_values = pd.Series({column: self.data[column].dtypes for column in self.data.columns})
        unique_values = pd.Series({column: self.data[column].unique() for column in self.data.columns})
        pivot_info = pd.DataFrame({'count': self.data.count(),
                                       'null': self.data.isnull().sum(),
                                       'unique': self.data.nunique(),
                                       'type': type_values,
                                       'unique_values': unique_values
                                       })

        object_types = {}
        for column in self.data.select_dtypes(include='object').columns:
          unique_types = self.data[column].apply(lambda x: type(x) if x is not None else float).unique()
          object_types[column] = [i for i in unique_types]
        pivot_info['object_types'] = pivot_info.index.map(lambda col: object_types.get(col, None))

        pivot_info = pivot_info[['count', 'null', 'type', 'object_types', 'unique', 'unique_values']]

        print(f'Shape of the data: {self.data.shape}')
        return pivot_info

# cleaning of "garbage" signs containing information about money
def clean_currency_column(value):
    value = re.sub(r'[€]', '', str(value))
    value = re.sub(r'\s+', '', value)
    value = value.replace('.', '')
    value = value.replace(',', '.')
    return float(value)

"""# ***Part 1.1. Data cleaning and processing***"""

data_calls = pd.read_excel('/content/drive/MyDrive/IT Career Hub/PROJECT    COMPLEX/Data source/Calls (Done).xlsx', dtype={'Id': str, "CONTACTID": str})
data_contacts = pd.read_excel('/content/drive/MyDrive/IT Career Hub/PROJECT    COMPLEX/Data source/Contacts (Done).xlsx', dtype={'Id': str})
data_deals = pd.read_excel('/content/drive/MyDrive/IT Career Hub/PROJECT    COMPLEX/Data source/Deals (Done).xlsx', dtype={'Id': str, 'Contact Name': str})
data_spend = pd.read_excel('/content/drive/MyDrive/IT Career Hub/PROJECT    COMPLEX/Data source/Spend (Done).xlsx')

"""## ***1.***   *Calls*

### *Preliminary data assessment*
"""

display(data_calls.head(2))

info_calls = InfoDataSet("Calls_info original", data_calls)
pivot_info_calls = info_calls.pivot_info()
display(pivot_info_calls)

"""### *Removing duplicate and irrelevant columns*

----------------------------------------
✅ Dialled Number (The dialed phone number) and Tag (Call tag) are absolutes empty, I'm deleting them.
"""

data_calls.drop(['Dialled Number', 'Tag'], axis=1, inplace=True)

data_calls.shape

"""----------------------------------------
✅ Check for duplicate rows (excluding ID) and remove them. Assume that the same manager cannot call multiple people at the same time and talk for a long duration. Therefore, identify duplicates where the Call Duration (in seconds) exceeds 50 seconds.
"""

duplicates = data_calls[(data_calls['Call Duration (in seconds)'] > 50) & data_calls.duplicated(subset=data_calls.columns[1:])]
print(duplicates.shape)
duplicates.head(2)

data_calls = data_calls.drop(index=duplicates.index)

data_calls.shape

"""### *Handling missing values and checking data types for each feature*"""

info_calls_2 = InfoDataSet("Calls_info аfter removing duplicates and irrelevant rows", data_calls)
pivot_info_calls_2 = info_calls_2.pivot_info()
display(pivot_info_calls_2)

"""----------------------------------------
✅ ***Id*** - Unique identifier for each call.

All good — no missing values, and the str data type is suitable for IDs

----------------------------------------
✅ ***Call Start Time*** Call start time.

Changing the data type to
"""

data_calls["Call Start Time"] = pd.to_datetime(data_calls["Call Start Time"], errors="raise")

"""----------------------------------------
✅ ***Call Owner Name*** - Name of the person responsible for the call.

All good — no missing values, 33 unique entries, and the data type object/str is appropriate.

----------------------------------------
***✅CONTACTID*** - Unique contact identifier.

All good — many missing values, but we’re not removing them. The str data type is suitable for IDs.


✔️ Existing missing values are not deleted — they won’t affect the analysis since they won’t be joined.

----------------------------------------
✅ ***Call Type*** - Call type (Incoming, Outgoing, Missed).

All good — no missing values, 3 unique entries, and the data type object/str is appropriate

----------------------------------------
✅ ***Call Duration (in seconds)*** - Call duration in seconds.

Data type: float64. There are 83 missing values, which are also of type float64 since they are represented as NaN.

All NaN values — 83 calls were scheduled by the CRM system, but for some reason, the calls did not take place.
"""

data_calls['Call Status'][data_calls['Call Duration (in seconds)'].isna()].unique()

"""'Cancelled', 'Overdue', 'Scheduled'"""

data_calls['Outgoing Call Status'][data_calls['Call Duration (in seconds)'].isna()].unique()

"""Create an additional column called "Flag_Call Duration (in seconds)" to indicate rows where the value was NaN (marked as 1). Then replace NaN values with 0 and convert the data type to int."""

data_calls['Flag_Call Duration (in seconds)'] = data_calls['Call Duration (in seconds)'].apply(lambda x: 1 if pd.isna(x) else 0)
data_calls['Call Duration (in seconds)'] = data_calls['Call Duration (in seconds)'].fillna(0).astype(int)

"""----------------------------------------
✅ ***Call Status*** - Final call status.

All good — no missing values, 11 unique entries, and the data type is object.

----------------------------------------
✅ ***Outgoing Call Status*** - Status of outgoing calls.

Data type: object/str + float due to NaN values. There are 4 unique entries.

NaN values are present because these calls are incoming, not outgoing, and therefore do not have any status.

----------------------------------------
✅ ***Scheduled in CRM*** - Status of outgoing calls.

Data type: object/str + float due to NaN values. There are 4 unique entries.

NaN values are present because these calls are incoming, not outgoing, and therefore do not have any status.
"""

data_calls['Scheduled in CRM'].value_counts()

# Create an additional column called "Flag_Scheduled in CRM" to indicate rows where the value was NaN (marked as 1).
# Then replace NaN values with 0 and convert the data type to int.
data_calls['Flag_Scheduled in CRM'] = data_calls['Scheduled in CRM'].apply(lambda x: 1 if pd.isna(x) else 0)
data_calls['Scheduled in CRM'] = data_calls['Scheduled in CRM'].fillna(0).astype(int)

info_calls_3 = InfoDataSet("Calls_info cleaned", data_calls)
pivot_info_calls_3 = info_calls_3.pivot_info()
display(pivot_info_calls_3)

"""## ***2.***   *Contacts*

### *Preliminary data assessment*
"""

display(data_contacts.head(2))

info_contacts = InfoDataSet("Contacts_info original", data_contacts)
display(info_contacts.pivot_info())

"""### *Removing duplicate and irrelevant columns*

----------------------------------------
✅ Check for duplicate rows (excluding ID) and remove them, provided that Created Time equals Modified Time
"""

duplicates = data_contacts[(data_contacts['Created Time'] == data_contacts['Modified Time']) & data_contacts.duplicated(subset=data_contacts.columns[1:])]
print(duplicates.shape)
duplicates.head(2)

data_contacts = data_contacts.drop(index=duplicates.index)

data_contacts.shape

"""### *Handling missing values and checking data types for each feature*"""

info_contacts_2 = InfoDataSet("Сontacts_info аfter removing duplicates and irrelevant rows", data_contacts)
pivot_info_contacts_2 = info_contacts_2.pivot_info()
display(pivot_info_contacts_2)

"""✅ ***Id:*** Contact identifier — all good.

✅ ***Contact Owner Name:*** Name of the person responsible for managing the contact.

No missing values, but the object data type includes two subtypes: str and bool. The column is intended to contain names, but some entries are mistakenly recorded as True or False..
"""

data_contacts[data_contacts['Contact Owner Name'].isin([True, False])]

"""Only one row contains False. Given that there are 18,548 rows in total, I’m deleting it."""

data_contacts = data_contacts[data_contacts['Contact Owner Name'] != False]

"""✅ ***Created Time:*** Date the contact was added to the database

✅ ***Modified Time:*** Date of last contact modification.

No missing values in either column. Although the data type is object/str, the content represents date and time, so I’m converting it to datetime format.
"""

data_contacts["Created Time"] = pd.to_datetime(data_contacts["Created Time"], errors="raise")

data_contacts["Modified Time"] = pd.to_datetime(data_contacts["Modified Time"], errors="raise")

info_contacts_3 = InfoDataSet("Contacts_info cleaned", data_contacts)
pivot_info_contacts_3 = info_contacts_3.pivot_info()
display(pivot_info_contacts_3)

"""## ***3.***   *Deals*

### *Preliminary data assessment*
"""

display(data_deals.head(2))

info_deals_1 = InfoDataSet("Deals_info original", data_deals)
pivot_info_deals = info_deals_1.pivot_info()
display(pivot_info_deals)

"""### *Removing duplicate and irrelevant columns*

----------------------------------------
✅ Check for duplicate rows (excluding ID) and remove them
"""

data_deals[data_deals.duplicated(subset=data_deals.columns[1:])].shape

data_deals[data_deals.duplicated(subset=data_deals.columns[1:])].head(2)

data_deals.drop_duplicates(subset=data_deals.columns[1:], inplace=True)

data_deals[data_deals.duplicated(subset=data_deals.columns[1:])].shape

"""----------------------------------------
✅ Information from the data developer:

The "Lost Reason" column contains the value "Duplicate" — these rows should be deleted.
"""

data_deals[data_deals['Lost Reason'] == 'Duplicate'].head(1)

data_deals[data_deals['Lost Reason'] == 'Duplicate'].shape

data_deals = data_deals[data_deals['Lost Reason'] != 'Duplicate']

data_deals[data_deals['Lost Reason'] == 'Duplicate'].shape

"""----------------------------------------
✅ Information from the data developer:

The "Source" column contains the value "Test" — these rows should be deleted.
"""

data_deals[data_deals['Source'] == 'Test'].head(1)

data_deals[data_deals['Source'] == 'Test'].shape

data_deals = data_deals[data_deals['Source'] != 'Test']

data_deals[data_deals['Source'] == 'Test'].shape

"""----------------------------------------
✅ ***Id:*** Unique identifier for each deal.

There are 2 missing values. The data type is object, with mixed subtypes: str and float (due to NaN).

I’m not changing the data type. I’m deleting the 2 rows with missing values (all columns contain NaN).

"""

data_deals[data_deals['Id'].isna()]

data_deals = data_deals.dropna(subset=['Id'])

"""----------------------------------------
✅ ***Contact Name***: Contact person identifier for the deal.

There are 47 missing values (remaining after removing test data and duplicates). The data type is object, with subtypes str and float due to NaN values. I'm unable to fill in the missing values, so these rows are being deleted — their origin is unclear and it’s uncertain whether they represent real data.


"""

data_deals = data_deals.dropna(subset=['Contact Name'])

"""### *Handling missing values and checking data types for each feature*"""

info_deals_2 = InfoDataSet("Deals_info аfter removing duplicates and irrelevant rows", data_deals)
pivot_info_deals_2 = info_deals_2.pivot_info()
display(pivot_info_deals_2)

"""----------------------------------------
✅ ***Deal Owner Name:*** - Name of the person responsible for the deal.

There are 28 missing values. The data type is object, with subtypes str and float due to NaN values.

Missing entries are first filled based on the "Contact Name" field — if a manager has previously worked with a client, that same manager is assigned by default for that Contact Name. Remaining missing values are filled with 'Unknown'.



"""

mode_values = data_deals.groupby('Contact Name')['Deal Owner Name'].agg(lambda x: x.mode()[0] if not x.mode().empty else None)
data_deals['Deal Owner Name'] = data_deals['Contact Name'].map(mode_values)

data_deals['Deal Owner Name'].isna().sum()

"""Managed to fill in 6 missing values. The remaining ones are replaced with 'Unknown'."""

data_deals['Deal Owner Name'] = data_deals['Deal Owner Name'].fillna('Unknown')

"""----------------------------------------
✅ ***Created Time:*** Timestamp when the deal was created.

No missing values; currently stored as object/str. Converting to datetime64.
"""

data_deals["Created Time"] = pd.to_datetime(data_deals["Created Time"], errors="coerce")

"""----------------------------------------
✅ ***Closing Date:*** Deal closing date, if applicable.

Many missing values — 6,602 in total. The column is of type object/str and float due to NaN entries. Converting to datetime64.

✔️ No need to fill in the missing values — imputation is not feasible, and NaNs will not affect calculations.

"""

data_deals["Closing Date"] = pd.to_datetime(data_deals["Closing Date"], errors="coerce")

"""----------------------------------------
***Chronology validation between Created Time and Closing Date.***

In the Closing Date column, many rows show a time of 00:00 (likely auto-filled). As a result, there are 2,380 rows where Closing Date appears earlier than Created Time. If we ignore the time component and compare only the dates, we’re left with 37 rows where Closing Date truly precedes Created Time — I’ll swap the values in those rows.

The remaining rows (out of the 2,380) have matching dates for opening and closing; only the time differs.
"""

# retain the hour and minute component
data_deals.loc[data_deals['Closing Date'] < data_deals['Created Time']].shape

# Removed the influence of the hour and minute component
data_deals.loc[data_deals['Closing Date'].dt.date < data_deals['Created Time'].dt.date].shape

data_deals[['Closing Date', 'Created Time']].loc[data_deals['Closing Date'].dt.date < data_deals['Created Time'].dt.date].head(1)

maska = data_deals['Closing Date'].dt.date < data_deals['Created Time'].dt.date
temp_columns = data_deals.loc[maska, 'Closing Date']

data_deals.loc[maska, 'Closing Date'] = data_deals.loc[maska, 'Created Time']
data_deals.loc[maska, 'Created Time'] = temp_columns

data_deals[['Closing Date', 'Created Time']].iloc[427]

"""----------------------------------------
✅  ***Quality***:  Deal quality classification indicating its potential or target status.

Many missing values; data type is object/str and float due to NaNs. There are 5 unique entries.

Since imputation is not feasible, missing values are filled with 'Unknown'.

"""

data_deals['Quality'] = data_deals['Quality'].fillna('Unknown')

"""----------------------------------------
✅ ***Stage***: Current deal stage.

No missing values; data type is object/str. There are 13 unique entries

"""

# data_deals['Stage'].unique()

"""----------------------------------------
✅ ***Lost Reason***: Reason the deal was lost, if applicable.

Many missing values; data type is object/str and float due to NaNs. There are 20 unique values.

NaNs are retained, as not all deals are lost — therefore, this field may legitimately remain empty for certain records.

----------------------------------------
✅ ***Page***: Web page or landing page where the lead was captured.

No missing values; data type is object/str. There are 31 unique entries.

----------------------------------------
✅ ***Campaign***: Name or code of the marketing campaign associated with the deal.

Many missing values — 4,199 in total. The column is of type object/str and float due to NaNs. There are 152 unique values.

Missing entries are filled with 'Unknown'
"""

data_deals['Campaign'] = data_deals['Campaign'].fillna('Unknown')

"""----------------------------------------
✅ ***SLA***: Service Level Agreement (SLA) response time — the duration from lead capture to initial call.

There are many missing values — 4,804 in total. The column is of type object, containing three subtypes: float, datetime.time, and datetime.timedelta.

float values represent NaNs and will be retained. The other types will be converted into seconds, minutes, and hours. The results will be stored in new columns, and the original SLA column will be deleted.


"""

pivot_info_deals_2['object_types']['SLA']

def convert_to_seconds(value):
    if pd.isna(value):
        return np.nan

    elif isinstance(value, time):
        return value.hour * 3600 + value.minute * 60 + value.second

    elif isinstance(value, timedelta):
        return value.total_seconds()

data_deals['SLA_seconds'] = data_deals["SLA"].apply(convert_to_seconds)
# data_deals['SLA_seconds'].value_counts()

def convert_to_minutes(value):
    if pd.isna(value):
        return np.nan

    elif isinstance(value, time):
        return (value.hour * 60) + value.minute + (value.second / 60)

    elif isinstance(value, timedelta):
        return value.total_seconds() / 60

data_deals['SLA_minutes'] = data_deals["SLA"].apply(convert_to_minutes)
# data_deals['SLA_minutes'].value_counts()

def convert_to_hours(value):
    if pd.isna(value):
        return np.nan

    elif isinstance(value, time):
      hour1 = round(value.hour + (value.minute / 60) + (value.second / 3600), 2)
      return hour1

    elif isinstance(value, timedelta):
      hour2 = round(value.total_seconds() / 3600, 2)
      return hour2

data_deals['SLA_hours'] = data_deals["SLA"].apply(convert_to_hours)
# data_deals['SLA_hours'].value_counts()

data_deals = data_deals.drop(columns=['SLA'])

"""----------------------------------------
✅ ***Content  (=Ad):*** Specific advertisement shown to users.

Many missing values — 6,021 in total. Data type is object/str and float due to NaNs. There are 179 unique values.

Missing entries are replaced with 'Unknown'.

"""

data_deals['Content'] = data_deals['Content'].fillna('Unknown')

"""----------------------------------------
✅ ***Term*** ***(=AdGroup):*** Subset within a campaign containing one or more ads with shared goals or settings.

Many missing values — 7,717 in total. Data type is object/str and float due to NaNs. There are 214 unique values.

Missing entries are replaced with 'Unknown'.

"""

data_deals['Term'] = data_deals['Term'].fillna('Unknown')

"""----------------------------------------
✅ ***Source***: Lead source.

No missing values; data type is object/str. There are 12 unique entries.

----------------------------------------
✅ ***Payment Type***: Type of payment method used or expected.

 Many missing values, as this data relates to sold courses (successful leads) or deals that haven’t been closed. Data type is object/str and float due to NaNs. There are 3 unique values.

----------------------------------------
✅ ***Product***: Specific product or service associated with the deal.

Many missing values, as this data relates to sold courses (successful leads) or deals that haven’t been closed. Data type is object/str and float due to NaNs. There are 5 unique values.

Missing entries are retained — they represent lost leads or deals that remain unclosed.
"""

data_deals['Product'].value_counts()

"""The products "Find Yourself in IT" and "Data Analytics" have only 4 data entries. The reason is unclear — perhaps they were discontinued due to low enrollment, or the intake has only just begun. This volume lacks statistical significance, so I’m removing these records."""

data_deals = data_deals[~data_deals['Product'].isin(['Find yourself in IT', 'Data Analytics'])]

"""----------------------------------------
✅ ***Education Type***: Type of education or training.

Many missing values, as this data relates to sold courses (successful leads) or deals that haven’t been closed. Data type is object/str and float

----------------------------------------
✅ ***Course duration***: Course duration for enrolled students.

Many missing values — 16,148 in total. Data type is float64. Only 2 unique values: 6.0 and 11.0.

Verified that when the Product is known, the Course Duration is also known.

All NaN values are replaced with 0, and the data type is converted to int
"""

data_deals['Course duration'] = data_deals['Course duration'].fillna(0).astype(np.int32)

"""----------------------------------------
✅ ***Months of study***: Number of months the student attended the course.

Many missing values — 18,826 in total. Data type is float64, with 12 unique values (maximum duration is 11 months plus 0). Missing values are replaced with 0, as they indicate the student did not attend (either declined or never started). The data type is converted to int.
"""

data_deals['Months of study'] = data_deals['Months of study'].fillna(0).astype(np.int32)

"""----------------------------------------
✅ ***Initial Amount Paid***: Initial client payment — the amount they’re expected to contribute, though it may not have been paid.

Many missing values — 15,621 in total. Data type is object/str and float due to NaNs.

Since this represents monetary values, it will be converted to float. First, values are cleaned of extraneous characters using a helper function (clean_currency_column). Then, all NaNs are replaced with 0. The result is stored in a new column.
"""

data_deals['InAmountPaid cleaned'] = data_deals['Initial Amount Paid'].apply(clean_currency_column)
data_deals['InAmountPaid cleaned'].fillna(0, inplace=True)

"""----------------------------------------
✅ ***Offer Total Amount***: Total offer amount presented to the client.

Many missing values — 15,601 in total. Data type is object/str and float due to NaNs.

Since this represents monetary values, it will be converted to float. First, values are cleaned of extraneous characters using a helper function (clean_currency_column). Then, all NaNs are replaced with 0. The result is stored in a new column.
"""

data_deals['OfTotAmount cleaned'] = data_deals['Offer Total Amount'].apply(clean_currency_column)
data_deals['OfTotAmount cleaned'].fillna(0, inplace=True)

"""----------------------------------------
***Validation of correct amount entries***

The amount in Initial Amount Paid must be less than Offer Total Amount, since it represents the initial payment (it cannot exceed the full course price). In cases where the initial payment is greater, the values are swapped — this likely indicates a data entry error by a manager or a system issue.

Validation is performed on the cleaned columns. The original columns are deleted.
"""

mask = data_deals['OfTotAmount cleaned'] < data_deals['InAmountPaid cleaned']
temp_columns = data_deals.loc[mask, 'OfTotAmount cleaned']

data_deals.loc[mask, 'OfTotAmount cleaned'] = data_deals.loc[mask, 'InAmountPaid cleaned']
data_deals.loc[mask, 'InAmountPaid cleaned'] = temp_columns

data_deals [['InAmountPaid cleaned', 'OfTotAmount cleaned']].loc[data_deals['OfTotAmount cleaned'] != 0].head()

"""Original columns are deleted."""

data_deals.drop(['Initial Amount Paid', 'Offer Total Amount'], axis=1, inplace=True)

# print(data_deals.columns)

"""----------------------------------------
✅ ***City***: Client’s associated city.

Very high number of missing values — 17,138 in total. Data type is object/str and float due to NaNs. There are 874 unique values, so converting to categories is not meaningful.

Data type remains unchanged. Since people rarely change their place of residence, I attempt to fill missing values based on Contact Name, which often repeats (managers interact with the same individuals multiple times).

"""

mode_values = data_deals.groupby('Contact Name')['City'].agg(lambda x: x.mode()[0] if not x.mode().empty else np.nan)
data_deals['City'] = data_deals['Contact Name'].map(mode_values)

data_deals['City'].isna().sum()

"""The number of missing values in "City" decreased from 17,138 to 16,519.

----------------------------------------
✅ ***Level of Deutsch***: Client’s German language proficiency level, if applicable.

Very high number of missing values — 18,390 in total. Data type is object/str and float due to NaNs. There are 214 unique values, so converting to categories is not meaningful.

Since language proficiency tends to remain stable over time, I attempt to fill missing values based on Contact Name.
"""

mode_values = data_deals.groupby('Contact Name')['Level of Deutsch'].agg(lambda x: x.mode()[0] if not x.mode().empty else np.nan)
data_deals['Level of Deutsch'] = data_deals['Contact Name'].map(mode_values)

data_deals['Level of Deutsch'].isna().sum()

"""The number of missing values in "Level of Deutsch" has decreased."""

info_deals_3 = InfoDataSet("Spend_info cleaned", data_deals)
pivot_info_deals_3 = info_deals_3.pivot_info()
display(pivot_info_deals_3)

"""##  ***4.***   *Spend*

### *Preliminary data assessment*
"""

display(data_spend.head(2))

info_spend_1 = InfoDataSet("Spend_info original", data_spend)
pivot_info_spend_1 = info_spend_1.pivot_info()
display(pivot_info_spend_1)

"""### *Removing duplicate and irrelevant columns*

----------------------------------------
✅ Checking rows for duplicates (excluding ID) and removing them.
"""

data_spend[data_spend.duplicated(subset=data_spend.columns[1:])].shape

data_spend[data_spend.duplicated(subset=data_spend.columns[1:])].head(2)

data_spend.drop_duplicates(subset=data_spend.columns[1:], inplace=True)

data_spend[data_spend.duplicated(subset=data_spend.columns[1:])].shape

"""----------------------------------------
✅ Information from the data developer:

The "Source" field contains the value "Test" — these rows should be removed
"""

data_spend[data_spend['Source'] == 'Test'].head(1)

data_spend[data_spend['Source'] == 'Test'].shape

data_spend = data_spend[data_spend['Source'] != 'Test']

data_spend[data_spend['Source'] == 'Test'].shape

"""### *Handling missing values and checking data types for each feature*"""

info_spend_2 = InfoDataSet("Spend_info аfter removing duplicates and irrelevant rows", data_spend)
pivot_info_spend_2 = info_spend_2.pivot_info()
display(pivot_info_spend_2)

"""----------------------------------------
✅***Date:***   Date indicating when impressions, clicks, and ad spend were tracked.

All good — data type is datetime64, and there are no missing values.

----------------------------------------
✅***Source:***   Channel where the advertisement was displayed.

No missing values; data type is object/str. There are 13 unique entries.
"""

# data_spend['Source'].unique()

"""----------------------------------------
✅***Campaign:***   Campaign under which the advertisement was displayed.

There are 1,252 missing values. Data type is object/str and float due to NaNs. The field contains 50 unique values.

Missing entries are filled with 'Unknown'.
"""

data_spend['Campaign'] = data_spend['Campaign'].fillna('Unknown')

"""----------------------------------------
✅***Impressions:***   Number of ad impressions shown to users.

All good — no missing values, and the data type is int64.

----------------------------------------
✅***Spend:***   Amount of money spent on the advertising campaign or ad group during the specified period.

All good — no missing values, and the data type is float64 (non-integer values due to cost calculations).

----------------------------------------
✅***Clicks:***   Number of user clicks on the advertisement.

All good — no missing values, and the data type is int64.

----------------------------------------
✅***AdGroup:***   Subset within a campaign containing one or more ads with shared goals or targeting settings (audience).

Many missing values — 2,086 in total. Data type is object/str and float
"""

# data_spend.loc[data_spend['AdGroup'].isna()] - действительно Unknown, на первый взгляд не видно от чего зависит

data_spend['AdGroup'] = data_spend['AdGroup'].fillna('Unknown')

"""----------------------------------------
✅***Ad:***   Specific advertisement shown to users.

Many missing values — 2,086 in total, same as in AdGroup. These columns are interdependent, as their NaN entries coincide, though it’s unclear which features influence both.

Data type is object/str and float due to NaNs. There are 165 unique values.

Missing values are replaced with 'Unknown'.


"""

data_spend['Ad'] = data_spend['Ad'].fillna('Unknown')

info_spend_3 = InfoDataSet("Spend_info cleaned", data_spend)
pivot_info_spend_3 = info_spend_3.pivot_info()
display(pivot_info_spend_3)



"""# ***Part 1.2. Descriptive statistics***

## *Calculate summary statistics for numeric fields.*

### data_calls
"""

data_calls.describe()

data_calls[data_calls['Call Duration (in seconds)'] == data_calls['Call Duration (in seconds)'].max()]

for column in data_calls.select_dtypes([int, float]).columns:
    print("--" * 30, column, "--" * 30)
    plt.figure(figsize = (8, 2))
    plt.subplot(1, 2, 1)
    data_calls[column].hist(grid=False)
    plt.ylabel('count')
    plt.subplot(1, 2, 2)
    sns.boxplot(x=data_calls[column])
    plt.show()

"""In fact, this table contains only one numeric column — Call Duration (in seconds). The rest have values of 0 or 1, so their plots resemble those of categorical variables.

### data_contacts
"""

data_contacts.describe()

"""Здесь нет числовых переменных, только datetime64

### data_deals
"""

data_deals.describe()

for column in data_deals.select_dtypes([int, float]).columns:
    print("--" * 20, column, "--" * 20)
    plt.figure(figsize = (8, 2))
    plt.subplot(1, 2, 1)
    data_deals[column].hist(grid=False)
    plt.ylabel('count')
    plt.subplot(1, 2, 2)
    sns.boxplot(x=data_deals[column])
    plt.show()

"""Only the SLA variables (all variants), InAmountPaid cleaned, and OfTotAmount cleaned are fully numeric. The rest appear to behave like categorical variables.

### data_spend
"""

data_spend.describe()

for column in data_spend.select_dtypes([int, float]).columns:
    print("--" * 20, column, "--" * 20)
    plt.figure(figsize = (8, 2))
    plt.subplot(1, 2, 1)
    data_spend[column].hist(grid=False)
    plt.ylabel('count')
    plt.subplot(1, 2, 2)
    sns.boxplot(x=data_spend[column])
    plt.show()

data_spend[data_spend['Impressions'] == data_spend['Impressions'].max()]

"""There is an outlier in the "Impressions" field — 431,445 ad views. However, the cost of this ad is not the highest (maximum spend is 774, while this one is only 236.1). The number of clicks is high. The source of this ad is Google Ads — it’s worth verifying whether such a cost for this volume of impressions is acceptable for this platform.

### Time series compatibility across all tables.

All tables contain temporal features. A compatibility check is required — they must all cover the same time period.
"""

print(data_calls['Call Start Time'].min(), data_calls['Call Start Time'].max())
print(data_contacts['Created Time'].min(), data_contacts['Created Time'].max())
print(data_deals['Created Time'].min(), data_deals['Created Time'].max())
print(data_spend['Date'].min(), data_spend['Date'].max())

"""In all four tables, the latest date matches, but the initial dates differ. To ensure time series compatibility, I’ll select the latest of the initial dates and trim the data in the other three tables accordingly."""

start_max_date = max(data_calls['Call Start Time'].min(), data_contacts['Created Time'].min(), data_deals['Created Time'].min(), data_spend['Date'].min())
start_max_date

data_calls = data_calls[data_calls['Call Start Time'] >= start_max_date]
data_contacts = data_contacts[data_contacts['Created Time'] >= start_max_date]
data_deals = data_deals[data_deals['Created Time'] >= start_max_date]

# print(data_calls['Call Start Time'].min(), data_calls['Call Start Time'].max())
# print(data_contacts['Created Time'].min(), data_contacts['Created Time'].max())
# print(data_deals['Created Time'].min(), data_deals['Created Time'].max())
# print(data_spend['Date'].min(), data_spend['Date'].max())

"""## *Analyze categorical fields such as quality, stage, source, and product.*

### data_calls
"""

data_calls.describe(include=['object'])

"""Outbound  / Attended Dialled  / Completed

Considering that the table contains nearly 96,000 records, I don’t see anything unusual. There are many outgoing calls and dialed numbers — the managers are actively working. Almost all entries are marked as completed, which is also a good sign, indicating that managers are fully processing requests.

### data_contacts
"""

data_contacts.describe(include=['object', 'category'])

"""Charlie Davis has a very high number of repeated entries. Let’s compare with other managers to determine whether it’s excessive or typical."""

aggregated_data = data_contacts.groupby('Contact Owner Name').agg({'Id': 'count','Created Time': 'min','Modified Time': 'max'})
sorted_data = aggregated_data.sort_values(by='Id', ascending=False)

print(sorted_data.head())

"""Charlie Davis has been working for a long time, and his performance is higher than others — but not by much. The second-ranking manager is only 200 records behind. Looking at the difference between managers, this might be normal. It’s important to check how many working days each has had to draw a final conclusion.

### data_deals
"""

data_deals.describe(include=['object', 'category'])

"""There are many categorical variables here, and many of them contain the value "Unknown". The importance of each category should be investigated during domain-specific analysis. If we filter out seemingly "uninformative" values for each feature at this stage, it may lead to excessive data loss. Therefore, filtering will only be done during targeted analysis.

### data_spend
"""

data_spend.describe(include=['object', 'category'])

"""All four fields can be considered categorical — the number of unique values is significantly smaller than the total number of records.

# ***Saving the results***
"""

df = {'calls_clear': data_calls, 'contacts_clear': data_contacts, 'deals_clear': data_deals, 'spend_clear': data_spend}

with open('data_1.pkl', 'wb') as f:
    pickle.dump(df, f)

with open('data_1.pkl', 'rb') as f:
    data_1 = pickle.load(f)

data_1.keys()

calls_clear, contacts_clear, deals_clear, spend_clear  = data_1.values()

