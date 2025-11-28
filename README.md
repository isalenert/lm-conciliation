<p align="center">
  <img src="https://img.shields.io/badge/Status-Em%20Produção-brightgreen" alt="Status">
  <img src="https://img.shields.io/badge/Versão-1.0.0-blue" alt="Versão">
  <img src="https://img.shields.io/badge/Licença-MIT-yellow" alt="Licença">
</p>

<h1 align="center">💰 LM Conciliation</h1>

<p align="center">
  <strong>Sistema de Conciliação Bancária Automatizada</strong>
</p>

<p align="center">
  Plataforma inteligente para conciliar extratos bancários com registros internos de forma rápida, precisa e fácil de usar.
</p>

<p align="center">
  <a href="https://d1tbkb02om326z.cloudfront.net">🌐 Acessar Aplicação</a> •
  <a href="https://lm-conciliation.duckdns.org/docs">📚 API Docs</a> •
  <a href="../../wiki">📖 Wiki</a>
</p>

---

## 📋 Índice

- [Sobre o Projeto](#-sobre-o-projeto)
- [Funcionalidades](#-funcionalidades)
- [Demonstração](#-demonstração)
- [Tecnologias](#-tecnologias)
- [Arquitetura](#-arquitetura)
- [Instalação Local](#-instalação-local)
- [Variáveis de Ambiente](#-variáveis-de-ambiente)
- [Testes](#-testes)
- [Deploy](#-deploy)
- [Documentação](#-documentação)
- [Autora](#-autora)

---

## 🎯 Sobre o Projeto

O **LM Conciliation** é um sistema web desenvolvido como Trabalho de Conclusão de Curso (TCC) que automatiza o processo de conciliação bancária. O sistema permite que analistas financeiros comparem extratos bancários com relatórios internos de forma inteligente, utilizando algoritmos de matching fuzzy para identificar correspondências mesmo quando há pequenas diferenças nos dados.

### O Problema

A conciliação bancária manual é um processo tedioso, demorado e propenso a erros. Analistas financeiros gastam horas comparando planilhas linha a linha, tentando identificar quais transações do banco correspondem aos registros internos da empresa.

### A Solução

O LM Conciliation automatiza esse processo através de:
- **Upload simples** de arquivos CSV ou PDF
- **Mapeamento visual** de colunas
- **Algoritmo inteligente** que considera tolerâncias de data, valor e similaridade de descrição
- **Dashboard interativo** com resultados categorizados
- **Conciliação manual** para casos especiais

---

## ✨ Funcionalidades

| Funcionalidade | Descrição |
|----------------|-----------|
| 🔐 **Autenticação** | Registro, login e recuperação de senha com JWT |
| 📤 **Upload de Arquivos** | Suporte a CSV e PDF |
| 🗂️ **Mapeamento de Colunas** | Interface visual para mapear Data, Valor e Descrição |
| ⚡ **Conciliação Automática** | Algoritmo fuzzy matching com tolerâncias configuráveis |
| 📊 **Dashboard** | Gráficos interativos e estatísticas detalhadas |
| ✋ **Conciliação Manual** | Interface para resolver pendências manualmente |
| 📜 **Histórico** | Consulta de conciliações anteriores |
| ⚙️ **Configurações** | Personalização de tolerâncias padrão |

---

## 🖥️ Demonstração

### Fluxo Principal

```mermaid
flowchart LR
    subgraph Upload["1️⃣ Upload"]
        A1["📤 Upload<br/>Arquivos"]
    end

    subgraph Preview["2️⃣ Preview"]
        B1["👁️ Preview<br/>Dados"]
    end

    subgraph Mapeamento["3️⃣ Mapeamento"]
        C1["🗂️ Mapear<br/>Colunas"]
    end

    subgraph Processamento["4️⃣ Processamento"]
        D1["⚡ Processar<br/>Matching"]
    end

    subgraph Resultado["5️⃣ Resultado"]
        E1["📊 Dashboard<br/>Resultados"]
    end

    A1 --> B1 --> C1 --> D1 --> E1

    style A1 fill:#e1f5fe,stroke:#01579b
    style B1 fill:#e8f5e9,stroke:#1b5e20
    style C1 fill:#fff3e0,stroke:#e65100
    style D1 fill:#fce4ec,stroke:#880e4f
    style E1 fill:#f3e5f5,stroke:#4a148c
```

> 🔗 **Acesse a aplicação:** [https://d1tbkb02om326z.cloudfront.net](https://d1tbkb02om326z.cloudfront.net)

---

## 🛠️ Tecnologias

### Backend
| Tecnologia | Versão | Descrição |
|------------|--------|-----------|
| Python | 3.10+ | Linguagem principal |
| FastAPI | 0.100+ | Framework web assíncrono |
| PostgreSQL | 15+ | Banco de dados relacional |
| SQLAlchemy | 2.0+ | ORM para Python |
| PyPDF2 | 3.0+ | Extração de texto de PDFs |
| Fuzzywuzzy | 0.18+ | Algoritmo de fuzzy matching |
| Pandas | 2.0+ | Manipulação de dados |
| Pytest | 7.0+ | Framework de testes |

### Frontend
| Tecnologia | Versão | Descrição |
|------------|--------|-----------|
| React | 18+ | Biblioteca de UI |
| Vite | 5+ | Build tool |
| TailwindCSS | 3+ | Framework CSS |
| React Router | 6+ | Roteamento SPA |
| Recharts | 2+ | Gráficos interativos |
| Axios | 1+ | Cliente HTTP |

### DevOps & Infraestrutura
| Tecnologia | Descrição |
|------------|-----------|
| Docker | Containerização |
| GitHub Actions | CI/CD Pipeline |
| AWS EC2 | Hospedagem do backend |
| AWS S3 | Hospedagem do frontend |
| AWS CloudFront | CDN com HTTPS |
| Nginx | Proxy reverso |
| Let's Encrypt | Certificado SSL |

---

## 🏗️ Arquitetura

O sistema segue uma arquitetura de **três camadas** (3-tier):

```mermaid
flowchart TB
    Usuario["👤 Usuário"]

    subgraph AWS["☁️ Amazon Web Services"]
        subgraph Frontend["Frontend"]
            SPA["🖥️ React SPA<br/>S3 + CloudFront"]
        end

        subgraph Backend["Backend"]
            API["⚙️ FastAPI<br/>EC2 + Nginx"]
        end

        subgraph Database["Database"]
            DB[("🗄️ PostgreSQL")]
        end
    end

    Usuario -->|"HTTPS"| SPA
    SPA -->|"REST API"| API
    API -->|"SQL"| DB

    style SPA fill:#438dd5,stroke:#2e6295,color:#fff
    style API fill:#438dd5,stroke:#2e6295,color:#fff
    style DB fill:#438dd5,stroke:#2e6295,color:#fff
```

> 📖 Para diagramas C4 detalhados, consulte a [Wiki do projeto](../../wiki/Arquitetura).

---

## 🚀 Instalação Local

### Pré-requisitos

- Python 3.10+
- Node.js 18+
- PostgreSQL 15+
- Git

### 1. Clonar o Repositório

```bash
git clone https://github.com/seu-usuario/lm-conciliation.git
cd lm-conciliation
```

### 2. Configurar o Backend

```bash
cd backend

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou: venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Edite o arquivo .env com suas configurações

# Criar banco de dados
createdb lm_conciliation

# Executar migrations
alembic upgrade head

# Iniciar servidor de desenvolvimento
uvicorn app.main:app --reload --port 8000
```

### 3. Configurar o Frontend

```bash
cd frontend

# Instalar dependências
npm install

# Configurar variáveis de ambiente
cp .env.example .env.local
# Edite o arquivo .env.local

# Iniciar servidor de desenvolvimento
npm run dev
```

### 4. Acessar a Aplicação

- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **Swagger Docs:** http://localhost:8000/docs

---

## 🔐 Variáveis de Ambiente

### Backend (.env)

```env
# Banco de Dados
DATABASE_URL=postgresql://user:password@localhost:5432/lm_conciliation

# JWT
SECRET_KEY=sua-chave-secreta-muito-segura
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Email (SendGrid)
SENDGRID_API_KEY=SG.xxx
SENDER_EMAIL=noreply@lmconciliation.com
SENDER_NAME=LM Conciliation

# URLs
FRONTEND_URL=http://localhost:5173
BACKEND_URL=http://localhost:8000
```

### Frontend (.env.local)

```env
VITE_API_URL=http://localhost:8000
```

---

## 🧪 Testes

### Backend

```bash
cd backend

# Executar todos os testes
pytest

# Com cobertura
pytest --cov=app --cov-report=html

# Apenas testes unitários
pytest tests/unit/

# Apenas testes de integração
pytest tests/integration/
```

### Frontend

```bash
cd frontend

# Executar testes
npm run test

# Com cobertura
npm run test:coverage
```

### Métricas de Qualidade

| Métrica | Meta | Atual |
|---------|------|-------|
| Cobertura Backend | >75% | ✅ |
| Cobertura Frontend | >25% | ✅ |
| SonarCloud Quality Gate | Pass | ✅ |

---

## 🌐 Deploy

O deploy é automatizado via **GitHub Actions**. A cada push na branch `main`:

```mermaid
flowchart LR
    Push["📤 Push"] --> Tests["🧪 Testes"]
    Tests --> Quality["🔍 SonarCloud"]
    Quality --> Build["🔨 Build"]
    Build --> DeployBE["🚀 Backend"]
    Build --> DeployFE["🚀 Frontend"]
    DeployFE --> Cache["🔄 Invalidate"]

    style Push fill:#24292e,color:#fff
    style Tests fill:#3572A5,color:#fff
    style Quality fill:#f3702a,color:#fff
    style DeployBE fill:#ff9900,color:#fff
    style DeployFE fill:#569a31,color:#fff
```

### Deploy Manual

Consulte as [Instruções de Deploy](../../wiki/Deploy) na Wiki.

---

## 📚 Documentação

| Documento | Descrição |
|-----------|-----------|
| [Wiki](../../wiki) | Documentação completa do projeto |
| [Requisitos Funcionais](../../wiki/Requisitos-Funcionais) | Lista detalhada de RF e RNF |
| [Casos de Uso](../../wiki/Casos-de-Uso) | Descrição dos casos de uso |
| [Arquitetura](../../wiki/Arquitetura) | Diagramas C4 e decisões técnicas |
| [Instruções de Deploy](../../wiki/Deploy) | Guia passo a passo de deploy |
| [API Reference](https://lm-conciliation.duckdns.org/docs) | Documentação Swagger da API |

---

## 👩‍💻 Autora

**Isabela Lenert**

- GitHub: [@isalenert](https://github.com/isalenert)
- Email: isalenert@icloud.com

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

