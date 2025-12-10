from estruturasAux import NoArvore

class CodigoIntermediario:
    def __init__(self, arvore_sintatica):
        self.raiz = arvore_sintatica
        self.instrucoes = []
        self.temp_count = 0
        self.label_count = 0
        self.func_atual = None 

    def novo_temp(self):
        self.temp_count += 1
        return f"t{self.temp_count}"

    def novo_label(self):
        self.label_count += 1
        return f"L{self.label_count}"

    def emit(self, instr):
        self.instrucoes.append(instr)

    # --- HELPERS SEGUROS ---
    def is_token_node(self, no):
        if no is None: return False
        return not isinstance(no.valor, str)

    def token_tipo(self, no):
        if self.is_token_node(no): return no.valor.token
        return None

    def token_lexema(self, no):
        if self.is_token_node(no): return no.valor.lexema
        return "" 
        
    def buscar_filho(self, no, valor_buscado):
        """ Busca segura de um filho pelo valor (nome do nó) """
        if not no or not no.filhos: return None
        for filho in no.filhos:
            if not self.is_token_node(filho) and filho.valor == valor_buscado:
                return filho
        return None
    # -----------------------

    def gerar(self):
        self.instrucoes = []
        self.temp_count = 0
        self.label_count = 0
        self.CI(self.raiz)
        return self.instrucoes

    def CI(self, no):
        if no is None: return

        tipo = no.valor if isinstance(no.valor, str) else "TOKEN"

        # 1. PROGRAMA (RAIZ)
        if tipo == "PROGRAMA":
            self.emit("jmp main")
            
            # Busca segura pelo CORPO
            corpo = self.buscar_filho(no, "CORPO")
            if corpo:
                # 1. Gera Declarações (Funções)
                declaracoes = self.buscar_filho(corpo, "DECLARACOES")
                if declaracoes:
                    self.CI(declaracoes)
                
                # 2. Gera Main
                self.emit("lbl main")
                lista_com = self.buscar_filho(corpo, "LISTA_COM")
                if lista_com:
                    self.CI(lista_com) # Garante que visita a lista de comandos
            
            self.emit("halt")
            return

        # 2. FUNÇÕES
        if tipo == "FUNCAO":
            nome_func_node = self.buscar_filho(no, "NOME_FUNCAO")
            if nome_func_node and len(nome_func_node.filhos) > 1:
                token_id = nome_func_node.filhos[1]
                nome_func = self.token_lexema(token_id)
                
                self.emit(f"lbl {nome_func}")
                self.func_atual = nome_func
                
                bloco_func = self.buscar_filho(no, "BLOCO_FUNCAO")
                if bloco_func: self.CI(bloco_func)
                
                self.emit(f"ret {nome_func}")
                self.func_atual = None
            return

        # 3. COMANDOS (Delega para gerar_instrucao controlar a ordem)
        if tipo == "COMANDO":
            self.gerar_instrucao(no)
            return

        # 4. RECURSÃO PADRÃO (Para LISTA_COM, BLOCO, etc)
        # Visita todos os filhos sequencialmente
        for f in no.filhos:
            self.CI(f)
        
        self.gerar_instrucao(no)


    def gerar_instrucao(self, no):
        if self.is_token_node(no): return
        tipo = no.valor

        if tipo == "COMANDO":
            if not no.filhos: return
            primeiro = no.filhos[0]

            # CASO: ATRIBUIÇÃO
            if not self.is_token_node(primeiro) and primeiro.valor == "NOME":
                nome_node = no.filhos[0]
                if len(no.filhos) > 2:
                    valor_node = no.filhos[2]
                    target = self.nome_para_texto(nome_node)
                    place = self.gerar_expr(valor_node)
                    self.emit(f"atrib {target} {place}")
                return

            # CASO: WHILE
            if self.is_token_node(primeiro) and self.token_tipo(primeiro) == "Loop":
                exp_node = self.buscar_filho(no, "EXP_LOGICA")
                bloco_node = self.buscar_filho(no, "BLOCO")
                
                Lstart, Ltrue, Lend = self.novo_label(), self.novo_label(), self.novo_label()
                self.emit(f"lbl {Lstart}")
                cond = self.gerar_expr(exp_node)
                self.emit(f"jnz {Ltrue} {cond}")
                self.emit(f"jmp {Lend}")
                self.emit(f"lbl {Ltrue}")
                self.CI(bloco_node)
                self.emit(f"jmp {Lstart}")
                self.emit(f"lbl {Lend}")
                return

            # CASO: IF
            if self.is_token_node(primeiro) and self.token_tipo(primeiro) == "Se":
                exp_node = self.buscar_filho(no, "EXP_LOGICA")
                then_block = None
                else_block = None
                
                # Identifica os blocos manualmente pois podem haver dois BLOCOs
                # O primeiro é o THEN, o segundo (dentro de ELSE) é o ELSE
                blocos_encontrados = []
                for f in no.filhos:
                    if not self.is_token_node(f) and f.valor == "BLOCO":
                        blocos_encontrados.append(f)
                
                if blocos_encontrados: then_block = blocos_encontrados[0]
                
                else_node = self.buscar_filho(no, "ELSE")
                if else_node:
                    # ELSE -> Senao BLOCO
                    else_block = self.buscar_filho(else_node, "BLOCO")

                Ltrue, Lfalse, Lend = self.novo_label(), self.novo_label(), self.novo_label()
                cond = self.gerar_expr(exp_node)
                self.emit(f"jnz {Ltrue} {cond}")
                self.emit(f"jmp {Lfalse}") 
                self.emit(f"lbl {Ltrue}")
                self.CI(then_block)
                self.emit(f"jmp {Lend}")
                self.emit(f"lbl {Lfalse}")
                if else_block: self.CI(else_block)
                self.emit(f"lbl {Lend}")
                return

            # CASO: WRITE
            if self.is_token_node(primeiro) and self.token_tipo(primeiro) == "Escrita":
                if len(no.filhos) > 1:
                    const_node = no.filhos[1]
                    # Busca segura por STRING_LITERAL
                    str_lit = self.buscar_filho(const_node, "STRING_LITERAL")
                    if str_lit:
                        texto = " ".join([self.token_lexema(t) for t in str_lit.filhos if self.is_token_node(t)])
                        self.emit(f'write "{texto}"')
                    else:
                        exp = self.gerar_expr(const_node)
                        self.emit(f"write {exp}")
                return
            
            # CASO: READ
            # Verificação dupla: 'Leitura' ou 'Read' (para compatibilidade)
            ttype = self.token_tipo(primeiro)
            if self.is_token_node(primeiro) and (ttype == "Leitura" or ttype == "Read"):
                if len(no.filhos) > 1:
                    target = self.nome_para_texto(no.filhos[1])
                    self.emit(f"read {target}")
                return


    def gerar_expr(self, no):
        if no is None: return "0"
        if self.is_token_node(no): return self.token_lexema(no)
        tipo = no.valor

        if tipo == "CONST_VALOR":
             exp_mat = self.buscar_filho(no, "EXP_MAT")
             if exp_mat: return self.gerar_expr(exp_mat)

        if tipo == "VALOR":
            if not no.filhos: return "0"
            primeiro = no.filhos[0]
            
            if not self.is_token_node(primeiro) and primeiro.valor == "EXP_MAT":
                return self.gerar_expr(primeiro)
            
            if self.is_token_node(primeiro) and self.token_tipo(primeiro) == "ID":
                nome = self.token_lexema(primeiro)
                if len(no.filhos) > 1: # LISTA_PARAM
                     return self.gerar_chamada_funcao(nome, no.filhos[1])
                return nome

        if tipo == "EXP_MAT":
            if not no.filhos: return "0"
            left = self.gerar_expr(no.filhos[0])
            i = 1
            while i < len(no.filhos):
                op_node, right_node = no.filhos[i], no.filhos[i+1]
                op_lex = "+"
                if op_node.filhos and self.is_token_node(op_node.filhos[0]): op_lex = self.token_lexema(op_node.filhos[0])
                right = self.gerar_expr(right_node)
                temp = self.novo_temp()
                instr = {"+":"add", "-":"sub", "*":"mul", "/":"div"}.get(op_lex, "add")
                self.emit(f"{instr} {temp} {left} {right}")
                left = temp
                i += 2
            return left

        if tipo == "PARAMETRO":
            if not no.filhos: return "0"
            primeiro = no.filhos[0]
            if self.is_token_node(primeiro):
                ttype = self.token_tipo(primeiro)
                if ttype == "AParent": return self.gerar_expr(no.filhos[1])
                elif ttype == "Num": return self.token_lexema(primeiro)
            else:
                if primeiro.valor == "NOME": return self.processar_nome(primeiro)

        if tipo == "EXP_LOGICA":
            left = self.gerar_expr(no.filhos[0])
            if len(no.filhos) > 1:
                op_node, right = no.filhos[1], self.gerar_expr(no.filhos[2])
                op_lex = "="
                if op_node.filhos and self.is_token_node(op_node.filhos[0]): op_lex = self.token_lexema(op_node.filhos[0])
                temp = self.novo_temp()
                instr = {"=":"eql", "<>":"dif", "!":"dif", ">":"grt", "<":"les"}.get(op_lex, "eql")
                self.emit(f"{instr} {temp} {left} {right}")
                return temp
            return left
        return "0"

    def processar_nome(self, nome_node):
        if not nome_node or not nome_node.filhos: return ""
        id_token = nome_node.filhos[0]
        base_name = self.token_lexema(id_token) if self.is_token_node(id_token) else ""
        
        texto = base_name
        is_call = False
        lista_param_node = None

        if len(nome_node.filhos) > 1:
            for filho in nome_node.filhos[1:]:
                if not self.is_token_node(filho) and filho.valor == "NOME_LINHA":
                     if not filho.filhos: continue
                     primeiro_f = filho.filhos[0]
                     
                     if not self.is_token_node(primeiro_f) and primeiro_f.valor == "LISTA_PARAM":
                         is_call = True
                         lista_param_node = primeiro_f
                     elif self.is_token_node(primeiro_f) and self.token_tipo(primeiro_f) == "Pont":
                         if len(filho.filhos) > 1: texto += f".{self.token_lexema(filho.filhos[1])}"
                     elif self.is_token_node(primeiro_f) and self.token_tipo(primeiro_f) == "AColch":
                         if len(filho.filhos) > 1:
                             idx = self.gerar_expr(filho.filhos[1])
                             texto += f"[{idx}]"
        
        if is_call: return self.gerar_chamada_funcao(base_name, lista_param_node)
        return texto

    def gerar_chamada_funcao(self, nome_func, node_lista_param):
        args = []
        if len(node_lista_param.filhos) > 1:
            lista_nome = node_lista_param.filhos[1]
            for f in lista_nome.filhos:
                if not self.is_token_node(f) and f.valor == "EXP_MAT":
                    args.append(self.gerar_expr(f))
        
        for arg in args: self.emit(f"param {arg}")
        ret_temp = self.novo_temp()
        self.emit(f"call {nome_func}, {len(args)}, {ret_temp}")
        return ret_temp

    def nome_para_texto(self, nome_node):
        return self.processar_nome(nome_node)