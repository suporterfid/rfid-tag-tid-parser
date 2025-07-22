#!/usr/bin/env python3
"""
Patch de correção para os testes unitários.
Adicione este conteúdo ao arquivo tests/test_tag_tid_parser.py
"""

import unittest
import logging
from rfid_tag_parser import TagTidParser, parse_tid, get_serial_from_tid
from rfid_tag_parser.exceptions import InvalidTidError, TagTidParserError  # ← ADICIONAR ESTA IMPORTAÇÃO
from rfid_tag_parser.tag_tid_parser import validate_tid


logger = logging.getLogger(__name__)


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
                logger.info(f"valid_init: {name} -> {parser._tid_hex}")
    
    def test_invalid_tid_initialization(self):
        """Testa inicialização com TIDs inválidos."""
        # Casos que devem gerar InvalidTidError (TIDs vazios/None)
        empty_tids = ["", "   ", None]
        
        for tid in empty_tids:
            with self.subTest(tid=tid):
                with self.assertRaises(InvalidTidError):  # ← MUDANÇA AQUI
                    TagTidParser(tid)
                logger.info(f"invalid_init_empty: {tid}")
        
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
                logger.info(f"invalid_init_format: {tid}")
    
    def test_serial_extraction_hex(self):
        """Testa extração de serial em hexadecimal."""
        parser = TagTidParser(self.valid_tids["impinj_monza_r6"])
        serial = parser.get_40bit_serial_hex()
        self.assertEqual(len(serial), 10)  # 40 bits = 10 caracteres hex
        self.assertTrue(all(c in '0123456789ABCDEF' for c in serial))
        logger.info(f"serial_hex: {serial}")
    
    def test_serial_extraction_decimal(self):
        """Testa extração de serial em decimal."""
        parser = TagTidParser(self.valid_tids["impinj_monza_r6"])
        serial_hex = parser.get_40bit_serial_hex()
        serial_dec = parser.get_40bit_serial_decimal()

        # Verifica se a conversão está correta
        self.assertEqual(serial_dec, int(serial_hex, 16))
        logger.info(f"serial_dec: {serial_dec} serial_hex: {serial_hex}")
    
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
                logger.info(
                    f"impinj_detection: {name} -> impinj={parser._is_impinj_tid()} nxp={parser._is_nxp_ucode9_tid()}"
                )
    
    def test_nxp_detection(self):
        """Testa detecção de tags NXP."""
        parser = TagTidParser(self.valid_tids["nxp_ucode9"])
        self.assertTrue(parser._is_nxp_ucode9_tid())
        self.assertFalse(parser._is_impinj_tid())
        logger.info(
            f"nxp_detection: nxp={parser._is_nxp_ucode9_tid()} impinj={parser._is_impinj_tid()}"
        )
    
    def test_model_number_extraction(self):
        """Testa extração do número do modelo."""
        parser = TagTidParser(self.valid_tids["impinj_monza_r6"])
        model_number = parser.get_tag_model_number()
        self.assertEqual(len(model_number), 3)  # 3 caracteres hex
        self.assertTrue(all(c in '0123456789ABCDEF' for c in model_number))
        logger.info(f"model_number: {model_number}")
    
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
                logger.info(f"vendor_ident: {name} -> {vendor}")
    
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
        logger.info(f"get_tid_info: {info}")
    
    def test_monza_series_id(self):
        """Testa extração do ID da série Monza."""
        parser = TagTidParser(self.valid_tids["impinj_monza_r6"])
        if parser._is_impinj_tid():
            series_id = parser.get_monza_series_id()
            self.assertIn(series_id, [0, 1, 2, 3])  # Valores válidos: 0-3
            logger.info(f"monza_series_id: {series_id}")


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
        logger.info(f"parse_tid: {self.tid} -> {info}")
    
    def test_get_serial_from_tid_hex(self):
        """Testa extração de serial em hexadecimal."""
        serial = get_serial_from_tid(self.tid, "hex")
        self.assertIsInstance(serial, str)
        self.assertEqual(len(serial), 10)
        logger.info(f"serial_from_tid_hex: {serial}")
    
    def test_get_serial_from_tid_decimal(self):
        """Testa extração de serial em decimal."""
        serial = get_serial_from_tid(self.tid, "decimal")
        self.assertIsInstance(serial, int)
        self.assertGreaterEqual(serial, 0)
        logger.info(f"serial_from_tid_decimal: {serial}")
    
    def test_get_serial_conversion_consistency(self):
        """Testa consistência entre conversões hex/decimal."""
        serial_hex = get_serial_from_tid(self.tid, "hex")
        serial_dec = get_serial_from_tid(self.tid, "decimal")

        self.assertEqual(serial_dec, int(serial_hex, 16))
        logger.info(f"serial_conversion: hex={serial_hex} dec={serial_dec}")


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
        logger.info(f"tid_spaces: {parser1.get_40bit_serial_hex()} tid_hyphens: {parser2.get_40bit_serial_hex()}")
    
    def test_lowercase_tid(self):
        """Testa TID em minúsculas."""
        tid_lower = "e2801190000000000000000a"
        parser = TagTidParser(tid_lower)
        self.assertIsNotNone(parser.get_40bit_serial_hex())
        logger.info(f"lowercase_tid: {parser.get_40bit_serial_hex()}")
    
    def test_unknown_vendor(self):
        """Testa comportamento com fabricante desconhecido."""
        # TID fictício que não está no dicionário de prefixos
        unknown_tid = "FF00AA00000000000000000A"
        parser = TagTidParser(unknown_tid)

        vendor = parser.get_vendor_from_tid()
        self.assertEqual(vendor, "Desconhecido")
        logger.info(f"unknown_vendor: {vendor}")
    
    def test_unknown_model(self):
        """Testa comportamento com modelo desconhecido."""
        # TID com prefixo conhecido mas modelo desconhecido
        unknown_model_tid = "E280FF00000000000000000A"
        parser = TagTidParser(unknown_model_tid)

        model_name = parser.get_tag_model_name()
        self.assertIn("Desconhecido", model_name)
        logger.info(f"unknown_model: {model_name}")


class Test38BitSerialValidation(unittest.TestCase):
    """Testes específicos para validação do serial de 38 bits."""

    def setUp(self):
        self.valid_r6 = "E280112000003FFFFFFFFF0A"
        self.no_xtid = "E200112000003FFFFFFFFF0A"
        self.non_r6 = "E2801190000000000000000A"

    def test_valid_38bit_serial_int(self):
        parser = TagTidParser(self.valid_r6)
        serial = parser.get_38bit_serial_int()
        self.assertEqual(serial, 0x3FFFFFFFFF)
        self.assertLess(serial, 1 << 38)
        logger.info(f"38bit_serial_int: {serial}")

    def test_valid_38bit_serial_bin(self):
        parser = TagTidParser(self.valid_r6)
        bserial = parser.get_38bit_serial_bin()
        self.assertEqual(len(bserial), 38)
        self.assertTrue(all(c in "01" for c in bserial))
        logger.info(f"38bit_serial_bin: {bserial}")

    def test_xtid_missing(self):
        parser = TagTidParser(self.no_xtid)
        with self.assertRaises(InvalidTidError):
            parser.get_38bit_serial_int()
        logger.info("38bit_xtid_missing raised InvalidTidError")

    def test_non_r6_series(self):
        parser = TagTidParser(self.non_r6)
        with self.assertRaises(TagTidParserError):
            parser.get_38bit_serial_int()
        logger.info("38bit_non_r6_series raised TagTidParserError")


class TestAdditionalTidExamples(unittest.TestCase):
    """Testes para TIDs extras fornecidos nos exemplos."""

    def test_parsing_and_serial_extraction(self):
        """Garante que o parser extrai corretamente o serial dos novos TIDs."""
        examples = {
            "E2801170200044DC7EC10B9B": "04DC7EC10B",
            "E28011B0200051F7E4810358": "11F7E48103",
            # Adicione novos exemplos de TID e serial abaixo
        }

        for tid, expected_serial in examples.items():
            with self.subTest(tid=tid):
                info = parse_tid(tid)
                self.assertEqual(info["serial_hex"], expected_serial)
                self.assertEqual(
                    get_serial_from_tid(tid, "hex"), expected_serial
                )
                self.assertEqual(
                    get_serial_from_tid(tid, "decimal"), int(expected_serial, 16)
                )
                logger.info(
                    f"additional_example: {tid} -> {info['serial_hex']}"
                )


class TestValidateTidFunction(unittest.TestCase):
    """Testa a função validate_tid com TIDs específicos."""

    def test_specific_tids_are_valid(self):
        """Verifica se os TIDs fornecidos são considerados válidos."""
        tids = [
            "E2801190000000000000000A",
            "E2801190000000000000000B",
        ]
        for tid in tids:
            with self.subTest(tid=tid):
                self.assertTrue(validate_tid(tid))
                logger.info(f"validate_tid: {tid} -> True")

if __name__ == "__main__":
    unittest.main()
