from fastapi import APIRouter, Depends
from app.dependencies import get_current_user
from app.schemas.chat import SendMessageResponse, SendMessageRequest
from app.core.response import success_response

router = APIRouter()


@router.post("/send", response_model=SendMessageResponse)
async def send_message(
    body: SendMessageRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    User sends a message to the AI psychologist.

    Flow (Firestore option):
    1. Save user message to users/{uid}/chats/{auto_id}
    2. Fetch recent session history for context (last 20 messages)
    3. Call Gemini AI with history + new message
    4. Save AI response to users/{uid}/chats/{auto_id}
    5. Flutter StreamBuilder picks up the new AI message automatically

    Returns immediately after saving user message.
    AI response arrives via Firestore listener on the frontend — no polling needed.

    session_id: if None, a new session is created (new conversation).
    """
    # TODO: ChatService.send(body, uid)
    return success_response(data=None, message="Chat send endpoint ready")