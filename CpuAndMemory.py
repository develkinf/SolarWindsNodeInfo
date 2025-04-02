import logging
import os
import matplotlib.pyplot as plt
import requests
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

# Configurar el registro de eventos
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Estados de la conversación
WAITING_FOR_CHOICE = 1

# Credenciales de SolarWinds
username = os.getenv('DASH_USERNAME')
password = os.getenv('DASH_PASSWORD')

# Función para obtener información de los nodos desde SolarWinds
def all_nodes_info():
    query = "SELECT n.NodeID, n.Caption, n.CPULoad, n.PercentMemoryUsed FROM Orion.Nodes n WHERE n.CustomProperties.Ambiente='Produccion'"
    base_url = "https://localhost:17774/SolarWinds/InformationService/v3/Json/Query"
    solarwinds_api_url = f"{base_url}?query={query}"
    headers = {'Content-Type': 'application/json'}

    try:
        response = requests.get(solarwinds_api_url, auth=(username, password), headers=headers, verify=False)
        if response.status_code == 200:
            return response.json().get('results', [])
        else:
            logger.error(f"Error en la API: {response.status_code}")
            return None
    except requests.RequestException as e:
        logger.error(f"Excepción en la petición: {e}")
        return None


# Función para obtener el top 5 de nodos por CPU o Memoria
def get_top_nodes(all_nodes, metric, top_n=5):
    if not all_nodes:
        return None
    return sorted(all_nodes, key=lambda x: x.get(metric, 0), reverse=True)[:top_n]

# Función para generar y guardar la gráfica
def generate_graph(top_nodes, metric, filename):
    labels = [node.get('Caption', 'N/A') for node in top_nodes]
    values = [node.get(metric, 0) for node in top_nodes]

    plt.figure(figsize=(10, 6))
    plt.bar(labels, values, color='blue' if metric == "PercentMemoryUsed" else 'green')
    plt.xlabel('Nodos')
    plt.ylabel(f'{metric} (%)')
    plt.title(f'Top 5 Nodos por {"Memoria" if metric == "PercentMemoryUsed" else "CPU"}')
    plt.xticks(rotation=45)
    for i, value in enumerate(values):
        plt.text(i, value, str(value), ha='center', va='bottom')
    plt.tight_layout()
    plt.savefig(filename)

# Comando /start con menú de opciones
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [["CPU"], ["Memoria"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("¿Qué información deseas ver?", reply_markup=reply_markup)
    return WAITING_FOR_CHOICE

# Función para manejar la elección del usuario
async def handle_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    choice = update.message.text.strip().lower()
    all_nodes = all_nodes_info()

    if not all_nodes:
        await update.message.reply_text("Error al obtener datos de SolarWinds. Inténtalo más tarde.")
        return ConversationHandler.END

    if choice == "cpu":
        top_nodes = get_top_nodes(all_nodes, "CPULoad")
        filename = "/tmp/top_nodes_cpu_usage.png"
    elif choice == "memoria":
        top_nodes = get_top_nodes(all_nodes, "PercentMemoryUsed")
        filename = "/tmp/top_nodes_memory_usage.png"
    else:
        await update.message.reply_text("Opción no válida. Usa 'CPU' o 'Memoria'.")
        return WAITING_FOR_CHOICE

    generate_graph(top_nodes, "PercentMemoryUsed" if choice == "memoria" else "CPULoad", filename)

    with open(filename, 'rb') as file:
        await update.message.reply_photo(file)

    await update.message.reply_text("¿Quieres ver otra información?", reply_markup=ReplyKeyboardMarkup([["CPU"], ["Memoria"]], one_time_keyboard=True, resize_keyboard=True))
    return WAITING_FOR_CHOICE

# Función para cancelar la conversación
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Operación cancelada.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# Función principal
def main() -> None:
    application = Application.builder().token("YOURTOKEN").build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={WAITING_FOR_CHOICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_choice)]},
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == "__main__":
    main()
