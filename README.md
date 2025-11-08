# 🏦 LM Conciliation - Sistema de Conciliação Bancária

[![Coverage](https://img.shields.io/badge/coverage-93%25-brightgreen.svg)](https://github.com/isalenert/lm-conciliation)
[![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Sistema automatizado de conciliação bancária desenvolvido como Trabalho de Conclusão de Curso (TCC) do curso de Engenharia de Software.

## 📋 Descrição

Sistema que realiza a conciliação automática entre extratos bancários (PDF/CSV) e registros de sistemas internos, identificando transações correspondentes, divergências e pendências usando algoritmos de fuzzy matching.

## ✨ Funcionalidades

- 📄 **Suporte a múltiplos formatos**: CSV e PDF
- 🔍 **Matching inteligente**: Algoritmo fuzzy com tolerâncias configuráveis
- 📊 **Dashboard visual**: Resultados com gráficos e estatísticas
- 🎯 **Alta precisão**: >90% de taxa de match em cenários reais
- 📝 **Histórico completo**: Registro de todas as conciliações
- 🔒 **Seguro**: Dados criptografados em trânsito e em repouso

## 🚀 Tecnologias

### Backend
- **Python 3.12** - Linguagem principal
- **FastAPI** - Framework web moderno e rápido
- **Pandas** - Processamento de dados
- **PyPDF2** - Extração de texto de PDFs
- **FuzzyWuzzy** - Matching de strings
- **PostgreSQL** - Banco de dados

### Frontend
- **React 18** - Biblioteca UI
- **Vite** - Build tool
- **TailwindCSS** - Estilização
- **Axios** - Requisições HTTP
- **React Router** - Navegação

### DevOps
- **Docker** - Containerização
- **GitHub Actions** - CI/CD
- **pytest** - Testes unitários

## 📦 Como Rodar Localmente

### Pré-requisitos
- Docker e Docker Compose instalados
- Git instalado

### Passos

1. **Clone o repositório:**
```bash
git clone https://github.com/isalenert/lm-conciliation.git
cd lm-conciliation
```

2. **Suba os containers:**
```bash
docker-compose up --build
```

3. **Acesse:**
- Frontend: http://localhost:80
- Backend API: http://localhost:8000
- Documentação da API: http://localhost:8000/docs

## 🧪 Testes

### Rodar todos os testes
```bash
cd backend
pytest tests/ -v
```

### Ver cobertura de código
```bash
pytest tests/ --cov=app --cov-report=html
open htmlcov/index.html
```

### Estatísticas
- ✅ **Cobertura**: 93%
- ✅ **Testes**: 7 testes unitários
- ✅ **TDD**: Desenvolvimento guiado por testes

## 📚 Documentação

- [Wiki do Projeto](https://github.com/isalenert/lm-conciliation/wiki)
- [Requisitos Funcionais](https://github.com/isalenert/lm-conciliation/wiki/Requisitos)
- [Arquitetura C4](https://github.com/isalenert/lm-conciliation/wiki/Arquitetura)
- [API Documentation](https://github.com/isalenert/lm-conciliation/wiki/API)

## 🏗️ Arquitetura
```
lm-conciliation/
├── backend/              # API Python/FastAPI
│   ├── app/
│   │   ├── core/        # Lógica de negócio
│   │   ├── api/         # Endpoints REST
│   │   └── database/    # Modelos e conexão
│   └── tests/           # Testes unitários
├── frontend/            # Interface React
│   └── src/
│       ├── components/  # Componentes reutilizáveis
│       ├── pages/       # Páginas da aplicação
│       └── services/    # Integração com API
├── infrastructure/      # IaC (Terraform)
└── .github/
    └── workflows/       # CI/CD
```

## 👩‍💻 Autora

**Isabela Lenert**  
Engenharia de Software  
📧 isalenert@icloud.com

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 🙏 Agradecimentos

- Orientador: DIOGO VINÍCIUS WINCK
- Instituição: Centro Universitário da Católica de Santa Catarina
- Período: 2025

---

⭐ **Desenvolvido com TDD, CI/CD e boas práticas de Engenharia de Software**
