import os
from dotenv import load_dotenv
from trello import TrelloClient

load_dotenv("agente_tarefas/.env")

cliente = TrelloClient(
    api_key=os.getenv("TRELLO_API_KEY"),
    api_secret=os.getenv("TRELLO_API_SECRET"),
    token=os.getenv("TRELLO_TOKEN"),
)

for quadro in cliente.list_boards():
    print(quadro.name)
