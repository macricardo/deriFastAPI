from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from routes.security_police import router as security_police_router
import orjson

class PrettyORJSONResponse(ORJSONResponse):
    def render(self, content: any) -> bytes:
        return orjson.dumps(content, option=orjson.OPT_INDENT_2)

app = FastAPI(default_response_class=PrettyORJSONResponse)

# Include the security_police router
app.include_router(security_police_router, prefix="/api")