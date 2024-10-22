from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from azure.communication.identity import CommunicationIdentityClient
from azure.core.credentials import AzureKeyCredential
from azure.cosmos import CosmosClient
from azure.identity import DefaultAzureCredential
import os

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Azure Communication Services client
acs_endpoint = os.getenv("ACS_ENDPOINT")
acs_client = CommunicationIdentityClient(acs_endpoint, DefaultAzureCredential())

# Azure Cosmos DB client
cosmos_endpoint = os.getenv("COSMOS_ENDPOINT")
cosmos_key = os.getenv("COSMOS_KEY")
cosmos_client = CosmosClient(cosmos_endpoint, credential=AzureKeyCredential(cosmos_key))
database = cosmos_client.get_database_client("tutoring_db")
users_container = database.get_container_client("users")
sessions_container = database.get_container_client("sessions")

@app.post("/create_session")
async def create_session(user_id: str):
    # Create a new ACS identity
    identity = acs_client.create_user()
    token = acs_client.get_token(identity, ["voip"])

    # Store session data in Cosmos DB
    session_data = {
        "id": str(identity),
        "user_id": user_id,
        "token": token.token,
        "expiration": token.expires_on.isoformat()
    }
    sessions_container.create_item(session_data)

    return {"identity": str(identity), "token": token.token}

@app.get("/join_session/{session_id}")
async def join_session(session_id: str, user_id: str):
    # Retrieve session data from Cosmos DB
    query = f"SELECT * FROM c WHERE c.id = '{session_id}'"
    session = list(sessions_container.query_items(query, enable_cross_partition_query=True))

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Generate a new token for the joining user
    identity = acs_client.get_identity(session_id)
    token = acs_client.get_token(identity, ["voip"])

    return {"token": token.token}

# Add more endpoints for user management, session listing, etc.

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)