"""
Dados de teste centralizados para o RFID Tag TID Parser.

Este módulo contém todos os dados de teste, casos de teste e resultados esperados
para validar o funcionamento do parser de TID de tags RFID.
"""

# ============================================================================
# SAMPLES DE TID VÁLIDOS
# ============================================================================

TID_SAMPLES = {
    # Tags Impinj Monza R6 Series
    "impinj_monza_r6_1": {
        "tid": "E2801190000000000000000A",
        "description": "Impinj Monza R6 - Exemplo 1"
    },
    "impinj_monza_r6_2": {
        "tid": "E280119000000000000000FF",
        "description": "Impinj Monza R6 - Exemplo 2"
    },
    "impinj_monza_r6_3": {
        "tid": "E2801190123456789ABCDEF0",
        "description": "Impinj Monza R6 - Serial complexo"
    },
    
    # Tags Impinj M730
    "impinj_m730_1": {
        "tid": "E2801191000000000000000B",
        "description": "Impinj M730 - Exemplo 1"
    },
    "impinj_m730_2": {
        "tid": "E2801191ABCDEF0123456789",
        "description": "Impinj M730 - Serial complexo"
    },
    
    # Tags Impinj M770
    "impinj_m770_1": {
        "tid": "E28011A0000000000000000C",
        "description": "Impinj M770 - Exemplo 1"
    },
    "impinj_m770_2": {
        "tid": "E28011A0FEDCBA9876543210",
        "description": "Impinj M770 - Serial alto"
    },
    
    # Tags Impinj M830/M850
    "impinj_m830_1": {
        "tid": "E28011B0000000000000000D",
        "description": "Impinj M830/M850 - Exemplo 1"
    },
    "impinj_m830_2": {
        "tid": "E28011B01111111111111111",
        "description": "Impinj M830/M850 - Padrão 1s"
    },
    
    # Tags NXP UCODE 9
    "nxp_ucode9_variant1": {
        "tid": "E2806915000000000000000E",
        "description": "NXP UCODE 9 - Variante 0x15"
    },
    "nxp_ucode9_variant2": {
        "tid": "E2806995000000000000000F",
        "description": "NXP UCODE 9 - Variante 0x95"
    },
    "nxp_ucode9_complex": {
        "tid": "E28069159876543210FEDCBA",
        "description": "NXP UCODE 9 - Serial complexo"
    },
    
    # Tags desconhecidas (para teste de fallback)
    "unknown_vendor_1": {
        "tid": "FF00AA00000000000000002A",
        "description": "Fabricante desconhecido - Teste 1"
    },
    "unknown_vendor_2": {
        "tid": "AA55FF00123456789ABCDEF0",
        "description": "Fabricante desconhecido - Teste 2"
    },
    
    # Casos especiais para teste de edge cases
    "all_zeros": {
        "tid": "000000000000000000000000",
        "description": "TID com todos os bytes zero"
    },
    "all_ffs": {
        "tid": "FFFFFFFFFFFFFFFFFFFFFFFF",
        "description": "TID com todos os bytes FF"
    },
    "alternating_pattern": {
        "tid": "AAAAAAAAAAAAAAAAAAAAAAA5",
        "description": "TID com padrão alternado"
    }
}

# ============================================================================
# TIDs INVÁLIDOS PARA TESTE DE VALIDAÇÃO
# ============================================================================

INVALID_TIDS = [
    # TIDs vazios ou None
    {
        "tid": "",
        "description": "TID vazio",
        "expected_error": "TID não pode ser vazio ou nulo"
    },
    {
        "tid": None,
        "description": "TID None",
        "expected_error": "TID não pode ser vazio ou nulo"
    },
    {
        "tid": "   ",
        "description": "TID apenas espaços",
        "expected_error": "TID não pode ser vazio ou nulo"
    },
    
    # TIDs com tamanho incorreto
    {
        "tid": "E280119",
        "description": "TID muito curto (7 chars)",
        "expected_error": "TID deve ter 24 caracteres hexadecimais"
    },
    {
        "tid": "E2801190000000000000000",
        "description": "TID com 23 caracteres",
        "expected_error": "TID deve ter 24 caracteres hexadecimais"
    },
    {
        "tid": "E2801190000000000000000ABC",
        "description": "TID com 27 caracteres",
        "expected_error": "TID deve ter 24 caracteres hexadecimais"
    },
    {
        "tid": "E280119000000000000000000000000000000",
        "description": "TID muito longo (36 chars)",
        "expected_error": "TID deve ter 24 caracteres hexadecimais"
    },
    
    # TIDs com caracteres inválidos
    {
        "tid": "G2801190000000000000000A",
        "description": "TID com caractere inválido 'G'",
        "expected_error": "TID contém caracteres hexadecimais inválidos"
    },
    {
        "tid": "E2801190000000000000000Z",
        "description": "TID com caractere inválido 'Z'",
        "expected_error": "TID contém caracteres hexadecimais inválidos"
    },
    {
        "tid": "E2801190-00000000000000A",
        "description": "TID com hífen no meio (após limpeza fica 23 chars)",
        "expected_error": "TID deve ter 24 caracteres hexadecimais"
    },
    {
        "tid": "E280119@000000000000000A",
        "description": "TID com caractere especial '@'",
        "expected_error": "TID contém caracteres hexadecimais inválidos"
    },
    {
        "tid": "E2801190 00000000000000A",
        "description": "TID com espaço no meio (após limpeza fica 23 chars)",
        "expected_error": "TID deve ter 24 caracteres hexadecimais"
    }
]

# ============================================================================
# RESULTADOS ESPERADOS PARA TIDs VÁLIDOS
# ============================================================================

EXPECTED_RESULTS = {
    "impinj_monza_r6_1": {
        "tid": "E2801190000000000000000A",
        "vendor": "Impinj Monza R6",
        "model_name": "Impinj M750",
        "model_number": "190",
        "serial_hex": "000000000A",  # Impinj: bytes 6-10
        "serial_decimal": 10,
        "monza_series_id": 0,  # Será calculado do byte 10
        "is_impinj": True,
        "is_nxp_ucode9": False
    },
    
    "impinj_m730_1": {
        "tid": "E2801191000000000000000B",
        "vendor": "Impinj M730",
        "model_name": "Impinj M730",
        "model_number": "191",
        "serial_hex": "000000000B",
        "serial_decimal": 11,
        "monza_series_id": 0,
        "is_impinj": True,
        "is_nxp_ucode9": False
    },
    
    "impinj_m770_1": {
        "tid": "E28011A0000000000000000C",
        "vendor": "Impinj M770",
        "model_name": "Impinj M770",
        "model_number": "1A0",
        "serial_hex": "000000000C",
        "serial_decimal": 12,
        "monza_series_id": 0,
        "is_impinj": True,
        "is_nxp_ucode9": False
    },
    
    "impinj_m830_1": {
        "tid": "E28011B0000000000000000D",
        "vendor": "Impinj M830/M850",
        "model_name": "Impinj M830/M850",
        "model_number": "1B0",
        "serial_hex": "000000000D",
        "serial_decimal": 13,
        "monza_series_id": 0,
        "is_impinj": True,
        "is_nxp_ucode9": False
    },
    
    "nxp_ucode9_variant1": {
        "tid": "E2806915000000000000000E",
        "vendor": "NXP UCODE 9",
        "model_name": "NXP UCODE 9",
        "model_number": "915",
        "serial_hex": "000000000E",  # NXP UCODE9: bytes 7-11
        "serial_decimal": 14,
        "monza_series_id": None,  # Não é Impinj
        "is_impinj": False,
        "is_nxp_ucode9": True
    },
    
    "nxp_ucode9_variant2": {
        "tid": "E2806995000000000000000F",
        "vendor": "NXP UCODE 9",
        "model_name": "NXP UCODE 9",
        "model_number": "995",
        "serial_hex": "000000000F",
        "serial_decimal": 15,
        "monza_series_id": None,
        "is_impinj": False,
        "is_nxp_ucode9": True
    },
    
    "unknown_vendor_1": {
        "tid": "FF00AA00000000000000002A",
        "vendor": "Desconhecido",
        "model_name": "Desconhecido (TMN 0xA00)",
        "model_number": "A00",
        "serial_hex": "000000002A",  # Fallback: últimos 5 bytes
        "serial_decimal": 42,
        "monza_series_id": None,
        "is_impinj": False,
        "is_nxp_ucode9": False
    }
}

# ============================================================================
# FABRICANTES CONHECIDOS
# ============================================================================

FABRICANTES_CONHECIDOS = {
    "Impinj Monza R6": ["E2801190"],
    "Impinj M730": ["E2801191"],
    "Impinj M770": ["E28011A0"],
    "Impinj M830/M850": ["E28011B0"],
    "NXP UCODE 9": ["E2806915", "E2806995"]
}

# ============================================================================
# MODELOS CONHECIDOS (TMN -> Nome)
# ============================================================================

MODELOS_CONHECIDOS = {
    # Impinj M700 Series
    0x190: "Impinj M750",
    0x191: "Impinj M730",
    0x1A0: "Impinj M770",
    
    # Impinj M800 Series
    0x1B0: "Impinj M830/M850",
    
    # Impinj Monza R6 Family
    0x120: "Impinj Monza R6",
    0x121: "Impinj Monza R6-A",
    0x122: "Impinj Monza R6-P",
    
    # Impinj Monza 4 Series
    0x0B2: "Impinj Monza 4D",
    0x0B3: "Impinj Monza 4E",
    0x0B4: "Impinj Monza 4U",
    0x0B5: "Impinj Monza 4QT",
    
    # Impinj Monza 5 Series
    0x0C0: "Impinj Monza 5",
    
    # NXP UCODE 9
    0x915: "NXP UCODE 9",
    0x995: "NXP UCODE 9",
    
    # NXP UCODE 8
    0x910: "NXP UCODE 8",
    0x990: "NXP UCODE 8",
    
    # NXP UCODE 7
    0x970: "NXP UCODE 7"
}

# ============================================================================
# CASOS DE TESTE PARA FORMATAÇÃO DE TID
# ============================================================================

TID_FORMATTING_CASES = [
    # Diferentes formatos de entrada que devem ser normalizados
    {
        "input": "E2801190000000000000000A",
        "expected_normalized": "E2801190000000000000000A",
        "description": "TID já normalizado"
    },
    {
        "input": "e2801190000000000000000a",
        "expected_normalized": "E2801190000000000000000A",
        "description": "TID em minúsculas"
    },
    {
        "input": "E2-80-11-90-00-00-00-00-00-00-00-0A",
        "expected_normalized": "E2801190000000000000000A",
        "description": "TID com hífens"
    },
    {
        "input": "E2 80 11 90 00 00 00 00 00 00 00 0A",
        "expected_normalized": "E2801190000000000000000A",
        "description": "TID com espaços"
    },
    {
        "input": "  E2801190000000000000000A  ",
        "expected_normalized": "E2801190000000000000000A",
        "description": "TID com espaços nas bordas"
    },
    {
        "input": "E2-80 11-90 00 00-00 00 00-00 00-0A",
        "expected_normalized": "E2801190000000000000000A",
        "description": "TID com formatação mista"
    }
]

# ============================================================================
# CASOS DE TESTE PARA ALGORITMOS DE EXTRAÇÃO DE SERIAL
# ============================================================================

SERIAL_EXTRACTION_CASES = [
    # Casos específicos para testar os diferentes algoritmos
    {
        "tid": "E2801190123456789ABCDEF0",  # Impinj
        "algorithm": "impinj",
        "expected_serial_bytes": [0x56, 0x78, 0x9A, 0xBC, 0xDE],  # bytes 6-10
        "expected_serial_hex": "56789ABCDE",
        "expected_serial_decimal": 372470367198
    },
    {
        "tid": "E28069150123456789ABCDEF",  # NXP UCODE 9
        "algorithm": "nxp_ucode9", 
        "expected_serial_bytes": [0x56, 0x78, 0x9A, 0xBC, 0xDE],  # bytes 7-11
        "expected_serial_hex": "56789ABCDE",
        "expected_serial_decimal": 372470367198
    },
    {
        "tid": "FF00AA000123456789ABCDEF",  # Fallback
        "algorithm": "fallback",
        "expected_serial_bytes": [0x56, 0x78, 0x9A, 0xBC, 0xDE],  # últimos 5 bytes
        "expected_serial_hex": "56789ABCDE", 
        "expected_serial_decimal": 372470367198
    }
]

# ============================================================================
# CASOS DE TESTE PARA EDGE CASES
# ============================================================================

EDGE_CASES = [
    {
        "name": "serial_maximo",
        "tid": "E2801190000000FFFFFFFFFF",
        "description": "Serial com valor máximo (40 bits = 0xFFFFFFFFFF)",
        "expected_serial_decimal": 1099511627775  # 2^40 - 1
    },
    {
        "name": "serial_zero",
        "tid": "E2801190000000000000000000",
        "description": "Serial com valor zero",
        "expected_serial_decimal": 0
    },
    {
        "name": "monza_series_diferentes",
        "tids_e_series": [
            ("E2801190000000000000000000", 0),  # série 0 (bits 7-6 = 00)
            ("E2801190000000000000000040", 1),  # série 1 (bits 7-6 = 01) 
            ("E2801190000000000000000080", 2),  # série 2 (bits 7-6 = 10)
            ("E28011900000000000000000C0", 3),  # série 3 (bits 7-6 = 11)
        ],
        "description": "Teste de diferentes IDs de série Monza"
    }
]

# ============================================================================
# CASOS DE TESTE PARA PERFORMANCE
# ============================================================================

PERFORMANCE_TEST_DATA = {
    "small_batch": [
        "E2801190000000000000000A",
        "E2801191000000000000000B", 
        "E28011A0000000000000000C"
    ] * 10,  # 30 TIDs
    
    "medium_batch": [
        "E2801190000000000000000A",
        "E2801191000000000000000B",
        "E28011A0000000000000000C",
        "E28011B0000000000000000D",
        "E2806915000000000000000E"
    ] * 100,  # 500 TIDs
    
    "large_batch": [
        "E2801190000000000000000A",
        "E2801191000000000000000B",
        "E28011A0000000000000000C"
    ] * 1000  # 3000 TIDs
}

# ============================================================================
# HELPER FUNCTIONS PARA TESTES
# ============================================================================

def get_tid_by_name(name: str) -> str:
    """
    Retorna um TID pelos nome do sample.
    
    Args:
        name: Nome do sample (ex: 'impinj_monza_r6_1')
        
    Returns:
        TID em formato hexadecimal
    """
    if name in TID_SAMPLES:
        return TID_SAMPLES[name]["tid"]
    raise KeyError(f"Sample '{name}' não encontrado")

def get_expected_result(name: str) -> dict:
    """
    Retorna o resultado esperado para um sample.
    
    Args:
        name: Nome do sample
        
    Returns:
        Dicionário com resultado esperado
    """
    if name in EXPECTED_RESULTS:
        return EXPECTED_RESULTS[name].copy()
    raise KeyError(f"Resultado esperado para '{name}' não encontrado")

def get_all_valid_tids() -> list:
    """
    Retorna lista com todos os TIDs válidos dos samples.
    
    Returns:
        Lista de TIDs válidos
    """
    return [sample["tid"] for sample in TID_SAMPLES.values()]

def get_all_invalid_tids() -> list:
    """
    Retorna lista com todos os TIDs inválidos.
    
    Returns:
        Lista de TIDs inválidos
    """
    return [case["tid"] for case in INVALID_TIDS if case["tid"] is not None]

def get_impinj_tids() -> list:
    """
    Retorna apenas TIDs de tags Impinj.
    
    Returns:
        Lista de TIDs Impinj
    """
    impinj_samples = [
        "impinj_monza_r6_1", "impinj_monza_r6_2", "impinj_monza_r6_3",
        "impinj_m730_1", "impinj_m730_2",
        "impinj_m770_1", "impinj_m770_2", 
        "impinj_m830_1", "impinj_m830_2"
    ]
    return [TID_SAMPLES[name]["tid"] for name in impinj_samples if name in TID_SAMPLES]

def get_nxp_tids() -> list:
    """
    Retorna apenas TIDs de tags NXP.
    
    Returns:
        Lista de TIDs NXP
    """
    nxp_samples = [
        "nxp_ucode9_variant1", "nxp_ucode9_variant2", "nxp_ucode9_complex"
    ]
    return [TID_SAMPLES[name]["tid"] for name in nxp_samples if name in TID_SAMPLES]

# ============================================================================
# CONSTANTES DE TESTE
# ============================================================================

# Número máximo de TIDs para testes de performance
MAX_PERFORMANCE_TEST_SIZE = 10000

# Timeout para testes de performance (segundos)
PERFORMANCE_TEST_TIMEOUT = 30

# Tolerância para testes de performance (segundos por TID)
PERFORMANCE_TOLERANCE = 0.001  # 1ms por TID