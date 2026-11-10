import os
from datetime import datetime
from dotenv import load_dotenv
from trello import TrelloClient
from google.adk.agents.llm_agent import Agent

pasta = os.path.dirname(__file__)
load_dotenv(os.path.join(pasta, ".env"))

NOME_QUADRO = "DIO"

STATUS_VALIDOS = {
    "a fazer": "A fazer",
    "afazer": "A fazer",
    "pendente": "A fazer",
    "em andamento": "Em andamento",
    "andamento": "Em andamento",
    "fazendo": "Em andamento",
    "concluído": "Concluído",
    "concluido": "Concluído",
    "concluída": "Concluído",
    "concluida": "Concluído",
    "feito": "Concluído",
    "pronto": "Concluído",
}


def normalizar_status(status: str) -> str:
    chave = status.strip().lower()
    return STATUS_VALIDOS.get(chave, status)

def conectar_quadro():
    cliente = TrelloClient(
        api_key=os.getenv("TRELLO_API_KEY"),
        api_secret=os.getenv("TRELLO_API_SECRET"),
        token=os.getenv("TRELLO_TOKEN"),
    )
    for quadro in cliente.list_boards():
        if quadro.name == NOME_QUADRO:
            return quadro
    return None


def criar_tarefa(nome: str, descricao: str, data: str) -> dict:
    """Cria um card na lista 'A fazer' do quadro.

    Args:
        nome: título da tarefa.
        descricao: detalhes da tarefa.
        data: data da tarefa no formato AAAA-MM-DD.

    Returns:
        Um dicionário com o status da operação.
    """
    try:
        quadro = conectar_quadro()
        if quadro is None:
            return {"status": "erro", "mensagem": "Quadro não encontrado."}

        for lista in quadro.list_lists():
            if lista.name == "A fazer":
                card = lista.add_card(name=nome, desc=descricao)
                dia = datetime.strptime(data, "%Y-%m-%d")
                card.set_due(dia.replace(hour=12))
                return {"status": "ok", "mensagem": "Card criado: " + nome}

        return {"status": "erro", "mensagem": "Lista 'A fazer' não encontrada."}
    except Exception as erro:
        return {"status": "erro", "mensagem": str(erro)}


def listar_tarefas(status: str = "") -> dict:
    """Lista os cards do quadro, todos ou só de um status.

    Args:
        status: nome da lista ('A fazer', 'Em andamento' ou 'Concluído').
            Se ficar vazio, lista todos os cards.

    Returns:
        Um dicionário com o status da operação e a lista de tarefas.
    """
    try:
        quadro = conectar_quadro()
        if quadro is None:
            return {"status": "erro", "mensagem": "Quadro não encontrado."}

        tarefas = []
        for lista in quadro.list_lists():
            if status != "" and lista.name != normalizar_status(status):
                continue
            for card in lista.list_cards():
                tarefas.append({
                    "nome": card.name,
                    "descricao": card.desc,
                    "data": str(card.due)[:10],
                    "status": lista.name,
                })

        return {"status": "ok", "tarefas": tarefas}
    except Exception as erro:
        return {"status": "erro", "mensagem": str(erro)}

def mover_tarefa(nome: str, novo_status: str) -> dict:
    """Move um card para outra lista do quadro.

    Args:
        nome: título exato da tarefa que será movida.
        novo_status: nome da lista de destino ('A fazer',
            'Em andamento' ou 'Concluído').

    Returns:
        Um dicionário com o status da operação.
    """
    try:
        quadro = conectar_quadro()
        if quadro is None:
            return {"status": "erro", "mensagem": "Quadro não encontrado."}

        destino = None
        for lista in quadro.list_lists():
            if lista.name == normalizar_status(novo_status):
                destino = lista
        if destino is None:
            return {"status": "erro", "mensagem": "Status inválido: " + novo_status}

        for lista in quadro.list_lists():
            for card in lista.list_cards():
                if card.name == nome:
                    card.change_list(destino.id)
                    return {"status": "ok", "mensagem": nome + " movido para " + destino.name}

        return {"status": "erro", "mensagem": "Tarefa não encontrada: " + nome}
    except Exception as erro:
        return {"status": "erro", "mensagem": str(erro)}


hoje = datetime.now().strftime("%Y-%m-%d")

instrucao = (
    "Você é um assistente que organiza as tarefas do dia do usuário "
    "num quadro do Trello. A data de hoje é " + hoje + ". "
    "Comece a conversa cumprimentando o usuário, dizendo a data de hoje "
    "e perguntando quais tarefas ele quer organizar. "
    "Para cada tarefa, use a ferramenta criar_tarefa com nome, descrição "
    "e data (formato AAAA-MM-DD). Se faltar alguma informação, pergunte. "
    "Para mostrar tarefas, use listar_tarefas, com ou sem status. "
    "Quando o usuário disser que começou ou terminou algo, use "
    "mover_tarefa com um destes status: 'A fazer', 'Em andamento' ou "
    "'Concluído'. Você não consegue remover tarefas."
)

root_agent = Agent(
    model='gemini-3.5-flash-lite',
    name='root_agent',
    description='Organiza as tarefas do dia num quadro do Trello.',
    instruction=instrucao,
    tools=[criar_tarefa, listar_tarefas, mover_tarefa],
)
