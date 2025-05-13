# HuB‑IA – Assistente Inteligente para Dados Públicos da Fecomércio

**HuB‑IA** é uma aplicação interativa desenvolvida com **Streamlit** e **LangChain**, capaz de transformar perguntas em linguagem natural em **consultas SQL** eficientes e interpretá-las com naturalidade. Os dados vêm de uma base SQLite contendo informações econômicas como IPCA, PMS, PMC e transações com cartões.

---

## Demonstração
> Pergunte algo como:  
> “Qual a inflação acumulada em Recife?”

<div style="text-align: center;">
  <img src="demo.png" width="700"/>
</div>

---

## Funcionalidades

- Interpretação de perguntas com modelo LLM local (`phi4-mini`)
- Geração de queries SQL automáticas (somente leitura)
- Interpretação amigável e responsiva dos resultados
- Correção automática de colunas inválidas via fuzzy match
- Interface natural com efeito de digitação
- Sugestões contextuais baseadas na pergunta

---

## Estrutura do projeto

```plaintext
hubia_app/
│
├── core/                  # Lógica de negócio
│   ├── database.py        # Conexão e execução SQL
│   ├── engine.py          # Orquestra LLM + SQL + validações
│   ├── history.py         # Histórico de interações
│   ├── llm_agent.py       # Interação com o modelo LLM
│   ├── prompts.py         # Geração de system prompts
│   └── utils.py           # Funções auxiliares gerais
│
├── ui/                    # Interface e efeitos visuais
│   ├── layout.py          # Estilo visual da página
│   └── typing_effect.py   # Efeito de digitação da resposta
│
├── config/
│   └── table_aliases.yaml # Descrições das tabelas
│
├── __init__.py
│
app.py                    # Interface principal Streamlit
````

---

## Requisitos

* Python 3.10+
* [Ollama](https://ollama.com/) instalado localmente com o modelo `phi4-mini`
* [Streamlit](https://streamlit.io/)
* SQLite

---

## Instalação

```bash
# Clone o projeto
git clone https://github.com/ronierisonmaciel/hub-ia.git
cd hub-ia

# Crie e ative o ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

# Instale as dependências
pip install -r requirements.txt
```

---

## Executando

```bash
streamlit run app.py
```

---

## Exemplos de perguntas

- Qual foi o IPCA em Recife?
- Qual a bandeira de cartão com mais emissão?
- Qual o volume de serviços no RN?
- Quantas transações foram feitas com crédito?

---

## Base de dados

O banco `fecomdb.db` é composto por múltiplas tabelas extraídas de dados estatísticos públicos. As descrições legíveis das tabelas estão no arquivo [`table_aliases.yaml`](hubia_app/table_aliases.yaml).

---

## Segurança

* Todas as queries são somente leitura (proibido `INSERT`, `UPDATE`, `DELETE`).
* A identificação de colunas é validada contra `PRAGMA table_info`.
* SQL Injection é prevenido com checagem de nomes e validação regex.

---

## LLM e prompting

O sistema utiliza o modelo `matilde` via Ollama, com prompts personalizados para:

- Geração de SQL (usando descrições e nomes das tabelas)
- Interpretação humanizada dos resultados
- Adição de contexto semântico à pergunta (ex: IPCA localização)

---

## Limpeza de histórico

Caso deseje apagar os registros anteriores:

```bash
rm hubia_history.db
```

---

## Contribuindo

1. Fork este repositório
2. Crie sua branch (`git checkout -b feature/minha-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'feat: adiciona nova feature'`)
4. Push para a branch (`git push origin feature/minha-funcionalidade`)
5. Crie um Pull Request

---

## Licença

Este projeto é licenciado sob os termos da [MIT License](LICENSE).

---

## Autores

Equipe de desenvolvido:

- ALBERTO SILVA
- ARTHUR LIMA
- CARLOS JUNIOR
- GABRIEL VIEIRA
- JEAN SILVA
- JÚLIA ALBERTIM
- JULIANA MOREIRA
- LUANA SILVA
- PEDRO CAMELLO
- PEDRO SOUZA
- VITOR GOMES

> Professor/orientador - Ronierison Maciel
---
