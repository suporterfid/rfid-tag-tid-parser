#!/usr/bin/env python3
"""
Exemplo de Integração Completa - RFID Tag TID Parser

Este exemplo demonstra como integrar o RFID Tag TID Parser em aplicações reais,
incluindo cenários comuns como:
- Sistemas de inventário
- Controle de acesso
- Rastreamento de produtos
- APIs REST
- Bancos de dados
- Processamento em tempo real

Autor: Exemplo de integração
Data: 2025-07-04
"""

import json
import sqlite3
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from rfid_tag_parser import TagTidParser, parse_tid, get_serial_from_tid
except ImportError:
    print("❌ Erro: rfid_tag_parser não está instalado.")
    print("Execute: pip install git+https://github.com/suporterfid/rfid-tag-tid-parser.git")
    exit(1)


# ============================================================================
# CLASSES DE MODELO DE DADOS
# ============================================================================

@dataclass
class RfidTag:
    """Modelo de dados para uma tag RFID."""
    tid: str
    serial_hex: str
    serial_decimal: int
    vendor: str
    model_name: str
    model_number: str
    first_seen: datetime
    last_seen: datetime
    read_count: int = 1
    location: Optional[str] = None
    status: str = "active"
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> dict:
        """Converte para dicionário com timestamps como string."""
        data = asdict(self)
        data['first_seen'] = self.first_seen.isoformat()
        data['last_seen'] = self.last_seen.isoformat()
        return data

    @classmethod
    def from_tid(cls, tid: str, location: Optional[str] = None) -> 'RfidTag':
        """Cria uma instância RfidTag a partir de um TID."""
        try:
            info = parse_tid(tid)
            now = datetime.now()
            
            return cls(
                tid=info['tid'],
                serial_hex=info['serial_hex'],
                serial_decimal=info['serial_decimal'],
                vendor=info['vendor'],
                model_name=info['model_name'],
                model_number=info['model_number'],
                first_seen=now,
                last_seen=now,
                location=location,
                metadata={
                    'is_impinj': info['is_impinj'],
                    'is_nxp_ucode9': info['is_nxp_ucode9'],
                    'monza_series_id': info.get('monza_series_id')
                }
            )
        except Exception as e:
            raise ValueError(f"Erro ao processar TID {tid}: {e}")


@dataclass
class ReadEvent:
    """Evento de leitura de tag RFID."""
    tid: str
    timestamp: datetime
    reader_id: str
    location: str
    signal_strength: Optional[int] = None
    antenna_id: Optional[int] = None

    def to_dict(self) -> dict:
        """Converte para dicionário."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


# ============================================================================
# SISTEMA DE INVENTÁRIO RFID
# ============================================================================

class RfidInventorySystem:
    """
    Sistema completo de inventário RFID.
    
    Funcionalidades:
    - Registro e rastreamento de tags
    - Histórico de leituras
    - Relatórios e estatísticas
    - Persistência em banco de dados
    """
    
    def __init__(self, db_path: str = "rfid_inventory.db"):
        """
        Inicializa o sistema de inventário.
        
        Args:
            db_path: Caminho para o banco de dados SQLite
        """
        self.db_path = db_path
        self.tags: Dict[str, RfidTag] = {}
        self.read_events: List[ReadEvent] = []
        self._init_database()
        self._load_existing_tags()
    
    def _init_database(self):
        """Inicializa o banco de dados SQLite."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS rfid_tags (
                    tid TEXT PRIMARY KEY,
                    serial_hex TEXT NOT NULL,
                    serial_decimal INTEGER NOT NULL,
                    vendor TEXT NOT NULL,
                    model_name TEXT NOT NULL,
                    model_number TEXT NOT NULL,
                    first_seen TEXT NOT NULL,
                    last_seen TEXT NOT NULL,
                    read_count INTEGER DEFAULT 1,
                    location TEXT,
                    status TEXT DEFAULT 'active',
                    metadata TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS read_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tid TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    reader_id TEXT NOT NULL,
                    location TEXT NOT NULL,
                    signal_strength INTEGER,
                    antenna_id INTEGER,
                    FOREIGN KEY (tid) REFERENCES rfid_tags (tid)
                )
            """)
            
            # Índices para performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tags_vendor ON rfid_tags (vendor)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tags_model ON rfid_tags (model_name)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_events_timestamp ON read_events (timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_events_location ON read_events (location)")
    
    def _load_existing_tags(self):
        """Carrega tags existentes do banco de dados."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM rfid_tags")
            
            for row in cursor.fetchall():
                tag = RfidTag(
                    tid=row['tid'],
                    serial_hex=row['serial_hex'],
                    serial_decimal=row['serial_decimal'],
                    vendor=row['vendor'],
                    model_name=row['model_name'],
                    model_number=row['model_number'],
                    first_seen=datetime.fromisoformat(row['first_seen']),
                    last_seen=datetime.fromisoformat(row['last_seen']),
                    read_count=row['read_count'],
                    location=row['location'],
                    status=row['status'],
                    metadata=json.loads(row['metadata']) if row['metadata'] else None
                )
                self.tags[tag.tid] = tag
    
    def register_tag_reading(self, tid: str, reader_id: str, location: str, 
                           signal_strength: Optional[int] = None, 
                           antenna_id: Optional[int] = None) -> RfidTag:
        """
        Registra a leitura de uma tag RFID.
        
        Args:
            tid: TID da tag em formato hexadecimal
            reader_id: Identificador do leitor RFID
            location: Local da leitura
            signal_strength: Força do sinal (opcional)
            antenna_id: ID da antena (opcional)
            
        Returns:
            Objeto RfidTag atualizado
        """
        now = datetime.now()
        
        # Criar evento de leitura
        event = ReadEvent(
            tid=tid,
            timestamp=now,
            reader_id=reader_id,
            location=location,
            signal_strength=signal_strength,
            antenna_id=antenna_id
        )
        self.read_events.append(event)
        
        # Atualizar ou criar tag
        if tid in self.tags:
            # Tag existente - atualizar
            tag = self.tags[tid]
            tag.last_seen = now
            tag.read_count += 1
            tag.location = location  # Atualizar localização
        else:
            # Nova tag - criar
            tag = RfidTag.from_tid(tid, location)
            self.tags[tid] = tag
        
        # Persistir no banco
        self._save_tag(tag)
        self._save_event(event)
        
        return tag
    
    def _save_tag(self, tag: RfidTag):
        """Salva ou atualiza uma tag no banco de dados."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO rfid_tags 
                (tid, serial_hex, serial_decimal, vendor, model_name, model_number,
                 first_seen, last_seen, read_count, location, status, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                tag.tid, tag.serial_hex, tag.serial_decimal, tag.vendor,
                tag.model_name, tag.model_number, tag.first_seen.isoformat(),
                tag.last_seen.isoformat(), tag.read_count, tag.location,
                tag.status, json.dumps(tag.metadata) if tag.metadata else None
            ))
    
    def _save_event(self, event: ReadEvent):
        """Salva um evento de leitura no banco de dados."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO read_events 
                (tid, timestamp, reader_id, location, signal_strength, antenna_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                event.tid, event.timestamp.isoformat(), event.reader_id,
                event.location, event.signal_strength, event.antenna_id
            ))
    
    def get_tags_by_vendor(self, vendor: str) -> List[RfidTag]:
        """Retorna todas as tags de um fabricante específico."""
        return [tag for tag in self.tags.values() if vendor.lower() in tag.vendor.lower()]
    
    def get_tags_by_location(self, location: str) -> List[RfidTag]:
        """Retorna todas as tags em um local específico."""
        return [tag for tag in self.tags.values() if tag.location == location]
    
    def get_recent_readings(self, hours: int = 24) -> List[ReadEvent]:
        """Retorna leituras recentes das últimas N horas."""
        cutoff = datetime.now() - timedelta(hours=hours)
        return [event for event in self.read_events if event.timestamp >= cutoff]
    
    def generate_inventory_report(self) -> Dict[str, Any]:
        """Gera um relatório completo do inventário."""
        total_tags = len(self.tags)
        vendor_stats = {}
        model_stats = {}
        location_stats = {}
        
        for tag in self.tags.values():
            # Estatísticas por fabricante
            vendor_stats[tag.vendor] = vendor_stats.get(tag.vendor, 0) + 1
            
            # Estatísticas por modelo
            model_stats[tag.model_name] = model_stats.get(tag.model_name, 0) + 1
            
            # Estatísticas por localização
            if tag.location:
                location_stats[tag.location] = location_stats.get(tag.location, 0) + 1
        
        # Tags mais lidas
        top_tags = sorted(self.tags.values(), key=lambda t: t.read_count, reverse=True)[:10]
        
        return {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tags": total_tags,
                "total_readings": len(self.read_events),
                "unique_vendors": len(vendor_stats),
                "unique_models": len(model_stats),
                "unique_locations": len(location_stats)
            },
            "vendor_distribution": vendor_stats,
            "model_distribution": model_stats,
            "location_distribution": location_stats,
            "top_read_tags": [
                {
                    "tid": tag.tid,
                    "model": tag.model_name,
                    "read_count": tag.read_count,
                    "location": tag.location
                }
                for tag in top_tags
            ]
        }


# ============================================================================
# SIMULADOR DE LEITOR RFID
# ============================================================================

class RfidReaderSimulator:
    """
    Simulador de leitor RFID para testes e demonstrações.
    
    Simula leituras realísticas com:
    - TIDs de diferentes fabricantes
    - Variação de força de sinal
    - Múltiplas antenas
    - Diferentes localizações
    """
    
    def __init__(self, reader_id: str = "READER-001"):
        """
        Inicializa o simulador.
        
        Args:
            reader_id: Identificador único do leitor
        """
        self.reader_id = reader_id
        self.locations = ["Almoxarifado", "Linha_Producao", "Expedicao", "Recebimento"]
        self.sample_tids = [
            # Impinj tags
            "E2801190000000000000000A",  # Monza R6
            "E2801191000000000000000B",  # M730
            "E28011A0000000000000000C",  # M770
            "E28011B0000000000000000D",  # M830
            "E2801190123456789ABCDEF0",  # Monza R6 #2
            
            # NXP tags
            "E2806915000000000000000E",  # UCODE 9
            "E2806995000000000000000F",  # UCODE 9 #2
            "E28069159876543210FEDCBA",  # UCODE 9 #3
            

        ]
    
    def simulate_reading_session(self, duration_seconds: int = 60, 
                               tags_per_second: float = 2.0) -> List[ReadEvent]:
        """
        Simula uma sessão de leitura de tags.
        
        Args:
            duration_seconds: Duração da simulação em segundos
            tags_per_second: Taxa média de leitura de tags
            
        Returns:
            Lista de eventos de leitura simulados
        """
        import random
        
        events = []
        start_time = datetime.now()
        
        print(f"🔄 Iniciando simulação de leitura ({duration_seconds}s, {tags_per_second} tags/s)")
        
        while (datetime.now() - start_time).total_seconds() < duration_seconds:
            # Selecionar tag aleatória
            tid = random.choice(self.sample_tids)
            
            # Parâmetros aleatórios
            location = random.choice(self.locations)
            signal_strength = random.randint(-70, -20)  # dBm
            antenna_id = random.randint(1, 4)
            
            event = ReadEvent(
                tid=tid,
                timestamp=datetime.now(),
                reader_id=self.reader_id,
                location=location,
                signal_strength=signal_strength,
                antenna_id=antenna_id
            )
            
            events.append(event)
            
            # Aguardar próxima leitura
            time.sleep(1.0 / tags_per_second + random.uniform(-0.1, 0.1))
        
        print(f"✅ Simulação concluída: {len(events)} leituras geradas")
        return events


# ============================================================================
# API REST SIMPLES (SIMULADA)
# ============================================================================

class RfidApiService:
    """
    Serviço de API REST para integração com sistemas externos.
    
    Simula endpoints típicos de uma API RFID:
    - POST /tags/reading - Registrar leitura
    - GET /tags - Listar tags
    - GET /reports/inventory - Relatório de inventário
    """
    
    def __init__(self, inventory_system: RfidInventorySystem):
        """
        Inicializa o serviço de API.
        
        Args:
            inventory_system: Sistema de inventário RFID
        """
        self.inventory = inventory_system
    
    def handle_tag_reading(self, data: dict) -> dict:
        """
        Endpoint: POST /tags/reading
        
        Processa uma leitura de tag via API.
        
        Args:
            data: Dados da requisição {tid, reader_id, location, ...}
            
        Returns:
            Resposta da API
        """
        try:
            tid = data.get('tid', '').strip()
            reader_id = data.get('reader_id', 'UNKNOWN')
            location = data.get('location', 'UNKNOWN')
            signal_strength = data.get('signal_strength')
            antenna_id = data.get('antenna_id')
            
            if not tid:
                return {
                    "status": "error",
                    "message": "TID é obrigatório",
                    "code": 400
                }
            
            # Registrar leitura
            tag = self.inventory.register_tag_reading(
                tid=tid,
                reader_id=reader_id,
                location=location,
                signal_strength=signal_strength,
                antenna_id=antenna_id
            )
            
            return {
                "status": "success",
                "message": "Leitura registrada com sucesso",
                "data": tag.to_dict(),
                "code": 200
            }
            
        except ValueError as e:
            return {
                "status": "error",
                "message": f"TID inválido: {str(e)}",
                "code": 400
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Erro interno: {str(e)}",
                "code": 500
            }
    
    def handle_list_tags(self, filters: dict = None) -> dict:
        """
        Endpoint: GET /tags
        
        Lista tags com filtros opcionais.
        
        Args:
            filters: Filtros {vendor, location, model, ...}
            
        Returns:
            Lista de tags
        """
        try:
            tags = list(self.inventory.tags.values())
            
            # Aplicar filtros
            if filters:
                if 'vendor' in filters:
                    tags = [t for t in tags if filters['vendor'].lower() in t.vendor.lower()]
                if 'location' in filters:
                    tags = [t for t in tags if t.location == filters['location']]
                if 'model' in filters:
                    tags = [t for t in tags if filters['model'].lower() in t.model_name.lower()]
            
            return {
                "status": "success",
                "data": [tag.to_dict() for tag in tags],
                "total": len(tags),
                "code": 200
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Erro ao listar tags: {str(e)}",
                "code": 500
            }
    
    def handle_inventory_report(self) -> dict:
        """
        Endpoint: GET /reports/inventory
        
        Gera relatório de inventário.
        
        Returns:
            Relatório completo
        """
        try:
            report = self.inventory.generate_inventory_report()
            
            return {
                "status": "success",
                "data": report,
                "code": 200
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Erro ao gerar relatório: {str(e)}",
                "code": 500
            }


# ============================================================================
# PROCESSAMENTO EM LOTE DE ALTA PERFORMANCE
# ============================================================================

class HighPerformanceProcessor:
    """
    Processador de alta performance para grandes volumes de TIDs.
    
    Características:
    - Processamento paralelo com ThreadPoolExecutor
    - Batch processing otimizado
    - Estatísticas de performance
    - Tratamento de erros robusto
    """
    
    def __init__(self, max_workers: int = 4):
        """
        Inicializa o processador.
        
        Args:
            max_workers: Número máximo de threads trabalhadoras
        """
        self.max_workers = max_workers
    
    def process_tid_batch(self, tids: List[str], batch_size: int = 100) -> Dict[str, Any]:
        """
        Processa um lote de TIDs em paralelo.
        
        Args:
            tids: Lista de TIDs para processar
            batch_size: Tamanho do lote para processamento
            
        Returns:
            Resultados do processamento com estatísticas
        """
        start_time = time.time()
        results = []
        errors = []
        
        print(f"🚀 Iniciando processamento de {len(tids)} TIDs...")
        print(f"📊 Configuração: {self.max_workers} workers, lotes de {batch_size}")
        
        # Dividir em lotes
        batches = [tids[i:i + batch_size] for i in range(0, len(tids), batch_size)]
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submeter lotes para processamento
            future_to_batch = {
                executor.submit(self._process_single_batch, batch): i 
                for i, batch in enumerate(batches)
            }
            
            # Coletar resultados
            for future in as_completed(future_to_batch):
                batch_index = future_to_batch[future]
                try:
                    batch_results, batch_errors = future.result()
                    results.extend(batch_results)
                    errors.extend(batch_errors)
                    print(f"✅ Lote {batch_index + 1}/{len(batches)} concluído")
                except Exception as e:
                    print(f"❌ Erro no lote {batch_index + 1}: {e}")
                    errors.append({"batch": batch_index, "error": str(e)})
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Estatísticas
        stats = {
            "total_tids": len(tids),
            "successful": len(results),
            "errors": len(errors),
            "processing_time": processing_time,
            "tids_per_second": len(tids) / processing_time if processing_time > 0 else 0,
            "success_rate": len(results) / len(tids) * 100 if tids else 0
        }
        
        print(f"\n📈 Estatísticas de Performance:")
        print(f"   Total processados: {stats['total_tids']}")
        print(f"   Sucessos: {stats['successful']}")
        print(f"   Erros: {stats['errors']}")
        print(f"   Tempo: {stats['processing_time']:.2f}s")
        print(f"   Velocidade: {stats['tids_per_second']:.1f} TIDs/s")
        print(f"   Taxa de sucesso: {stats['success_rate']:.1f}%")
        
        return {
            "results": results,
            "errors": errors,
            "statistics": stats
        }
    
    def _process_single_batch(self, batch: List[str]) -> tuple:
        """
        Processa um único lote de TIDs.
        
        Args:
            batch: Lista de TIDs do lote
            
        Returns:
            Tupla (resultados, erros)
        """
        results = []
        errors = []
        
        for tid in batch:
            try:
                info = parse_tid(tid)
                results.append(info)
            except Exception as e:
                errors.append({"tid": tid, "error": str(e)})
        
        return results, errors


# ============================================================================
# EXEMPLOS DE USO E DEMONSTRAÇÃO
# ============================================================================

def exemplo_sistema_inventario():
    """Demonstra o uso completo do sistema de inventário."""
    print("=" * 80)
    print("🏭 EXEMPLO: SISTEMA DE INVENTÁRIO RFID")
    print("=" * 80)
    
    # Inicializar sistema
    inventory = RfidInventorySystem("exemplo_inventario.db")
    
    # Simular algumas leituras
    sample_readings = [
        ("E2801190000000000000000A", "READER-001", "Almoxarifado"),
        ("E2801191000000000000000B", "READER-002", "Linha_Producao"),
        ("E28011A0000000000000000C", "READER-001", "Almoxarifado"),
        ("E2806915000000000000000E", "READER-003", "Expedicao"),
        ("E2801190000000000000000A", "READER-001", "Almoxarifado"),  # Re-leitura
    ]
    
    print("\n📊 Registrando leituras de tags...")
    for tid, reader, location in sample_readings:
        tag = inventory.register_tag_reading(
            tid=tid,
            reader_id=reader,
            location=location,
            signal_strength=-45,
            antenna_id=1
        )
        print(f"   ✓ {tag.model_name} (Serial: {tag.serial_hex}) em {location}")
    
    # Relatório
    print("\n📈 Gerando relatório de inventário...")
    report = inventory.generate_inventory_report()
    
    print(f"\n📋 Resumo do Inventário:")
    print(f"   Total de tags: {report['summary']['total_tags']}")
    print(f"   Total de leituras: {report['summary']['total_readings']}")
    print(f"   Fabricantes únicos: {report['summary']['unique_vendors']}")
    
    print(f"\n🏷️ Distribuição por fabricante:")
    for vendor, count in report['vendor_distribution'].items():
        print(f"   {vendor}: {count} tags")
    
    return inventory


def exemplo_simulacao_leitor():
    """Demonstra o simulador de leitor RFID."""
    print("\n" + "=" * 80)
    print("📡 EXEMPLO: SIMULAÇÃO DE LEITOR RFID")
    print("=" * 80)
    
    # Inicializar simulador e inventário
    simulator = RfidReaderSimulator("SIM-READER-001")
    inventory = RfidInventorySystem("exemplo_simulacao.db")
    
    # Executar simulação curta
    events = simulator.simulate_reading_session(duration_seconds=10, tags_per_second=3.0)
    
    print(f"\n📊 Processando {len(events)} eventos simulados...")
    for event in events:
        inventory.register_tag_reading(
            tid=event.tid,
            reader_id=event.reader_id,
            location=event.location,
            signal_strength=event.signal_strength,
            antenna_id=event.antenna_id
        )
    
    # Estatísticas
    print(f"\n📈 Resultados da simulação:")
    print(f"   Tags únicas detectadas: {len(inventory.tags)}")
    print(f"   Eventos de leitura: {len(events)}")
    
    return events


def exemplo_api_service():
    """Demonstra o serviço de API."""
    print("\n" + "=" * 80)
    print("🌐 EXEMPLO: SERVIÇO DE API REST")
    print("=" * 80)
    
    # Inicializar serviços
    inventory = RfidInventorySystem("exemplo_api.db")
    api = RfidApiService(inventory)
    
    # Simular chamadas de API
    print("\n📡 Simulando chamadas de API...")
    
    # POST /tags/reading
    reading_data = {
        "tid": "E2801190123456789ABCDEF0",
        "reader_id": "API-READER-001",
        "location": "API_Test_Location",
        "signal_strength": -35,
        "antenna_id": 2
    }
    
    response = api.handle_tag_reading(reading_data)
    print(f"   POST /tags/reading: {response['status']} - {response['message']}")
    
    # GET /tags
    response = api.handle_list_tags({"vendor": "Impinj"})
    print(f"   GET /tags?vendor=Impinj: {response['status']} - {response['total']} tags encontradas")
    
    # GET /reports/inventory
    response = api.handle_inventory_report()
    print(f"   GET /reports/inventory: {response['status']} - Relatório gerado")
    
    return api


def exemplo_processamento_alta_performance():
    """Demonstra o processamento de alta performance."""
    print("\n" + "=" * 80)
    print("⚡ EXEMPLO: PROCESSAMENTO DE ALTA PERFORMANCE")
    print("=" * 80)
    
    # Gerar lote de TIDs para teste
    base_tids = [
        "E2801190000000000000000A",
        "E2801191000000000000000B", 
        "E28011A0000000000000000C",
        "E2806915000000000000000E",
        "INVALID_TID_FOR_TEST",  # TID inválido para teste
    ]
    
    # Multiplicar para criar lote maior
    test_tids = base_tids * 50  # 250 TIDs total
    
    # Processar com alta performance
    processor = HighPerformanceProcessor(max_workers=4)
    results = processor.process_tid_batch(test_tids, batch_size=25)
    
    # Mostrar alguns resultados
    print(f"\n📋 Primeiras 3 tags processadas:")
    for i, result in enumerate(results['results'][:3]):
        print(f"   {i+1}. {result['model_name']} - Serial: {result['serial_hex']}")
    
    return results


def exemplo_integracao_completa():
    """Exemplo de integração completa de todos os componentes."""
    print("\n" + "=" * 80)
    print("🔧 EXEMPLO: INTEGRAÇÃO COMPLETA")
    print("=" * 80)
    
    print("🎯 Demonstrando pipeline completo de RFID...")
    
    # 1. Inicializar todos os componentes
    print("\n📡 1. Inicializando componentes do sistema...")
    inventory = RfidInventorySystem("integracao_completa.db")
    simulator = RfidReaderSimulator("MAIN-READER")
    api = RfidApiService(inventory)
    processor = HighPerformanceProcessor(max_workers=2)
    
    # 2. Simular captura de dados
    print("\n📊 2. Simulando captura de dados RFID...")
    events = simulator.simulate_reading_session(duration_seconds=8, tags_per_second=2.0)
    
    # 3. Processar eventos via API
    print("\n🌐 3. Processando eventos via API...")
    api_results = []
    for event in events[:5]:  # Processar apenas alguns via API
        api_data = {
            "tid": event.tid,
            "reader_id": event.reader_id,
            "location": event.location,
            "signal_strength": event.signal_strength,
            "antenna_id": event.antenna_id
        }
        result = api.handle_tag_reading(api_data)
        api_results.append(result)
        if result["status"] == "success":
            print(f"   ✓ API: {result['data']['model_name']} processada")
    
    # 4. Processamento em lote dos restantes
    print("\n⚡ 4. Processamento em lote de alta performance...")
    remaining_tids = [e.tid for e in events[5:]]
    if remaining_tids:
        batch_results = processor.process_tid_batch(remaining_tids, batch_size=10)
        
        # Registrar resultados do lote no inventário
        for result in batch_results["results"]:
            inventory.register_tag_reading(
                tid=result["tid"],
                reader_id="BATCH-PROCESSOR",
                location="Processamento_Lote"
            )
    
    # 5. Análise e relatórios
    print("\n📈 5. Gerando análises e relatórios...")
    
    # Relatório de inventário
    inventory_report = inventory.generate_inventory_report()
    
    # Estatísticas por fabricante
    vendor_stats = inventory_report["vendor_distribution"]
    
    # Relatório via API
    api_report = api.handle_inventory_report()
    
    # 6. Apresentar resultados
    print("\n" + "=" * 60)
    print("📋 RESULTADOS DA INTEGRAÇÃO COMPLETA")
    print("=" * 60)
    
    print(f"\n🏷️ Resumo Geral:")
    print(f"   Eventos simulados: {len(events)}")
    print(f"   Processados via API: {len(api_results)}")
    print(f"   Tags únicas identificadas: {inventory_report['summary']['total_tags']}")
    print(f"   Total de leituras: {inventory_report['summary']['total_readings']}")
    
    print(f"\n🏭 Distribuição por Fabricante:")
    for vendor, count in vendor_stats.items():
        percentage = (count / inventory_report['summary']['total_tags']) * 100
        print(f"   {vendor:<25} {count:>3} tags ({percentage:>5.1f}%)")
    
    print(f"\n📊 Top 3 Tags Mais Lidas:")
    for i, tag in enumerate(inventory_report["top_read_tags"][:3], 1):
        print(f"   {i}. {tag['model']:<20} Serial: {tag['tid'][-10:]} ({tag['read_count']} leituras)")
    
    # 7. Demonstrar consultas específicas
    print(f"\n🔍 Consultas Específicas:")
    
    # Tags Impinj
    impinj_tags = inventory.get_tags_by_vendor("Impinj")
    print(f"   Tags Impinj encontradas: {len(impinj_tags)}")
    
    # Tags por localização
    for location in ["Almoxarifado", "Linha_Producao", "Expedicao"]:
        location_tags = inventory.get_tags_by_location(location)
        if location_tags:
            print(f"   Tags em {location}: {len(location_tags)}")
    
    # Leituras recentes
    recent_readings = inventory.get_recent_readings(hours=1)
    print(f"   Leituras na última hora: {len(recent_readings)}")
    
    print("\n" + "=" * 60)
    print("✅ INTEGRAÇÃO COMPLETA FINALIZADA COM SUCESSO!")
    print("=" * 60)
    
    return {
        "inventory": inventory,
        "events": events,
        "api_results": api_results,
        "reports": {
            "inventory": inventory_report,
            "api": api_report
        }
    }


def exemplo_casos_uso_reais():
    """Demonstra casos de uso reais em diferentes indústrias."""
    print("\n" + "=" * 80)
    print("🏭 CASOS DE USO REAIS POR INDÚSTRIA")
    print("=" * 80)
    
    # Caso 1: Manufatura - Controle de Linha de Produção
    print("\n🔧 CASO 1: MANUFATURA - CONTROLE DE LINHA DE PRODUÇÃO")
    print("-" * 60)
    
    manufacturing_inventory = RfidInventorySystem("manufacturing.db")
    
    # Simular produtos passando por estações
    production_stages = [
        "Entrada_Materiais", "Montagem_Principal", "Teste_Qualidade", 
        "Embalagem", "Expedicao"
    ]
    
    sample_products = [
        "E2801190000000000000001A",  # Produto A
        "E2801191000000000000001B",  # Produto B
        "E28011A0000000000000001C",  # Produto C
    ]
    
    print("   Rastreando produtos através da linha de produção...")
    for stage in production_stages:
        for product_tid in sample_products:
            manufacturing_inventory.register_tag_reading(
                tid=product_tid,
                reader_id=f"READER-{stage}",
                location=stage,
                signal_strength=-35
            )
        print(f"   ✓ Estágio {stage}: {len(sample_products)} produtos processados")
    
    # Relatório de rastreabilidade
    manufacturing_report = manufacturing_inventory.generate_inventory_report()
    print(f"\n   📊 Resultado: {manufacturing_report['summary']['total_readings']} leituras em {len(production_stages)} estágios")
    
    # Caso 2: Varejo - Gestão de Inventário
    print("\n🛒 CASO 2: VAREJO - GESTÃO DE INVENTÁRIO")
    print("-" * 60)
    
    retail_inventory = RfidInventorySystem("retail.db")
    
    # Simular diferentes tipos de produtos
    retail_products = {
        "Roupas": ["E2806915000000000000010A", "E2806915000000000000010B"],
        "Eletronicos": ["E2801190000000000000020A", "E2801191000000000000020B"],
        "Livros": ["E28011A0000000000000030A", "E28011A0000000000000030B"],
    }
    
    retail_locations = ["Estoque", "Loja_Principal", "Vitrine", "Vendido"]
    
    print("   Simulando movimentação de produtos no varejo...")
    for category, products in retail_products.items():
        for location in retail_locations:
            for product in products:
                retail_inventory.register_tag_reading(
                    tid=product,
                    reader_id=f"RETAIL-READER-{location.upper()}",
                    location=location
                )
        print(f"   ✓ Categoria {category}: produtos rastreados em {len(retail_locations)} locais")
    
    # Análise de rotatividade
    retail_report = retail_inventory.generate_inventory_report()
    print(f"\n   📊 Inventário: {retail_report['summary']['total_tags']} produtos únicos")
    print(f"   📍 Distribuição por local:")
    for location, count in retail_report['location_distribution'].items():
        print(f"      {location}: {count} produtos")
    
    # Caso 3: Logística - Rastreamento de Carga
    print("\n🚛 CASO 3: LOGÍSTICA - RASTREAMENTO DE CARGA")
    print("-" * 60)
    
    logistics_inventory = RfidInventorySystem("logistics.db")
    
    # Simular containers e pallets
    logistics_items = [
        ("E2827802000000000000100A", "Container_001"),
        ("E2827803000000000000100B", "Pallet_001"), 
        ("E2827804000000000000100C", "Pallet_002"),
        ("E2806995000000000000100D", "Container_002"),
    ]
    
    logistics_checkpoints = [
        "Centro_Distribuicao", "Transporte", "Hub_Regional", 
        "Ultima_Milha", "Entregue"
    ]
    
    print("   Rastreando carga através da cadeia logística...")
    for checkpoint in logistics_checkpoints:
        for item_tid, item_name in logistics_items:
            logistics_inventory.register_tag_reading(
                tid=item_tid,
                reader_id=f"LOGISTICS-{checkpoint}",
                location=checkpoint,
                signal_strength=-40
            )
        print(f"   ✓ Checkpoint {checkpoint}: {len(logistics_items)} itens processados")
    
    logistics_report = logistics_inventory.generate_inventory_report()
    print(f"\n   📊 Rastreamento: {logistics_report['summary']['total_readings']} verificações")
    print(f"   🚚 Itens únicos: {logistics_report['summary']['total_tags']}")
    
    return {
        "manufacturing": manufacturing_report,
        "retail": retail_report,
        "logistics": logistics_report
    }


def exemplo_monitoramento_tempo_real():
    """Demonstra sistema de monitoramento em tempo real."""
    print("\n" + "=" * 80)
    print("⏱️ MONITORAMENTO EM TEMPO REAL")
    print("=" * 80)
    
    # Sistema de alertas
    class RfidAlertSystem:
        def __init__(self):
            self.alerts = []
            self.thresholds = {
                "signal_strength_min": -60,  # dBm
                "read_frequency_max": 10,    # leituras por minuto
                "location_change_alert": True
            }
        
        def check_alerts(self, tag: RfidTag, event: ReadEvent):
            """Verifica condições de alerta."""
            alerts = []
            
            # Alerta de sinal fraco
            if event.signal_strength and event.signal_strength < self.thresholds["signal_strength_min"]:
                alerts.append(f"⚠️ Sinal fraco para {tag.model_name}: {event.signal_strength} dBm")
            
            # Alerta de mudança de localização
            if self.thresholds["location_change_alert"] and tag.location != event.location:
                alerts.append(f"📍 Localização alterada: {tag.model_name} de {tag.location} para {event.location}")
            
            # Alerta de frequência alta
            if tag.read_count > self.thresholds["read_frequency_max"]:
                alerts.append(f"🔄 Alta frequência de leitura: {tag.model_name} ({tag.read_count} leituras)")
            
            return alerts
    
    # Inicializar sistema
    monitoring_inventory = RfidInventorySystem("monitoring.db")
    alert_system = RfidAlertSystem()
    
    print("\n📡 Iniciando monitoramento em tempo real...")
    
    # Simular eventos com diferentes condições
    monitoring_events = [
        # Evento normal
        ("E2801190000000000000001A", "MONITOR-001", "Zona_A", -35, 1),
        
        # Sinal fraco
        ("E2801191000000000000001B", "MONITOR-002", "Zona_B", -65, 2),
        
        # Mudança de localização
        ("E2801190000000000000001A", "MONITOR-003", "Zona_C", -40, 1),
        
        # Alta frequência
        ("E28011A0000000000000001C", "MONITOR-001", "Zona_A", -30, 1),
        ("E28011A0000000000000001C", "MONITOR-001", "Zona_A", -32, 1),
        ("E28011A0000000000000001C", "MONITOR-001", "Zona_A", -28, 1),
    ]
    
    all_alerts = []
    
    for tid, reader_id, location, signal_strength, antenna_id in monitoring_events:
        # Registrar leitura
        tag = monitoring_inventory.register_tag_reading(
            tid=tid,
            reader_id=reader_id,
            location=location,
            signal_strength=signal_strength,
            antenna_id=antenna_id
        )
        
        # Criar evento para verificação
        event = ReadEvent(
            tid=tid,
            timestamp=datetime.now(),
            reader_id=reader_id,
            location=location,
            signal_strength=signal_strength,
            antenna_id=antenna_id
        )
        
        # Verificar alertas
        alerts = alert_system.check_alerts(tag, event)
        all_alerts.extend(alerts)
        
        # Log do evento
        print(f"   📊 {tag.model_name} lida em {location} (Sinal: {signal_strength} dBm)")
        for alert in alerts:
            print(f"      {alert}")
    
    print(f"\n📈 Resumo do Monitoramento:")
    print(f"   Eventos processados: {len(monitoring_events)}")
    print(f"   Alertas gerados: {len(all_alerts)}")
    print(f"   Tags monitoradas: {len(monitoring_inventory.tags)}")
    
    return {
        "inventory": monitoring_inventory,
        "alerts": all_alerts,
        "alert_system": alert_system
    }


def exemplo_analise_avancada():
    """Demonstra análises avançadas de dados RFID."""
    print("\n" + "=" * 80)
    print("📊 ANÁLISE AVANÇADA DE DADOS RFID")
    print("=" * 80)
    
    # Criar dataset para análise
    analysis_inventory = RfidInventorySystem("analysis.db")
    
    # Gerar dados históricos simulados
    print("\n📈 Gerando dados históricos para análise...")
    
    analysis_tids = [
        "E2801190000000000000001A", "E2801191000000000000001B",
        "E28011A0000000000000001C", "E2806915000000000000001D",
        "E2827802000000000000001E"
    ]
    
    locations = ["Entrada", "Processamento", "Armazenamento", "Saida"]
    
    # Simular 30 dias de dados
    import random
    from datetime import timedelta
    
    base_date = datetime.now() - timedelta(days=30)
    total_events = 0
    
    for day in range(30):
        current_date = base_date + timedelta(days=day)
        daily_events = random.randint(5, 15)
        
        for _ in range(daily_events):
            tid = random.choice(analysis_tids)
            location = random.choice(locations)
            
            # Simular timestamp dentro do dia
            event_time = current_date + timedelta(
                hours=random.randint(8, 17),
                minutes=random.randint(0, 59)
            )
            
            analysis_inventory.register_tag_reading(
                tid=tid,
                reader_id=f"ANALYTICS-READER-{random.randint(1,3)}",
                location=location,
                signal_strength=random.randint(-70, -20)
            )
            total_events += 1
    
    print(f"   ✓ Gerados {total_events} eventos ao longo de 30 dias")
    
    # Análises estatísticas
    print("\n🔍 Executando análises estatísticas...")
    
    # 1. Análise de frequência por tag
    tag_frequency = {}
    for tag in analysis_inventory.tags.values():
        tag_frequency[tag.model_name] = tag_frequency.get(tag.model_name, 0) + tag.read_count
    
    print(f"\n   📊 Frequência de Leitura por Modelo:")
    for model, frequency in sorted(tag_frequency.items(), key=lambda x: x[1], reverse=True):
        print(f"      {model:<20} {frequency:>6} leituras")
    
    # 2. Análise de distribuição por localização
    location_analysis = {}
    for event in analysis_inventory.read_events:
        location_analysis[event.location] = location_analysis.get(event.location, 0) + 1
    
    print(f"\n   📍 Distribuição por Localização:")
    total_reads = sum(location_analysis.values())
    for location, count in sorted(location_analysis.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_reads) * 100
        print(f"      {location:<15} {count:>6} ({percentage:>5.1f}%)")
    
    # 3. Análise de fabricantes
    vendor_analysis = {}
    for tag in analysis_inventory.tags.values():
        vendor = tag.vendor.split()[0]  # Primeiro palavra (Impinj, NXP, etc.)
        vendor_analysis[vendor] = vendor_analysis.get(vendor, 0) + 1
    
    print(f"\n   🏭 Distribuição por Fabricante:")
    for vendor, count in sorted(vendor_analysis.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(analysis_inventory.tags)) * 100
        print(f"      {vendor:<15} {count:>6} tags ({percentage:>5.1f}%)")
    
    # 4. Métricas de performance
    print(f"\n   ⚡ Métricas de Performance:")
    print(f"      Tags únicas processadas: {len(analysis_inventory.tags)}")
    print(f"      Total de leituras: {len(analysis_inventory.read_events)}")
    print(f"      Média de leituras por tag: {len(analysis_inventory.read_events) / len(analysis_inventory.tags):.1f}")
    
    # 5. Identificar padrões
    print(f"\n   🔍 Padrões Identificados:")
    
    # Tag mais ativa
    most_active_tag = max(analysis_inventory.tags.values(), key=lambda t: t.read_count)
    print(f"      Tag mais ativa: {most_active_tag.model_name} ({most_active_tag.read_count} leituras)")
    
    # Localização mais movimentada
    busiest_location = max(location_analysis.items(), key=lambda x: x[1])
    print(f"      Local mais movimentado: {busiest_location[0]} ({busiest_location[1]} eventos)")
    
    # Fabricante dominante
    dominant_vendor = max(vendor_analysis.items(), key=lambda x: x[1])
    print(f"      Fabricante dominante: {dominant_vendor[0]} ({dominant_vendor[1]} tags)")
    
    return {
        "inventory": analysis_inventory,
        "analytics": {
            "tag_frequency": tag_frequency,
            "location_analysis": location_analysis,
            "vendor_analysis": vendor_analysis,
            "most_active_tag": most_active_tag,
            "total_events": total_events
        }
    }


# ============================================================================
# FUNÇÃO PRINCIPAL DE DEMONSTRAÇÃO
# ============================================================================

def main():
    """Função principal que executa todos os exemplos de integração."""
    print("🚀" * 40)
    print("🏷️  RFID TAG TID PARSER - EXEMPLOS DE INTEGRAÇÃO COMPLETA")
    print("🚀" * 40)
    
    try:
        # 1. Sistema básico de inventário
        print("\n🔄 Executando exemplo de sistema de inventário...")
        inventory_result = exemplo_sistema_inventario()
        
        # 2. Simulação de leitor
        print("\n🔄 Executando exemplo de simulação de leitor...")
        simulation_result = exemplo_simulacao_leitor()
        
        # 3. Serviço de API
        print("\n🔄 Executando exemplo de serviço de API...")
        api_result = exemplo_api_service()
        
        # 4. Processamento de alta performance
        print("\n🔄 Executando exemplo de alta performance...")
        performance_result = exemplo_processamento_alta_performance()
        
        # 5. Integração completa
        print("\n🔄 Executando integração completa...")
        integration_result = exemplo_integracao_completa()
        
        # 6. Casos de uso reais
        print("\n🔄 Executando casos de uso reais...")
        use_cases_result = exemplo_casos_uso_reais()
        
        # 7. Monitoramento em tempo real
        print("\n🔄 Executando monitoramento em tempo real...")
        monitoring_result = exemplo_monitoramento_tempo_real()
        
        # 8. Análise avançada
        print("\n🔄 Executando análise avançada...")
        analysis_result = exemplo_analise_avancada()
        
        # Resumo final
        print("\n" + "🎉" * 80)
        print("🎯 TODOS OS EXEMPLOS DE INTEGRAÇÃO EXECUTADOS COM SUCESSO!")
        print("🎉" * 80)
        
        print(f"\n📊 Resumo dos Resultados:")
        print(f"   ✅ Sistema de inventário: Funcional")
        print(f"   ✅ Simulação de leitor: {len(simulation_result)} eventos gerados")
        print(f"   ✅ Serviço de API: Endpoints funcionais")
        print(f"   ✅ Alta performance: {performance_result['statistics']['tids_per_second']:.1f} TIDs/s")
        print(f"   ✅ Integração completa: Pipeline funcional")
        print(f"   ✅ Casos de uso reais: 3 indústrias demonstradas")
        print(f"   ✅ Monitoramento: {len(monitoring_result['alerts'])} alertas gerados")
        print(f"   ✅ Análise avançada: {analysis_result['analytics']['total_events']} eventos analisados")
        
        print(f"\n🎓 Estes exemplos demonstram como integrar o RFID Tag TID Parser em:")
        print(f"   🏭 Sistemas de inventário empresariais")
        print(f"   📡 Aplicações de leitura RFID em tempo real")
        print(f"   🌐 APIs REST e microserviços")
        print(f"   ⚡ Processamento de alta performance")
        print(f"   📊 Sistemas de análise e relatórios")
        print(f"   🔔 Monitoramento e alertas")
        print(f"   📈 Análises estatísticas avançadas")
        
        print(f"\n📚 Para implementação em produção, considere:")
        print(f"   🔒 Adicionar autenticação e autorização")
        print(f"   🛡️ Implementar validação de entrada robusta")
        print(f"   📊 Adicionar logging e monitoramento")
        print(f"   🔄 Implementar tratamento de erros e retry")
        print(f"   💾 Configurar backup e recovery de dados")
        print(f"   📈 Implementar métricas e alertas operacionais")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erro durante execução dos exemplos: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    """
    Execute este arquivo para ver todos os exemplos de integração em ação.
    
    Uso:
        python examples/integration_example.py
    """
    success = main()
    exit(0 if success else 1)