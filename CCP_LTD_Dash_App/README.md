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

