# Documentação Técnica — Gerador de Senhas

Documentação de uso e de arquitetura da aplicação. Para uma visão rápida e
orientada a portfólio, veja o [README](../README.md).

---

## 1. Objetivo

Fornecer uma ferramenta desktop simples e segura para gerar senhas fortes,
com foco em três pilares:

1. **Facilidade** — gerar e copiar em um clique.
2. **Segurança** — aleatoriedade criptográfica e geração 100% local.
3. **Manutenibilidade** — lógica separada da interface e coberta por testes.

## 2. Requisitos

| Item | Versão / Observação |
|---|---|
| Python | 3.10 ou superior (uso de `str | None`, `list[str]`) |
| Tkinter | Incluso no Python (no Linux: `sudo apt install python3-tk`) |
| pyperclip | `>= 1.8.2` (opcional; há fallback com o clipboard do Tk) |

## 3. Instalação e execução

```bash
pip install -r requirements.txt
python main.py                 # ou: python -m gerador_senhas
```

## 4. Arquitetura

O projeto adota uma separação clara entre **núcleo** e **apresentação**:

```
┌────────────────────┐        ┌────────────────────┐
│   interface.py     │  usa   │    gerador.py      │
│   (Tkinter / GUI)  │ ─────► │  (lógica pura)     │
│                    │        │  sem dependência   │
│                    │        │  de Tkinter        │
└────────────────────┘        └────────────────────┘
```

- **`gerador.py`** não importa Tkinter. Pode ser usado em scripts, testes,
  numa CLI ou numa API web sem alterações.
- **`interface.py`** apenas lê as opções da tela, chama o núcleo e exibe o
  resultado. Não contém regras de geração.

Essa divisão é o que permite a suíte de testes rodar sem abrir janela alguma.

### 4.1 Fluxo de uma geração

```
Usuário clica "Gerar senha"
        │
        ▼
interface._ler_opcoes()  ──►  monta um objeto Opcoes
        │
        ▼
gerador.gerar_senha(opcoes)
        │  1. valida a configuração
        │  2. garante 1 caractere de cada grupo ativo
        │  3. completa o restante a partir do universo
        │  4. embaralha com Fisher-Yates seguro
        ▼
interface exibe a senha, calcula a força e copia
```

## 5. Referência da API (`gerador_senhas.gerador`)

### `Opcoes` (dataclass)
Representa as preferências de geração.

| Campo | Tipo | Padrão | Descrição |
|---|---|---|---|
| `comprimento` | `int` | `16` | Tamanho da senha (4 a 128). |
| `usar_minusculas` | `bool` | `True` | Inclui `a-z`. |
| `usar_maiusculas` | `bool` | `True` | Inclui `A-Z`. |
| `usar_digitos` | `bool` | `True` | Inclui `0-9`. |
| `usar_simbolos` | `bool` | `True` | Inclui `!@#$%&...`. |
| `evitar_ambiguos` | `bool` | `False` | Remove caracteres confundíveis. |

Métodos:
- `alfabetos() -> list[str]` — grupos de caracteres ativos (já filtrados).
- `validar() -> None` — levanta `ConfiguracaoInvalidaError` se a combinação
  for impossível.

### `gerar_senha(opcoes: Opcoes | None = None) -> str`
Gera a senha. Garante ao menos um caractere de cada grupo selecionado e
embaralha o resultado com uma fonte segura.

```python
from gerador_senhas.gerador import Opcoes, gerar_senha

gerar_senha()                              # 16 caracteres, todos os tipos
gerar_senha(Opcoes(comprimento=24))
gerar_senha(Opcoes(comprimento=8, usar_simbolos=False, evitar_ambiguos=True))
```

### `calcular_entropia(senha: str, opcoes: Opcoes) -> float`
Entropia em bits: `comprimento × log2(tamanho_do_alfabeto)`.

### `classificar_forca(entropia: float) -> tuple[str, float]`
Retorna um rótulo e um percentual (0 a 1) para a barra de força.

| Entropia (bits) | Rótulo |
|---|---|
| `< 40` | Fraca |
| `40 – 59` | Média |
| `60 – 79` | Forte |
| `>= 80` | Excelente |

### `ConfiguracaoInvalidaError`
Subclasse de `ValueError`. É lançada quando:
- nenhum tipo de caractere está selecionado;
- o comprimento está fora do intervalo de 4 a 128;
- o comprimento é menor que a quantidade de tipos selecionados.

## 6. Decisões de segurança

- **`secrets` em vez de `random`** — o módulo `random` é previsível e não deve
  ser usado para senhas. Todo sorteio (`secrets.choice`, `secrets.randbelow`)
  usa o gerador criptográfico do sistema operacional.
- **Embaralhamento próprio** — `random.shuffle` não é criptográfico, então o
  embaralhamento final usa Fisher-Yates alimentado por `secrets.randbelow`.
- **Garantia de composição** — ao forçar um caractere de cada grupo, evita-se
  o caso em que uma senha "com símbolos" acaba sem nenhum por acaso.
- **Tudo local** — nenhuma senha é enviada pela rede ou gravada em disco.

## 7. Interface e usabilidade

| Elemento | Comportamento |
|---|---|
| Botão **Gerar senha** | Gera e já copia. |
| Botão **Copiar** | Recopia a senha atual. |
| Clique no visor | Copia a senha exibida. |
| Controle deslizante | Ajusta o comprimento e regenera na hora. |
| Caixas de seleção | Alteram os tipos e regeneram na hora. |
| Barra de força | Muda de cor conforme a entropia. |

### Atalhos de teclado
| Tecla | Ação |
|---|---|
| `Enter` / `Espaço` | Gerar nova senha |
| `Ctrl + C` | Copiar |
| `Esc` | Fechar a aplicação |

### Cópia para a área de transferência
Primeiro tenta o `pyperclip`. Se ele não estiver disponível ou não encontrar um
backend de clipboard no sistema, a aplicação recorre automaticamente ao
clipboard nativo do Tkinter (`clipboard_append`). O usuário sempre recebe uma
mensagem de status informando o que aconteceu.

## 8. Testes

Os testes cobrem a lógica de geração e classificação:

```bash
python -m unittest discover -s tests -v
```

Casos verificados:
- comprimento exato respeitado;
- presença de cada grupo selecionado;
- modo "somente dígitos";
- exclusão de caracteres ambíguos;
- unicidade entre gerações sucessivas;
- erros de configuração (sem tipos, comprimento inválido, comprimento < tipos);
- crescimento da entropia com o comprimento e faixas de classificação.

## 9. Solução de problemas

| Sintoma | Causa provável | Solução |
|---|---|---|
| `ModuleNotFoundError: tkinter` | Tkinter ausente (Linux) | `sudo apt install python3-tk` |
| `ModuleNotFoundError: pyperclip` | Dependência não instalada | `pip install -r requirements.txt` (ou use o fallback do Tk) |
| Cópia não funciona no Linux | Sem backend de clipboard | Instale `xclip` ou `xsel` |
| Janela não abre por SSH | Sem servidor gráfico | Execute em ambiente com display |

## 10. Extensões possíveis

- Versão CLI reutilizando `gerador.py` (o núcleo já está pronto para isso).
- Geração de frases-senha (palavras memorizáveis).
- Histórico temporário em memória com botão "gerar várias".
- Empacotamento com PyInstaller para distribuir um `.exe`.

---

_Autor: Leandro Miozzo Bonato — projeto de portfólio._
