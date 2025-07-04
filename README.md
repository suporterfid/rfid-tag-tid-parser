# RFID Tag TID Parser

[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Parser Python para análise de TID (Tag Identifier) de tags RFID. Extrai informações como fabricante, modelo, número serial e outras características técnicas das tags.

## 🚀 Características

- **Suporte a múltiplos fabricantes**: Impinj, NXP
- **Extração de serial**: 40 bits em formato hexadecimal e decimal
- **Identificação automática**: Modelo, fabricante e características da tag
- **Fácil integração**: API simples e intuitiva
- **Sem dependências externas**: Apenas Python padrão

## 📦 Instalação

### Instalação direta do GitHub
```bash
pip install git+https://github.com/suporterfid/rfid-tag-tid-parser.git
```

### Instalação local
```bash
git clone https://github.com/suporterfid/rfid-tag-tid-parser.git
cd rfid-tag-tid-parser
pip install -e .
```

## 🎯 Uso Rápido

```python
from rfid_tag_parser import TagTidParser, parse_tid

# Exemplo básico
tid = "E2801190000000000000000A"
parser = TagTidParser(tid)

print(f"Fabricante: {parser.get_vendor_from_tid()}")
print(f"Modelo: {parser.get_tag_model_name()}")
print(f"Serial: {parser.get_40bit_serial_hex()}")

# Ou obter todas as informações
info = parse_tid(tid)
print(info)
```

## 📋 Saída de Exemplo

```python
{
    'tid': 'E2801190000000000000000A',
    'vendor': 'Impinj Monza R6',
    'model_name': 'Impinj M750',
    'model_number': '190',
    'serial_hex': '000000000A',
    'serial_decimal': 10,
    'monza_series_id': 0,
    'is_impinj': True,
    'is_nxp_ucode9': False
}
```

## 🏷️ Tags Suportadas

### Impinj
- Monza R6 Series (R6, R6-A, R6-P)
- M700 Series (M730, M750, M770)
- M800 Series (M830, M850)
- Monza 4 Series (4D, 4E, 4U, 4QT)
- Monza 5

### NXP
- UCODE 7
- UCODE 8
- UCODE 9


## 📚 Documentação

- [API Reference](docs/API.md)
- [Supported Tags](docs/SUPPORTED_TAGS.md)
- [Examples](examples/)

## 🧪 Testes

```bash
# Executar testes
python -m pytest tests/

# Com cobertura
python -m pytest tests/ --cov=rfid_tag_parser
```

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🐛 Bugs e Sugestões

Encontrou um bug ou tem uma sugestão? Abra uma [issue](https://github.com/suporterfid/rfid-tag-tid-parser/issues).


