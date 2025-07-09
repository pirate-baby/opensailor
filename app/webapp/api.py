from ninja import NinjaAPI
from webapp.settings import APP_NAME

api = NinjaAPI(
    title=f"{APP_NAME} API",
)


@api.get("/add")
def add(_request, a: int, b: int):
    return {"result": a + b}
