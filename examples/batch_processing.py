#!/usr/bin/env python3
"""
Exemplo de processamento em lote de tags RFID.

Este exemplo demonstra como processar múltiplas tags RFID,
gerar relatórios e salvar resultados em arquivo.
"""

import csv
import json
from datetime import datetime
from rfid_tag_parser import parse_tid


def processar_tags_em_lote(lista_tids):
    """
    Processa uma lista de TIDs e retorna resultados estruturados.
    
    Args:
        lista_tids (list): Lista de TIDs em formato hexadecimal
        
    Returns:
        dict: Resultados do processamento com estatísticas
    """
    resultados = {
        "timestamp": datetime.now().isoformat(),
        "total_tags": len(lista_tids),
        "processadas_com_sucesso": 0,
        "erros": 0,
        "tags": [],
        "estatisticas": {
            "fabricantes": {},
            "modelos": {},
            "series_impinj": {}
        }
    }
    
    for i, tid in enumerate(lista_tids, 1):
        try:
            info = parse_tid(tid)
            info["indice"] = i
            resultados["tags"].append(info)
            resultados["processadas_com_sucesso"] += 1
            
            # Atualizar estatísticas
            vendor = info["vendor"]
            modelo = info["model_name"]
            
            # Contagem por fabricante
            resultados["estatisticas"]["fabricantes"][vendor] = \
                resultados["estatisticas"]["fabricantes"].get(vendor, 0) + 1
            
            # Contagem por modelo
            resultados["estatisticas"]["modelos"][modelo] = \
                resultados["estatisticas"]["modelos"].get(modelo, 0) + 1
            
            # Estatísticas específicas do Impinj
            if info["is_impinj"] and info["monza_series_id"] is not None:
                series_id = info["monza_series_id"]
                resultados["estatisticas"]["series_impinj"][f"Serie_{series_id}"] = \
                    resultados["estatisticas"]["series_impinj"].get(f"Serie_{series_id}", 0) + 1
            
        except Exception as e:
            resultados["erros"] += 1
            resultados["tags"].append({
                "indice": i,
                "tid": tid,
                "erro": str(e),
                "processado_com_sucesso": False
            })
    
    return resultados


def salvar_resultados_csv(resultados, nome_arquivo="resultados_tags.csv"):
    """
    Salva os resultados em formato CSV.
    
    Args:
        resultados (dict): Resultados do processamento
        nome_arquivo (str): Nome do arquivo de saída
    """
    with open(nome_arquivo, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'indice', 'tid', 'vendor', 'model_name', 'model_number',
            'serial_hex', 'serial_decimal', 'is_impinj', 'is_nxp_ucode9',
            'monza_series_id', 'erro'
        ]
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for tag in resultados["tags"]:
            # Preparar linha para CSV
            row = {field: tag.get(field, '') for field in fieldnames}
            writer.writerow(row)
    
    print(f"Resultados salvos em: {nome_arquivo}")


def salvar_resultados_json(resultados, nome_arquivo="resultados_tags.json"):
    """
    Salva os resultados em formato JSON.
    
    Args:
        resultados (dict): Resultados do processamento
        nome_arquivo (str): Nome do arquivo de saída
    """
    with open(nome_arquivo, 'w', encoding='utf-8') as jsonfile:
        json.dump(resultados, jsonfile, indent=2, ensure_ascii=False)
    
    print(f"Resultados salvos em: {nome_arquivo}")


def gerar_relatorio(resultados):
    """
    Gera um relatório resumido dos resultados.
    
    Args:
        resultados (dict): Resultados do processamento
    """
    print("=" * 60)
    print("           RELATÓRIO DE PROCESSAMENTO DE TAGS")
    print("=" * 60)
    print(f"Data/Hora: {resultados['timestamp']}")
    print(f"Total de tags: {resultados['total_tags']}")
    print(f"Processadas com sucesso: {resultados['processadas_com_sucesso']}")
    print(f"Erros: {resultados['erros']}")
    print(f"Taxa de sucesso: {(resultados['processadas_com_sucesso']/resultados['total_tags']*100):.1f}%")
    
    print("\n" + "-" * 40)
    print("DISTRIBUIÇÃO POR FABRICANTE:")
    print("-" * 40)
    for fabricante, count in resultados["estatisticas"]["fabricantes"].items():
        percentual = (count / resultados["processadas_com_sucesso"]) * 100
        print(f"{fabricante:.<25} {count:>3} ({percentual:>5.1f}%)")
    
    print("\n" + "-" * 40)
    print("DISTRIBUIÇÃO POR MODELO:")
    print("-" * 40)
    for modelo, count in sorted(resultados["estatisticas"]["modelos"].items()):
        percentual = (count / resultados["processadas_com_sucesso"]) * 100
        print(f"{modelo:.<25} {count:>3} ({percentual:>5.1f}%)")
    
    # Estatísticas específicas do Impinj
    if resultados["estatisticas"]["series_impinj"]:
        print("\n" + "-" * 40)
        print("SÉRIES IMPINJ MONZA:")
        print("-" * 40)
        for serie, count in resultados["estatisticas"]["series_impinj"].items():
            print(f"{serie:.<25} {count:>3}")


def exemplo_processamento_lote():
    """Exemplo principal de processamento em lote."""
    # Lista de TIDs de exemplo (misturando diferentes fabricantes)
    tids_exemplo = [
        "E2801190000000000000000A",  # Impinj Monza R6
        "E2801191000000000000000B",  # Impinj M730
        "E28011A0000000000000000C",  # Impinj M770
        "E28011B0000000000000000D",  # Impinj M830/M850
        "E2806915000000000000000E",  # NXP UCODE 9
        "E2806995000000000000000F",  # NXP UCODE 9
        "E2801190000000000000001A",  # Impinj Monza R6 #2
        "E2801191000000000000001B",  # Impinj M730 #2
        "INVALID_TID_EXAMPLE",        # TID inválido para teste
        "E28011A0000000000000001C",  # Impinj M770 #2
    ]
    
    print("Processando lote de tags RFID...")
    print(f"Total de tags: {len(tids_exemplo)}")
    
    # Processar tags
    resultados = processar_tags_em_lote(tids_exemplo)
    
    # Gerar relatório
    gerar_relatorio(resultados)
    
    # Salvar resultados
    salvar_resultados_csv(resultados)
    salvar_resultados_json(resultados)
    
    print("\n" + "=" * 60)
    print("Processamento concluído!")


def carregar_tids_de_arquivo(nome_arquivo):
    """
    Carrega TIDs de um arquivo de texto (um TID por linha).
    
    Args:
        nome_arquivo (str): Nome do arquivo com TIDs
        
    Returns:
        list: Lista de TIDs
    """
    try:
        with open(nome_arquivo, 'r', encoding='utf-8') as file:
            tids = [linha.strip() for linha in file if linha.strip()]
        return tids
    except FileNotFoundError:
        print(f"Arquivo {nome_arquivo} não encontrado.")
        return []


def exemplo_carregar_de_arquivo():
    """Exemplo de carregamento de TIDs de arquivo."""
    # Criar arquivo de exemplo
    tids_exemplo = [
        "E2801190000000000000000A",
        "E2801191000000000000000B", 
        "E28011A0000000000000000C"
    ]
    
    nome_arquivo = "tids_exemplo.txt"
    
    # Criar arquivo de exemplo
    with open(nome_arquivo, 'w', encoding='utf-8') as file:
        for tid in tids_exemplo:
            file.write(f"{tid}\n")
    
    print(f"Arquivo de exemplo criado: {nome_arquivo}")
    
    # Carregar e processar
    tids = carregar_tids_de_arquivo(nome_arquivo)
    if tids:
        resultados = processar_tags_em_lote(tids)
        gerar_relatorio(resultados)


if __name__ == "__main__":
    exemplo_processamento_lote()
    print("\n" + "=" * 60)
    exemplo_carregar_de_arquivo()
