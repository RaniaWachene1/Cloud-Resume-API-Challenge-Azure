import os
import azure.functions as func
import logging
import json
from azure.cosmos import CosmosClient, exceptions

# Initialize Cosmos client using environment variables
cosmos_url = os.getenv("CosmosDB_URL")
cosmos_key = os.getenv("CosmosDB_Key")
database_name = os.getenv("CosmosDB_Database")
container_name = os.getenv("CosmosDB_Container")

# Log the environment variables
logging.info(f"CosmosDB_URL: {cosmos_url}")
logging.info(f"CosmosDB_Key: {cosmos_key}")
logging.info(f"CosmosDB_Database: {database_name}")
logging.info(f"CosmosDB_Container: {container_name}")

cosmos_client = CosmosClient(cosmos_url, credential=cosmos_key)
database = cosmos_client.get_database_client(database_name)
container = database.get_container_client(container_name)

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="resumeapi")
def resumeapi(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        item_id = req.params.get('id')
        if not item_id:
            return func.HttpResponse("Please pass an id in the query string", status_code=400)

        logging.info(f"Fetching item with ID: {item_id}")
        item_response = container.read_item(item=item_id, partition_key=item_id)
        
        # Return the entire document for debugging
        return func.HttpResponse(json.dumps(item_response, indent=2), status_code=200)
    except exceptions.CosmosHttpResponseError as e:
        logging.error(f"Error reading item from Cosmos DB: {e.message}")
        return func.HttpResponse("Error reading item from Cosmos DB", status_code=500)
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return func.HttpResponse("Unexpected error", status_code=500)
