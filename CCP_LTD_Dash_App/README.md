# Financial Analytics Dashboard using Plotly & Dash

Natalia Kazakevych, Oktober 2025

Keywords: Python, Pandas, Plotly, requests, Dash App, Render, Supabase.

## Overview

Contemporary financial analysis requires not only data collection but also rapid visual interpretation to enhance data informativeness. This project automates the full data pipeline — from extraction and processing to visualization — providing a clear and intuitive view of financial performance trends.

## Tech Stack

**Frontend/Application** - *Plotly + Dash App*

**Backend/Logic** - *Python*

**Data Processing** - *pandas, io, os, sqlite3, zipfile, requests, dash*  

**Hosting/Deployment** - *Render* ( [`Dash_on_Render↗️`](https://ccp-ltd-dash-app-dcip.onrender.com) )

**Database/Storage** - *Supabase (JSON Storage)*

**Raw Data Source** - from another GitHub page ( [`Roni Hogri↗️`](https://github.com/ronihogri/financial-doc-reader/blob/main/steps/step3_extract_by_concept/SEC_filing_reader_step3.py) ).


## Features/Functionality

**Dashboard description**:

The dashboard shows the dynamics of financial indicators such as CCP (Cash and Cash Position) and LTD (Long-Term Debt) in 2019-2024: [`image_dash↗️`](./image/image_dash.jpeg). The dashboard has two common slicers. The first one is by company - you can select all companies, one or several companies. The second choice of the period is that you can set one year, or any range between 2019 and 2024.

**Interactive visualizations**:

[`visualization_1↗️`](./image/image_fig_1.ccp_ltd_chart.png) - CCP and LTD by Company,

[`visualization_2↗️`](./image/image_fig_2.ccp_ltd_ratio_chart.png) - Ratio CCP/LTD by Company,

[`visualization_3↗️`](./image/image_fig_3.Ratio_CCP_LTD%20Heatmap.png) - Ratio CCP/LTD Heatmap by Company and Quarter.

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

***1. ETL Pipeline:***

The data is sourced from [`Roni Hogri↗️`](https://github.com/ronihogri/financial-doc-reader/blob/main/steps/step3_extract_by_concept/SEC_filing_reader_step3.py).

A script is being used [`preparation_data.py↗️`](./preparation_data.py) for cleaning, transformation, and formation of the Final Dataset.

The final Dataset and JSON visualizations are uploaded to Supabase for quick access.

***2. Create Visualizations:***

All visualizations are created using Plotly Python.

*The first visualization:*

<img width="1000" height="311" alt="image" src="https://github.com/user-attachments/assets/1c887f47-5b35-4812-a293-9e03cb4697f7" />


It presents CCP and LTD dynamics in absolute values, offering a clear view of how each company’s liquidity and debt positions change over time. With an interactive slicer, users can focus on specific metrics or companies, making it easy to detect growth patterns, financial stability, and relative scale differences. This chart effectively conveys the overall magnitude and direction of financial movements, serving as a key step toward understanding broader financial trends.

*The second visualization:* 

<img width="600" height="383" alt="image" src="https://github.com/user-attachments/assets/8e0e26fa-14a3-4180-b190-51cab606e36d" />


It extends the analysis by shifting the focus from absolute to relative values — highlighting efficiency and sustainability. It visualizes the liquidity ratio (CCP/LTD), showing how effectively companies can cover long-term debt with available cash. Standard thresholds (0.2, 0.5, and 1) serve as benchmarks for evaluating performance, making it easy to compare companies regardless of their scale. This chart enables quick identification of financial stability levels and trends, offering a deeper understanding of operational soundness beyond simple growth figures.

*The third visualization:* 

 <img width="600" height="365" alt="image" src="https://github.com/user-attachments/assets/8697c9cd-40d7-4655-bdb7-84cf34549025" />


It presents a heatmap of the liquidity ratio, offering an intuitive overview of companies’ financial health across different periods. The visualization includes four main color ranges: 0–0.2 (red) – critical, 0.2–0.5 (yellow) – moderate, 0.5–1 (blue) – acceptable, and above 1 (green) – excellent. The varying color intensity enhances visual perception and helps quickly identify patterns and anomalies. This format enables efficient pattern recognition, making it easy to spot trends, risks, and stability zones when comparing indicators across different companies and time periods.

***Comments:***

**First**, keep in mind that the actual ranges for the absolute liquidity ratio in practice may slightly vary depending on the industry a company operates in.

**Second**, the choice of benchmarks specifically for the absolute liquidity ratio is somewhat questionable, as the components of CCP and LTD are not clearly defined. Depending on the numerator and denominator, different liquidity ratios can be calculated — such as the current ratio, quick ratio, absolute liquidity ratio, and others. Accordingly, the benchmark values (0.2, 0.5, and 1) may vary. However, when focusing on cash and cash equivalents, the absolute liquidity ratio remains the most relevant.

***3. Build Dashboard:***

The dashboard are created using DashApp  in the [`dash_created.py↗️`](./dash_created.py) script, which combines all visualizations into a single web interface [`image_dash↗️`](./image/image_dash.jpeg). The code automatically detects whether to run locally (on your computer) or on Render for deployment. If deployed on Render, it uses the environment variable RENDER to set the correct host and port [`go to Dash_on_Render↗️`](https://ccp-ltd-dash-app-dcip.onrender.com). Otherwise, it runs on localhost: 8051 for local testing.

## Deployment
Platform: Deployed on Render.

Link: [`go to Dash_on_Render↗️`](https://ccp-ltd-dash-app-dcip.onrender.com)

## Contacts of the authors of the project
Author: [`NataLK-tech↗️`](https://github.com/NataLK-tech)

For questions or suggestions: [`Linkedn↗️`](https://www.linkedin.com/in/natalia-kazakevych-131478348/)

Data source for analysis: [`Roni Hogri↗️`](https://github.com/ronihogri/financial-doc-reader/blob/main/steps/step3_extract_by_concept/SEC_filing_reader_step3.py).
