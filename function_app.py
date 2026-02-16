import azure.functions as func
import logging
import json
import os

from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings, TurnContext
from botbuilder.schema import Activity, ActivityTypes, Attachment

# --- Adaptive Card builder (your card, unchanged idea) ---
def build_adaptive_card_content(message: str):
    return {
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "type": "AdaptiveCard",
        "version": "1.4",
        "body": [
            {"type": "TextBlock", "size": "Large", "weight": "Bolder", "text": "New Message Received"},
            {"type": "TextBlock", "text": message, "wrap": True},
            {"type": "FactSet", "facts": [{"title": "Source:", "value": "Azure Function (Bot Endpoint)"}]},
        ],
    }

def build_adaptive_card_activity(message: str) -> Activity:
    card = build_adaptive_card_content(message)
    attachment = Attachment(
        content_type="application/vnd.microsoft.card.adaptive",
        content=card
    )
    return Activity(
        type=ActivityTypes.message,
        attachments=[attachment]
    )

# --- Bot logic: what to do when a message arrives ---
async def on_turn(turn_context: TurnContext):
    if turn_context.activity.type == ActivityTypes.message:
        user_text = turn_context.activity.text or ""
        reply = build_adaptive_card_activity(user_text)
        await turn_context.send_activity(reply)

# --- Adapter setup (Bot Framework) ---
APP_ID = os.environ.get("MicrosoftAppId", "")
APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")

settings = BotFrameworkAdapterSettings(APP_ID, APP_PASSWORD)
adapter = BotFrameworkAdapter(settings)

app = func.FunctionApp()

@app.function_name("TeamsBotMessages")
@app.route(route="messages", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
async def messages(req: func.HttpRequest) -> func.HttpResponse:
    """
    Bot Framework messaging endpoint for Teams.
    Azure Bot -> Teams channel will POST activities here.
    """
    try:
        body = req.get_body().decode("utf-8")
        activity = Activity().deserialize(json.loads(body))
        auth_header = req.headers.get("Authorization", "")

        # process_activity validates auth and routes to your on_turn
        invoke_response = await adapter.process_activity(activity, auth_header, on_turn)

        # Bot Framework expects 200/201; invoke_response is used for invoke activities.
        if invoke_response:
            return func.HttpResponse(
                status_code=invoke_response.status,
                body=json.dumps(invoke_response.body) if invoke_response.body else None,
                mimetype="application/json"
            )

        return func.HttpResponse(status_code=200)

    except Exception as e:
        logging.exception("Bot endpoint error")
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)
