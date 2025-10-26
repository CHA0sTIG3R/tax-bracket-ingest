# lambda_handler.py
from tax_bracket_ingest.run_ingest import main

def handler(event, context):
    if event.get("dry_run", True):
        print("Dry run mode - no data will be pushed to backend or S3.")
    print("Starting tax bracket ingestion process...")
    
    main()
    return {"statusCode": 200, "body": "Ingestion completed successfully."}