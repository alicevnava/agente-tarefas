from agente_tarefas.agent import normalizar_status

print(normalizar_status("concluido"))
print(normalizar_status("CONCLUÍDO"))
print(normalizar_status(" em andamento "))
print(normalizar_status("xyz"))
