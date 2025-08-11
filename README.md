# 🤖 Automação NFE Vinhedo - B/PALMA

Sistema automatizado para emissão de notas fiscais eletrônicas no portal da Prefeitura de Vinhedo.

## 📋 Funcionalidades

- ✅ Automação completa de emissão de NF-e
- ✅ Interface gráfica intuitiva
- ✅ Validação de dados de entrada
- ✅ Sistema de logging detalhado
- ✅ Tratamento de erros robusto
- ✅ Configuração centralizada
- ✅ Progresso em tempo real
- ✅ Copy/Paste automático entre campos
- ✅ Suporte a qualquer formato de competência

## 🚀 Instalação

### Pré-requisitos
- Python 3.8 ou superior
- Google Chrome instalado
- Acesso ao portal NFE Vinhedo

### Passos de Instalação

1. **Clone ou baixe o projeto**
```bash
git clone [URL_DO_REPOSITORIO]
cd automacao-LANCAMENTO-NF-VINHEDO
```

2. **Instale as dependências**
```bash
pip install -r requirements.txt
```

3. **Configure as credenciais**
   
   Crie um arquivo `.env` na raiz do projeto:
   ```env
   NFE_USUARIO=seu_usuario
   NFE_SENHA=sua_senha
   ```

## ⚙️ Configuração

### Estrutura do Excel
O arquivo Excel deve conter as seguintes colunas:
- `CNPJ`: CNPJ da empresa (formato: 00.000.000/0000-00)
- `RAZAO SOCIAL`: Nome da empresa
- `VALOR`: Valor do serviço (número)

### Formato da Competência
Digite qualquer texto para a competência. O sistema aceita qualquer formato.

**Exemplos válidos:**
- `JUNHO`
- `JANEIRO/2025`
- `QUALQUER COISA`
- `123456`
- `ABC`

## 🎯 Como Usar

### Interface Gráfica
1. Execute o arquivo principal:
   ```bash
   python ui.py
   ```

2. Selecione o arquivo Excel com os dados
3. Digite a competência (qualquer formato)
4. Clique em "Iniciar Automação"

### Linha de Comando
```bash
python back.py
```

## 📁 Estrutura do Projeto

```
automacao-LANCAMENTO-NF-VINHEDO/
├── back.py              # Lógica principal da automação
├── ui.py                # Interface gráfica
├── config.py            # Configurações centralizadas
├── validators.py        # Validação de dados
├── logger_config.py     # Configuração de logging
├── requirements.txt     # Dependências do projeto
├── README.md           # Este arquivo
├── .env                # Credenciais (criar manualmente)
└── automacao_nfe.log   # Log de execução (gerado automaticamente)
```

## 🔧 Configurações Avançadas

### Timeouts
Edite o arquivo `config.py` para ajustar os timeouts:
```python
TIMEOUTS = {
    'LOGIN': 60,        # Timeout para login
    'ELEMENT': 15,      # Timeout para elementos
    'PAGE_LOAD': 180,   # Timeout para carregamento de página
    'CLICK': 10,        # Timeout para cliques
    'WAIT': 1          # Tempo de espera padrão
}
```

### Logging
O sistema gera logs detalhados em `automacao_nfe.log` com:
- Início e fim de cada operação
- Erros e exceções
- Progresso da automação
- Informações de debug
- Valores copiados e colados em cada campo

## 🛠️ Solução de Problemas

### Erro: "Driver não encontrado"
- Verifique se o Google Chrome está instalado
- Execute: `pip install webdriver-manager --upgrade`

### Erro: "Arquivo Excel inválido"
- Verifique se o arquivo tem as colunas obrigatórias
- Certifique-se de que os dados estão no formato correto

### Erro: "Credenciais inválidas"
- Verifique o arquivo `.env`
- Confirme se as credenciais estão corretas

### Erro: "Elemento não encontrado"
- Verifique se o site está acessível
- Ajuste os timeouts no `config.py`

### Problema com Copy/Paste
- O sistema usa JavaScript para copy/paste
- Verifique os logs para ver se os valores estão sendo copiados corretamente
- Se houver problemas, o sistema tenta novamente automaticamente

## 📊 Monitoramento

### Logs
- **INFO**: Operações normais
- **WARNING**: Avisos e situações não críticas
- **ERROR**: Erros que impedem a continuação
- **DEBUG**: Informações detalhadas para debug

### Status na Planilha
- `Nota Emitida`: Sucesso na emissão
- `Erro: [descrição]`: Erro durante o processamento
- `[vazio]`: Ainda não processado

## 🔒 Segurança

- ✅ Credenciais em arquivo `.env` (não versionado)
- ✅ Validação de dados de entrada
- ✅ Tratamento seguro de exceções
- ✅ Logs sem informações sensíveis

## 🎯 Funcionalidades Técnicas

### Copy/Paste Automático
O sistema copia automaticamente os seguintes campos do tomador para o serviço:
- **Rua**: `RuaTomador` → `RuaServico`
- **Número**: `NumeroTomador` → `NumeroServico`
- **UF**: `UFTomador` → `UFServico`
- **Bairro**: `BairroTomador` → `BairroServico`
- **CEP**: `CEPTomador` → `CEPServico`
- **Cidade**: `CidadeTomador` → `CidadeServico`

### Validação de Dados
- Verifica se o arquivo Excel existe
- Valida se as colunas obrigatórias estão presentes
- Verifica formato do CNPJ
- Valida se os valores são numéricos
- Aceita qualquer formato de competência

### Tratamento de Erros
- Continua processando mesmo se uma empresa falhar
- Registra erros detalhados nos logs
- Atualiza status na planilha Excel
- Não para a automação por erros individuais

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique os logs em `automacao_nfe.log`
2. Consulte a seção "Solução de Problemas"
3. Entre em contato com a equipe de TI

## 📝 Changelog

### v2.1.0 (Atual)
- ✨ Copy/Paste automático entre campos
- ✨ Suporte a qualquer formato de competência
- ✨ Logs detalhados de copy/paste
- ✨ Verificação dupla de valores copiados
- ✨ Tratamento robusto de erros de copy/paste

### v2.0.0 (Anterior)
- ✨ Sistema de configuração centralizada
- ✨ Validação robusta de dados
- ✨ Logging detalhado
- ✨ Tratamento de erros melhorado
- ✨ Interface gráfica aprimorada

### v1.0.0 (Inicial)
- 🎯 Funcionalidade básica de automação
- 🎯 Interface simples
- 🎯 Processamento sequencial

## 🤝 Contribuição

Para contribuir com o projeto:
1. Faça um fork do repositório
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Abra um Pull Request

## 📄 Licença

Este projeto é de uso interno da empresa B/PALMA.
