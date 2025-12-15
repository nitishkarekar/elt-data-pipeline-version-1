# elt-data-pipeline-version-1
# Serverless EV Data Pipeline (GCP, dbt, MotherDuck, Streamlit)

This repository contains a fully automated, end-to-end data pipeline built using entirely **free-tier** cloud tools.

The goal is to extract real-time Electric Vehicle (EV) registration data, transform it using the dbt framework, and publish a live analytics dashboard. The entire pipeline runs daily with zero manual intervention.

## Architecture Overview

This project follows a Modern Data Stack (MDS) pattern, integrating four key components:

1.  **Extract & Load (EL):** Google Cloud Function (GCF) pulls data and stores it in Google Cloud Storage (GCS).
2.  **Scheduling:** Google Cloud Scheduler orchestrates the GCF to run daily.
3.  **Transform (T):** GitHub Actions runs a dbt (data build tool) project, which connects to the cloud data warehouse.
4.  **Warehouse:** MotherDuck (DuckDB in the cloud) serves as the persistent, high-performance analytical database.
5.  **Visualize:** Streamlit Cloud hosts a live, public dashboard connected to MotherDuck.



## Components and Setup

### Prerequisites

You need accounts and environments set up for the following:

1.  **Google Cloud Platform (GCP):** For Cloud Function, Cloud Scheduler, and Cloud Storage.
2.  **GitHub Account:** To host the code and run GitHub Actions.
3.  **MotherDuck Account:** Obtain your **MotherDuck Token** (the connection password).
4.  **Streamlit Cloud Account:** To host the free dashboard.

### 1. Google Cloud Setup (EL)

This sets up the daily data ingestion job.

| File | Description |
| :--- | :--- |
| `main.py` | The Cloud Function code that fetches the API data, converts it to Parquet, and uploads it to GCS. |
| `requirements.txt` | Lists Python dependencies for the Cloud Function (`functions-framework`, `requests`, `pandas`, `google-cloud-storage`, `pyarrow`). |

**Key Steps:**

* **Cloud Storage:** Create a bucket (e.g., `ev-pipeline-fresh-v1`) to store the raw Parquet files.
* **Cloud Function:** Deploy the `main.py` function as an HTTP-triggered function.
* **Cloud Scheduler:** Create an HTTP job targeting the Cloud Function URL, set to run daily (e.g., `0 6 * * *` for 6:00 AM UTC). **Ensure OIDC authentication is configured.**

### 2. Data Transformation (dbt)

dbt defines the models and transformation logic.

* **Location:** The dbt project files (`dbt_project.yml`, `models/`, etc.) reside in the subfolder `elt_data_pipeline_version_1/`.
* **Models:** The `models/test_data.sql` file reads the raw Parquet file from GCS and creates the final, clean table (`ev_analytics.test_data`) in MotherDuck.

**Crucial Fixes for Cloud Integration:**

* **Secrets:** GCP Access Keys (`GCP_ACCESS_KEY`, `GCP_SECRET_KEY`) and the `MOTHERDUCK_TOKEN` must be stored as **GitHub Secrets**.
* **Initialization Hook:** The GCP keys are activated globally in `dbt_project.yml` using the `on-run-start` hook to allow dbt to access GCS via S3 compatibility.
* **Data Quality:** `models/schema.yml` contains data tests (`not_null`, `unique`) to ensure pipeline integrity.

### 3. Pipeline Automation (GitHub Actions)

The workflow runs daily and acts as the "orchestrator" for the transformation step.

* **File:** `.github/workflows/daily_pipeline.yml`
* **Frequency:** Runs daily via `schedule: - cron: '0 6 * * *'` and manually via `workflow_dispatch`.
* **Dependencies:** Installs the required libraries, including pinned versions for compatibility: `pip install dbt-duckdb>=1.8.1 duckdb==1.4.2 fsspec s3fs gcsfs`.
* **Execution:** Runs `dbt deps`, `dbt run`, and **`dbt test`**.

### 4. Live Dashboard (Streamlit Cloud)

The final visualization layer.

| File | Description |
| :--- | :--- |
| `app.py` | The Streamlit Python script that connects to MotherDuck and renders the charts (Market Share, Adoption Trend, etc.). |
| `requirements.txt` | Defines the necessary Python libraries (`streamlit`, `duckdb==1.4.2`, `pandas`, `altair`). |

**Key Steps:**

1.  **Deployment:** Deploy the app from your GitHub repository to [Streamlit Community Cloud](https://share.streamlit.io/).
2.  **Secrets:** The `MOTHERDUCK_TOKEN` is securely passed to the Streamlit app using the **Streamlit Secrets** configuration (using the TOML format).
3.  **Query Path:** The SQL query in `app.py` uses the fully qualified name `FROM ev_analytics.test_data` to ensure the table is found in MotherDuck.

## Contribution

Feel free to fork this repository, adapt the dbt models for different APIs, or contribute enhancements!

***