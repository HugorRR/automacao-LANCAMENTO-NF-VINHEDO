import logging
import os
from datetime import datetime
from config import Config

def setup_logger(name='automacao_nfe'):
    """Configura e retorna o logger do sistema"""
    
    # Cria o logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, Config.LOGGING['level']))
    
    # Evita duplicação de handlers
    if logger.handlers:
        return logger
    
    # Cria o formato das mensagens
    formatter = logging.Formatter(Config.LOGGING['format'])
    
    # Handler para arquivo
    log_file = os.path.join(os.path.dirname(__file__), Config.LOGGING['file'])
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    
    # Handler para console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Adiciona os handlers ao logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def log_automation_start(empresa, cnpj):
    """Log do início da automação para uma empresa"""
    logger = setup_logger()
    logger.info(f"Iniciando automação para empresa: {empresa} (CNPJ: {cnpj})")

def log_automation_success(empresa, cnpj):
    """Log de sucesso da automação"""
    logger = setup_logger()
    logger.info(f"Automação concluída com sucesso para: {empresa} (CNPJ: {cnpj})")

def log_automation_error(empresa, cnpj, error):
    """Log de erro na automação"""
    logger = setup_logger()
    logger.error(f"Erro na automação para {empresa} (CNPJ: {cnpj}): {str(error)}")

def log_system_info():
    """Log de informações do sistema"""
    logger = setup_logger()
    logger.info("=" * 50)
    logger.info("INÍCIO DA SESSÃO DE AUTOMAÇÃO")
    logger.info(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    logger.info("=" * 50)
