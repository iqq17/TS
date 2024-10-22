from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer
from msal import ConfidentialClientApplication
import jwt

# Azure AD B2C configuration
tenant_id = "your_tenant_id"
client_id = "your_client_id"
client_secret = "your_client_secret"
policy_name = "your_policy_name"

# Key Vault configuration
key_vault_url = "https://your-keyvault.vault.azure.net/"

# Initialize Key Vault client
credential = DefaultAzureCredential()
secret_client = SecretClient(vault_url=key_vault_url, credential=credential)

# Retrieve secrets from Key Vault
acs_connection_string = secret_client.get_secret("acs-connection-string").value
cosmos_connection_string = secret_client.get_secret("cosmos-connection-string").value

# Initialize MSAL application
msal_app = ConfidentialClientApplication(
    client_id,
    authority=f"https://{tenant_id}.b2clogin.com/{tenant_id}.onmicrosoft.com/{policy_name}",
    client_credential=client_secret,
)

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"https://{tenant_id}.b2clogin.com/{tenant_id}.onmicrosoft.com/{policy_name}/oauth2/v2.0/authorize",
    tokenUrl=f"https://{tenant_id}.b2clogin.com/{tenant_id}.onmicrosoft.com/{policy_name}/oauth2/v2.0/token",
)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, verify=False)  # In production, verify the token
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
    
    # Here you would typically validate the user against your database
    return username

# Use this dependency in your FastAPI routes to ensure authentication
# @app.get("/protected-route")
# async def protected_route(current_user: str = Depends(get_current_user)):
#     return {"message": f"Hello, {current_user}"}