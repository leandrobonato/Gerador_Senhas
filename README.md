<h1 align="center">🔐 Gerador de Senhas</h1>

<p align="center">
  <strong>Aplicação desktop em Python para gerar senhas fortes com um único clique.</strong><br>
  Interface gráfica moderna em Tkinter, cópia automática para a área de transferência
  e medidor de força em tempo real.
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white">
  <img alt="Tkinter" src="https://img.shields.io/badge/GUI-Tkinter-FF6F00">
  <img alt="Licença" src="https://img.shields.io/badge/Licen%C3%A7a-MIT-green">
  <img alt="Testes" src="https://img.shields.io/badge/Testes-11%20passando-brightgreen">
</p>

---

## ✨ Visão geral

O **Gerador de Senhas** é um utilitário desktop pensado para o dia a dia: você abre,
clica em **Gerar senha** e a senha já está copiada, pronta para colar onde precisar.
Por trás da interface simples há uma geração **criptograficamente segura** (módulo
`secrets` do Python) e um medidor de força baseado em entropia real.

Este projeto faz parte do meu **portfólio comercial** e demonstra boas práticas de
arquitetura, separação de responsabilidades, testes automatizados e documentação.

## 🎯 Principais recursos

| Recurso | Descrição |
|---|---|
| ⚡ **Um clique** | Gera e copia a senha na mesma ação. |
| 🖥️ **Interface visual** | Janela moderna feita com Tkinter, tema escuro. |
| 📋 **Cópia automática** | Envia a senha para a área de transferência via `pyperclip`. |
| 🔒 **Aleatoriedade segura** | Usa `secrets` (CSPRNG), não o `random` comum. |
| 🎚️ **Personalização** | Comprimento de 4 a 128 e escolha dos tipos de caractere. |
| 📊 **Medidor de força** | Barra e rótulo (Fraca → Excelente) com entropia em bits. |
| 🚫 **Sem ambíguos** | Opção para excluir caracteres confundíveis (`0/O`, `1/l/I`…). |
| ⌨️ **Atalhos** | `Enter`/`Espaço` gera, `Ctrl+C` copia, `Esc` fecha. |

## 🖼️ Interface

```
┌─────────────────────────────────────────┐
│  Gerador de Senhas                        │
│  Senhas fortes e aleatórias...            │
│  ┌─────────────────────────────────────┐ │
│  │        IOw<%YqZ+LV$6c@              │ │
│  └─────────────────────────────────────┘ │
│  ████████████████████████░░░░  Excelente  │
│  Força: Excelente        103 bits         │
│  Comprimento                        16    │
│  ●────────────────────────────────────    │
│  ☑ Minúsculas   ☑ Maiúsculas              │
│  ☑ Números      ☑ Símbolos                │
│  ☐ Evitar caracteres ambíguos             │
│  [   Gerar senha   ] [   Copiar   ]       │
│  Senha gerada e copiada ✓                 │
└─────────────────────────────────────────┘
```

## 🚀 Como executar

### Pré-requisitos
- **Python 3.10 ou superior** ([download](https://www.python.org/downloads/))
- Tkinter já vem com a instalação padrão do Python no Windows e no macOS.
  No Linux, se necessário: `sudo apt install python3-tk`.

### Instalação
```bash
# 1. Clone ou baixe este repositório
git clone <url-do-repositorio>
cd Gerador_Senhas

# 2. (Opcional) crie um ambiente virtual
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# 3. Instale as dependências
pip install -r requirements.txt
```

### Executando
```bash
python main.py
```
ou, como módulo:
```bash
python -m gerador_senhas
```

## 🧪 Testes

A lógica de geração é totalmente testada e independe da interface gráfica:

```bash
python -m unittest discover -s tests -v
```

## 🛠️ Tecnologias e bibliotecas

- **[Python](https://www.python.org/)** — linguagem principal.
- **[Tkinter](https://docs.python.org/3/library/tkinter.html)** — interface gráfica (biblioteca padrão).
- **[pyperclip](https://pypi.org/project/pyperclip/)** — cópia para a área de transferência.
- **[secrets](https://docs.python.org/3/library/secrets.html)** — geração aleatória segura (biblioteca padrão).

## 📂 Estrutura do projeto

```
Gerador_Senhas/
├── gerador_senhas/
│   ├── __init__.py        # metadados do pacote
│   ├── __main__.py        # permite "python -m gerador_senhas"
│   ├── gerador.py         # lógica: geração, entropia e força (sem GUI)
│   └── interface.py       # interface gráfica em Tkinter
├── tests/
│   └── test_gerador.py    # testes automatizados da lógica
├── docs/
│   └── DOCUMENTACAO.md    # documentação técnica e de uso
├── main.py                # atalho de execução
├── requirements.txt       # dependências
└── README.md
```

> A **lógica** (`gerador.py`) é separada da **interface** (`interface.py`).
> Isso deixa o núcleo testável e reutilizável em uma futura versão CLI ou web.

## 🔐 Nota de segurança

As senhas são geradas localmente com o gerador criptográfico do sistema operacional
(`secrets`). **Nada é enviado pela internet** e nenhuma senha é armazenada em disco.
Uma senha de 16 caracteres com todos os tipos habilitados atinge ~103 bits de
entropia — muito acima do necessário para resistir a ataques offline.

## 📄 Licença

Distribuído sob a licença MIT. Consulte [`LICENSE`](LICENSE) para mais detalhes.

---

<p align="center">
  Desenvolvido por <strong>Leandro Miozzo Bonato</strong> · Projeto de portfólio
</p>
