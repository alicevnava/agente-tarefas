# agente-tarefas

Agente de IA em Python que organiza as tarefas do dia num quadro do Trello a partir de uma conversa. Feito com o Google ADK e o Gemini, como Desafio de Projeto da DIO.

## O que o agente faz

Ao começar a conversa, ele cumprimenta, diz a data de hoje e pergunta as tarefas do dia. Cada função Python do arquivo `agente_tarefas/agent.py` vira uma ferramenta:

| Ferramenta | O que faz |
|---|---|
| `criar_tarefa` | Cria um card na lista "A fazer", com nome, descrição e data |
| `listar_tarefas` | Lista os cards do quadro, todos ou só de um status |
| `mover_tarefa` | Move um card entre "A fazer", "Em andamento" e "Concluído" |

O agente decide qual ferramenta chamar lendo a descrição (docstring) de cada função e o que o usuário disse.

## Como configurar

### 1. Trello
1. Crie um quadro chamado `DIO` com as listas `A fazer`, `Em andamento` e `Concluído`.
2. Em `trello.com/power-ups/admin`, crie um aplicativo (marcando que ele não usa recursos de Power-up).
3. Na página "Autenticação do Trello" do app, pegue a **API Key** e o **Secret**, e gere um **Token** com permissão de leitura e escrita.

### 2. Gemini
Crie uma chave gratuita no Google AI Studio (`aistudio.google.com/apikey`).

### 3. Ambiente (Python 3.10 ou superior)
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 4. Credenciais
Copie o modelo e preencha com as suas chaves:
```
cp agente_tarefas/.env.exemplo agente_tarefas/.env
```
O arquivo `.env` está no `.gitignore` e nunca deve ser versionado.

### 5. Rodar
```
adk web --port 8080
```
Abra `http://localhost:8080` e escolha o agente `agente_tarefas`. Usei a porta 8080 porque a 8000 já estava ocupada por outro serviço no meu Windows.

## Melhoria escolhida: aceitar variações de status

**Problema:** as ferramentas exigiam o nome exato da lista. Se o Gemini mandasse `concluido` (sem acento) ou `CONCLUÍDO`, o resultado era "Status inválido".

**Solução:** a função `normalizar_status` deixa o texto em minúsculas, tira espaços das pontas e consulta uma tabela de variações (`concluido`, `feito`, `pronto` viram `Concluído`, e assim por diante). `listar_tarefas` e `mover_tarefa` usam essa função antes de procurar a lista. Se a palavra não estiver na tabela, o erro "Status inválido" continua, de propósito.

**Como testei:**
- Evidência: `prints/07-melhoria-status.png` mostra `concluido` (sem acento) sendo aceito.
- `teste_status.py` testa a função sozinha.
- `teste_melhoria.py` usa o Trello de verdade: `mover_tarefa("Teste do agente", "concluido")` move o card para "Concluído", e uma palavra desconhecida retorna erro.

## Outras decisões
- `conectar_quadro()` concentra a conexão com o Trello numa função só, em vez de repetir em cada ferramenta.
- Todas as ferramentas usam `try/except` e devolvem um dicionário com `status` e `mensagem`, para não quebrar o agente.
- A instrução do agente diz que ele **não** consegue remover tarefas, porque essa ferramenta não existe.
- A data do card é salva ao meio-dia, para evitar o "dia a menos" por causa do fuso horário.

## Testes
Cada ferramenta foi testada direto pelo Python, sem o Gemini:
```
python teste_criar.py
python teste_listar.py
python teste_mover.py
python teste_status.py
python teste_melhoria.py
```
Também testei conversando no `adk web`. Os prints estão na pasta `prints/`.

## Observações
- O modelo usado no `agent.py` é o `gemini-3.5-flash-lite`. Durante os testes, o Gemini devolveu erro 503 (demanda alta) em alguns modelos, e a solução foi trocar de modelo.
- A chave gratuita tem limite diário.
