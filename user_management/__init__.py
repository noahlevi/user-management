from user_management.app import app


@app.on_event("startup")
async def startup_event():
    from user_management.db import _create_collection

    _create_collection()


@app.on_event("shutdown")
async def startup_event():
    from user_management.db import _drop_collection

    _drop_collection()
