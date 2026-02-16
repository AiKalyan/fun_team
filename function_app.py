import azure.functions as func
import logging
import json
import os

from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings, TurnContext
from botbuilder.schema import Activity, ActivityTypes, Attachment

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
        text="Here’s your card:",   # fallback text
        attachments=[attachment]
    )

async def on_turn(turn_context: TurnContext):
    if turn_context.activity.type == ActivityTypes.message:
        user_text = turn_context.activity.text or ""
        await turn_context.send_activity(build_adaptive_card_activity(user_text))

APP_ID = os.environ.get("MicrosoftAppId", "")
APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")

settings = BotFrameworkAdapterSettings(APP_ID, APP_PASSWORD)
adapter = BotFrameworkAdapter(settings)

async def on_error(turn_context: TurnContext, error: Exception):
    logging.exception(f"[on_turn_error] {error}")
    await turn_context.send_activity("Sorry—something went wrong in the bot.")

adapter.on_turn_error = on_error

app = func.FunctionApp()

@app.function_name("TeamsBotMessages")
@app.route(route="messages", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
async def messages(req: func.HttpRequest) -> func.HttpResponse:
    try:
        body = req.get_body().decode("utf-8")
        activity = Activity().deserialize(json.loads(body))
        auth_header = req.headers.get("Authorization", "")

        invoke_response = await adapter.process_activity(activity, auth_header, on_turn)

        if invoke_response:
            return func.HttpResponse(
                status_code=invoke_response.status,
                body=json.dumps(invoke_response.body) if invoke_response.body else None,
                mimetype="application/json"
            )

        # Standard “accepted” for normal message activities
        return func.HttpResponse(status_code=201)

    except Exception as e:
        logging.exception("Bot endpoint error")
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)
