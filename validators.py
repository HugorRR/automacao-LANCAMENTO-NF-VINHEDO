import pandas as pd
import os
import re
from datetime import datetime
from config import Config
from logger_config import setup_logger

logger = setup_logger()

class ValidationError(Exception):
    """Exceção personalizada para erros de validação"""
    pass

def validate_excel_file(file_path):
    """Valida se o arquivo Excel existe e é válido"""
    if not os.path.exists(file_path):
        raise ValidationError(f"Arquivo não encontrado: {file_path}")
    
    if not file_path.lower().endswith(('.xlsx', '.xls')):
        raise ValidationError("Arquivo deve ser do tipo Excel (.xlsx ou .xls)")
    
    try:
        df = pd.read_excel(file_path)
        return df
    except Exception as e:
        raise ValidationError(f"Erro ao ler arquivo Excel: {str(e)}")

def validate_excel_structure(df):
    """Valida se o DataFrame tem as colunas obrigatórias"""
    missing_columns = []
    
    for column in Config.REQUIRED_COLUMNS:
        if column not in df.columns:
            missing_columns.append(column)
    
    if missing_columns:
        raise ValidationError(f"Colunas obrigatórias ausentes: {', '.join(missing_columns)}")
    
    logger.info(f"Estrutura do Excel validada. Colunas encontradas: {list(df.columns)}")

def validate_data_types(df):
    """Valida os tipos de dados das colunas"""
    errors = []
    
    # Valida CNPJ
    if 'CNPJ' in df.columns:
        df['CNPJ'] = df['CNPJ'].astype(str)
        for idx, cnpj in enumerate(df['CNPJ']):
            if not is_valid_cnpj(cnpj):
                errors.append(f"CNPJ inválido na linha {idx + 1}: {cnpj}")
    
    # Valida VALOR
    if 'VALOR' in df.columns:
        for idx, valor in enumerate(df['VALOR']):
            try:
                float(valor)
            except (ValueError, TypeError):
                errors.append(f"Valor inválido na linha {idx + 1}: {valor}")
    
    if errors:
        raise ValidationError(f"Erros de validação:\n" + "\n".join(errors))
    
    logger.info("Tipos de dados validados com sucesso")

def is_valid_cnpj(cnpj):
    """Valida formato básico do CNPJ"""
    # Remove caracteres especiais
    cnpj_clean = re.sub(r'[^\d]', '', str(cnpj))
    
    # Verifica se tem 14 dígitos
    if len(cnpj_clean) != 14:
        return False
    
    # Verifica se não são todos iguais
    if len(set(cnpj_clean)) == 1:
        return False
    
    return True

def validate_competencia(competencia):
    """Valida se a competência foi informada"""
    if not competencia or not competencia.strip():
        raise ValidationError("Competência é obrigatória")
    
    # Retorna a competência como está, sem validação de formato
    competencia_limpa = competencia.strip()
    logger.info(f"Competência aceita: {competencia_limpa}")
    return competencia_limpa

def validate_all_inputs(excel_path, competencia):
    """Valida todas as entradas do sistema"""
    logger.info("Iniciando validação de entradas...")
    
    try:
        # Valida arquivo Excel
        df = validate_excel_file(excel_path)
        
        # Valida estrutura
        validate_excel_structure(df)
        
        # Valida tipos de dados
        validate_data_types(df)
        
        # Valida competência e obtém o formato correto
        competencia_formatada = validate_competencia(competencia)
        
        logger.info("Todas as validações passaram com sucesso!")
        return df, competencia_formatada
        
    except ValidationError as e:
        logger.error(f"Erro de validação: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Erro inesperado durante validação: {str(e)}")
        raise ValidationError(f"Erro inesperado: {str(e)}")
