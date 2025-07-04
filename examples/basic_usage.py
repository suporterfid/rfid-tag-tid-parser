#!/usr/bin/env python3
"""
Exemplo básico de uso do RFID Tag TID Parser.

Este exemplo demonstra como usar o parser para extrair informações
básicas de tags RFID.
"""

from rfid_tag_parser import TagTidParser, parse_tid, get_serial_from_tid
from rfid_tag_parser.exceptions import InvalidTidError  # ← ADICIONAR ESTA IMPORTAÇÃO


def exemplo_basico():
    """Demonstra o uso básico do parser."""
    print("=== Exemplo Básico - RFID Tag TID Parser ===\n")
    
    # TID de exemplo (Impinj Monza R6)
    tid_exemplo = "E2801190000000000000000A"
    
    print(f"TID: {tid_exemplo}")
    print("-" * 40)
    
    # Método 1: Usando a classe TagTidParser
    print("1. Usando a classe TagTidParser:")
    parser = TagTidParser(tid_exemplo)
    
    print(f"   Fabricante: {parser.get_vendor_from_tid()}")
    print(f"   Modelo: {parser.get_tag_model_name()}")
    print(f"   Número do modelo: {parser.get_tag_model_number()}")
    print(f"   Serial (Hex): {parser.get_40bit_serial_hex()}")
    print(f"   Serial (Decimal): {parser.get_40bit_serial_decimal()}")
    print(f"   É Impinj: {parser._is_impinj_tid()}")
    print(f"   É NXP UCODE9: {parser._is_nxp_ucode9_tid()}")
    
    if parser._is_impinj_tid():
        print(f"   Monza Series ID: {parser.get_monza_series_id()}")
    
    print()
    
    # Método 2: Usando a função de conveniência
    print("2. Usando a função parse_tid:")
    info = parse_tid(tid_exemplo)
    
    for chave, valor in info.items():
        print(f"   {chave}: {valor}")
    
    print()
    
    # Método 3: Extraindo apenas o serial
    print("3. Extraindo apenas o serial:")
    serial_hex = get_serial_from_tid(tid_exemplo, "hex")
    serial_dec = get_serial_from_tid(tid_exemplo, "decimal")
    
    print(f"   Serial (Hex): {serial_hex}")
    print(f"   Serial (Decimal): {serial_dec}")


def exemplo_multiplas_tags():
    """Demonstra o processamento de múltiplas tags."""
    print("\n=== Exemplo com Múltiplas Tags ===\n")
    
    # Lista de TIDs de diferentes fabricantes
    tids_exemplo = [
        "E2801190000000000000000A",  # Impinj Monza R6
        "E2801191000000000000000B",  # Impinj M730
        "E2806915000000000000000C",  # NXP UCODE 9
        "E28011A0000000000000000D",  # Impinj M770
    ]
    
    print("Processando múltiplas tags:")
    print("-" * 50)
    
    for i, tid in enumerate(tids_exemplo, 1):
        try:
            info = parse_tid(tid)
            print(f"Tag {i}:")
            print(f"  TID: {tid}")
            print(f"  Fabricante: {info['vendor']}")
            print(f"  Modelo: {info['model_name']}")
            print(f"  Serial: {info['serial_hex']}")
            print()
        except Exception as e:
            print(f"Tag {i}: Erro ao processar - {e}")
            print()


def exemplo_tratamento_erro():
    """Demonstra o tratamento de erros."""
    print("=== Exemplo de Tratamento de Erros ===\n")
    
    tids_invalidos = [
        "",                           # TID vazio
        "INVALID",                    # TID inválido
        "E2801190000000000000000",    # TID muito curto
        "E2801190000000000000000ABC", # TID muito longo
        "G2801190000000000000000A",   # Caracteres inválidos
    ]
    
    for tid in tids_invalidos:
        try:
            parser = TagTidParser(tid)
            print(f"TID '{tid}': Válido")
        except InvalidTidError as e:  # ← CAPTURA InvalidTidError ESPECIFICAMENTE
            print(f"TID '{tid}': Erro - {e}")
        except ValueError as e:       # ← CAPTURA ValueError ESPECIFICAMENTE
            print(f"TID '{tid}': Erro - {e}")
        except Exception as e:        # ← CAPTURA OUTROS ERROS
            print(f"TID '{tid}': Erro inesperado - {e}")


if __name__ == "__main__":
    exemplo_basico()
    exemplo_multiplas_tags()
    exemplo_tratamento_erro()
