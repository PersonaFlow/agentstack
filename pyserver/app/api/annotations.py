from typing import Annotated

from fastapi import Depends
from pyserver.app.core.api_key import get_api_key

from fastapi.security.api_key import APIKey

ApiKey = Annotated[APIKey, Depends(get_api_key)]
