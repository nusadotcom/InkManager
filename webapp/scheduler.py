import schedule
import time
from emails import correr_todos

# Corre todos os dias às 09:00
schedule.every().day.at("09:00").do(correr_todos)

print("⏰ Scheduler de emails ativo — a correr todos os dias às 09:00")
print("   (Ctrl+C para parar)\n")

# Corre uma vez logo ao iniciar para testar
correr_todos()

while True:
    schedule.run_pending()
    time.sleep(60)
