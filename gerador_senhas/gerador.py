"""Lógica de geração e avaliação de senhas.

Este módulo não depende de Tkinter e pode ser usado isoladamente
(scripts, testes ou uma futura versão web/CLI).
"""

from __future__ import annotations

import secrets
import string
from dataclasses import dataclass

MINUSCULAS = string.ascii_lowercase
MAIUSCULAS = string.ascii_uppercase
DIGITOS = string.digits
SIMBOLOS = "!@#$%&*()-_=+[]{};:,.<>?/"

# Caracteres que se confundem visualmente em fontes comuns.
AMBIGUOS = "0O1lI|`'\"" + "5S2Z8B"

COMPRIMENTO_MINIMO = 4
COMPRIMENTO_MAXIMO = 128
COMPRIMENTO_PADRAO = 16


class ConfiguracaoInvalidaError(ValueError):
    """Erro para combinações de opções que não permitem gerar uma senha."""


@dataclass(frozen=True)
class Opcoes:
    """Preferências de geração escolhidas pelo usuário."""

    comprimento: int = COMPRIMENTO_PADRAO
    usar_minusculas: bool = True
    usar_maiusculas: bool = True
    usar_digitos: bool = True
    usar_simbolos: bool = True
    evitar_ambiguos: bool = False

    def alfabetos(self) -> list[str]:
        """Devolve os grupos de caracteres ativos, já filtrados."""
        grupos = [
            (self.usar_minusculas, MINUSCULAS),
            (self.usar_maiusculas, MAIUSCULAS),
            (self.usar_digitos, DIGITOS),
            (self.usar_simbolos, SIMBOLOS),
        ]
        ativos = []
        for ativo, grupo in grupos:
            if not ativo:
                continue
            if self.evitar_ambiguos:
                grupo = "".join(c for c in grupo if c not in AMBIGUOS)
            if grupo:
                ativos.append(grupo)
        return ativos

    def validar(self) -> None:
        if not COMPRIMENTO_MINIMO <= self.comprimento <= COMPRIMENTO_MAXIMO:
            raise ConfiguracaoInvalidaError(
                f"O comprimento deve estar entre {COMPRIMENTO_MINIMO} e "
                f"{COMPRIMENTO_MAXIMO} caracteres."
            )
        alfabetos = self.alfabetos()
        if not alfabetos:
            raise ConfiguracaoInvalidaError(
                "Selecione pelo menos um tipo de caractere."
            )
        if len(alfabetos) > self.comprimento:
            raise ConfiguracaoInvalidaError(
                "O comprimento é menor que a quantidade de tipos de caractere "
                "selecionados."
            )


def gerar_senha(opcoes: Opcoes | None = None) -> str:
    """Gera uma senha aleatória usando `secrets` (CSPRNG do sistema).

    Garante ao menos um caractere de cada grupo selecionado, o que evita
    resultados como uma senha "com símbolos" que por acaso não tem nenhum.
    """
    opcoes = opcoes or Opcoes()
    opcoes.validar()

    alfabetos = opcoes.alfabetos()
    universo = "".join(alfabetos)

    caracteres = [secrets.choice(grupo) for grupo in alfabetos]
    restante = opcoes.comprimento - len(caracteres)
    caracteres += [secrets.choice(universo) for _ in range(restante)]

    # Sem o embaralhamento, os primeiros caracteres seguiriam sempre a
    # mesma ordem de grupos e reduziriam a entropia real.
    _embaralhar(caracteres)
    return "".join(caracteres)


def _embaralhar(itens: list[str]) -> None:
    """Fisher-Yates com fonte segura (random.shuffle não é criptográfico)."""
    for i in range(len(itens) - 1, 0, -1):
        j = secrets.randbelow(i + 1)
        itens[i], itens[j] = itens[j], itens[i]


def calcular_entropia(senha: str, opcoes: Opcoes) -> float:
    """Entropia em bits, assumindo geração uniforme sobre o alfabeto ativo."""
    universo = len("".join(opcoes.alfabetos()))
    if universo <= 1 or not senha:
        return 0.0
    import math

    return len(senha) * math.log2(universo)


def classificar_forca(entropia: float) -> tuple[str, float]:
    """Traduz a entropia em um rótulo e um percentual de 0 a 1.

    Os limites seguem a recomendação prática de que ~80 bits já resistem a
    ataques offline com hardware atual.
    """
    if entropia < 40:
        rotulo = "Fraca"
    elif entropia < 60:
        rotulo = "Média"
    elif entropia < 80:
        rotulo = "Forte"
    else:
        rotulo = "Excelente"
    return rotulo, min(entropia / 100, 1.0)
