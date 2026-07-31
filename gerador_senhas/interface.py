"""Interface gráfica (Tkinter) do gerador de senhas."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

try:
    import pyperclip

    PYPERCLIP_DISPONIVEL = True
except ImportError:  # a app continua utilizável com o clipboard do Tk
    PYPERCLIP_DISPONIVEL = False

from gerador_senhas.gerador import (
    COMPRIMENTO_MAXIMO,
    COMPRIMENTO_MINIMO,
    COMPRIMENTO_PADRAO,
    ConfiguracaoInvalidaError,
    Opcoes,
    calcular_entropia,
    classificar_forca,
    gerar_senha,
)

# Paleta
FUNDO = "#12141c"
CARTAO = "#1c1f2b"
TEXTO = "#e8eaf2"
TEXTO_FRACO = "#8b90a6"
DESTAQUE = "#5b8cff"
DESTAQUE_HOVER = "#7aa2ff"
BORDA = "#2c3040"

CORES_FORCA = {
    "Fraca": "#ff5f57",
    "Média": "#ffbd2e",
    "Forte": "#4cd964",
    "Excelente": "#28c76f",
}

DURACAO_AVISO_MS = 2200


class GeradorSenhasApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()

        self.title("Gerador de Senhas")
        self.configure(bg=FUNDO)
        self.resizable(False, False)
        self.minsize(460, 0)

        self.var_senha = tk.StringVar(value="Clique em Gerar senha")
        self.var_comprimento = tk.IntVar(value=COMPRIMENTO_PADRAO)
        self.var_minusculas = tk.BooleanVar(value=True)
        self.var_maiusculas = tk.BooleanVar(value=True)
        self.var_digitos = tk.BooleanVar(value=True)
        self.var_simbolos = tk.BooleanVar(value=True)
        self.var_ambiguos = tk.BooleanVar(value=False)
        self.var_status = tk.StringVar(value="")

        self._id_aviso: str | None = None
        self._senha_atual = ""

        self._configurar_estilos()
        self._montar_layout()
        self._registrar_atalhos()

        self.gerar()
        self._centralizar()

    # ------------------------------------------------------------------ UI --

    def _configurar_estilos(self) -> None:
        estilo = ttk.Style(self)
        # "clam" é o único tema multiplataforma que aceita cores customizadas
        # nos widgets ttk sem ser sobrescrito pelo tema nativo do SO.
        estilo.theme_use("clam")

        estilo.configure("TFrame", background=FUNDO)
        estilo.configure("Cartao.TFrame", background=CARTAO)
        estilo.configure(
            "TLabel", background=FUNDO, foreground=TEXTO, font=("Segoe UI", 10)
        )
        estilo.configure(
            "Titulo.TLabel", font=("Segoe UI Semibold", 17), foreground=TEXTO
        )
        estilo.configure(
            "Subtitulo.TLabel", font=("Segoe UI", 9), foreground=TEXTO_FRACO
        )
        estilo.configure(
            "Fraco.TLabel", font=("Segoe UI", 9), foreground=TEXTO_FRACO
        )
        estilo.configure(
            "Status.TLabel", font=("Segoe UI", 9), foreground=CORES_FORCA["Forte"]
        )

        estilo.configure(
            "TCheckbutton",
            background=FUNDO,
            foreground=TEXTO,
            font=("Segoe UI", 10),
            focuscolor=FUNDO,
        )
        estilo.map(
            "TCheckbutton",
            background=[("active", FUNDO)],
            foreground=[("active", TEXTO)],
            indicatorcolor=[
                ("selected", DESTAQUE),
                ("!selected", BORDA),
            ],
        )

        estilo.configure(
            "TScale", background=FUNDO, troughcolor=BORDA, borderwidth=0
        )

        estilo.configure(
            "Primario.TButton",
            background=DESTAQUE,
            foreground="#ffffff",
            font=("Segoe UI Semibold", 11),
            borderwidth=0,
            focusthickness=0,
            padding=(16, 11),
        )
        estilo.map(
            "Primario.TButton",
            background=[("active", DESTAQUE_HOVER), ("pressed", DESTAQUE_HOVER)],
        )

        estilo.configure(
            "Secundario.TButton",
            background=CARTAO,
            foreground=TEXTO,
            font=("Segoe UI", 10),
            borderwidth=0,
            focusthickness=0,
            padding=(16, 11),
        )
        estilo.map("Secundario.TButton", background=[("active", BORDA)])

    def _montar_layout(self) -> None:
        raiz = ttk.Style()  # garante que o tema já foi aplicado
        del raiz

        container = ttk.Frame(self, padding=24)
        container.pack(fill="both", expand=True)

        ttk.Label(container, text="Gerador de Senhas", style="Titulo.TLabel").pack(
            anchor="w"
        )
        ttk.Label(
            container,
            text="Senhas fortes e aleatórias, copiadas com um clique.",
            style="Subtitulo.TLabel",
        ).pack(anchor="w", pady=(2, 18))

        self._montar_visor(container)
        self._montar_medidor(container)
        self._montar_comprimento(container)
        self._montar_opcoes(container)
        self._montar_acoes(container)

        ttk.Label(container, textvariable=self.var_status, style="Status.TLabel").pack(
            anchor="w", pady=(12, 0)
        )

    def _montar_visor(self, pai: ttk.Frame) -> None:
        cartao = tk.Frame(pai, bg=CARTAO, highlightbackground=BORDA, highlightthickness=1)
        cartao.pack(fill="x")

        self.entrada = tk.Entry(
            cartao,
            textvariable=self.var_senha,
            font=("Consolas", 14),
            bg=CARTAO,
            fg=TEXTO,
            readonlybackground=CARTAO,
            insertbackground=TEXTO,
            relief="flat",
            state="readonly",
            justify="center",
        )
        self.entrada.pack(fill="x", padx=14, pady=16)
        self.entrada.bind("<Button-1>", lambda _e: self.copiar())

    def _montar_medidor(self, pai: ttk.Frame) -> None:
        linha = ttk.Frame(pai)
        linha.pack(fill="x", pady=(12, 0))

        self.barra = tk.Canvas(
            linha, height=6, bg=BORDA, highlightthickness=0, bd=0
        )
        self.barra.pack(fill="x")
        self._preenchimento = self.barra.create_rectangle(
            0, 0, 0, 6, fill=CORES_FORCA["Forte"], width=0
        )
        # A largura só é conhecida após o gerenciador de layout calcular o
        # tamanho real, então redesenhamos a cada <Configure>.
        self.barra.bind("<Configure>", lambda _e: self._redesenhar_barra())

        rotulos = ttk.Frame(pai)
        rotulos.pack(fill="x", pady=(6, 0))
        self.rotulo_forca = ttk.Label(rotulos, text="", style="Fraco.TLabel")
        self.rotulo_forca.pack(side="left")
        self.rotulo_entropia = ttk.Label(rotulos, text="", style="Fraco.TLabel")
        self.rotulo_entropia.pack(side="right")

        self._percentual = 0.0
        self._cor_forca = CORES_FORCA["Forte"]

    def _montar_comprimento(self, pai: ttk.Frame) -> None:
        linha = ttk.Frame(pai)
        linha.pack(fill="x", pady=(20, 0))

        ttk.Label(linha, text="Comprimento").pack(side="left")
        self.rotulo_comprimento = ttk.Label(
            linha, text=str(COMPRIMENTO_PADRAO), style="TLabel"
        )
        self.rotulo_comprimento.pack(side="right")

        escala = ttk.Scale(
            pai,
            from_=COMPRIMENTO_MINIMO,
            to=COMPRIMENTO_MAXIMO,
            variable=self.var_comprimento,
            command=self._ao_mover_escala,
        )
        escala.pack(fill="x", pady=(6, 0))

    def _montar_opcoes(self, pai: ttk.Frame) -> None:
        grade = ttk.Frame(pai)
        grade.pack(fill="x", pady=(18, 0))
        grade.columnconfigure(0, weight=1)
        grade.columnconfigure(1, weight=1)

        opcoes = [
            ("Letras minúsculas (a-z)", self.var_minusculas),
            ("Letras maiúsculas (A-Z)", self.var_maiusculas),
            ("Números (0-9)", self.var_digitos),
            ("Símbolos (!@#$)", self.var_simbolos),
            ("Evitar caracteres ambíguos", self.var_ambiguos),
        ]
        for indice, (texto, variavel) in enumerate(opcoes):
            ttk.Checkbutton(
                grade,
                text=texto,
                variable=variavel,
                command=self.gerar,
            ).grid(row=indice // 2, column=indice % 2, sticky="w", pady=3)

    def _montar_acoes(self, pai: ttk.Frame) -> None:
        linha = ttk.Frame(pai)
        linha.pack(fill="x", pady=(22, 0))
        linha.columnconfigure(0, weight=2)
        linha.columnconfigure(1, weight=1)

        ttk.Button(
            linha, text="Gerar senha", style="Primario.TButton", command=self.gerar
        ).grid(row=0, column=0, sticky="ew", padx=(0, 8))
        ttk.Button(
            linha, text="Copiar", style="Secundario.TButton", command=self.copiar
        ).grid(row=0, column=1, sticky="ew")

    def _registrar_atalhos(self) -> None:
        self.bind("<Return>", lambda _e: self.gerar())
        self.bind("<space>", lambda _e: self.gerar())
        self.bind("<Control-c>", lambda _e: self.copiar())
        self.bind("<Escape>", lambda _e: self.destroy())

    def _centralizar(self) -> None:
        self.update_idletasks()
        largura = self.winfo_width()
        altura = self.winfo_height()
        x = (self.winfo_screenwidth() - largura) // 2
        y = (self.winfo_screenheight() - altura) // 3
        self.geometry(f"+{x}+{y}")

    # ------------------------------------------------------------- Ações --

    def gerar(self) -> None:
        """Gera uma nova senha e já a copia — o fluxo de 1 clique."""
        opcoes = self._ler_opcoes()
        try:
            senha = gerar_senha(opcoes)
        except ConfiguracaoInvalidaError as erro:
            self._senha_atual = ""
            self.var_senha.set("—")
            self._atualizar_medidor(0.0, "Fraca")
            self._avisar(str(erro), erro=True)
            return

        self._senha_atual = senha
        self.var_senha.set(senha)

        entropia = calcular_entropia(senha, opcoes)
        rotulo, percentual = classificar_forca(entropia)
        self._atualizar_medidor(percentual, rotulo, entropia)

        if self._copiar_para_area_de_transferencia(senha):
            self._avisar("Senha gerada e copiada para a área de transferência.")
        else:
            self._avisar("Senha gerada. Use o botão Copiar.", erro=True)

    def copiar(self) -> None:
        if not self._senha_atual:
            self._avisar("Gere uma senha primeiro.", erro=True)
            return
        if self._copiar_para_area_de_transferencia(self._senha_atual):
            self._avisar("Copiada para a área de transferência.")
        else:
            self._avisar("Não foi possível acessar a área de transferência.", erro=True)

    def _copiar_para_area_de_transferencia(self, texto: str) -> bool:
        if PYPERCLIP_DISPONIVEL:
            try:
                pyperclip.copy(texto)
                return True
            except pyperclip.PyperclipException:
                pass  # sem backend de clipboard: cai no fallback do Tk

        try:
            self.clipboard_clear()
            self.clipboard_append(texto)
            self.update()  # mantém o conteúdo disponível para outros apps
            return True
        except tk.TclError:
            return False

    def _ler_opcoes(self) -> Opcoes:
        return Opcoes(
            comprimento=int(self.var_comprimento.get()),
            usar_minusculas=self.var_minusculas.get(),
            usar_maiusculas=self.var_maiusculas.get(),
            usar_digitos=self.var_digitos.get(),
            usar_simbolos=self.var_simbolos.get(),
            evitar_ambiguos=self.var_ambiguos.get(),
        )

    # ---------------------------------------------------------- Feedback --

    def _ao_mover_escala(self, valor: str) -> None:
        comprimento = int(float(valor))
        self.var_comprimento.set(comprimento)
        self.rotulo_comprimento.configure(text=str(comprimento))
        self.gerar()

    def _atualizar_medidor(
        self, percentual: float, rotulo: str, entropia: float = 0.0
    ) -> None:
        self._percentual = percentual
        self._cor_forca = CORES_FORCA[rotulo]
        self.rotulo_forca.configure(text=f"Força: {rotulo}", foreground=self._cor_forca)
        self.rotulo_entropia.configure(
            text=f"{entropia:.0f} bits de entropia" if entropia else ""
        )
        self._redesenhar_barra()

    def _redesenhar_barra(self) -> None:
        largura = self.barra.winfo_width()
        self.barra.coords(self._preenchimento, 0, 0, largura * self._percentual, 6)
        self.barra.itemconfigure(self._preenchimento, fill=self._cor_forca)

    def _avisar(self, mensagem: str, erro: bool = False) -> None:
        if self._id_aviso is not None:
            self.after_cancel(self._id_aviso)
        cor = CORES_FORCA["Fraca"] if erro else CORES_FORCA["Forte"]
        ttk.Style(self).configure("Status.TLabel", foreground=cor)
        self.var_status.set(mensagem)
        self._id_aviso = self.after(DURACAO_AVISO_MS, lambda: self.var_status.set(""))


def executar() -> None:
    GeradorSenhasApp().mainloop()
