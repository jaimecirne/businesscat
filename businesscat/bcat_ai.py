import sys
import os
import logging
import ocrspace
from bcat_pagamento_dao import (obter_pagamentos)
from langchain.chains import create_extraction_chain_pydantic
from langchain_core.pydantic_v1 import BaseModel
from langchain.text_splitter import CharacterTextSplitter
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from datetime import datetime

class Quando(BaseModel):
    datetime:datetime
    ano:str
    mes:str
    dia:str
    hora:str
    minutos:str
    segundos:str
    
class Pagamento(BaseModel):
    valor:int                              
    quando:Quando                
    estabelecimento:str
    categoria:str

# enable logging
logging.basicConfig(
    # filename=f"log {__name__} pix2txt_bot.log",
    format='%(asctime)s - %(funcName)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# get logger
logger = logging.getLogger(__name__)

api = ocrspace.API()


def respond_error(error_details):
    logger.error(f"{error_details}", exc_info=True)
    sys.exit(1)


def analisar_texto_pagamento(source_text, OPENAI_API_KEY):
    text_splitter = CharacterTextSplitter()
    texts = text_splitter.split_text(source_text)

    logger.info(texts)        

    try:
        llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo", openai_api_key=OPENAI_API_KEY)

        chain = create_extraction_chain_pydantic(pydantic_schema=Pagamento, llm=llm)
    
        result = chain.run(texts)

        return result[0]
    
    except Exception as e:
        logger.error(f"unable to using a openIA for analize the text from picture -- {e}", exc_info=True)
        raise ValueError("Não to conseguindo entender esse print, eu sou só um gato")
    

