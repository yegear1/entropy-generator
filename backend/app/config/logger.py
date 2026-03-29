from loguru import logger
import sys

def setup_app_logger():
    # 1. Limpa o configurador padrão
    logger.remove()

    # 2. Configuração para o TERMINAL (Stdout) - Ideal para Containers
    logger.add(
        sys.stdout,
        colorize=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="DEBUG"
    )

    # 3. Configuração para ARQUIVO (Sem cores, com rotação)
    logger.add(
        "logs/app.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
        level="DEBUG",
        rotation="10 MB",    # Cria novo arquivo a cada 10MB
        retention="5 days",  # Mantém apenas os últimos 5 dias
        compression="zip",   # Compacta logs antigos para economizar espaço
        encoding="utf-8"
    )

setup_app_logger()