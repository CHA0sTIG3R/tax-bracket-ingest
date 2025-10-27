# lambda_handler.py
from tax_bracket_ingest.run_ingest import main, is_dry_run

def handler(event, context):
    if is_dry_run():
        print("Dry run enabled via DRY_RUN env var - backend and S3 writes are skipped.")
    print("Starting tax bracket ingestion process...")
    
    main()
    return {"statusCode": 200, "body": "Ingestion completed successfully."}
