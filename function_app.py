import azure.functions as func

app = func.FunctionApp()

@app.function_name(name="HelloFunction")
@app.route(route="hello", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def hello(req: func.HttpRequest) -> func.HttpResponse:
    name = req.params.get("name", "World")
    return func.HttpResponse(f"Hello {name}!", status_code=200)
