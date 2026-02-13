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

@app.function_name("MessageHandler")
@app.route(route="messages", methods=["POST"])
def message_handler(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Function that processes messages via POST request
    Expects a JSON body with a 'message' field containing a string
    """
    logging.info('Message handler function processing a POST request.')
    
    try:
        req_body = req.get_json()
        message = req_body.get('message')
        
        if not message:
            return func.HttpResponse(
                "Error: 'message' field is required in the request body",
                status_code=400
            )
        
        if not isinstance(message, str):
            return func.HttpResponse(
                "Error: 'message' must be a string",
                status_code=400
            )
        
        logging.info(f'Received message: {message}')
        
        return func.HttpResponse(
            f"Message received successfully: {message}",
            status_code=200
        )
        
    except ValueError:
        return func.HttpResponse(
            "Error: Invalid JSON in request body",
            status_code=400
        )
    except Exception as e:
        logging.error(f'Error processing message: {str(e)}')
        return func.HttpResponse(
            f"Error processing message: {str(e)}", 
            status_code=500
        )
