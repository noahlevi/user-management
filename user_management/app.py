import logging

from fastapi import FastAPI

from user_management.config import init_config, Config

log = logging.getLogger(__name__)


init_config()
# configure_logging()
log.info('Initialization done')

app = FastAPI(docs_url=Config.c.app.docs_url)


# app.include_router(healthcheck.router)
from user_management.api import routes
app.include_router(routes.router)

# app.add_middleware(TrackRequestsMiddleware)
