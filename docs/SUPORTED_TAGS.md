# Tags RFID Suportadas

Este documento lista todas as tags RFID suportadas pelo **RFID Tag TID Parser**, incluindo informações técnicas, prefixos TID e características específicas de cada fabricante.

## Índice

- [Resumo Geral](#resumo-geral)
- [Impinj](#impinj)
- [NXP Semiconductors](#nxp-semiconductors)
- [Como Adicionar Suporte a Novas Tags](#como-adicionar-suporte-a-novas-tags)
- [Algoritmos de Extração](#algoritmos-de-extração)
- [Referências Técnicas](#referências-técnicas)

---

## Resumo Geral

### Estatísticas de Suporte

| Fabricante | Séries Suportadas | Total de Modelos | Algoritmo de Serial |
|------------|-------------------|------------------|---------------------|
| **Impinj** | Monza 4, 5, R6, M700, M800 | 11 modelos | Bytes 6-10 |
| **NXP** | UCODE 7, 8, 9 | 5 modelos | Bytes 7-11 (UCODE 9), Fallback (outros) |

### Cobertura Total
- **22+ modelos específicos** identificados
- **3 fabricantes principais** suportados
- **Fallback universal** para tags desconhecidas
- **Compatibilidade com padrão ISO 18000-6C**

---

## Impinj

Impinj é líder mundial em conectividade RFID UHF. O parser suporta múltiplas séries de chips Impinj.

### Características Gerais Impinj
- **Prefixo TID**: `E2 80 1X XX` (onde X varia por modelo)
- **Algoritmo de Serial**: Bytes 6-10 (40 bits)
- **Monza Series ID**: Disponível nos bits 7-6 do byte 10
- **Frequência**: 860-960 MHz (UHF)

### Monza R6 Series

#### Impinj Monza R6
- **Prefixo TID**: `E2 80 11 90`
- **TMN (Tag Model Number)**: `0x190`
- **Características**:
  - Memória EPC: 96 bits
  - Memória de usuário: 32 bits
  - Sensibilidade: -20 dBm
  - Performance balanceada

**Exemplo de TID:**
```
E2 80 11 90 00 00 00 00 00 00 00 0A
├─┤ ├─┤ ├─────┤ ├─────────────────┤
│  │  │       │ Serial (40 bits)
│  │  │       └─ Dados específicos
│  │  └─ TMN (0x190 = Monza R6)
│  └─ Classe/Fabricante
└─ ISO/IEC 18000-6C
```

#### Impinj Monza R6-A
- **Prefixo TID**: `E2 80 11 21`
- **TMN**: `0x121`
- **Características**:
  - Versão aprimorada do R6
  - Melhor performance de link
  - Memória EPC: 96 bits

#### Impinj Monza R6-P
- **Prefixo TID**: `E2 80 11 22`
- **TMN**: `0x122`
- **Características**:
  - Otimizado para aplicações de alta performance
  - Sensibilidade aprimorada
  - Compatibilidade com Gen2v2

### M700 Series (Geração Atual)

#### Impinj M730
- **Prefixo TID**: `E2 80 11 91`
- **TMN**: `0x191`
- **Características**:
  - Memória EPC: 128 bits
  - Memória de usuário: 32 bits
  - Excelente sensibilidade: -23 dBm
  - Baixo consumo de energia

#### Impinj M750
- **Prefixo TID**: `E2 80 11 90`
- **TMN**: `0x190`
- **Características**:
  - Memória EPC: 128 bits  
  - Memória de usuário: 64 bits
  - Alta performance em ambientes densos
  - Suporte completo a Gen2v2

#### Impinj M770
- **Prefixo TID**: `E2 80 11 A0`
- **TMN**: `0x1A0`
- **Características**:
  - Memória EPC: 128 bits
  - Memória de usuário: 128 bits
  - Máxima capacidade de memória da série
  - Ideal para aplicações complexas

### M800 Series (Próxima Geração)

#### Impinj M830
- **Prefixo TID**: `E2 80 11 B0`
- **TMN**: `0x1B0`
- **Características**:
  - Tecnologia de nova geração
  - Performance superior em ambientes desafiadores
  - Memória EPC: 128 bits
  - Eficiência energética aprimorada

#### Impinj M850  
- **Prefixo TID**: `E2 80 11 B0`
- **TMN**: `0x1B0` (mesmo TMN do M830)
- **Características**:
  - Versão premium da série M800
  - Máxima performance e alcance
  - Recursos avançados de segurança

### Monza 4 Series (Legado)

#### Impinj Monza 4D
- **Prefixo TID**: `E2 80 10 B2`
- **TMN**: `0x0B2`
- **Características**:
  - Memória EPC: 128 bits
  - Memória de usuário: 128 bits
  - Operação básica

#### Impinj Monza 4E
- **Prefixo TID**: `E2 80 10 B3`
- **TMN**: `0x0B3`
- **Características**:
  - Memória EPC: 496 bits
  - Memória de usuário: 128 bits
  - Maior capacidade EPC

#### Impinj Monza 4U
- **Prefixo TID**: `E2 80 10 B4`
- **TMN**: `0x0B4`
- **Características**:
  - Memória EPC: 128 bits
  - Memória de usuário: 512 bits
  - Focado em dados de usuário

#### Impinj Monza 4QT
- **Prefixo TID**: `E2 80 10 B5`
- **TMN**: `0x0B5`
- **Características**:
  - Recursos de privacidade QT
  - Controle de visibilidade da tag
  - Segurança aprimorada

### Monza 5 Series

#### Impinj Monza 5
- **Prefixo TID**: `E2 80 10 C0`
- **TMN**: `0x0C0`
- **Características**:
  - Evolução da série Monza 4
  - Performance aprimorada
  - Compatibilidade com Gen2v2

---

## NXP Semiconductors

NXP é um fabricante em semicondutores com presença no mercado RFID.

### Características Gerais NXP
- **Prefixo TID**: Varia por série
- **Algoritmo de Serial**: Específico por modelo
- **Frequência**: 860-960 MHz (UHF)
- **Padrão**: ISO 18000-6C

### UCODE 9 Series

#### NXP UCODE 9
- **Prefixo TID**: 
  - `E2 80 69 15` (Variante 1)
  - `E2 80 69 95` (Variante 2)
- **TMN**: 
  - `0x915` (Variante 1)
  - `0x995` (Variante 2)
- **Algoritmo de Serial**: Bytes 7-11 (específico para UCODE 9)
- **Características**:
  - Memória EPC: 128 bits
  - Memória de usuário: 224 bits
  - Excelente sensibilidade: -25 dBm
  - Tecnologia de nova geração

**Exemplo de TID UCODE 9:**
```
E2 80 69 15 00 00 00 12 34 56 78 9A
├─┤ ├─┤ ├─┤ ├─┤ ├─┤ ├─────────────┤
│  │  │  │  │  │  Serial (40 bits) - bytes 7-11
│  │  │  │  │  └─ Dados específicos
│  │  │  │  └─ Variante (15 ou 95)
│  │  │  └─ UCODE 9 identifier (69)
│  │  └─ Classe NXP (80)
│  └─ ISO/IEC 18000-6C
└─ Class identifier
```

### UCODE 8 Series

#### NXP UCODE 8
- **Prefixo TID**: 
  - `E2 80 69 10` (estimado)
  - `E2 80 69 90` (estimado)
- **TMN**: 
  - `0x910`
  - `0x990`
- **Algoritmo de Serial**: Fallback (últimos 5 bytes)
- **Características**:
  - Memória EPC: 128 bits
  - Memória de usuário: 128 bits
  - Performance balanceada

### UCODE 7 Series

#### NXP UCODE 7
- **Prefixo TID**: `E2 80 69 70` (estimado)
- **TMN**: `0x970`
- **Algoritmo de Serial**: Fallback (últimos 5 bytes)
- **Características**:
  - Memória EPC: 96-128 bits
  - Tecnologia estabelecida
  - Ampla compatibilidade

---

## Como Adicionar Suporte a Novas Tags

### Passo 1: Identificar o Prefixo TID

```python
# Adicionar ao dicionário KNOWN_TID_PREFIXES
KNOWN_TID_PREFIXES = {
    # ... prefixos existentes ...
    "E280XXXX": "Novo Fabricante Modelo Y",
}
```

### Passo 2: Mapear o Modelo

```python
# Adicionar ao dicionário TAG_MODEL_MAP
TAG_MODEL_MAP = {
    # ... modelos existentes ...
    0xXXX: "Nome do Novo Modelo",
}
```

### Passo 3: Implementar Algoritmo de Serial (se necessário)

```python
def _is_novo_fabricante_tid(self) -> bool:
    """Detecta tags do novo fabricante."""
    return (self._tid[0] == 0xXX and 
            self._tid[1] == 0xYY and 
            # critérios específicos
           )

# Atualizar get_40bit_serial_hex()
if self._is_novo_fabricante_tid():
    # algoritmo específico
    pass
```

### Passo 4: Adicionar Testes

```python
# Em test_data.py
"novo_modelo_1": {
    "tid": "XXXXXXXXXXXXXXXXXXXXXXXX",
    "description": "Novo Modelo - Teste 1"
}
```

---

## Algoritmos de Extração

### Impinj (Bytes 6-10)

```
TID: E2 80 1X XX YY YY [SS SS SS SS SS] ZZ
                      └─────────────────┘
                        Serial 40 bits
Posições: 0  1  2  3  4  5  6  7  8  9  10 11
```

### NXP UCODE 9 (Bytes 7-11)

```
TID: E2 80 69 15 YY YY YY [SS SS SS SS SS]
                         └─────────────────┘
                           Serial 40 bits
Posições: 0  1  2  3  4  5  6  7  8  9  10 11
```

### Fallback (Últimos 5 bytes)

```
TID: XX XX XX XX XX XX XX [SS SS SS SS SS]
                         └─────────────────┘
                           Serial 40 bits
Posições: 0  1  2  3  4  5  6  7  8  9  10 11
```

---

## Referências Técnicas

### Documentação Oficial

#### Impinj
- [Impinj Tag Chip Datasheets](https://www.impinj.com/products/tag-chips)
- [Monza R6 Family Datasheet](https://www.impinj.com/products/tag-chips/monza-r6-family)
- [M700 Series Documentation](https://www.impinj.com/products/tag-chips/m700-series)

#### NXP
- [UCODE 9 Product Brief](https://www.nxp.com/products/rfid-nfc/uhf-rfid/ucode-9)
- [NXP RFID Tag Chips Overview](https://www.nxp.com/products/rfid-nfc/uhf-rfid)

### Padrões e Especificações

#### ISO/IEC 18000-6C
- **Título**: "Information technology — Radio frequency identification for item management — Part 6: Parameters for air interface communications at 860 MHz to 960 MHz Type C"
- **Escopo**: Define o protocolo de comunicação para tags RFID UHF
- **TID Structure**: Especifica a estrutura dos 96 bits do TID

#### EPCglobal Gen2v2
- **Título**: "EPC™ Radio-Frequency Identity Protocols Generation-2 UHF RFID"
- **Versão**: 2.1.0
- **Features**: Recursos avançados como criptografia e autenticação

### Estrutura do TID (96 bits)

```
Bits:    8      8      8      8      8      8      8      8      8      8      8      8
       ┌──────┬──────┬──────┬──────┬──────┬──────┬──────┬──────┬──────┬──────┬──────┬──────┐
Bytes: │  0   │  1   │  2   │  3   │  4   │  5   │  6   │  7   │  8   │  9   │ 10   │ 11   │
       └──────┴──────┴──────┴──────┴──────┴──────┴──────┴──────┴──────┴──────┴──────┴──────┘
         │      │      │      │      │             │                                   │
         │      │      │      │      │             └─── Serial Number Area ──────────┘
         │      │      │      │      └─ Vendor/Model Specific Data
         │      │      └──────┴─ Tag Model Number (TMN) - 12 bits
         │      └─ Allocation Class (0x80 para Gen2)
         └─ ISO/IEC 15963 Class (0xE2 para 18000-6C)
```

### Exemplos Práticos de Decodificação

#### Exemplo 1: Impinj Monza R6
```
TID: E2 80 11 90 00 00 00 00 00 00 00 0A

Decodificação:
- E2: ISO/IEC Class (18000-6C)
- 80: Allocation Class (Gen2)
- 11 90: TMN = 0x190 = Impinj M750
- 00 00 00: Dados específicos do vendor
- 00 00 00 00 0A: Serial = 0x000000000A = 10

Algoritmo Impinj (bytes 6-10):
Serial bytes: [00, 00, 00, 00, 0A]
Serial hex: "000000000A"
Serial decimal: 10
```

#### Exemplo 2: NXP UCODE 9
```
TID: E2 80 69 15 12 34 56 78 9A BC DE F0

Decodificação:
- E2: ISO/IEC Class
- 80: Allocation Class  
- 69 15: TMN = 0x915 = NXP UCODE 9
- 12 34 56: Dados específicos
- 78 9A BC DE F0: Área do serial

Algoritmo UCODE 9 (bytes 7-11):
Serial bytes: [78, 9A, BC, DE, F0]
Serial hex: "789ABCDEF0"
Serial decimal: 516003413744
```

### Ferramentas de Desenvolvimento

#### Validação Online
- [TID Decoder Tool](exemplo.com/tid-decoder) - Ferramenta web para validação
- [RFID Tag Simulator](exemplo.com/simulator) - Simulador para testes

#### Bibliotecas Relacionadas
- **Python**: `rfid-tag-tid-parser` (esta biblioteca)
- **JavaScript**: Possível port futuro
- **C#**: Implementação original (base desta biblioteca)

---

## Histórico de Atualizações

### Versão 1.0.0 (2025-07-04)
- ✅ Suporte inicial para Impinj (Monza R6, M700, M800, Monza 4/5)
- ✅ Suporte para NXP UCODE 9
- ✅ Algoritmos de extração específicos por fabricante
- ✅ Fallback universal para tags desconhecidas

### Roadmap Futuro
- 🔄 Expansão do suporte NXP (UCODE 7, 8 completo)
- 🔄 Suporte para Alien Technology
- 🔄 Suporte para Smartrac/Avery Dennison
- 🔄 Detecção automática de novos modelos
- 🔄 API para registro dinâmico de novos fabricantes

---

*Última atualização: 04 de Julho de 2025*  
*Para reportar tags não suportadas ou solicitar novos fabricantes, abra uma [issue no GitHub](https://github.com/suporterfid/rfid-tag-tid-parser/issues).*