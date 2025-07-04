"""
Módulo de testes para o RFID Tag TID Parser.

Este módulo contém todos os testes unitários e dados de teste
para validar o funcionamento correto do parser de TID.

Estrutura dos testes:
- test_tag_tid_parser.py: Testes principais da classe TagTidParser
- test_data.py: Dados de teste centralizados e casos de teste

Para executar os testes:
    python -m pytest tests/
    python -m pytest tests/ -v  # modo verboso
    python -m pytest tests/ --cov=rfid_tag_parser  # com cobertura

Para executar testes específicos:
    python -m pytest tests/test_tag_tid_parser.py
    python -m pytest tests/test_tag_tid_parser.py::TestTagTidParser::test_valid_tid_initialization
"""

# Importações para facilitar o uso nos testes
from .test_data import (
    TID_SAMPLES,
    INVALID_TIDS,
    EXPECTED_RESULTS,
    FABRICANTES_CONHECIDOS,
    MODELOS_CONHECIDOS
)

__all__ = [
    "TID_SAMPLES",
    "INVALID_TIDS", 
    "EXPECTED_RESULTS",
    "FABRICANTES_CONHECIDOS",
    "MODELOS_CONHECIDOS"
]