import datetime
from datetime import time, timedelta
import warnings
import pickle

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import plotly.graph_objects as go
import plotly.express as px
import plotly.figure_factory as ff
from plotly.subplots import make_subplots

warnings.filterwarnings('ignore')

with open('/content/drive/MyDrive/IT Career Hub/PROJECT    COMPLEX/data_1.pkl', 'rb') as f:
    data_1 = pickle.load(f)

data_1.keys()

calls_clear, contacts_clear, deals_clear, spend_clear  = data_1.values()

"""# Auxiliary functions and calculations for analysis"""

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

"""## calculation of the actual payment received for courses

We are adding a new column AOV_i to the Deals table — representing the average monthly value of the course (based on a formula from a product analytics instructor):

(InAmountPaid cleaned + (OfTotAmount cleaned – InAmountPaid cleaned) / (Course duration – 1) × (Months of study – 1)) / Months of study

Translated formula explanation:

(Prepayment + (Total course cost – Prepayment) / (Course duration – 1) × (Months attended – 1)) / Months attended
"""

# adding a column AOV_i
deals_clear['AOV_i'] = ((deals_clear['InAmountPaid cleaned'] +
                        (deals_clear['OfTotAmount cleaned'] -
                         deals_clear['InAmountPaid cleaned']) /
                        (deals_clear['Course duration'] - 1) *
                        (deals_clear['Months of study'] - 1)) /
                        deals_clear['Months of study'])

# deals_clear[deals_clear['Stage'] == "Payment Done"].head(1)

"""We are adding a column R_i — representing the actual amount of money received by the school from the customer.

R_i = AOV_i × Months of study

the average monthly value of the course * how many months the customer attended
"""

deals_clear['R_i'] = deals_clear['AOV_i'] * deals_clear['Months of study']

# deals_clear[(deals_clear['Stage'] == "Payment Done") & (deals_clear['Months of study']== 3)].head()

"""# Overview of the source data"""

info_contacts = InfoDataSet("Contacts_info cleaned", contacts_clear)
display(info_contacts.pivot_info())

info_calls = InfoDataSet("Calls_info cleaned", calls_clear)
pivot_info_calls = info_calls.pivot_info()
display(pivot_info_calls)

info_deals_1 = InfoDataSet("Deals_info cleaned", deals_clear)
pivot_info_deals = info_deals_1.pivot_info()
display(pivot_info_deals)

info_spend_1 = InfoDataSet("Spend_info cleaned", spend_clear)
pivot_info_spend_1 = info_spend_1.pivot_info()
display(pivot_info_spend_1)



"""# ***Part 3.1. Time series analysis***

## *1. Analyze the trend of deal creation over time and its correlation with calls*

I will group the data based on deal creation time. Since the dataset contains daily records and the trend is hard to visualize, I’m aggregating it by week. I'm also grouping all potentially relevant data for analysis upfront.
"""

deals_per_week = deals_clear.groupby(pd.Grouper(key='Created Time', freq='W')).size().reset_index(name='Total Deals Count')
calls_per_week = calls_clear.groupby(pd.Grouper(key='Call Start Time', freq='W')).size().reset_index(name='Calls Count')
contacts_per_week = contacts_clear.groupby(pd.Grouper(key='Created Time', freq='W')).size().reset_index(name='Сontacts Count')

# Counting the quantity of successful = paid deals (Payment Done в Stage)
payment_deals = deals_clear[deals_clear['Stage'] == "Payment Done"]
successful_per_week_count = payment_deals.groupby(pd.Grouper(key='Created Time', freq='W')).size().reset_index(name='Successful Deals Count')

# Weekly aggregation of ad expenses, impression count, and click volume
spend_per_week = spend_clear.groupby(pd.Grouper(key='Date', freq='W')).agg(Spend = ('Spend', 'sum'),
                                                                           Spend_avg = ('Spend', 'mean'),
                                                                           Impressions = ('Impressions', 'sum'),
                                                                           Clicks = ('Clicks', 'sum')
                                                                           ).reset_index()

# calculating the amount of successful = paid transactions (Payment Done в Stage)
successful_per_week_sum = payment_deals.groupby(pd.Grouper(key='Created Time', freq='W'))['R_i'] \
                                        .sum().reset_index(name='Real Amount')

deals_per_week.set_index('Created Time', inplace=True)
calls_per_week.set_index('Call Start Time', inplace=True)
contacts_per_week.set_index('Created Time', inplace=True)
successful_per_week_count.set_index('Created Time', inplace=True)
spend_per_week.set_index('Date', inplace=True)
successful_per_week_sum.set_index('Created Time', inplace=True)

# Merging through join
time_series_data = deals_per_week.join(calls_per_week) \
                                 .join(contacts_per_week) \
                                 .join(successful_per_week_count) \
                                 .join(spend_per_week) \
                                 .join(successful_per_week_sum).dropna()

time_series_data.index.name = 'Week'
time_series_data.rename(columns={'Created Time': 'Week'}, inplace=True)
time_series_data = time_series_data.reset_index()
# time_series_data['Week'] = pd.to_datetime(time_series_data['Week'])

print(time_series_data.shape)
time_series_data.head(2)

"""I will visually assess whether there is a relationship between the number of calls, contacts, total number of deals, and the number of successful deals."""

time_series_data['Week'] = pd.to_datetime(time_series_data['Week'])

custom_colors = ['#9aa255', '#415d3b', '#53df66', '#e4d933']

fig3_1_1 = px.scatter(time_series_data,
                    x='Week',
                    y=['Calls Count', 'Total Deals Count', 'Сontacts Count', 'Successful Deals Count'],
                    trendline = "ols",
                    labels={'variable': 'Count', 'Week': 'Week', 'value': 'Count'},
                    marginal_y = "box",
                    color_discrete_sequence=custom_colors
                    )

fig3_1_1.update_layout(title="Dynamics of the number of calls, contacts and deals by week",
                       title_x = 0.5,
                       title_font=dict(family="Georgia", size=20, color="black", weight="bold"),
                       xaxis=dict(title=dict(text="Week",font=dict(size=14,color="black", weight="bold"))),
                       yaxis=dict(title=dict(text="Count",font=dict(size=14,color="black", weight="bold")))
                       )

fig3_1_1.update_layout(showlegend=True,
                       legend=dict(orientation = "v", yanchor = "top", y = 0.95, x = 1, xanchor = "right", title=""),
                       legend_font=dict(family="Georgia", size=12, color="black", weight="bold")
                       )


fig3_1_1.update_layout(plot_bgcolor="white")



fig3_1_1.update_xaxes(showgrid=False)
fig3_1_1.update_yaxes(showgrid=False)

fig3_1_1.show()

"""The difference between the number of established contacts and the total number of deals is relatively small, so one of these metrics can be excluded. For the analysis, I’m excluding Contacts Count, as in some cases the number of contacts is lower than the number of deals — possibly because the same individuals enter into multiple deals.

Visually, the correlation between the number of calls and the number of deals (especially paid deals) appears weak.

Next, I’ll explore how the number of ad impressions and clicks impacts the number of deals closed.
"""

time_series_data['Week'] = pd.to_datetime(time_series_data['Week']).dt.date

fig3_1_2 = go.Figure(layout=dict(width=1100, height=600))

fig3_1_2.add_trace(go.Bar(x = time_series_data['Week'],
                     y = time_series_data['Impressions'],
                     name ='Impressions',
                     hovertext = [f"Week: {week}, Impressions: {value}" for week, value in zip(time_series_data['Week'], time_series_data['Impressions'])],
                     hoverinfo='text',
                     marker = dict(color= 'lightgreen',
                                   line=dict(color='black', width=2),
                                   opacity = 0.2),
                     yaxis='y2'
                     )
              )

fig3_1_2.add_trace(go.Scatter(x = time_series_data['Week'],
                         y = time_series_data['Clicks'],
                         mode ='lines+markers',
                         name ='Clicks',
                         hovertext = [f"Week: {week}, Clicks: {value}" for week, value in zip(time_series_data['Week'], time_series_data['Clicks'])],
                         hoverinfo='text',
                         line = dict(dash='dot', color = '#e4d933', width=5)))

fig3_1_2.add_trace(go.Scatter(x = time_series_data['Week'],
                         y = time_series_data['Calls Count'],
                         mode = 'lines+markers',
                         name = 'Calls Count',
                         hovertext = [f"Week: {week}, Calls Count: {value}" for week, value in zip(time_series_data['Week'], time_series_data['Calls Count'])],
                         hoverinfo='text',
                         line = dict(color = '#748c47')
                         )
              )

fig3_1_2.add_trace(go.Scatter(x = time_series_data['Week'],
                         y = time_series_data['Total Deals Count'],
                         mode = 'lines+markers',
                         name = 'Total Deals Count',
                         hovertext = [f"Week: {week}, Deals Count: {value}" for week, value in zip(time_series_data['Week'], time_series_data['Total Deals Count'])],
                         hoverinfo='text',
                         line = dict(dash='dot', color = '#334832', width=3))
              )

fig3_1_2.update_layout(title="Dynamics of Impressions, Clicks, Calls and Total Deals by week",
                       title_x = 0.5,
                       title_y = 1,
                       title_font=dict(family="Georgia", size=20, color="black", weight="bold"),
                       xaxis=dict(title=dict(text="Week", font=dict(size=14, color="black", weight="bold")),
                                  tickangle=45),
                       yaxis=dict(title=dict(text="Count (Calls, Deals, Clicks)",font=dict(size=14,color="black", weight="bold"))),
                       yaxis2=dict(title=dict(text="Impressions",font=dict(size=14,color="black", weight="bold")),
                                   overlaying='y',
                                   side='right',
                                   anchor='x')
                       )


fig3_1_2.update_layout(showlegend=True,
                       legend=dict(orientation = "v", yanchor = "top", xanchor = "center", y = 1.1, x = 0.14, title=""),
                       legend_font=dict(family="Georgia", size=12, color="black", weight="bold")
                       )


fig3_1_2.update_layout(plot_bgcolor="white")

fig3_1_2.update_xaxes(showgrid=False)
fig3_1_2.update_yaxes(showgrid=False)

fig3_1_2.show()

"""The difference between the number of established contacts and the total number of deals is relatively small, so one of these metrics can be excluded. For the analysis, I’m excluding Contacts Count, as in some cases the number of contacts is lower than the number of deals — possibly because the same individuals enter into multiple deals.

Visually, the correlation between the number of calls and the number of deals (especially paid deals) appears weak.

Next, I’ll explore how the number of ad impressions and clicks impacts the number of deals closed.

Next, I will analyze the impact of advertising spend on the number of deals closed, as well as on the total value of successful deals.
"""

fig1_3 = go.Figure(layout=dict(width=1100, height=600))

fig1_3.add_trace(go.Scatter(x=time_series_data['Week'],
                            y=time_series_data['Successful Deals Count'],
                            mode='lines+markers',
                            name='Successful Deals Count',
                            hovertext = [f"Week: {week}, Successful Deals: {value}" for week, value in zip(time_series_data['Week'], time_series_data['Successful Deals Count'])],
                            hoverinfo='text',
                            line = dict(color = '#5c7a41')
                            )
                  )


fig1_3.add_trace(go.Scatter(x=time_series_data['Week'],
                            y=time_series_data['Spend_avg'],
                            mode='lines+markers',
                            name='Ad Spend mean',
                            hovertext = [f"Week: {week}, Ad Spend: {value}" for week, value in zip(time_series_data['Week'], time_series_data['Spend'])],
                            hoverinfo='text',
                            line = dict(dash='dot', color = '#53df66', width=5)
                            )
                  )


fig1_3.add_trace(go.Scatter(x=time_series_data['Week'],
                            y=time_series_data['Real Amount'],
                            mode='lines+markers',
                            name='Real Amount',
                            yaxis='y2',
                            hovertext = [f"Week: {week}, Real Amount: {value}" for week, value in zip(time_series_data['Week'], time_series_data['Real Amount'])],
                            hoverinfo='text',
                            line = dict(dash='dot', color = '#e4d933', width=5)
                            )
                  )

fig1_3.update_layout(title="Dynamics of Deals, Ad Spend and Sum from Deals by week",
                     title_x = 0.5,
                     title_y = 1,
                     title_font=dict(family="Georgia", size=20, color="black", weight="bold"),

                     xaxis=dict(title=dict(text="Week", font=dict(size=14, color="black", weight="bold")),
                                tickangle=45),
                     yaxis=dict(title=dict(text="Count of Deals \ Ad Spend mean",font=dict(size=14,color="black", weight="bold"))),

                     yaxis2=dict(title=dict(text="Real Amount",font=dict(size=14,color="black", weight="bold")),
                                 overlaying='y',
                                 side='right',
                                 anchor='x'
                                 )
                     )

fig1_3.update_layout(showlegend=True,
                     legend=dict(orientation = "v", yanchor = "top", xanchor = "center", y = 1.1, x = 0.14, title=""),
                     legend_font=dict(family="Georgia", size=12, color="black", weight="bold"))


fig1_3.update_layout(plot_bgcolor="white")

fig1_3.update_xaxes(showgrid=False)
fig1_3.update_yaxes(showgrid=False)
fig1_3.show()

"""An increase in advertising spend does not always lead to higher revenue — this is especially evident in recent periods, where an inverse correlation has been observed. However, higher ad expenditures do contribute to an increase in the total number of deals closed.

The trends in revenue from successful deals and the overall deal count generally align.

A correlation matrix will allow for a more precise view of this correlation
"""

corr_matrix = time_series_data[['Impressions', 'Clicks', 'Spend', 'Сontacts Count', 'Calls Count', 'Total Deals Count',
       'Successful Deals Count', 'Real Amount']].corr()
corr_matrix_percent = round(corr_matrix * 100, 2)
corr_matrix_percent

fig1_4 = px.imshow(corr_matrix_percent,
                   text_auto=True,
                   color_continuous_scale=px.colors.sequential.speed,
                   aspect='auto',
                   #  zmin=-1
                   #  zmax=1
                   )

fig1_4.update_layout(title="Correlation Matrix of time series",
                     title_x = 0.5,
                     title_font=dict(family="Arial", size=24, color="black", weight='bold')
                     )

fig1_4.show()

"""The number of Contacts and Deals is almost identical, which results in a very high correlation coefficient — 94.85%.

The Total Deals Count largely depends on the number of calls (Calls Count — 79.3%) and advertising spend (Spend — 80.78%). This may suggest that higher-quality advertising led to increased interest in the school. The correlation between Total Deals Count and ad impressions (54.46%) as well as clicks (51.08%) is moderate, indicating that many other influencing factors were not captured in this analysis.

Successful deals (in terms of count and revenue) are formed at a later stage and, therefore, do not directly affect Total Deals Count. However, Total Deals Count influences their formation with a moderate correlation of 45–50%.

When analyzing the chronology of these metrics — beginning with ad impressions and ending with the quantity and value of successful deals — there is virtually no correlation between the two. This suggests that when making a purchase decision, clients are guided by completely different factors rather than the volume of advertising exposure, which is quite logical.

## *2. Explore the distribution of deal closing time and the duration of the period from deal creation to closure*.

To evaluate the duration of the period from deal creation to closure, it is necessary to know both dates, as well as to account for the outcome of the deal — whether it was successfully completed and paid for, or if it fell through. All required data is contained in the deals_clear table.
"""

last_date_in_df = deals_clear['Created Time'].max()
# Open deals that have been paid but not closed
open_successful_deals = deals_clear[(deals_clear['Closing Date'].isna()) & (deals_clear['Stage'] == 'Payment Done')]

# Their duration (the difference between the latest date and the Created Time)
time_successful_opened_deals = (last_date_in_df - open_successful_deals['Created Time']).dt.days

time_successful_opened_deals.shape

# An additional column that calculates the time interval between deal opening and closure
deals_clear['Time_to_Close'] = abs(deals_clear['Closing Date'] - deals_clear['Created Time']).dt.days

# Two variables to classify closed deals as successful (those that had payment activity and a Closing Date.)
# And lost deals, where no payment was made and they have also been closed
successful_closed_deals_time = deals_clear[deals_clear['Stage'] == 'Payment Done']['Time_to_Close'].dropna()
lost_deals_time = deals_clear[deals_clear['Stage'] == 'Lost']['Time_to_Close'].dropna()

successful_closed_deals_time.shape, lost_deals_time.shape

"""Calculate the key statistical metrics for all three numerical time interval variables."""

time_successful_opened_deals.max(), time_successful_opened_deals.min(), round(time_successful_opened_deals.mean(),0), time_successful_opened_deals.median()

successful_closed_deals_time.max(), successful_closed_deals_time.min(), round(successful_closed_deals_time.mean(),0), successful_closed_deals_time.median()

lost_deals_time.max(), lost_deals_time.min(), round(lost_deals_time.mean(),0), lost_deals_time.median()

variables = [time_successful_opened_deals, successful_closed_deals_time, lost_deals_time]
variable_names = ['Successful opened Deals', 'Successful closed Deals', 'Lost Deals']


for variable, name in zip(variables, variable_names):
    print("--" * 20, name, "--" * 20)
    plt.figure(figsize=(8, 2))
    plt.subplot(1, 2, 1)
    pd.Series(variable).hist(grid=False)
    plt.ylabel('count')
    plt.subplot(1, 2, 2)
    sns.boxplot(x=pd.Series(variable))
    plt.show()

"""The maximum duration of study is 11 months (330 days), but some paid deals remain open for up to two years. This could be due to clients postponing their studies or a potential error in the CRM system. Since there is only one such case (as shown in the box plot), I consider it an outlier — regardless of whether it's a real situation or a mistake — and I’m excluding it from the dataset.

As for closed deals, it's unclear why some take a long time to be finalized, but since there are many such cases, this might reflect a common business practice. Therefore, I’m keeping all values for closed deals.
"""

hist_data = [successful_closed_deals_time, lost_deals_time, time_successful_opened_deals]
group_labels = ['Successful closed Deals', 'Lost Deals', 'Successful opened Deals']

fig2_1 = ff.create_distplot(
    hist_data,
    group_labels,
    show_hist=True,
    show_rug=True,
    bin_size=5,
    colors=['black', '#53df66', '#9aa255']
)



fig2_1.update_layout(title="Distribution of Time to Close for Successful and Lost Deals",
                     title_x = 0.5,
                     title_font=dict(family="Georgia", size=20, color="black", weight="bold"),
                     xaxis=dict(title=dict(text="Time to Close (days)",font=dict(size=14,color="black", weight="bold"))),
                     yaxis=dict(title=dict(text="Density",font=dict(size=14,color="black", weight="bold"))),
                     bargap=0.05
                   )

fig2_1.update_layout(showlegend=True,
                   legend=dict(orientation = "v", yanchor = "top", y = 0.95, x = 1, xanchor = "right", title=""),
                   legend_font=dict(family="Georgia", size=12, color="black", weight="bold"))


fig2_1.update_layout(plot_bgcolor="white")


fig2_1.update_xaxes(showgrid=False)
fig2_1.update_yaxes(showgrid=False)


fig2_1.show()

"""The chart shows Lost Deals — transactions that were never paid and typically closed within the first 150 days. This may indicate that the client was undecided about enrolling, did not provide a clear response, or that managers failed to close the deal promptly.

There are also Successful but Closed Deals — where the client started making payments but, for some reason, the deal was closed (perhaps due to dropping out of the course). This suggests a high likelihood of course abandonment within the first 50 days of enrollment.

Another category includes Successful but Still Open Deals — these are rare (333 deals) and likely represent clients who were still enrolled during the observation period. Most of them do not exceed 300 days, which aligns with the maximum course duration of 11 months (~335 days). Only 2 deals exceed this duration, possibly indicating non-completion.

Due to limited dataset documentation, these are assumptions. However, if the assumptions hold, it is feasible to estimate the financial loss associated with early deal closures.

"""

count_over_335 = (time_successful_opened_deals > 335).sum()
count_over_335

"""# ***Part 3.2. Campaign Effectiveness Analysis***

## *1. Compare the effectiveness of different campaigns in terms of lead generation and conversion rate.*

Group by Campaign and calculate the number of Leads (defined as the number of Contact Name entries in Deals — representing the highest-quality leads that entered a deal), as well as the number of Customers (i.e., successful deals where Payment Done is recorded in the Stage field).

Calculate the conversion rate for each campaign. Exclude campaigns with fewer than 100 leads, as well as those labeled Unknown, since it’s unclear whether these belong to the same company or which campaign performed better. Then, sort the results in descending order by conversion rate.
"""

campaign_deals = deals_clear.groupby('Campaign').agg({'Contact Name': 'count', \
                                                     'Stage': lambda x: (x == 'Payment Done').sum()}).reset_index()
campaign_deals.rename(columns={'Contact Name': 'Leads Deals', 'Stage': 'Customers'}, inplace=True)
campaign_deals['Сonversion'] = round(campaign_deals['Customers'] / campaign_deals['Leads Deals'] * 100, 2)

campaign_eff = campaign_deals[campaign_deals['Leads Deals'] >= 100]
campaign_eff = campaign_eff[campaign_eff['Campaign'] != 'Unknown']
campaign_eff = campaign_eff.sort_values(by='Сonversion', ascending=False)

top_20 = campaign_eff.head(30)

fig3_2_1 = px.scatter(top_20,
                      x='Campaign',
                      y='Сonversion',
                      size='Customers',
                      size_max=40,
                      labels={'Campaign': 'Campaign ',
                              'Leads Deals': 'Leads Deals ',
                              'Customers': 'Customers ',
                              'Сonversion': 'Сonversion % '},
                      hover_data=['Campaign', 'Leads Deals', 'Customers', 'Сonversion'],
                      color='Leads Deals',
                      color_continuous_scale=px.colors.sequential.speed[::-1]
                      )

fig3_2_1.update_layout(title="Conversion of companies (more 100 Leads)",
                       title_x = 0.5,
                       title_y = 1,
                       title_font=dict(family="Georgia", size=20, color="black", weight="bold"),

                       xaxis=dict(title=dict(text="Campaign", font=dict(size=14, color="black", weight="bold")),
                                  tickangle=45),
                       yaxis=dict(title=dict(text="Сonversion %",font=dict(size=14,color="black", weight="bold"))),
                       )


fig3_2_1.update_layout(showlegend=True,
                       legend=dict(orientation = "v", yanchor = "top", xanchor = "center", y = 1.1, x = 0.14, title=""),
                       legend_font=dict(family="Georgia", size=10, color="black", weight="bold"))


fig3_2_1.update_layout(plot_bgcolor="white")

fig3_2_1.update_xaxes(showgrid=False)
fig3_2_1.update_yaxes(showgrid=False)

fig3_2_1.show()

"""The larger the dot size, the greater the number of successful deals generated by the campaign. The lighter the color, the more leads the campaign attracted.

Since dot size reflects the number of customers, some campaigns with over 100 leads but no converted customers are not represented by a dot — indicating they were among the least effective campaigns.

I will separately analyze campaigns that attracted fewer than 100 leads but achieved a conversion rate greater than zero.
"""

campaign_noneff = campaign_deals[campaign_deals['Leads Deals'] < 100]
campaign_noneff = campaign_noneff[campaign_noneff['Campaign'] != 'Unknown']
campaign_noneff = campaign_noneff.sort_values(by='Сonversion', ascending=False)
campaign_noneff = campaign_noneff[campaign_noneff['Сonversion'] > 0]
campaign_noneff.head(2)

fig3_2_2 = px.bar(campaign_noneff,
                  x='Campaign',
                  y='Сonversion',
                  labels={'Campaign': 'Campaign ',
                          'Leads Deals': 'Leads Deals ',
                          'Customers': 'Customers ',
                          'Сonversion': 'Сonversion % '},
                  hover_data=['Campaign', 'Leads Deals', 'Customers', 'Сonversion'],
                  color='Leads Deals',
                  color_continuous_scale= px.colors.sequential.speed[::-1]
                  )

fig3_2_2.update_layout(title="Conversion of unsuccessful/small сampaign (less 100 Leads and Conversion is more than 0)",
                       title_x = 0.5,
                       title_y = 1,
                       title_font=dict(family="Georgia", size=20, color="black", weight="bold"),
                       xaxis=dict(title=dict(text="Campaign", font=dict(size=14, color="black", weight="bold")),
                                  tickangle=45),
                       yaxis=dict(title=dict(text="Сonversion %",font=dict(size=14,color="black", weight="bold")))
                       )


fig3_2_2.update_layout(showlegend=True,
                       legend=dict(orientation = "v", yanchor = "top", xanchor = "center", y = 1.1, x = 0.14, title=""),
                       legend_font=dict(family="Georgia", size=10, color="black", weight="bold")
                       )


fig3_2_2.update_layout(plot_bgcolor="white")

fig3_2_2.update_xaxes(showgrid=False)
fig3_2_2.update_yaxes(showgrid=False)

fig3_2_2.show()

"""The results from this group of campaigns are considered uninformative, as the low number of outcomes does not accurately reflect the campaign’s true conversion rate. The reason for the low or nonexistent lead volume should be investigated individually for each case — it’s possible that the campaign was newly launched and hasn’t had enough time to produce results, or it may be genuinely ineffective, having generated no outcomes despite a large number of impressions.

An additional noteworthy observation: the more leads a campaign attracts, the lower its conversion rate tends to be. This implies that as the data volume increases, the accuracy of performance metrics improves.

## *2. Evaluate the effectiveness of different marketing sources (Source) in generating high-quality deals.*

Group by Source, calculate the number of Leads (defined as the count of Contact Name entries in Deals — representing the highest-quality leads that entered a deal), and the number of Customers — successful deals where Payment Done is recorded in the Stage field.

The highest number of customers came from sources such as Facebook Ads, Google Ads, and Organic, with the first two generating the largest number of Leads. The absence of a dot in the Source visualization indicates that no customers were acquired from that source.

It might be worth trying to link the source to revenue
"""

source_deals = deals_clear.groupby(['Source', 'Quality']).agg({'Contact Name': 'count', \
                                                     'Stage': lambda x: (x == 'Payment Done').sum(), \
                                                                'R_i': 'sum'}).reset_index()
source_deals.rename(columns={'Contact Name': 'Leads Deals', 'Stage': 'Customers', 'R_i': 'Real Amount'}, inplace=True)
source_deals['Сonversion'] = round(source_deals['Customers'] / source_deals['Leads Deals'] * 100, 2)

source_deals = source_deals.sort_values(by=['Сonversion'], ascending=False)
source_deals

custom_palette = ['#334832', '#5c7a41', '#9aa255', '#b8b368', '#f1ecc1', '#fefcda']
source_deals = source_deals.sort_values(by=['Leads Deals'], ascending= False)


fig3_2_3 = px.bar(source_deals,
                  x='Source',
                  y='Leads Deals',
                  color='Quality',
                  labels={'Source': 'Source ',
                          'Quality_Value': 'Count of Leads ',
                          'Quality': 'Quality Categories '},
                  color_discrete_sequence=custom_palette[::-1]
                  )

fig3_2_3.update_layout(title="Distribution of deals Quality by Source",
                       title_x = 0.5,
                       title_y = 1,
                       title_font=dict(family="Georgia", size=20, color="black", weight="bold"),
                       xaxis=dict(title=dict(text="Source", font=dict(size=14, color="black", weight="bold")),
                                  tickangle=45),
                       yaxis=dict(title=dict(text="Count of Leads",font=dict(size=14,color="black", weight="bold")))
                       )


fig3_2_3.update_layout(showlegend=True,
                       legend=dict(orientation = "v", yanchor = "top", xanchor = "center", y = 0.9, x = 0.9, title=""),
                       legend_font=dict(family="Georgia", size=12, color="black", weight="bold")
                       )


fig3_2_3.update_layout(plot_bgcolor="white")

fig3_2_3.update_xaxes(showgrid=False)
fig3_2_3.update_yaxes(showgrid=False)

fig3_2_3.show()

"""Most sources show a high proportion of Unknown, E – Non Qualified, and D – Non Target categories. In comparison, categories C – Low, B – Medium, and A – High are represented in much smaller numbers.

Sorting by Customers was applied during the table’s initial setup. Bar height reflects the number of Leads. The Offline source did not generate any customers, which is why its column is missing.

Google Ads and Facebook Ads delivered the highest number of customers and revenue. The Offline source did not generate any customers, so its column is absent.

# ***Part 3.3. Sales Department Performance Analysis***

## *Evaluate the performance of individual deal owners and marketing campaigns in terms of the number of processed deals, conversion rate, and total sales volume.*
"""

# Select the necessary information for analysis from the deals_clear table
owner_deals = deals_clear.groupby('Deal Owner Name').agg(Contact_Name = ('Contact Name', 'count'), \
                                                          Customers = ('Stage', lambda x: (x == 'Payment Done').sum()), \
                                                          median_SLA_hour = ('SLA_hours', 'median'),\
                                                          mean_SLA_hour = ('SLA_hours', 'mean'),\
                                                          Real_Amount = ('R_i', 'sum')).reset_index()

owner_deals.rename(columns={'Contact_Name': 'Leads Deals',  'median_SLA_hour': 'median SLA (hour)', 'mean_SLA_hour': 'mean SLA (hour)', 'Real_Amount': 'Real Amount'}, inplace=True)
owner_deals.shape

# Select the necessary information for analysis from the calls_clear table
owner_calls = calls_clear.groupby('Call Owner Name').agg(Count_Calls=('CONTACTID', 'count'), \
                                                         Leads_Calls=('CONTACTID', 'nunique'), \
                                                         Call_Duration_mean_in_seconds=('Call Duration (in seconds)', 'mean'), \
                                                         Call_Duration_median_in_seconds=('Call Duration (in seconds)', 'median'), \
                                                         Sum_Calls_in_seconds=('Call Duration (in seconds)', 'sum')).reset_index()

owner_calls.rename(columns={'Count_Calls': 'Count Calls', 'Leads_Calls': 'Leads Calls'}, inplace=True)
owner_calls['mean Calls (min)'] = round(owner_calls['Call_Duration_mean_in_seconds'] / 60, 2)
owner_calls['median Calls (min)'] = round(owner_calls['Call_Duration_median_in_seconds'] / 60, 2)
owner_calls['sum Calls (hour)'] = round(owner_calls['Sum_Calls_in_seconds'] / 3600, 2)

owner_calls = owner_calls.drop(columns=['Call_Duration_mean_in_seconds'])
owner_calls = owner_calls.drop(columns=['Call_Duration_median_in_seconds'])
owner_calls = owner_calls.drop(columns=['Sum_Calls_in_seconds'])

owner_calls.rename(columns={'Call Owner Name': 'Owner Name'}, inplace=True)

# Combine the retrieved information into a single table. I will join it to owner_calls1

owner_calls.set_index('Owner Name', inplace=True)
owner_deals.set_index('Deal Owner Name', inplace=True)

owner_name_data = owner_calls.join(owner_deals, how='left')
owner_name_data = owner_name_data.reset_index()
# owner_name_data

# owner_name_data

"""After reviewing the owner_name_data summary table across both datasets, the following conclusions can be drawn:

Not all managers listed in the calls table have any leads in the deals table, making it difficult to assess their impact on revenue generation.

Some managers have very few calls recorded in calls, yet they have a large number of leads in deals. It’s unclear how they managed to close so many deals without making calls.

Conclusion: The analysis of manager performance will be based solely on the deals table.

Initially, I will select managers who processed more than 100 leads and sort them by the number of customers acquired.
"""

owner_deals = owner_deals[owner_deals['Leads Deals'] > 100]
owner_deals['Conversion'] = round((owner_deals['Customers'] / owner_deals['Leads Deals'] ) * 100, 2)
owner_deals = owner_deals.sort_values(by=['Customers'], ascending=False)
owner_deals = owner_deals.reset_index()
owner_deals.head()

owner_deals = owner_deals.sort_values(by='Conversion', ascending=False)

fig3_3_1 = go.Figure(layout=dict(width=1100, height=600))

fig3_3_1.add_trace(go.Bar(x = owner_deals['Deal Owner Name'],
                     y = owner_deals['Leads Deals'],
                     name ='Leads Deals',
                     text=owner_deals['Customers'],
                     textposition='outside',
                     hovertext = [f"Deal Owner Name: {name}, Count: {value}" for name, value in zip(owner_deals['Deal Owner Name'], owner_deals['Leads Deals'])],
                     hoverinfo='text',
                     marker = dict(color = '#b8b368',
                                   line=dict(color='black', width=2),
                                   opacity = 0.5)
                     )
              )

fig3_3_1.add_trace(go.Scatter(x = owner_deals['Deal Owner Name'],
                         y = owner_deals['Conversion'],
                         mode ='markers',
                         name ='Conversion',
                         hovertext = [f"Deal Owner Name: {name}, Conversion %: {value}" for name, value in zip(owner_deals['Deal Owner Name'], owner_deals['Conversion'])],
                         hoverinfo='text',
                               yaxis='y2',
                         marker = dict(size = 10, color = '#334832')))

fig3_3_1.update_layout(title="Efficiency Analysis (Conversion) of the deals owners",
                        title_x = 0.5,
                        title_y = 1,
                        title_font=dict(family="Georgia", size=20, color="black", weight="bold"),
                        barmode='overlay',

                        xaxis=dict(title=dict(text="Owner Name", font=dict(size=14, color="black", weight="bold")),
                                   tickangle=45),
                        yaxis=dict(title=dict(text="Leads Deals", font=dict(size=14,color="black", weight="bold"))),
                        yaxis2=dict(title=dict(text="Conversion",font=dict(size=14,color="black", weight="bold")),
                                    overlaying='y',
                                    side='right',
                                    anchor='x',
                                    range=[0, 35] )
                        )


fig3_3_1.update_layout(showlegend=True,
                        legend=dict(orientation = "v", yanchor = "top", xanchor = "center", y = 1.1, x = 0.9, title=""),
                        legend_font=dict(family="Georgia", size=12, color="black", weight="bold"))


fig3_3_1.update_layout(plot_bgcolor="white")

fig3_3_1.update_xaxes(showgrid=False)
fig3_3_1.update_yaxes(showgrid=False)

fig3_3_1.show()

"""Questions arise about managers who have a high number of leads but a lower conversion rate than those with even more leads"""

owner_deals = owner_deals.sort_values(by='Conversion', ascending=False)

fig_3_3_2 = go.Figure(layout=dict(width=1100, height=600))

fig_3_3_2.add_trace(go.Bar(x = owner_deals['Deal Owner Name'],
                     y = owner_deals['Leads Deals'],
                     name ='Leads Deals',
                     hovertext = [f"Deal Owner Name: {name}, Count: {value}" for name, value in zip(owner_deals['Deal Owner Name'], owner_deals['Leads Deals'])],
                     hoverinfo='text',
                     marker = dict(color = '#b8b368',
                                   line=dict(color='black', width=2),
                                   opacity = 0.5)
                     )
              )

fig_3_3_2.add_trace(go.Bar(x = owner_deals['Deal Owner Name'],
                     y = owner_deals['Real Amount'],
                     name ='Real Amount',
                     hovertext = [f"Deal Owner Name: {name}, Sum: {value}" for name, value in zip(owner_deals['Deal Owner Name'], owner_deals['Real Amount'])],
                     hoverinfo='text',
                     marker = dict(color = '#a9eb9d',
                                   #line=dict(color='black', width=2),
                                   opacity = 0.5),
                      yaxis='y2'
                     )
              )

fig_3_3_2.update_layout(title="Efficiency Analysis (Real Amount) of the deals owners",
                     title_x = 0.5,
                     title_y = 1,
                     title_font=dict(family="Georgia", size=20, color="black", weight="bold"),
                        barmode='overlay',

                     xaxis=dict(title=dict(text="Owner Name", font=dict(size=14, color="black", weight="bold")),
                                tickangle=45),
                     yaxis=dict(title=dict(text="Leads Deals", font=dict(size=14,color="black", weight="bold"))),

                     yaxis2=dict(title=dict(text="Real Amount",font=dict(size=14,color="black", weight="bold")),
                                 overlaying='y',
                                 side='right',
                                 anchor='x'
                                 ))


fig_3_3_2.update_layout(showlegend=True,
                     legend=dict(orientation = "v", yanchor = "top", xanchor = "center", y = 1.1, x = 0.9, title=""),
                     legend_font=dict(family="Georgia", size=12, color="black", weight="bold"))


fig_3_3_2.update_layout(plot_bgcolor="white")

fig_3_3_2.update_xaxes(showgrid=False)
fig_3_3_2.update_yaxes(showgrid=False)

fig_3_3_2.show()

"""Instead of using conversion rate, I use the actual revenue generated. A lower conversion rate does not always indicate low performance in terms of income generated by the manager."""



"""# ***Part 3.4. Analysis of Payments and Products***

## *1. Analyze the distribution of payment types and their impact on deal success.*
"""

deals_clear['Payment Type'].value_counts()

payment_type_deals = deals_clear.groupby(['Payment Type', 'Stage']).agg(Count_Payment=('Contact Name', 'count'),
                                                             Payment_Done_Count=('Stage', lambda x: (x == 'Payment Done').sum()),
                                                             Other_Categories_Stage=('Stage', lambda x: (x != 'Payment Done').sum()),
                                                             Real_Amount=('R_i', 'sum')
                                                             ).reset_index()

payment_type_deals

"""Installment payments are more popular, but they also carry higher losses"""

custom_palette = ['#334832', '#5c7a41', '#9aa255', '#b8b368', '#f1ecc1', '#fefcda']
#source_deals = source_deals.sort_values(by=['Leads Deals'], ascending= False)


fig4_1_1 = px.bar(payment_type_deals,
                  x='Payment Type',
                  y='Count_Payment',
                  color='Stage',
                  labels={'Payment Type': 'Payment Type ',
                          'Count_Payment': 'Count_Payment ',
                          'Stage': 'Quality Categories '},
                  color_discrete_sequence=custom_palette[::-1]
                  )

fig4_1_1.update_layout(title="Distribution of Stage by Payment Type",
                       title_x = 0.5,
                       title_y = 1,
                       title_font=dict(family="Georgia", size=20, color="black", weight="bold"),
                       xaxis=dict(title=dict(text="Payment Type", font=dict(size=14, color="black", weight="bold")),
                                  tickangle=45),
                       yaxis=dict(title=dict(text="Count of Payment",font=dict(size=14,color="black", weight="bold")))
                       )


fig4_1_1.update_layout(showlegend=True,
                       legend=dict(orientation = "v", yanchor = "top", xanchor = "center", y = 0.9, x = 0.9, title=""),
                       legend_font=dict(family="Georgia", size=12, color="black", weight="bold")
                       )


fig4_1_1.update_layout(plot_bgcolor="white")

fig4_1_1.update_xaxes(showgrid=False)
fig4_1_1.update_yaxes(showgrid=False)

fig4_1_1.show()

"""In practice, there are two payment options — a one-time payment and installment plans. The latter is more popular, but it also accounts for a higher share of lost deals.

## *2. Analyze the popularity and effectiveness of different products and types of training.*
"""

deals_clear['Product'].value_counts()

deals_clear['Education Type'].value_counts()

product = deals_clear.groupby(['Product', 'Education Type']).agg(Count_deals=('Contact Name', 'count'),
                                                                 Payment_Done_Count=('Stage', lambda x: (x == 'Payment Done').sum()),
                                                                 Real_Amount=('R_i', 'sum')
                                                                 ).reset_index()
product['Percent Root'] = (product['Payment_Done_Count'] / product['Payment_Done_Count'].sum()) * 100
product

fig4_2_1 = px.sunburst(
    product,
    path=['Product', 'Education Type'],
    values='Payment_Done_Count',
    color='Product',
    color_discrete_map={
        'Digital Marketing': '#E4D933',
        'UX/UI Design': '#C5E38B',
        'Web Developer': '#5C7A41'
    }
)

fig4_2_1.update_layout(
    title="Distribution of succesfull Deals by Product and Education Type",
    title_x=0.5,
    title_y=1,
    title_font=dict(family="Georgia", size=20, color="black", weight="bold")
)

fig4_2_1.update_layout(
    showlegend=True,
    legend=dict(
        orientation="v",
        yanchor="top",
        xanchor="center",
        y=0.9,
        x=0.9,
        title=""
    ),
    legend_font=dict(family="Georgia", size=12, color="black", weight="bold")
)

fig4_2_1.update_traces(
    marker=dict(line=dict(color='#334832', width=2)),
    textinfo='label+percent root',
    customdata=product['Percent Root'],
    hovertemplate='<b>%{label}</b><br>Value: %{value}'

)

fig4_2_1.show()

"""Only two courses offer both daytime and evening formats, with the daytime option being more popular. The Digital Marketing course has the highest enrollment (56%) — twice as many students as the UX/UI Design course (27%). The Web Developer course has the lowest share of students (16%).

A more detailed breakdown of the online school’s product structure is available on the dashboard, including product evolution over time and revenue trends by category.

# ***finishing***

Saving data for product analytics
"""

df = {'calls_final': calls_clear, 'contacts_final': contacts_clear, 'deals_final': deals_clear, 'spend_final': spend_clear}

with open('data_2.pkl', 'wb') as f:
    pickle.dump(df, f)

with open('data_2.pkl', 'rb') as f:
    data_2 = pickle.load(f)

data_2.keys()

calls_final, contacts_final, deals_final, spend_final  = data_2.values()

"""Saving data for the dashboard"""

# calls_clear.to_csv('calls_final.csv')
# contacts_clear.to_csv('contacts_final.csv')
# deals_clear.to_csv('deals_final.csv')
# spend_clear.to_csv('spend_final.csv')

calls_clear.to_excel('calls_final.xlsx')
contacts_clear.to_excel('contacts_final.xlsx')
deals_clear.to_excel('deals_final.xlsx')
spend_clear.to_excel('spend_final.xlsx')
