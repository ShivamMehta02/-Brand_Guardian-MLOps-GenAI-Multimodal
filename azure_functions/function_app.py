import os
import sys
import azure.functions as func

# Ensure python can import the backend package which resides in the parent folder
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from azure.functions.asgi import AsgiMiddleware
from backend.src.api.server import app as fastapi_app

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="{*route_path}", auth_level=func.AuthLevel.ANONYMOUS)
async def asgi_handler(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    return await AsgiMiddleware(fastapi_app).handle_async(req, context)
