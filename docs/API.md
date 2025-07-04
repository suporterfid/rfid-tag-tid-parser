# API Reference - RFID Tag TID Parser

Este documento descreve a API completa do módulo `rfid_tag_parser`.

## Índice

- [Classe TagTidParser](#classe-tagdidparser)
- [Funções de Conveniência](#funções-de-conveniência)
- [Exceções](#exceções)
- [Tipos de Dados](#tipos-de-dados)
- [Exemplos de Uso](#exemplos-de-uso)

---

## Classe TagTidParser

A classe principal para parsing e análise de TID de tags RFID.

### Construtor

#### `TagTidParser(tid_hex: str)`

Inicializa o parser com um TID em formato hexadecimal.

**Parâmetros:**
- `tid_hex` (str): TID em formato hexadecimal. Deve ter exatamente 24 caracteres (96 bits). Espaços e hífens são automaticamente removidos.

**Raises:**
- `ValueError`: Se o TID for inválido (vazio, tamanho incorreto ou caracteres inválidos)

**Exemplo:**
```python
parser = TagTidParser("E2801190000000000000000A")
# Ou com formatação
parser = TagTidParser("E2-80-11-90-00-00-00-00-00-00-00-0A")
# Ou com espaços
parser = TagTidParser("E2 80 11 90 00 00 00 00 00 00 00 0A")
```

---

### Métodos Públicos

#### `get_40bit_serial_hex() -> str`

Extrai o número serial de 40 bits em formato hexadecimal.

**Returns:**
- `str`: Serial de 40 bits em hexadecimal maiúsculo (10 caracteres)

**Algoritmo:**
- **Tags NXP UCODE 9**: Extrai dos bytes 7-11
- **Tags Impinj**: Extrai dos bytes 6-10  
- **Outras tags**: Extrai dos últimos 5 bytes (fallback)

**Exemplo:**
```python
parser = TagTidParser("E2801190000000000000000A")
serial = parser.get_40bit_serial_hex()
# Retorna: "000000000A"
```

#### `get_40bit_serial_decimal() -> int`

Extrai o número serial de 40 bits em formato decimal.

**Returns:**
- `int`: Serial de 40 bits em decimal

**Exemplo:**
```python
parser = TagTidParser("E2801190000000000000000A")
serial = parser.get_40bit_serial_decimal()
# Retorna: 10
```

#### `get_tag_model_number() -> str`

Extrai o número do modelo da tag (TMN - Tag Model Number).

**Returns:**
- `str`: Número do modelo em hexadecimal maiúsculo (3 caracteres)

**Exemplo:**
```python
parser = TagTidParser("E2801190000000000000000A")
model_number = parser.get_tag_model_number()
# Retorna: "190"
```

#### `get_tag_model_name() -> str`

Obtém o nome descritivo do modelo da tag.

**Returns:**
- `str`: Nome do modelo ou "Desconhecido (TMN 0xXXX)" se não encontrado

**Exemplo:**
```python
parser = TagTidParser("E2801190000000000000000A")
model_name = parser.get_tag_model_name()
# Retorna: "Impinj M750"
```

#### `get_vendor_from_tid() -> str`

Identifica o fabricante baseado no prefixo do TID.

**Returns:**
- `str`: Nome do fabricante ou "Desconhecido"

**Fabricantes Suportados:**
- Impinj (Monza R6, M730, M770, M830/M850)
- NXP (UCODE 7, 8, 9)

**Exemplo:**
```python
parser = TagTidParser("E2801190000000000000000A")
vendor = parser.get_vendor_from_tid()
# Retorna: "Impinj Monza R6"
```

#### `get_monza_series_id() -> int`

Extrai o ID da série Monza (específico para tags Impinj).

**Returns:**
- `int`: ID da série Monza (0-3)

**Série IDs:**
- `0`: Série básica
- `1-3`: Séries específicas

**Exemplo:**
```python
parser = TagTidParser("E2801190000000000000000A")
if parser._is_impinj_tid():
    series_id = parser.get_monza_series_id()
    # Retorna: 0, 1, 2 ou 3
```

#### `get_tid_info() -> dict`

Retorna todas as informações extraídas do TID em um dicionário estruturado.

**Returns:**
- `dict`: Dicionário com todas as informações da tag

**Estrutura do dicionário retornado:**
```python
{
    "tid": str,                    # TID original em hexadecimal maiúsculo
    "vendor": str,                 # Nome do fabricante
    "model_name": str,             # Nome do modelo
    "model_number": str,           # Número do modelo (hex)
    "serial_hex": str,             # Serial em hexadecimal
    "serial_decimal": int,         # Serial em decimal
    "monza_series_id": int | None, # ID da série (apenas Impinj)
    "is_impinj": bool,             # True se for tag Impinj
    "is_nxp_ucode9": bool         # True se for NXP UCODE 9
}
```

**Exemplo:**
```python
parser = TagTidParser("E2801190000000000000000A")
info = parser.get_tid_info()
print(info)
# Retorna:
# {
#     'tid': 'E2801190000000000000000A',
#     'vendor': 'Impinj Monza R6',
#     'model_name': 'Impinj M750',
#     'model_number': '190',
#     'serial_hex': '000000000A',
#     'serial_decimal': 10,
#     'monza_series_id': 0,
#     'is_impinj': True,
#     'is_nxp_ucode9': False
# }
```

---

### Métodos Privados

#### `_is_impinj_tid() -> bool`

Verifica se o TID pertence a uma tag Impinj.

**Critério:** `E2 80 1X XX ...` (onde X pode ser qualquer dígito)

#### `_is_nxp_ucode9_tid() -> bool`

Verifica se o TID pertence a uma tag NXP UCODE 9.

**Critério:** `E2 80 69 [15|95] ...`

#### `_get_fallback_serial_hex() -> str`

Método fallback para extrair serial dos últimos 5 bytes quando o fabricante não é reconhecido.

---

## Funções de Conveniência

### `parse_tid(tid_hex: str) -> dict`

Função de conveniência para parsing rápido de TID.

**Parâmetros:**
- `tid_hex` (str): TID em formato hexadecimal

**Returns:**
- `dict`: Dicionário com todas as informações da tag (mesmo formato que `get_tid_info()`)

**Exemplo:**
```python
from rfid_tag_parser import parse_tid

info = parse_tid("E2801190000000000000000A")
print(f"Modelo: {info['model_name']}")
print(f"Serial: {info['serial_hex']}")
```

### `get_serial_from_tid(tid_hex: str, format_type: str = "hex") -> str | int`

Extrai apenas o número serial do TID.

**Parâmetros:**
- `tid_hex` (str): TID em formato hexadecimal
- `format_type` (str): Formato do retorno ("hex" ou "decimal")

**Returns:**
- `str`: Serial em hexadecimal se `format_type="hex"`
- `int`: Serial em decimal se `format_type="decimal"`

**Exemplo:**
```python
from rfid_tag_parser import get_serial_from_tid

# Serial em hexadecimal
serial_hex = get_serial_from_tid("E2801190000000000000000A", "hex")
# Retorna: "000000000A"

# Serial em decimal
serial_dec = get_serial_from_tid("E2801190000000000000000A", "decimal")
# Retorna: 10
```

---

## Exceções

### `TagTidParserError`

Exceção base para todos os erros do TagTidParser.

### `InvalidTidError`

Exceção específica para TIDs inválidos (herda de `TagTidParserError`).

**Casos que geram esta exceção:**
- TID vazio ou None
- TID com tamanho diferente de 24 caracteres
- TID com caracteres não-hexadecimais

**Exemplo de tratamento:**
```python
from rfid_tag_parser import TagTidParser, InvalidTidError

try:
    parser = TagTidParser("TID_INVÁLIDO")
except InvalidTidError as e:
    print(f"TID inválido: {e}")
except ValueError as e:
    print(f"Erro de valor: {e}")
```

---

## Tipos de Dados

### Constantes da Classe

#### `KNOWN_TID_PREFIXES: Dict[str, str]`

Dicionário que mapeia prefixos de TID (4 bytes) para nomes de fabricantes.

```python
{
    "E2801190": "Impinj Monza R6",
    "E2801191": "Impinj M730", 
    "E28011A0": "Impinj M770",
    "E28011B0": "Impinj M830/M850",
    "E2806915": "NXP UCODE 9",
    "E2806995": "NXP UCODE 9",
    # ... mais prefixos
}
```

#### `TAG_MODEL_MAP: Dict[int, str]`

Dicionário que mapeia números de modelo (TMN) para nomes descritivos.

```python
{
    0x190: "Impinj M750",
    0x191: "Impinj M730",
    0x1A0: "Impinj M770",
    0x1B0: "Impinj M830/M850",
    0x120: "Impinj Monza R6",
    0x915: "NXP UCODE 9",
    # ... mais modelos
}
```

---

## Exemplos de Uso

### Uso Básico

```python
from rfid_tag_parser import TagTidParser

# Criar parser
parser = TagTidParser("E2801190000000000000000A")

# Extrair informações individuais
print(f"Fabricante: {parser.get_vendor_from_tid()}")
print(f"Modelo: {parser.get_tag_model_name()}")
print(f"Serial (Hex): {parser.get_40bit_serial_hex()}")
print(f"Serial (Dec): {parser.get_40bit_serial_decimal()}")

# Verificar tipo de tag
if parser._is_impinj_tid():
    print(f"Série Monza: {parser.get_monza_series_id()}")
```

### Processamento em Lote

```python
from rfid_tag_parser import parse_tid

tids = [
    "E2801190000000000000000A",
    "E2801191000000000000000B", 
    "E2806915000000000000000C"
]

for tid in tids:
    try:
        info = parse_tid(tid)
        print(f"TID: {tid}")
        print(f"  Modelo: {info['model_name']}")
        print(f"  Serial: {info['serial_hex']}")
        print(f"  Fabricante: {info['vendor']}")
        print()
    except ValueError as e:
        print(f"Erro no TID {tid}: {e}")
```

### Extração Rápida de Serial

```python
from rfid_tag_parser import get_serial_from_tid

tid = "E2801190000000000000000A"

# Apenas o serial
serial_hex = get_serial_from_tid(tid, "hex")
serial_dec = get_serial_from_tid(tid, "decimal")

print(f"Serial Hex: {serial_hex}")
print(f"Serial Decimal: {serial_dec}")
```

### Tratamento de Erros

```python
from rfid_tag_parser import TagTidParser

def processar_tid_seguro(tid):
    try:
        parser = TagTidParser(tid)
        return parser.get_tid_info()
    except ValueError as e:
        return {"erro": str(e), "tid": tid}

# Teste com TID válido e inválido
result1 = processar_tid_seguro("E2801190000000000000000A")
result2 = processar_tid_seguro("INVALID")

print("Válido:", result1)
print("Inválido:", result2)
```

### Análise de Fabricantes

```python
from rfid_tag_parser import parse_tid

def analisar_fabricantes(lista_tids):
    fabricantes = {}
    
    for tid in lista_tids:
        try:
            info = parse_tid(tid)
            vendor = info['vendor']
            fabricantes[vendor] = fabricantes.get(vendor, 0) + 1
        except ValueError:
            fabricantes['Erro'] = fabricantes.get('Erro', 0) + 1
    
    return fabricantes

# Exemplo
tids = ["E2801190000000000000000A", "E2806915000000000000000B"]
stats = analisar_fabricantes(tids)
print("Estatísticas:", stats)
```

---

## Notas Técnicas

### Algoritmo de Extração de Serial

O parser utiliza diferentes algoritmos para extrair o serial baseado no fabricante:

1. **NXP UCODE 9**: Bytes 7-11 (posições específicas no TID)
2. **Impinj**: Bytes 6-10 (padrão Impinj)
3. **Fallback**: Últimos 5 bytes (para fabricantes não reconhecidos)

### Formato do TID

Um TID válido deve ter:
- **24 caracteres hexadecimais** (96 bits)
- **Formato**: `XXXXXXXXXXXXXXXXXXXXXXXX`
- **Espaços e hífens** são automaticamente removidos
- **Case insensitive** (maiúsculas/minúsculas aceitas)

### Compatibilidade

- **Python**: 3.6+
- **Dependências**: Nenhuma (apenas biblioteca padrão)
- **Codificação**: UTF-8
- **Thread-safe**: Sim (imutável após inicialização)