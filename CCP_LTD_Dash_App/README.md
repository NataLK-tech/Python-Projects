# Financial Analytics Dashboard using Plotly & Dash

Natalia Kazakevych, Oktober 2025

Keywords: Python, Pandas, Plotly, requests, Dash App, Render, Supabase.

## Overview

The project demonstrates the full development cycle of an interactive dashboard: from obtaining raw data from an external repository to deploying a ready-made application using Plotly Dash

## Tech Stack

**Frontend/Application** - *Plotly + Dash App*

**Backend/Logic** - *Python*

**Data Processing** - *pandas, io, os, sqlite3, zipfile, requests, dash*  

**Hosting/Deployment** - *Render*

**Database/Storage** - *Supabase (JSON Storage)*

**Raw Data Source** - https://github.com/ronihogri/financial-doc-reader/tree/main/steps/step3_extract_by_concept


## Features/Functionality

**Dashboard description**:

The dashboard shows the dynamics of financial indicators such as CCP (Cash and Cash Position) and LTD (Long-Term Debt) in 2019-2024: [`image_dash`](./image_dash.jpeg). The dashboard has two common slicers. The first one is by company - you can select all companies, one or several companies. The second choice of the period is that you can set one year, or any range between 2019 and 2024.

**Interactive visualizations**: 

[`visualization_1`](./image_fig_1.ccp_ltd_chart.png) - CCP and LTD by Company,

[`visualization_2`](./image_fig_2.ccp_ltd_ratio_chart.png) - Ratio CCP/LTD by Company, 

[`visualization_3`](./image_fig_3.Ratio_CCP_LTD%20Heatmap.png) - Ratio CCP/LTD Heatmap by Company and Quarter.


**Data sources**: 

https://github.com/ronihogri/financial-doc-reader/tree/main/steps/step3_extract_by_concept

**Deployment**: 

the dashboard is available via the link: https://ccp-ltd-dash-app-dcip.onrender.com/

**Storing results**: 

https://supabase.com/dashboard/project/jcobxvpdygzzmakkamoy


## Architecture and Process

### Project structure
```
├── images/              # Screenshots of the entire dashboard and visualizations separately
├── Procfile             # Command to launch the dashboard for deployment on Render
├── README.md            # Documentation
├── dash_created.py      # Main script for launching the dashboard
├── f1.py                # Visualization 1 — CCP and LTD by Company
├── f2.py                # Visualization 2 — Ratio CCP/LTD by Company
├── f3.py                # Visualization 3 — Ratio CCP/LTD Heatmap by Company and Quarter
├── preparation_data.py  # Script for receiving and processing data
├── requirements.txt     # List of dependencies

```
### Process schema

<img width="600" height="150" alt="image" src="https://github.com/user-attachments/assets/93e32694-f267-4a32-92e1-dba5e80f233c" />

### Description of the process steps

1. ETL Pipeline:

The data is sourced from [`Roni Hogri`](https://github.com/ronihogri/financial-doc-reader/blob/main/steps/step3_extract_by_concept/SEC_filing_reader_step3.py).

A script is being used [`preparation_data.py`](./preparation_data.py) for cleaning, transformation, and formation of the Final Dataset.

The final Dataset and JSON visualizations are uploaded to Supabase for quick access.

2. Create Visualizations:

The first visualization [`visualization_1`](./image_fig_1.ccp_ltd_chart.png) shows the dynamics of SSP and LTD in absolute terms. A separate slicer is created for it, where you can choose one of these indicators or both at the same time. The pros of this visualization are that we can see the trend. However, the cons include that it only helps compare companies by size. Even if we normalize the data using methods like StandardScaler, MinMaxScaler, or others, the chart becomes more readable, but the information doesn’t change — we can only compare companies by size. This information doesn’t allow us to assess how effectively a company operates in a some time period.

The second visualization [`visualization_2`](./image_fig_2.ccp_ltd_ratio_chart.png) addresses the cons of the first one — it shows the ratio of these indicators. A liquidity ratio is calculated, which helps determine a company’s ability to cover its obligations using liquid assets. The threshold values for this ratio are 0.2, 0.5, and 1 — these are standard benchmarks for absolute liquidity, as they relate to cash and cash equivalents (based on global standards of classic financial analysis). These benchmarks allow comparing companies regardless of their capital size, focusing on how efficiently they manage liquid assets. You don’t even need to compare companies — you can look at the trend of one company’s ratio, compare it with standard values, and make a preliminary assessment of its financial management efficiency.

The third visualization [`visualization_3`](./image_fig_3.Ratio_CCP_LTD%20Heatmap.png) is a heatmap of the liquidity ratio. It has four main color ranges: from 0 to 0.2 (red) – critical value, from 0.2 to 0.5 (yellow) – moderate, from 0.5 to 1 (blue) – acceptable, and above 1 (green) – excellent. The intensity of each color also varies, which improves the visual perception of the results.

Comments: First, keep in mind that the actual ranges for the absolute liquidity ratio in practice may slightly vary depending on the industry a company operates in. Second, the choice of benchmarks specifically for the absolute liquidity ratio is questionable, as the components of SSP and LTD are not clearly defined. Depending on the numerator and denominator, different liquidity ratios can be calculated—current liquidity ratio, quick liquidity ratio, absolute liquidity ratio, and others. Accordingly, the benchmarks will differ. However, when it comes to cash and cash equivalents, the absolute liquidity ratio is the most relevant.

