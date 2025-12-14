{% macro setup_gcp_secret() %}
    {% set create_secret_query %}
        CREATE OR REPLACE SECRET my_gcp_secret (
            TYPE S3,
            -- We use env_var to pull keys from the computer, NOT the file
            KEY_ID '{{ env_var("GCP_ACCESS_KEY") }}',
            SECRET '{{ env_var("GCP_SECRET_KEY") }}',
            ENDPOINT 'storage.googleapis.com',
            REGION 'us-east-1',
            URL_STYLE 'path'
        );
    {% endset %}

    {% do run_query(create_secret_query) %}
{% endmacro %}