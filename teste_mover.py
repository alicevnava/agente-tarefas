from agente_tarefas.agent import mover_tarefa, listar_tarefas

print(mover_tarefa("Teste do agente", "Em andamento"))
print(listar_tarefas("Em andamento"))
print(mover_tarefa("Teste do agente", "Inexistente"))
