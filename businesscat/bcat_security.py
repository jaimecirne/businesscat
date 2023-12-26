import os
from dotenv import load_dotenv
from telethon.tl.types import Chat

load_dotenv()

USUARIOS_PERMITIDOS = []

def is_usuario_permitido(user_id):    
    return user_id in get_allow_users()

def get_allow_users():
    if not os.environ.get("USUARIOS_PERMITIDOS"):
        raise("unable to get env USUARIOS_PERMITIDOS")
    else:
        l = os.environ.get('USUARIOS_PERMITIDOS').split()
        USUARIOS_PERMITIDOS = [eval(i) for i in l]
        return USUARIOS_PERMITIDOS

def get_allow_group():
    return int(os.environ.get("GRUPO_PERMITIDO_ID"))

async def verificar_permissao(event):
    user_id = event.sender_id
    # Verifica se a mensagem veio de uma conversa privada ou do grupo específico
    if event.is_private or (isinstance(event.chat, Chat) and event.chat.id == get_allow_group()):
        if not is_usuario_permitido(user_id):
            mensagem = "Desculpe, você não tem permissão para usar este bot."
            await event.respond(mensagem)
            return False
        return True
    return False    

def get_var_path():
    if not os.environ.get("API_ID"):
        raise("unable to get env API_ID")
    if not os.environ.get("API_HASH"):
        raise("unable to get env API_HASH")
    if not os.environ.get("TOKEN"):
        raise("unable to get env TOKEN")
    if not os.environ.get("OPENAI_API_KEY"):
        raise("unable to get env OPENIA_API_KEY")
    if not os.environ.get("USUARIOS_PERMITIDOS"):
        raise("unable to get env USUARIOS_PERMITIDOS")
    if not os.environ.get("GRUPO_PERMITIDO_ID"):
        raise("unable to get env GRUPO_PERMITIDO_ID")
    else:
        API_ID = os.environ.get("API_ID")
        API_HASH = os.environ.get("API_HASH")
        TOKEN = os.environ.get("TOKEN")
        OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
        USUARIOS_PERMITIDOS = get_allow_users()
        GRUPO_PERMITIDO_ID = get_allow_group()

    return API_ID, API_HASH, TOKEN, OPENAI_API_KEY, USUARIOS_PERMITIDOS, GRUPO_PERMITIDO_ID