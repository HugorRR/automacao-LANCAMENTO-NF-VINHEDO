from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
import time
import os

# Importações dos novos módulos
from config import Config
from logger_config import setup_logger, log_automation_start, log_automation_success, log_automation_error, log_system_info
from validators import validate_all_inputs, ValidationError

# Configuração do logger
logger = setup_logger()

def initialize_driver():
    """Inicializa o driver do Chrome com configurações otimizadas"""
    try:
        chrome_options = Options()
        chrome_options.add_argument(f'user-agent={Config.USER_AGENT}')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get(Config.URL_LOGIN)
        driver.maximize_window()
        
        logger.info("Driver do Chrome inicializado com sucesso")
        return driver
        
    except Exception as e:
        logger.error(f"Erro ao inicializar driver: {str(e)}")
        raise

def login(driver):
    """Realiza o login no sistema NFE Vinhedo"""
    try:
        logger.info("Iniciando processo de login...")
        
        # Clica no botão "Área do Prestador"
        bt_area_do_prestador = WebDriverWait(driver, Config.TIMEOUTS['LOGIN']).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="login"]/div[2]/a[2]'))
        )
        time.sleep(Config.TIMEOUTS['WAIT'])
        bt_area_do_prestador.click()
        logger.info("Botão 'Área do Prestador' clicado")

        # Preenche usuário
        cp_usuario = WebDriverWait(driver, Config.TIMEOUTS['ELEMENT']).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="usuario"]'))
        )
        time.sleep(Config.TIMEOUTS['WAIT'])
        cp_usuario.send_keys(Config.USUARIO)
        logger.info("Usuário preenchido")

        # Preenche senha
        cp_senha = WebDriverWait(driver, Config.TIMEOUTS['ELEMENT']).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="senha"]'))
        )
        time.sleep(Config.TIMEOUTS['WAIT'])
        cp_senha.send_keys(Config.SENHA)
        logger.info("Senha preenchida")

        # Pressiona Tab para finalizar
        cp_senha.send_keys(Keys.TAB)
        logger.info("Login realizado com sucesso")
        
    except Exception as e:
        logger.error(f"Erro durante o login: {str(e)}")
        raise

def copy_field_value(driver, element):
    """Copia o valor de um campo usando JavaScript"""
    try:
        # Seleciona todo o texto
        driver.execute_script("arguments[0].select();", element)
        time.sleep(0.5)
        
        # Copia usando JavaScript
        driver.execute_script("arguments[0].setAttribute('data-copied', arguments[0].value);", element)
        logger.info("Campo copiado com sucesso")
        return True
    except Exception as e:
        logger.error(f"Erro ao copiar campo: {str(e)}")
        return False

def paste_field_value(driver, element, value=None):
    """Cola um valor em um campo"""
    try:
        element.clear()
        if value:
            element.send_keys(value)
        else:
            # Tenta colar o valor copiado anteriormente
            driver.execute_script("arguments[0].value = arguments[0].getAttribute('data-copied') || '';", element)
        logger.info("Campo colado com sucesso")
        return True
    except Exception as e:
        logger.error(f"Erro ao colar campo: {str(e)}")
        return False

def copy_and_paste_between_fields(driver, source_element, target_element, field_name=""):
    """Copia de um campo e cola em outro"""
    try:
        # Copia do campo origem usando JavaScript
        source_value = driver.execute_script("return arguments[0].value;", source_element)
        logger.info(f"Valor copiado do campo {field_name}: '{source_value}'")
        
        # Cola no campo destino
        target_element.clear()
        time.sleep(0.2)
        target_element.send_keys(source_value)
        time.sleep(0.2)
        
        # Verifica se foi colado corretamente
        final_value = target_element.get_attribute('value')
        logger.info(f"Valor colado no campo {field_name}: '{final_value}'")
        
        # Se não foi colado corretamente, tenta com JavaScript
        if source_value != final_value:
            logger.warning(f"Campo {field_name} não foi colado corretamente! Tentando com JavaScript...")
            driver.execute_script("arguments[0].value = arguments[1];", target_element, source_value)
            time.sleep(0.2)
            final_value = target_element.get_attribute('value')
            logger.info(f"Valor após JavaScript no campo {field_name}: '{final_value}'")
        
        logger.info(f"Copy/paste do campo {field_name} realizado com sucesso")
        return True
    except Exception as e:
        logger.error(f"Erro no copy/paste do campo {field_name}: {str(e)}")
        return False

def emissao(driver, excel_path, competencia, progress_callback, status_callback):
    """Função principal de emissão de notas fiscais"""
    try:
        # Validação de entradas
        logger.info("Iniciando validação de entradas...")
        df, competencia_formatada = validate_all_inputs(excel_path, competencia)
        
        # Adiciona coluna de status se não existir
        if 'STATUS' not in df.columns:
            df['STATUS'] = ""
        
        # Prepara dados para processamento
        cnpj_list = df['CNPJ'].astype(str)
        razao_social_list = df['RAZAO SOCIAL'].astype(str)
        valor_list = df['VALOR']
        
        total_items = len(cnpj_list)
        logger.info(f"Total de itens para processar: {total_items}")
        
        # Inicia o processamento
        for index, (cnpj, razao, valor) in enumerate(zip(cnpj_list, razao_social_list, valor_list)):
            try:
                # Atualiza progresso
                progress = int((index + 1) / total_items * 100)
                if progress_callback:
                    progress_callback.emit(progress)
                if status_callback:
                    status_callback.emit(f"Processando: {razao}")
                
                # Log do início da automação para esta empresa
                log_automation_start(razao, cnpj)

                # Acessando botão lançamento
                bt_lançamento = WebDriverWait(driver, Config.TIMEOUTS['PAGE_LOAD']).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="menu"]/a[2]'))
                )
                time.sleep(Config.TIMEOUTS['WAIT'])
                bt_lançamento.click()
                logger.info("Botão 'Lançamento' clicado")

                # Acessando botão fiscal
                bt_nota_fiscal = WebDriverWait(driver, Config.TIMEOUTS['LOGIN']).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="menu"]/div[2]/a[2]'))
                )
                time.sleep(Config.TIMEOUTS['WAIT'])
                bt_nota_fiscal.click()
                logger.info("Botão 'Nota Fiscal' clicado")

                WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "conteudo_window"))) # iframe da emissão
                bt_gerar_notas = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//img[@src='../images/entrar_nfe.gif']")))
                driver.execute_script("arguments[0].scrollIntoView(true);", bt_gerar_notas)
                # Botão gerar notas
                bt_gerar_notas.click()

                # Campo de inserção de CNPJ
                bt_documento = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "Documento")))
                bt_documento.click()
                bt_documento.send_keys(cnpj)
                bt_documento.send_keys(Keys.TAB)
                time.sleep(0.5)

                # Campo de inserção de Rua - Copy/Paste
                cp_rua_tomador = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "RuaTomador")))
                cp_rua_servico = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "RuaServico")))
                copy_and_paste_between_fields(driver, cp_rua_tomador, cp_rua_servico, "Rua")
                time.sleep(0.5)

                # Campo numero - Copy/Paste
                numero_tomador = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "NumeroTomador")))
                numero_servico = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "NumeroServico")))
                copy_and_paste_between_fields(driver, numero_tomador, numero_servico, "Numero")
                time.sleep(0.5)

                # Campo UF - Copy/Paste
                cp_uf_tomador = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "UFTomador")))
                cp_uf_servico = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "UFServico")))
                copy_and_paste_between_fields(driver, cp_uf_tomador, cp_uf_servico, "UF")
                time.sleep(0.5)

                # Campo bairro - Copy/Paste
                bairro_tomador = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "BairroTomador")))
                bairro_servico = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "BairroServico")))
                copy_and_paste_between_fields(driver, bairro_tomador, bairro_servico, "Bairro")
                time.sleep(0.5)

                # Campo CEP - Copy/Paste
                cep_tomador = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "CEPTomador")))
                cep_servico = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "CEPServico")))
                
                # Clica no campo CEP do tomador para garantir que está ativo
                cep_tomador.click()
                time.sleep(0.5)
                
                # Tenta copiar o valor usando JavaScript
                cep_value = driver.execute_script("return arguments[0].value;", cep_tomador)
                logger.info(f"CEP copiado via JavaScript: '{cep_value}'")
                
                # Cola no campo destino
                cep_servico.clear()
                time.sleep(0.2)
                cep_servico.send_keys(cep_value)
                time.sleep(0.2)
                
                # Verifica se foi colado corretamente
                final_cep = cep_servico.get_attribute('value')
                logger.info(f"CEP final no campo serviço: '{final_cep}'")
                
                if cep_value != final_cep:
                    logger.warning(f"CEP não foi colado corretamente! Esperado: '{cep_value}', Obtido: '{final_cep}'")
                    # Tenta novamente com JavaScript
                    driver.execute_script("arguments[0].value = arguments[1];", cep_servico, cep_value)
                    time.sleep(0.2)
                    final_cep = cep_servico.get_attribute('value')
                    logger.info(f"CEP após segunda tentativa: '{final_cep}'")
                
                time.sleep(0.5)

                # Campo Cidade - Copy/Paste
                cidade_tomador = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "CidadeTomador")))
                cidade_servico = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "CidadeServico")))
                copy_and_paste_between_fields(driver, cidade_tomador, cidade_servico, "Cidade")
                time.sleep(0.5)

                # Campo descrição
                cp_descricao = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "descricao")))
                cp_descricao.click()
                descricao = f'REFERENTE AOS SERVIÇOS PRESTADOS {competencia_formatada}/2025.'
                cp_descricao.send_keys(descricao)

                # Selecionando código de atividade
                selecionar_codigo = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "Codigo")))
                selecionar_codigo.click()
                select_obj = Select(selecionar_codigo)
                select_obj.select_by_value("00802- 3.97")

                # Preenchendo valor
                cp_valor = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "Valor")))
                valor_formatado = '{:.2f}'.format(valor)
                cp_valor.send_keys(valor_formatado)

                # Gravando dados
                #cp_gravar_dados = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "gravar")))
                #cp_gravar_dados.click()

                # Voltar para o iframe
                driver.switch_to.default_content()

                # Atualizando status na planilha
                df.loc[df['CNPJ'] == cnpj, 'STATUS'] = 'Nota Emitida'
                df.to_excel(excel_path, index=False)
                time.sleep(5)

                # Log de sucesso
                log_automation_success(razao, cnpj)
                logger.info(f'Nota da empresa: {razao} emitida com sucesso')

            except Exception as e:
                # Log de erro para esta empresa
                log_automation_error(razao, cnpj, str(e))
                logger.error(f"Erro ao processar empresa {razao}: {str(e)}")
                
                # Atualiza status de erro na planilha
                df.loc[df['CNPJ'] == cnpj, 'STATUS'] = f'Erro: {str(e)[:50]}'
                df.to_excel(excel_path, index=False)
                
                # Continua com a próxima empresa
                continue

        logger.info("Processamento de todas as empresas concluído")
        
    except ValidationError as e:
        logger.error(f"Erro de validação: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Erro geral na automação: {str(e)}")
        raise

def run_automation(excel_path, competencia, progress_callback, status_callback):
    """Função principal que executa toda a automação"""
    driver = None
    try:
        # Log do início da sessão
        log_system_info()
        
        # Inicializa o driver
        driver = initialize_driver()
        
        # Realiza login
        login(driver)
        
        # Executa a emissão
        emissao(driver, excel_path, competencia, progress_callback, status_callback)
        
        logger.info("Automação concluída com sucesso!")
        
    except ValidationError as e:
        logger.error(f"Erro de validação: {str(e)}")
        if status_callback:
            status_callback.emit(f"Erro de validação: {str(e)}")
        raise
        
    except Exception as e:
        logger.error(f"Erro durante a automação: {str(e)}")
        if status_callback:
            status_callback.emit(f"Erro: {str(e)}")
        raise
        
    finally:
        # Sempre fecha o driver
        if driver:
            try:
                driver.quit()
                logger.info("Driver do Chrome fechado")
            except Exception as e:
                logger.warning(f"Erro ao fechar driver: {str(e)}")

if __name__ == "__main__":
    run_automation('G:\\Drives compartilhados\\BANCO DE DADOS T.I\\Automacoes\\automacoes-VANIA\\automacao-LANCAMENTO NF VINHEDO\\Dados.xlsx', '01/2025', None, None)
