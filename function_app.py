import azure.functions as func
import logging

app = func.FunctionApp()

@app.function_name("HttpTrigger")
@app.route(route="hello", methods=["GET", "POST"])
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Function that responds to HTTP requests
    """
    logging.info('HTTP trigger function processed a request.')
    
    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
            name = req_body.get('name')
        except ValueError:
            pass
    
    if name:
        return func.HttpResponse(
            f"Hello, {name}! This HTTP-triggered function executed successfully.",
            status_code=200
        )
    else:
        return func.HttpResponse(
            "Please pass a name on the query string or in the request body",
            status_code=400
        )
