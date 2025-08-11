import pyautogui
import time
import os
from config import Config
from logger_config import setup_logger

logger = setup_logger()

def safe_click_image(image_path, timeout=10, confidence=0.8):
    """
    Clica em uma imagem de forma segura com tratamento de erro
    
    Args:
        image_path: Caminho para a imagem
        timeout: Tempo limite para encontrar a imagem
        confidence: Confiança da correspondência (0-1)
    
    Returns:
        bool: True se clicou com sucesso, False caso contrário
    """
    tempo_inicio = time.time()
    
    while time.time() - tempo_inicio < timeout:
        try:
            posicao = pyautogui.locateCenterOnScreen(image_path, confidence=confidence)
            if posicao is not None:
                pyautogui.click(posicao)
                logger.info(f"Clique realizado com sucesso em: {os.path.basename(image_path)}")
                return True
        except pyautogui.ImageNotFoundException:
            pass
        except Exception as e:
            logger.warning(f"Erro ao tentar clicar em {image_path}: {str(e)}")
        
        time.sleep(Config.PYAUTOGUI_CONFIG['pause'])
    
    logger.warning(f"Timeout ao tentar clicar em: {os.path.basename(image_path)}")
    return False

def safe_write_text(text, delay=0.1):
    """
    Escreve texto de forma segura
    
    Args:
        text: Texto a ser escrito
        delay: Delay entre caracteres
    """
    try:
        pyautogui.write(str(text), interval=delay)
        logger.info(f"Texto escrito: {text}")
    except Exception as e:
        logger.error(f"Erro ao escrever texto: {str(e)}")

def safe_press_key(key, times=1):
    """
    Pressiona uma tecla de forma segura
    
    Args:
        key: Tecla a ser pressionada
        times: Número de vezes
    """
    try:
        for _ in range(times):
            pyautogui.press(key)
            time.sleep(0.1)
        logger.info(f"Tecla pressionada: {key} ({times} vezes)")
    except Exception as e:
        logger.error(f"Erro ao pressionar tecla {key}: {str(e)}")

def safe_hotkey(*keys, times=1):
    """
    Executa combinação de teclas de forma segura
    
    Args:
        *keys: Teclas a serem pressionadas simultaneamente
        times: Número de vezes
    """
    try:
        for _ in range(times):
            pyautogui.hotkey(*keys)
            time.sleep(0.1)
        logger.info(f"Hotkey executada: {'+'.join(keys)} ({times} vezes)")
    except Exception as e:
        logger.error(f"Erro ao executar hotkey {'+'.join(keys)}: {str(e)}")

def navigate_tabs(direction='forward', count=1):
    """
    Navega entre campos usando Tab ou Shift+Tab
    
    Args:
        direction: 'forward' para Tab, 'backward' para Shift+Tab
        count: Número de tabs a navegar
    """
    if direction == 'forward':
        safe_press_key('tab', count)
    elif direction == 'backward':
        safe_hotkey('shift', 'tab', times=count)
    
    logger.info(f"Navegação: {count} tabs para {direction}")

# Funções específicas para navegação (mantendo compatibilidade)
def tab10():
    """Navega 10 tabs para frente"""
    navigate_tabs('forward', 10)

def shift_tab8():
    """Navega 8 tabs para trás"""
    navigate_tabs('backward', 8)

def shift_tab9():
    """Navega 9 tabs para trás"""
    navigate_tabs('backward', 9)

def shift_tab15():
    """Navega 15 tabs para trás"""
    navigate_tabs('backward', 15)

def shift_tab6():
    """Navega 6 tabs para trás"""
    navigate_tabs('backward', 6)

def tab11():
    """Navega 11 tabs para frente"""
    navigate_tabs('forward', 11)

def copy_field():
    """Copia o conteúdo do campo atual"""
    safe_hotkey('ctrl', 'c')
    logger.info("Campo copiado")

def paste_field():
    """Cola o conteúdo no campo atual"""
    safe_hotkey('ctrl', 'v')
    logger.info("Campo colado")

def clear_field():
    """Limpa o conteúdo do campo atual"""
    safe_hotkey('ctrl', 'a')
    safe_press_key('delete')
    logger.info("Campo limpo")

def wait_for_element(timeout=5):
    """Aguarda um tempo para carregamento de elementos"""
    time.sleep(timeout)
    logger.info(f"Aguardou {timeout} segundos para carregamento")

def get_image_path(image_name):
    """
    Retorna o caminho completo para uma imagem
    
    Args:
        image_name: Nome do arquivo de imagem
    
    Returns:
        str: Caminho completo da imagem
    """
    return os.path.join(Config.IMAGEM_DIR, image_name)
