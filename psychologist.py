from langchain_gigachat.chat_models import GigaChat
from langchain_core.messages import HumanMessage, SystemMessage
import json
from bot.tokens import GigaChatKey

llm = GigaChat(
    credentials=GigaChatKey,
    scope="GIGACHAT_API_PERS",
    model="GigaChat",
    verify_ssl_certs=False, 
    streaming=False,
)

messages = [
    SystemMessage(
        content="Ты эмпатичный бот-психолог, который помогает пользователю решить его проблемы. Даешь советы, как чувствовать себя лучше, интересуешься самочувствием и эмоциями."
    )
]

def get_psychologist_response(user_message: str) -> str:
    messages.append(HumanMessage(content=user_message))
    
    res = llm.invoke(messages)
    
    return res.content
