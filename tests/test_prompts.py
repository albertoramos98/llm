from pathlib import Path
from unittest.mock import patch, MagicMock
import core.prompts as prompts

BASE_DIR = Path(__file__).resolve().parent.parent 

TABLE_ALIASES_PATH = BASE_DIR / "config" / "table_aliases.yaml"

DB_PATH = Path("fecomdb.db")

def test_load_table_aliases(tmp_path):
    content = "tabela_exemplo: Descrição da tabela exemplo"
    file_path = tmp_path / "table_aliases.yaml"
    file_path.write_text(content, encoding="utf-8")

    result = prompts.load_table_aliases(file_path)
    assert result == {"tabela_exemplo": "Descrição da tabela exemplo"}

def test_load_table_aliases_arquivo_inexistente():
    result = prompts.load_table_aliases("arquivo_inexistente.yaml")
    assert result == {}

@patch("core.prompts.describe_table")
@patch("core.prompts.DB_PATH", new=Path("exemplo.db"))
def test_make_system_prompt(mock_describe):
    mock_describe.return_value = [("coluna1", "TEXT"), ("coluna2", "INTEGER")]
    prompt = prompts.make_system_prompt("tabela_teste")

    assert "HuB-IA" in prompt
    assert "coluna1 (TEXT)" in prompt
    assert "coluna2 (INTEGER)" in prompt
    assert "tabela_teste" in prompt
    assert prompt.startswith("Você é a HuB-IA")

@patch("core.prompts.describe_table")
@patch("core.prompts.list_tables")
@patch("core.prompts.load_table_aliases")
def test_make_system_prompt_all(mock_aliases, mock_tables, mock_describe):
    mock_aliases.return_value = {"tabela_um": "Descrição um", "tabela_dois": "Descrição dois"}
    mock_tables.return_value = ["tabela_um", "tabela_dois"]
    mock_describe.side_effect = [
        [("col1", "TEXT"), ("col2", "INTEGER")],
        [("colA", "REAL")]
    ]

    prompt = prompts.make_system_prompt_all()

    assert "tabela_um" in prompt
    assert "tabela_dois" in prompt
    assert "Descrição um" in prompt
    assert "col1 (TEXT)" in prompt
    assert "colA (REAL)" in prompt
    assert prompt.startswith("Você é a HuB-IA")

def test_interpret_system_prompt_constante():
    assert isinstance(prompts.INTERPRET_SYSTEM_PROMPT, str)
    assert "linguagem natural" in prompts.INTERPRET_SYSTEM_PROMPT
