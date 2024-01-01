import logging
import time
import sys
from telethon.tl.types import Chat

# 3rd party libs
from telethon import (
    TelegramClient,
    errors,
    events
)

from bcat_helper import (respond_error, convrt_return_txt, clean_up_pix, gerar_planilha)

from businesscat.bcat_ai import (analisar_texto_pagamento)

from bcat_pagamento_dao import (adicionar_pagamento)

from bcat_security import (get_var_path, verificar_permissao)

try:
    (API_ID, API_HASH, TOKEN, OPENAI_API_KEY, USUARIOS_PERMITIDOS, GRUPO_PERMITIDO_ID) = get_var_path()
except ValueError as e:
    respond_error(e)

# enable logging
logging.basicConfig(
    format='%(asctime)s - %(funcName)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# get logger
logger = logging.getLogger(__name__)

botter = TelegramClient('MimiBCat', API_ID, API_HASH).start(bot_token=TOKEN)

@botter.on(events.NewMessage(incoming=True, pattern="/start"))
async def start_event_handler(event):
    if not await verificar_permissao(event):
        return
    user_id, user_name = await get_id_user_name(event)
    logger.info(f"user_id {user_id} user_name {user_name} has started the bot")
    await event.respond(f" Mewn **{user_name}** eu sou o Mimi contador, se você me mandar um print eu vou pegar os dados e colocar na planilha de gastos.")

@botter.on(events.NewMessage(incoming=True, pattern="/planilha"))
async def planilha_event_handler(event):
    if not await verificar_permissao(event):
        return
    user_id, user_name = await get_id_user_name(event)
    logger.info(f"user_id {user_id} user_name {user_name} has clicked /planilha")
    
    loading_gif = await event.reply("Deixa eu analizar esse print aqui, ...", file='loading.gif')
    
    try:
        planilha = gerar_planilha()
    except ValueError as e:
        await event.reply(f"Erro: {e}")
    else:
        await event.reply("", file=planilha)
    finally:
        await loading_gif.delete()


@botter.on(events.NewMessage(incoming=True, pattern="/help"))
async def help_event_handler(event):
    if not await verificar_permissao(event):
        return
    user_id, user_name = await get_id_user_name(event)
    logger.info(f"user_id {user_id} user_name {user_name} has clicked /help")
    await event.respond(
        "@buinesscat_bot posso arquivas seus pagamentos. "
        "__Apenas me envie os prints__"
        "\n\nPara começar, digite /start."
        "\n\nPara baixar a planilha, digite /planilha para uma planilha geral e /planilha [numero_do_ano-numero_do_mes] para um so daquele mês especifico."
        "\n\nUse /help para ter ajuda.\n\nEu só consigo entender bem a códificação LATIN."
    )

async def get_bot_info():
    self_id = await botter.get_me()
    return self_id

async def check_content(event):
    if not await verificar_permissao(event):
        return
    bot_info = await get_bot_info()
    user_id, user_name = await get_id_user_name(event)
    logger.info(f"checking if user_id {user_id} user_name {user_name} sent a picture")
    if event.photo:
        return True
    elif event.raw_text.lower() == "/start" or event.raw_text.lower() == f"@{bot_info.username.lower()} /start":
        return False
    elif event.raw_text.lower() == "/planilha" or event.raw_text.lower() == f"@{bot_info.username.lower()} /planilha":
        return False
    elif event.raw_text.lower() == "/help" or event.raw_text.lower() == f"@{bot_info.username.lower()} /help":
        return False
    else:
        await event.reply(
            f"**{user_name}**, você me enviou um __Comando que não sei fazer__, se tá complicado digite /help"
        )
        return False


@botter.on(events.NewMessage(incoming=True, func=check_content))
async def pic_event_handler(event):
    if not await verificar_permissao(event):
        return
    user_id, user_name = await get_id_user_name(event)
    logger.info(f"checking if user_id {user_id} user_name {user_name} did send a picture")
    pic_file = await botter.download_media(event.photo, file="comprovantes/")
    logger.info(f"downloading picture sent by user_id {user_id} user_name {user_name}")
    if not pic_file:
        logger.warning(f"user_id {user_id} user_name {user_name} didn't send a proper picture")
        await event.reply("Me mande o print de um comprovante pelo amor de Deus!!!")
        await event.delete()
    else:
        logger.info(f"user_id {user_id} user_name {user_name} has sent a proper picture")
        loading_gif = await event.reply("Deixa eu analizar esse print aqui, ...", file='loading.gif')
        logger.info(f"sent loading_gif to user_id {user_id} user_name {user_name}")        
        
        try:
            source_text = convrt_return_txt(pic_file)
            pagamento = analisar_texto_pagamento(source_text=source_text, OPENAI_API_KEY=OPENAI_API_KEY)
            logger.info(pagamento)
            logger.info(f"user_id {user_id} user_name {user_name} is done")
            adicionar_pagamento(user_id, user_name, pagamento.valor, pagamento.estabelecimento, pagamento.categoria, pagamento.quando)        
            data_print = f"{pagamento.quando.strftime('%d-%m-%Y %H:%M')}"
            await event.reply(f"{data_print} {user_name} pagou R$ {pagamento.valor} em {pagamento.estabelecimento} - Comporvante contabilizado")
        except ValueError as e:
            await event.reply(f"Erro: {e}")          
        else:
            logger.info(f"successfully sent extracted text to user_id {user_id} user_name {user_name}")
        finally:
            await loading_gif.delete()

async def get_id_user_name(event):
    if not await verificar_permissao(event):
        return
    user_id, user_name = None, None
    logger.info(f"extracting user_id and user_name from event")
    if event.is_group and event.sender_id:
        user = await botter.get_entity(event.sender_id)
        user_name = user.username
    elif event.chat.username:
        logger.info(f"username exists {event.chat.username}")
        user_name = event.chat.username
    elif event.chat.first_name:
        logger.info(f"username DOESN'T exists, using first_name instead {event.chat.first_name}")
        user_name = event.chat.first_name
    else:
        logger.info(f"neither username nor first_name exist, using unknown username instead")
        user_name = "unknown username"
    user_id = event.sender_id
    logger.info(f"successfully retrieved user_id {user_id} and user_name {user_name}")
    return user_id, user_name


if __name__ == "__main__":
    with botter:
        logger.info(f"starting the bot")
        try:
            botter.run_until_disconnected()
        except errors.FloodWaitError as fwe:
            logger.exception(f"hit flood wait error -- {fwe}, gotta sleep for {fwe.seconds}", exc_info=True)
            time.sleep(fwe.seconds)
            logger.info(f"attempting to re-start the bot")
            botter.run_until_disconnected()
        except errors.FloodError as fe:
            logger.exception(f"hit flood error -- {fe} with message -- {fe.message}", exc_info=True)
            time.sleep(5000)
            logger.info(f"attempting to re-start the bot")
            botter.run_until_disconnected()
        except Exception as e:
            logger.exception(f"unable to start bot -- {e}", exc_info=True)
            logger.info(f"attempting to re-start the bot")
            botter.run_until_disconnected()
        except KeyboardInterrupt:
            logger.warning(f"received EXITCMD, exiting")
            botter.disconnect()
            logger.info(f"bot disconnected, closing bot script")
            sys.exit(0)
        else:
            logger.info(f"successfully started the bot, starting operations")
