from estruturasAux import NoArvore

# CodigoIntermediario compatível com NoArvore(valor=str | token_obj) do seu parser.
class CodigoIntermediario:
    def __init__(self, arvore_sintatica):
        self.raiz = arvore_sintatica
        self.instrucoes = []
        self.temp_count = 0
        self.label_count = 0

    # ---------- helpers ----------
    def novo_temp(self):
        self.temp_count += 1
        return f"t{self.temp_count}"

    def novo_label(self):
        self.label_count += 1
        return f"L{self.label_count}"

    def emit(self, instr):
        self.instrucoes.append(instr)

    def is_token_node(self, no):
        # folha terminal: valor é o objeto token (possui .token e .lexema)
        return not isinstance(no.valor, str)

    def token_tipo(self, no):
        # retorna tipo do token (ex: 'ID', 'Num', 'OpMat', ...)
        return no.valor.token

    def token_lexema(self, no):
        # retorna lexema textual (ex: 'meuRegistro', '10', '+')
        return no.valor.lexema


    def gerar(self):
        """Chame gerar() para produzir e retornar a lista de instruções."""
        self.instrucoes = []
        self.temp_count = 0
        self.label_count = 0
        self.CI(self.raiz)
        return self.instrucoes

    # ---------- percorre em pós-ordem ----------
    def CI(self, no):
        if no is None:
            return

        # gerar para filhos primeiro
        for f in no.filhos:
            self.CI(f)

        # depois gerar para o nó atual
        self.gerar_instrucao(no)

    # ---------- geração por nó ----------
    def gerar_instrucao(self, no):
        # se for folha token — não gera instrução aqui (tratado em gerar_expr)
        if self.is_token_node(no):
            return

        tipo = no.valor  # ex: 'COMANDO', 'EXP_MAT', 'NOME', etc.

        # ---------- COMANDO: pode ser atribuição, while, if, write, read ----------
        if tipo == "COMANDO":
            # examina o primeiro filho para decidir o tipo
            if not no.filhos:
                return
            primeiro = no.filhos[0]
            # caso: ID ...  -> atribuição (NOME Atribuicao VALOR)
            if not self.is_token_node(primeiro) and primeiro.valor == "NOME":
                # o nó filho 'COMANDO' já teve seus filhos processados em pós-ordem,
                # então podemos extrair diretamente:
                # forma: NOME, Token(Atribuicao), VALOR
                # pegar o target (nome composto) e o node VALOR
                nome_node = no.filhos[0]
                # achar o índice do nó VALOR (normalmente 2)
                valor_node = None
                for f in no.filhos:
                    if not self.is_token_node(f) and f.valor == "VALOR":
                        valor_node = f
                        break
                target = self.nome_para_texto(nome_node)
                place = self.gerar_expr(valor_node)
                self.emit(f"atrib {target} {place}")
                return

            # caso: while
            if self.is_token_node(primeiro) and self.token_tipo(primeiro) == "Loop":
                # estrutura: Token(Loop) EXP_LOGICA BLOCO
                # o EXP_LOGICA e BLOCO já foram processados em filhos, geramos labels aqui
                # porém precisamos gerar saltos: reprocessar filhos para obter nodos
                exp_node = None
                bloco_node = None
                for f in no.filhos:
                    if not self.is_token_node(f) and f.valor == "EXP_LOGICA" and exp_node is None:
                        exp_node = f
                    if not self.is_token_node(f) and f.valor == "BLOCO":
                        bloco_node = f
                Lstart = self.novo_label()
                Lbody = self.novo_label()
                Lend = self.novo_label()
                self.emit(f"lbl {Lstart}")
                cond_place = self.gerar_expr(exp_node)
                self.emit(f"jnz {Lbody} {cond_place}")
                self.emit(f"jmp {Lend}")
                self.emit(f"lbl {Lbody}")
                # bloco já foi gerado por CI (filhos), mas se bloco é nó com filhos que não geraram instruções (ex: bloco não tratou internamente),
                # chamar CI nele garante a geração (idempotente)
                self.CI(bloco_node)
                self.emit(f"jmp {Lstart}")
                self.emit(f"lbl {Lend}")
                return

            # caso: if
            if self.is_token_node(primeiro) and self.token_tipo(primeiro) == "Se":
                # estrutura: Token(Se) EXP_LOGICA Token(Entao) BLOCO [ELSE]
                # extrai exp, then_block, else_block
                exp_node = None
                then_block = None
                else_block = None
                # localizar nós por tipo
                for f in no.filhos:
                    if not self.is_token_node(f) and f.valor == "EXP_LOGICA" and exp_node is None:
                        exp_node = f
                    elif not self.is_token_node(f) and f.valor == "BLOCO" and then_block is None:
                        then_block = f
                    elif not self.is_token_node(f) and f.valor == "ELSE":
                        else_block = f
                Lthen = self.novo_label()
                Lelse = self.novo_label()
                Lend = self.novo_label()
                cond_place = self.gerar_expr(exp_node)
                self.emit(f"jnz {Lthen} {cond_place}")
                self.emit(f"jmp {Lelse}")
                self.emit(f"lbl {Lthen}")
                # then_block já foi expandido por CI (filhos) — garantir geração
                if then_block:
                    self.CI(then_block)
                self.emit(f"jmp {Lend}")
                self.emit(f"lbl {Lelse}")
                if else_block:
                    # ELSE nó contém possivelmente token 'Senao' e BLOCO dentro; procurar BLOCO dentro do ELSE
                    for g in else_block.filhos:
                        if not self.is_token_node(g) and g.valor == "BLOCO":
                            self.CI(g)
                            break
                self.emit(f"lbl {Lend}")
                return

            # caso: write
            if self.is_token_node(primeiro) and self.token_tipo(primeiro) == "Escrita":
                # filho seguinte é CONST_VALOR
                const_node = None
                for f in no.filhos:
                    if not self.is_token_node(f) and f.valor == "CONST_VALOR":
                        const_node = f
                        break
                # CONST_VALOR pode conter STRING_LITERAL ou EXP_MAT
                if const_node:
                    # checar se tem STRING_LITERAL
                    for g in const_node.filhos:
                        if not self.is_token_node(g) and g.valor == "STRING_LITERAL":
                            # construir texto a partir das folhas (cada filha é NoArvore(token))
                            parts = []
                            for toknode in g.filhos:
                                if self.is_token_node(toknode):
                                    parts.append(self.token_lexema(toknode))
                            texto = " ".join(parts)
                            self.emit(f'write "{texto}"')
                            return
                    # senão é expressão
                    # achar EXP_MAT dentro de CONST_VALOR
                    for g in const_node.filhos:
                        if not self.is_token_node(g) and g.valor == "EXP_MAT":
                            place = self.gerar_expr(g)
                            self.emit(f"write {place}")
                            return
                return

            # caso: read (LEITURA) - opcional
            if self.is_token_node(primeiro) and self.token_tipo(primeiro) == "Leitura":
                # read NOME
                nome_node = None
                for f in no.filhos:
                    if not self.is_token_node(f) and f.valor == "NOME":
                        nome_node = f
                        break
                if nome_node:
                    target = self.nome_para_texto(nome_node)
                    self.emit(f"read {target}")
                return

            return  # outros subtipos de COMANDO não tratados aqui

        # ---------- LISTA_COM / BLOCO / LISTAS — não emitem instrução diretamente ----------
        if tipo in ("LISTA_COM", "BLOCO", "DECLARACOES", "LISTA_VAR", "LISTA_TIPOS", "CORPO", "PROGRAMA"):
            return

        # ---------- VALOR: pode ser EXP_MAT ou ID + LISTA_PARAM ----------
        if tipo == "VALOR":
            # nada a fazer aqui: expressão já processada em filhos; geração ocorre quando usado (atrib/write)
            return

        # ---------- NOME: composto por ID seguido de NOME_LINHA(s) ----------
        if tipo == "NOME":
            # não gera instrução isoladamente
            return

        # ---------- demais nós não produzem instrução aqui ----------
        return

    # ---------- gerar expressão: retorna "place" (literal, var ou temp) ----------
    def gerar_expr(self, no):
        if no is None:
            return "0"

        # caso folha token: NUM ou ID
        if self.is_token_node(no):
            ttype = self.token_tipo(no)
            lex = self.token_lexema(no)
            if ttype == "Num":
                return lex
            if ttype == "ID":
                return lex
            # operadores/parenteses não aparecem aqui isolados
            return lex

        tipo = no.valor

        # VALOR -> EXP_MAT ou ID LISTA_PARAM
        if tipo == "VALOR":
            # se contém EXP_MAT
            for f in no.filhos:
                if not self.is_token_node(f) and f.valor == "EXP_MAT":
                    return self.gerar_expr(f)
                # caso ID + LISTA_PARAM
                if self.is_token_node(f) and self.token_tipo(f) == "ID":
                    # construir nome possivelmente com lista_param (função chamada) — para IR simples tratamos como variável
                    return self.token_lexema(f)
            return "0"

        # PARAMETRO -> NOME ou Num
        if tipo == "PARAMETRO":
            # pode conter NOME (acesso composto) ou Num terminal
            for f in no.filhos:
                if not self.is_token_node(f) and f.valor == "NOME":
                    return self.nome_para_texto(f)
                if self.is_token_node(f) and self.token_tipo(f) == "Num":
                    return self.token_lexema(f)
            return "0"

        # EXP_MAT -> PARAMETRO (OP_MAT PARAMETRO)*
        if tipo == "EXP_MAT":
            # left associative: avalia primeiro parametro e aplica ops sequenciais
            parts = no.filhos[:]  # lista de NoArvore (PARAMETRO, OP_MAT, PARAMETRO, ...)
            if not parts:
                return "0"
            left_place = self.gerar_expr(parts[0])
            i = 1
            while i < len(parts):
                op_node = parts[i]        # OP_MAT (NoArvore) whose child is token OpMat
                right_node = parts[i+1]   # PARAMETRO
                # extrair operador lexema
                op_lex = None
                # OP_MAT tem um filho terminal token (NoArvore(token))
                if op_node.filhos and self.is_token_node(op_node.filhos[0]):
                    op_lex = self.token_lexema(op_node.filhos[0])
                else:
                    # fallback, procurar token dentro
                    for ff in op_node.filhos:
                        if self.is_token_node(ff):
                            op_lex = self.token_lexema(ff)
                            break
                right_place = self.gerar_expr(right_node)
                tmp = self.novo_temp()
                instr = { "+": "add", "-": "sub", "*": "mul", "/": "div" }[op_lex]
                self.emit(f"{instr} {tmp} {left_place} {right_place}")
                left_place = tmp
                i += 2
            return left_place

        # EXP_LOGICA -> EXP_MAT (OP_LOGICO EXP_MAT)*
        if tipo == "EXP_LOGICA":
            parts = no.filhos[:]
            if not parts:
                return "0"
            left_place = self.gerar_expr(parts[0])
            if len(parts) == 1:
                return left_place
            # se tem operador lógico no index 1
            i = 1
            # trata apenas o primeiro operador lógico (gramática permite encadeamento)
            while i < len(parts):
                op_node = parts[i]       # OP_LOGICO
                right_node = parts[i+1]  # EXP_MAT
                # extrair lexema do op
                op_lex = None
                if op_node.filhos and self.is_token_node(op_node.filhos[0]):
                    op_lex = self.token_lexema(op_node.filhos[0])
                else:
                    for ff in op_node.filhos:
                        if self.is_token_node(ff):
                            op_lex = self.token_lexema(ff)
                            break
                right_place = self.gerar_expr(right_node)
                tmp = self.novo_temp()
                instr = { "=": "eql", "<>": "dif", ">": "grt", "<": "les" }[op_lex]
                self.emit(f"{instr} {tmp} {left_place} {right_place}")
                left_place = tmp
                i += 2
            return left_place

        # NOME -> ID (NOME_LINHA)*
        if tipo == "NOME":
            return self.nome_para_texto(no)

        # default
        return "0"

    # ---------- Constrói representação textual de NOME (inclui .campo e [idx]) ----------
    def nome_para_texto(self, nome_node):
        # nome_node.valor == "NOME"
        # filho 0 é NoArvore(token ID)
        parts = []
        if not nome_node.filhos:
            return ""
        # primeiro filho pode ser terminal ID
        first = nome_node.filhos[0]
        if self.is_token_node(first) and self.token_tipo(first) == "ID":
            base = self.token_lexema(first)
            current = base
        else:
            # se não for terminal, tentar gerar por recursão
            current = self.gerar_expr(first)
        # processar NOME_LINHA(s)
        for f in nome_node.filhos[1:]:
            # cada f é NoArvore('NOME_LINHA')
            if not self.is_token_node(f) and f.valor == "NOME_LINHA":
                # se o primeiro filho de NOME_LINHA é token Pont -> .ID
                if f.filhos and self.is_token_node(f.filhos[0]) and self.token_tipo(f.filhos[0]) == "Pont":
                    # segundo filho é ID token
                    if len(f.filhos) > 1 and self.is_token_node(f.filhos[1]) and self.token_tipo(f.filhos[1]) == "ID":
                        field = self.token_lexema(f.filhos[1])
                        current = f"{current}.{field}"
                # se for acesso por colchetes: AColch PARAMETRO FColch
                elif f.filhos and self.is_token_node(f.filhos[0]) and self.token_tipo(f.filhos[0]) == "AColch":
                    # segundo filho é PARAMETRO
                    if len(f.filhos) > 1 and not self.is_token_node(f.filhos[1]) and f.filhos[1].valor == "PARAMETRO":
                        idx_place = self.gerar_expr(f.filhos[1])
                        current = f"{current}[{idx_place}]"
        return current

