# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
e este projeto segue [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-07-04

### Adicionado
- Implementação inicial do `TagTidParser`
- Suporte para tags Impinj (Monza R6, M730, M770, M830/M850, Monza 4/5 Series)
- Suporte para tags NXP (UCODE 7, 8, 9)
- Extração de serial de 40 bits em formato hexadecimal e decimal
- Identificação automática de fabricante e modelo
- Funções de conveniência `parse_tid()` e `get_serial_from_tid()`
- Tratamento de erros com exceções customizadas
- Documentação completa com exemplos
- Testes unitários abrangentes
- Configuração para instalação via pip

### Características
- Sem dependências externas
- Compatível com Python 3.6+
- API simples e intuitiva
- Código baseado na implementação C# original
- Estrutura de projeto profissional