#!/usr/bin/env python3
"""
Patch de correção para os testes unitários.
Adicione este conteúdo ao arquivo tests/test_tag_tid_parser.py
"""

import unittest
from rfid_tag_parser import TagTidParser, parse_tid, get_serial_from_tid
from rfid_tag_parser.exceptions import InvalidTidError  # ← ADICIONAR ESTA IMPORTAÇÃO


class TestTagTidParser(unittest.TestCase):
    """Testes para a classe TagTidParser."""
    
    def setUp(self):
        """Configura os dados de teste."""
        self.valid_tids = {
            "impinj_monza_r6": "E2801190000000000000000A",
            "impinj_m730": "E2801191000000000000000B", 
            "nxp_ucode9": "E2806915000000000000000C",
            "impinj_m770": "E28011A0000000000000000D",
        }
        
        self.invalid_tids = [
            "",                           # Vazio
            "INVALID",                    # Muito curto
            "E2801190000000000000000",    # 23 caracteres
            "E2801190000000000000000ABC", # 27 caracteres
            "G2801190000000000000000A",   # Caracteres inválidos
        ]
    
    def test_valid_tid_initialization(self):
        """Testa inicialização com TIDs válidos."""
        for name, tid in self.valid_tids.items():
            with self.subTest(name=name, tid=tid):
                parser = TagTidParser(tid)
                self.assertIsNotNone(parser)
    
    def test_invalid_tid_initialization(self):
        """Testa inicialização com TIDs inválidos."""
        # Casos que devem gerar InvalidTidError (TIDs vazios/None)
        empty_tids = ["", "   ", None]
        
        for tid in empty_tids:
            with self.subTest(tid=tid):
                with self.assertRaises(InvalidTidError):  # ← MUDANÇA AQUI
                    TagTidParser(tid)
        
        # Casos que devem gerar ValueError (formato incorreto)
        format_error_tids = [
            "INVALID",                    # Muito curto
            "E2801190000000000000000",    # 23 caracteres
            "E2801190000000000000000ABC", # 27 caracteres
            "G2801190000000000000000A",   # Caracteres inválidos
        ]
        
        for tid in format_error_tids:
            with self.subTest(tid=tid):
                with self.assertRaises(ValueError):  # ← MANTÉM ValueError PARA ESTES
                    TagTidParser(tid)
    
    def test_serial_extraction_hex(self):
        """Testa extração de serial em hexadecimal."""
        parser = TagTidParser(self.valid_tids["impinj_monza_r6"])
        serial = parser.get_40bit_serial_hex()
        self.assertEqual(len(serial), 10)  # 40 bits = 10 caracteres hex
        self.assertTrue(all(c in '0123456789ABCDEF' for c in serial))
    
    def test_serial_extraction_decimal(self):
        """Testa extração de serial em decimal."""
        parser = TagTidParser(self.valid_tids["impinj_monza_r6"])
        serial_hex = parser.get_40bit_serial_hex()
        serial_dec = parser.get_40bit_serial_decimal()
        
        # Verifica se a conversão está correta
        self.assertEqual(serial_dec, int(serial_hex, 16))
    
    def test_impinj_detection(self):
        """Testa detecção de tags Impinj."""
        impinj_tids = [
            "impinj_monza_r6",
            "impinj_m730", 
            "impinj_m770"
        ]
        
        for name in impinj_tids:
            with self.subTest(name=name):
                parser = TagTidParser(self.valid_tids[name])
                self.assertTrue(parser._is_impinj_tid())
                self.assertFalse(parser._is_nxp_ucode9_tid())
    
    def test_nxp_detection(self):
        """Testa detecção de tags NXP."""
        parser = TagTidParser(self.valid_tids["nxp_ucode9"])
        self.assertTrue(parser._is_nxp_ucode9_tid())
        self.assertFalse(parser._is_impinj_tid())
    
    def test_model_number_extraction(self):
        """Testa extração do número do modelo."""
        parser = TagTidParser(self.valid_tids["impinj_monza_r6"])
        model_number = parser.get_tag_model_number()
        self.assertEqual(len(model_number), 3)  # 3 caracteres hex
        self.assertTrue(all(c in '0123456789ABCDEF' for c in model_number))
    
    def test_vendor_identification(self):
        """Testa identificação do fabricante."""
        test_cases = [
            ("impinj_monza_r6", "Impinj"),
            ("nxp_ucode9", "NXP"),
        ]
        
        for name, expected_vendor in test_cases:
            with self.subTest(name=name):
                parser = TagTidParser(self.valid_tids[name])
                vendor = parser.get_vendor_from_tid()
                self.assertIn(expected_vendor, vendor)
    
    def test_get_tid_info(self):
        """Testa a função que retorna todas as informações."""
        parser = TagTidParser(self.valid_tids["impinj_monza_r6"])
        info = parser.get_tid_info()
        
        required_keys = [
            "tid", "vendor", "model_name", "model_number",
            "serial_hex", "serial_decimal", "is_impinj", "is_nxp_ucode9"
        ]
        
        for key in required_keys:
            self.assertIn(key, info)
    
    def test_monza_series_id(self):
        """Testa extração do ID da série Monza."""
        parser = TagTidParser(self.valid_tids["impinj_monza_r6"])
        if parser._is_impinj_tid():
            series_id = parser.get_monza_series_id()
            self.assertIn(series_id, [0, 1, 2, 3])  # Valores válidos: 0-3


class TestConvenienceFunctions(unittest.TestCase):
    """Testes para as funções de conveniência."""
    
    def setUp(self):
        """Configura os dados de teste."""
        self.tid = "E2801190000000000000000A"
    
    def test_parse_tid_function(self):
        """Testa a função parse_tid."""
        info = parse_tid(self.tid)
        self.assertIsInstance(info, dict)
        self.assertIn("tid", info)
        self.assertIn("vendor", info)
        self.assertIn("model_name", info)
    
    def test_get_serial_from_tid_hex(self):
        """Testa extração de serial em hexadecimal."""
        serial = get_serial_from_tid(self.tid, "hex")
        self.assertIsInstance(serial, str)
        self.assertEqual(len(serial), 10)
    
    def test_get_serial_from_tid_decimal(self):
        """Testa extração de serial em decimal."""
        serial = get_serial_from_tid(self.tid, "decimal")
        self.assertIsInstance(serial, int)
        self.assertGreaterEqual(serial, 0)
    
    def test_get_serial_conversion_consistency(self):
        """Testa consistência entre conversões hex/decimal."""
        serial_hex = get_serial_from_tid(self.tid, "hex")
        serial_dec = get_serial_from_tid(self.tid, "decimal")
        
        self.assertEqual(serial_dec, int(serial_hex, 16))


class TestEdgeCases(unittest.TestCase):
    """Testes para casos extremos."""
    
    def test_tid_with_spaces_and_hyphens(self):
        """Testa TID com espaços e hífens."""
        tid_with_spaces = "E2 80 11 90 00 00 00 00 00 00 00 0A"
        tid_with_hyphens = "E2-80-11-90-00-00-00-00-00-00-00-0A"
        
        parser1 = TagTidParser(tid_with_spaces)
        parser2 = TagTidParser(tid_with_hyphens)
        
        # Ambos devem funcionar
        self.assertIsNotNone(parser1.get_40bit_serial_hex())
        self.assertIsNotNone(parser2.get_40bit_serial_hex())
    
    def test_lowercase_tid(self):
        """Testa TID em minúsculas."""
        tid_lower = "e2801190000000000000000a"
        parser = TagTidParser(tid_lower)
        self.assertIsNotNone(parser.get_40bit_serial_hex())
    
    def test_unknown_vendor(self):
        """Testa comportamento com fabricante desconhecido."""
        # TID fictício que não está no dicionário de prefixos
        unknown_tid = "FF00AA00000000000000000A"
        parser = TagTidParser(unknown_tid)
        
        vendor = parser.get_vendor_from_tid()
        self.assertEqual(vendor, "Desconhecido")
    
    def test_unknown_model(self):
        """Testa comportamento com modelo desconhecido."""
        # TID com prefixo conhecido mas modelo desconhecido
        unknown_model_tid = "E280FF00000000000000000A"
        parser = TagTidParser(unknown_model_tid)
        
        model_name = parser.get_tag_model_name()
        self.assertIn("Desconhecido", model_name)


if __name__ == "__main__":
    unittest.main()
