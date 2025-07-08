from pyticktick import Client
from pyticktick.settings import TokenV1
from pydantic import SecretStr
from uuid import UUID
import os
from dotenv import load_dotenv

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
access_token = os.getenv("ACCESS_TOKEN")
expiration = os.getenv("EXPIRATION")
tt_username = os.getenv("TT_USERNAME")
tt_password = os.getenv("TT_PASSWORD")

if not all([client_id, client_secret, access_token, expiration, tt_username, tt_password]):
    raise ValueError("Missing required environment variables: CLIENT_ID, CLIENT_SECRET, ACCESS_TOKEN, EXPIRATION, TT_USERNAME, TT_PASSWORD")

# Type assertions after validation
assert client_id is not None
assert client_secret is not None
assert access_token is not None
assert expiration is not None
assert tt_username is not None
assert tt_password is not None

client = Client(
    v1_client_id=client_id,
    v1_client_secret=SecretStr(client_secret),
    v1_token=TokenV1(
        value=UUID(access_token),
        expiration=int(expiration),
    ),
    v2_username=tt_username,
    v2_password=SecretStr(tt_password),
    override_forbid_extra=True,
)