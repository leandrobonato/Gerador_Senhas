"""Testes da lógica de geração (independentes da interface gráfica).

Execute com:  python -m pytest   ou   python -m unittest
"""

import unittest

from gerador_senhas.gerador import (
    AMBIGUOS,
    DIGITOS,
    MAIUSCULAS,
    MINUSCULAS,
    SIMBOLOS,
    ConfiguracaoInvalidaError,
    Opcoes,
    calcular_entropia,
    classificar_forca,
    gerar_senha,
)


class TestGerarSenha(unittest.TestCase):
    def test_comprimento_respeitado(self):
        for n in (4, 16, 64, 128):
            self.assertEqual(len(gerar_senha(Opcoes(comprimento=n))), n)

    def test_inclui_cada_grupo_selecionado(self):
        senha = gerar_senha(Opcoes(comprimento=32))
        self.assertTrue(any(c in MINUSCULAS for c in senha))
        self.assertTrue(any(c in MAIUSCULAS for c in senha))
        self.assertTrue(any(c in DIGITOS for c in senha))
        self.assertTrue(any(c in SIMBOLOS for c in senha))

    def test_apenas_digitos(self):
        senha = gerar_senha(
            Opcoes(
                comprimento=10,
                usar_minusculas=False,
                usar_maiusculas=False,
                usar_digitos=True,
                usar_simbolos=False,
            )
        )
        self.assertTrue(all(c in DIGITOS for c in senha))

    def test_evita_ambiguos(self):
        senha = gerar_senha(Opcoes(comprimento=128, evitar_ambiguos=True))
        self.assertFalse(any(c in AMBIGUOS for c in senha))

    def test_senhas_sao_diferentes(self):
        senhas = {gerar_senha(Opcoes(comprimento=24)) for _ in range(50)}
        self.assertGreater(len(senhas), 45)  # praticamente todas únicas

    def test_sem_tipos_selecionados_gera_erro(self):
        with self.assertRaises(ConfiguracaoInvalidaError):
            gerar_senha(
                Opcoes(
                    usar_minusculas=False,
                    usar_maiusculas=False,
                    usar_digitos=False,
                    usar_simbolos=False,
                )
            )

    def test_comprimento_fora_do_intervalo(self):
        with self.assertRaises(ConfiguracaoInvalidaError):
            gerar_senha(Opcoes(comprimento=2))
        with self.assertRaises(ConfiguracaoInvalidaError):
            gerar_senha(Opcoes(comprimento=1000))

    def test_comprimento_menor_que_tipos(self):
        with self.assertRaises(ConfiguracaoInvalidaError):
            # 4 tipos selecionados, mas só 3 caracteres impossibilitam
            # incluir um de cada grupo.
            gerar_senha(Opcoes(comprimento=3))


class TestForca(unittest.TestCase):
    def test_entropia_cresce_com_comprimento(self):
        curta = gerar_senha(Opcoes(comprimento=8))
        longa = gerar_senha(Opcoes(comprimento=64))
        self.assertLess(
            calcular_entropia(curta, Opcoes(comprimento=8)),
            calcular_entropia(longa, Opcoes(comprimento=64)),
        )

    def test_classificacao(self):
        self.assertEqual(classificar_forca(20)[0], "Fraca")
        self.assertEqual(classificar_forca(50)[0], "Média")
        self.assertEqual(classificar_forca(70)[0], "Forte")
        self.assertEqual(classificar_forca(120)[0], "Excelente")

    def test_percentual_limitado(self):
        _, pct = classificar_forca(500)
        self.assertLessEqual(pct, 1.0)


if __name__ == "__main__":
    unittest.main()
