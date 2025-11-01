# 🏦 LM Conciliation - Sistema de Conciliação Bancária

Sistema automatizado de conciliação bancária desenvolvido como Trabalho de Conclusão de Curso (TCC) do curso de Engenharia de Software.

## 📋 Descrição

Sistema que realiza a conciliação automática entre extratos bancários (PDF/CSV) e registros de sistemas internos, identificando transações correspondentes, divergências e pendências.

## 🚀 Tecnologias

- **Backend**: Python, FastAPI, Pandas, PyPDF2
- **Frontend**: React, Vite, TailwindCSS
- **Banco de Dados**: PostgreSQL
- **DevOps**: Docker, GitHub Actions, Terraform

## 📦 Como Rodar Localmente

### Pré-requisitos
- Docker e Docker Compose instalados
- Git instalado

### Passos

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/lm-conciliation.git
cd lm-conciliation
```

2. Suba os containers:
```bash
docker-compose up --build
```

3. Acesse:
- Frontend: http://localhost:80
- Backend API: http://localhost:8000
- Documentação da API: http://localhost:8000/docs

## 🧪 Testes
```bash
cd backend
pytest --cov=app
```

## 👩‍💻 Autora

Isabela Lenert - Engenharia de Software

## 📄 Licença

MIT License
