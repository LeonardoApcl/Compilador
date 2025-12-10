from estruturasAux import Token, NoArvore
from tabelaSimbolos import TabelaSimbolos

class Semantico:
    def __init__(self, arvore):
        self.arvore = arvore
        self.tabela = TabelaSimbolos()
        
        # Variáveis de Estado para controle de contexto
        self.tipo_retorno_esperado = None # Para validar Regra 7
        self.contexto_decl = "variavel"   # Pode ser: "variavel", "parametro"
        self.contador_params = 0          # Para contar ordem dos parâmetros
        self.lista_tipos_params_temp = [] # Para guardar tipos dos params da função atual

    def analisar(self):
        self.visitar(self.arvore)
        return self.tabela

    def visitar(self, no):
        if no is None: return None

        if isinstance(no, str):
            # Se isso aparecer, é porque o sintático inseriu uma string solta na árvore
            print(f"ERRO INTERNO: O nó da árvore é uma string '{no}', mas deveria ser um Objeto NoArvore.")
            return None
        
        # Despacho Dinâmico
        if isinstance(no.valor, str):
            metodo_nome = f"visitar_{no.valor}"
            if hasattr(self, metodo_nome):
                return getattr(self, metodo_nome)(no)
        
        # Comportamento Padrão: Visitar filhos e retornar o último valor não nulo
        ultimo_retorno = None
        for filho in no.filhos:
            res = self.visitar(filho)
            if res: ultimo_retorno = res
        return ultimo_retorno

    # =========================================================================
    # IMPLEMENTAÇÃO DAS REGRAS
    # =========================================================================

    def visitar_PROGRAMA(self, no):
        # [PROGRAMA] -> Regra 1
        token_id = no.filhos[1].valor
        self.tabela.declarar(token_id, "programa", "void")
        self.visitar(no.filhos[3]) # Visita CORPO

    def visitar_CONSTANTE(self, no):
        # [CONSTANTE] -> Regra 1
        token_id = no.filhos[0].valor
        tipo_inferido = self.visitar(no.filhos[2]) # Visita CONST_VALOR
        self.tabela.declarar(token_id, "constante", tipo_inferido)

    def visitar_CONST_VALOR(self, no):
        # Auxiliar do visitar_CONSTANTE para inferir tipo
        primeiro = no.filhos[0]
        if isinstance(primeiro.valor, Token) and primeiro.valor.token == 'Aspas':
            return 'string'
        return self.visitar(primeiro) # EXP_MAT

    def visitar_TIPO(self, no):
        # [TIPO] -> Regra 1
        token_id = no.filhos[0].valor
        descricao_tipo = self.visitar(no.filhos[2]) 
        self.tabela.declarar(token_id, "tipo", descricao_tipo)

    def visitar_TIPO_DADO(self, no):
        # [TIPO_DADO] -> Regras 1, 2
        primeiro = no.filhos[0]
        
        # Caso Primitivo
        if isinstance(primeiro.valor, Token) and primeiro.valor.token == 'TipoSimples':
            return primeiro.valor.lexema
            
        # Caso ID (Alias) -> Regra 2
        elif isinstance(primeiro.valor, Token) and primeiro.valor.token == 'ID':
            simb = self.tabela.consultar(primeiro.valor)
            if not simb:
                print(f"Erro Semântico (Regra 2): Tipo '{primeiro.valor.lexema}' não declarado (Linha {primeiro.valor.linha}).")
                return 'erro'
            if simb.classificacao != 'tipo':
                print(f"Erro Semântico (Linha {primeiro.valor.linha}): '{primeiro.valor.lexema}' não é um tipo.")
                return 'erro'
            return simb.nome 

        # Caso Record
        elif isinstance(primeiro.valor, Token) and primeiro.valor.token == 'Record':
            # Cria nome único para o escopo do record
            nome_escopo_rec = f"record_def_linha_{primeiro.valor.linha}"
            self.tabela.entrar_escopo(nome_escopo_rec)
            
            # Dentro do record, LISTA_VAR declara campos (Regra 1)
            self.visitar(no.filhos[1]) 
            
            self.tabela.sair_escopo()
            return nome_escopo_rec 

        # Caso Array
        elif isinstance(primeiro.valor, Token) and primeiro.valor.token == 'Array':
            tipo_elem = self.visitar(no.filhos[5])
            return f"array of {tipo_elem}"

        print(f"O tipo de dado {primeiro.valor.lexema} não foi reconhecido. (Linha {primeiro.valor.linha})")
        return "desconhecido"

    def visitar_NOME_FUNCAO(self, no):
        # [NOME_FUNCAO] -> Regra 1
        token_id = no.filhos[1].valor
        
        # Pega tipo de retorno (último filho TIPO_DADO)
        tipo_retorno = self.visitar(no.filhos[6]) 
        
        # Declara a função (Regra 1)
        self.tabela.declarar(token_id, "funcao", tipo_retorno, qtd=0)
        
        # Entra no escopo
        self.tabela.entrar_escopo(token_id.lexema)
        self.tipo_retorno_esperado = tipo_retorno # Para Regra 7
        
        # Configura contexto para declarar parâmetros
        self.contexto_decl = "parametro"
        self.contador_params = 0
        self.lista_tipos_params_temp = []
        
        # Visita LISTA_VAR (agora declarando como parâmetros)
        self.visitar(no.filhos[3]) 
        
        # Restaura contexto
        self.contexto_decl = "variavel"
        
        # Atualiza a função com a quantidade e tipos dos parâmetros
        self.tabela.atualizar_qtd_params(token_id.lexema, self.contador_params, list(self.lista_tipos_params_temp))

    def visitar_BLOCO_FUNCAO(self, no):
        self.visitar_nos_filhos(no)
        self.tabela.sair_escopo()
        self.tipo_retorno_esperado = None

    def visitar_VARIAVEL(self, no):
        lista_ids = self.visitar(no.filhos[0]) # Chama visitar_LISTA_ID
        tipo_str = self.visitar(no.filhos[2])  # Chama visitar_TIPO_DADO
        
        if lista_ids and tipo_str:
            for token in lista_ids:
                ordem = None
                if self.contexto_decl == "parametro":
                    self.contador_params += 1
                    ordem = self.contador_params
                    self.lista_tipos_params_temp.append(tipo_str)
                
                self.tabela.declarar(token, self.contexto_decl, tipo_str, ordem=ordem)

    def visitar_LISTA_ID(self, no):
        ids = []
        for filho in no.filhos:
            if isinstance(filho.valor, Token) and filho.valor.token == 'ID':
                ids.append(filho.valor)
        return ids

    def visitar_COMANDO(self, no):
        # [COMANDO] -> Regras 1, 2, 3, 7
        
        # Caso 1: Atribuição ou Chamada de Procedimento (Começa com NOME/ID)
        if no.filhos[0].valor == 'NOME':
            no_nome = no.filhos[0]
            token_id = no_nome.filhos[0].valor 
            
            # Regra 2: Verifica existência e tipo da variável
            tipo_var = self.visitar(no_nome)
            
            # Se for atribuição (ID := VALOR)
            if len(no.filhos) > 2 and isinstance(no.filhos[1].valor, Token) and no.filhos[1].valor.token == 'Atribuicao':
                tipo_valor = self.visitar(no.filhos[2]) # Visita VALOR

                tipo_var_base = self._resolver_tipo_real(tipo_var)
                tipo_valor_base = self._resolver_tipo_real(tipo_valor)
                
                # Regra 7: Retorno de Função
                if token_id.lexema == self.tabela.obter_escopo_atual_nome():
                    tipo_esp_base = self._resolver_tipo_real(self.tipo_retorno_esperado)
                    if tipo_valor_base != tipo_esp_base:
                        print(f"Erro Semântico (Regra 7): Função '{token_id.lexema}' espera retorno '{self.tipo_retorno_esperado}', mas recebeu '{tipo_valor}' (Linha {token_id.linha}).")
                
                # Regra 3: Tipos iguais
                elif tipo_var_base != tipo_valor_base and tipo_var != 'erro' and tipo_valor != 'erro':
                    if not (tipo_var_base == 'real' and tipo_valor_base == 'integer'):
                         print(f"Erro Semântico (Regra 3): Atribuição incompatível. '{token_id.lexema}' ({tipo_var}) := {tipo_valor} (Linha {token_id.linha}).")

        # Caso 2: Outros comandos (While, If, Write, Read)
        # precisamos garantir que visitamos os filhos recursivamente aqui.
        else:
            self.visitar_nos_filhos(no)

    def visitar_VALOR(self, no):
        # [VALOR] -> EXP_MAT | ID [LISTA_PARAM]
        primeiro = no.filhos[0]
        
        if primeiro.valor == 'EXP_MAT':
            return self.visitar(primeiro)
        
        elif isinstance(primeiro.valor, Token) and primeiro.valor.token == 'ID':
            token_id = primeiro.valor
            simb = self.tabela.consultar(token_id)
            
            if not simb:
                print(f"Erro Semântico (Regra 2): '{token_id.lexema}' não declarado (Linha {token_id.linha}).")
                return 'erro'
            
            if len(no.filhos) > 1: # Tem [LISTA_PARAM]
                if simb.classificacao != 'funcao':
                    print(f"Erro Semântico (Regra 4): '{token_id.lexema}' não é função, não aceita argumentos (Linha {token_id.linha}).")
                else:
                    self._validar_chamada_funcao(simb, no.filhos[1])
            
            return simb.tipo
        return 'erro'

    def _validar_chamada_funcao(self, simbolo_func, no_lista_param):
        # Auxiliar para Regras 5 e 6
        no_lista_nome = no_lista_param.filhos[1]
        tipos_argumentos = self.visitar(no_lista_nome) 
        
        qtd_esperada = simbolo_func.qtd if simbolo_func.qtd else 0
        qtd_passada = len(tipos_argumentos)
        
        if qtd_passada != qtd_esperada:
            print(f"Erro Semântico (Regra 5): Função '{simbolo_func.nome}' espera {qtd_esperada} parâmetros, recebeu {qtd_passada} (Linha {simbolo_func.linha}).")
            return

        if hasattr(simbolo_func, 'params_tipos') and simbolo_func.params_tipos:
            for i, (tipo_passado, tipo_esperado) in enumerate(zip(tipos_argumentos, simbolo_func.params_tipos)):
                
                # --- MUDANÇA: Resolve Alias antes de comparar ---
                tipo_passado_base = self._resolver_tipo_real(tipo_passado)
                tipo_esperado_base = self._resolver_tipo_real(tipo_esperado)
                # ------------------------------------------------

                if tipo_passado_base != tipo_esperado_base and not (tipo_esperado_base == 'real' and tipo_passado_base == 'integer'):
                    print(f"Erro Semântico (Regra 6): Parâmetro {i+1} espera '{tipo_esperado}', recebeu '{tipo_passado}'.")

    def visitar_LISTA_NOME(self, no):
        tipos = []
        for filho in no.filhos:
            if filho.valor == 'PARAMETRO':
                tipos.append(self.visitar(filho))
            elif filho.valor == 'Virg':
                pass
        return tipos

    def visitar_PARAMETRO(self, no):
        filho = no.filhos[0]
        if filho.valor == 'NOME':
            return self.visitar(filho)
        elif isinstance(filho.valor, Token) and filho.valor.token == 'Num':
            if '.' in filho.valor.lexema: return 'real'
            return 'integer'
        
        # print(f"Tipo do {filho.valor.lexema} não reconhecido.") # Opcional
        return 'erro'

    def visitar_EXP_MAT(self, no):
        # [EXP_MAT] -> [PARAMETRO] { [OP_MAT] [PARAMETRO] }
        tipo_resultado = self.visitar(no.filhos[0])
        
        if tipo_resultado not in ['integer', 'real']:
            print(f"Erro Semântico (Regra 3): Operação aritmética espera números, mas o primeiro termo é '{tipo_resultado}'.")
            return 'erro'

        num_filhos = len(no.filhos)
        i = 1
        
        while i < num_filhos:
            no_op = no.filhos[i]      
            no_param = no.filhos[i+1] 

            tipo_proximo = self.visitar(no_param)

            if tipo_proximo not in ['integer', 'real']:
                print(f"Erro Semântico (Regra 3): Operação aritmética encontrou termo inválido '{tipo_proximo}'.")
                return 'erro'

            token_op = no_op.filhos[0].valor 
            
            if token_op.lexema == '/':
                tipo_resultado = 'real'
            elif tipo_resultado == 'real' or tipo_proximo == 'real':
                tipo_resultado = 'real'
            
            i += 2

        return tipo_resultado
    
    def visitar_EXP_LOGICA(self, no):
        tipo_1 = self.visitar(no.filhos[0])
        if len(no.filhos) > 2:
            tipo_2 = self.visitar(no.filhos[2])
            if tipo_1 != tipo_2 and not (tipo_1 in ['integer','real'] and tipo_2 in ['integer','real']):
                 print(f"Erro Semântico (Regra 3): Comparação lógica incompatível entre '{tipo_1}' e '{tipo_2}'.")
        return "boolean"

    def visitar_NOME(self, no):
        # [NOME] -> ID [NOME'] -> Regras 1, 8, 9, 10
        token_id = no.filhos[0].valor
        simb = self.tabela.consultar(token_id)
        
        if not simb:
            print(f"Erro Semântico (Regra 2): Variável '{token_id.lexema}' não declarada (Linha {token_id.linha}).")
            return 'erro'
        
        tipo_atual = simb.tipo

        # Resolve alias
        tipo_atual = self._resolver_tipo_real(tipo_atual)
        
        # Verifica acessos complexos (Array ou Record)
        if len(no.filhos) > 1:
            for filho in no.filhos[1:]: 
                if filho.valor == 'NOME_LINHA': 
                    op = filho.filhos[0].valor
                    
                    # Regra 8: Array
                    if isinstance(op, Token) and op.token == 'AColch':
                        if 'array of' not in tipo_atual:
                            print(f"Erro Semântico (Regra 8): '{token_id.lexema}' não é array para usar [].")
                        else:
                            tipo_atual = tipo_atual.replace("array of ", "")
                            # Resolve se o array for de um alias (ex: array of tInteiro)
                            tipo_atual = self._resolver_tipo_real(tipo_atual)

                    # Regra 9/10: Record/Classe
                    elif isinstance(op, Token) and op.token == 'Pont':
                        token_campo = filho.filhos[1].valor # ID do campo
                        
                        if not tipo_atual.startswith("record_def_linha_"):
                             print(f"Erro Semântico (Regra 9): '{token_id.lexema}' não é record para usar ponto (.).")
                             return 'erro'
                        
                        campo_simb = self.tabela.consultar_campo_record(token_campo.lexema, tipo_atual)
                        if not campo_simb:
                             print(f"Erro Semântico (Regra 10): Campo '{token_campo.lexema}' não existe (Linha {token_campo.linha}).")
                             return 'erro'
                        
                        tipo_atual = campo_simb.tipo
                        # Resolve alias do campo recém acessado
                        tipo_atual = self._resolver_tipo_real(tipo_atual)

        return tipo_atual

    # =========================================================================
    # MÉTODOS AUXILIARES (ESSENCIAIS)
    # =========================================================================

    def _resolver_tipo_real(self, nome_tipo):
        """
        Percorre a tabela de símbolos para encontrar o tipo base de um alias.
        Ex: tIdade -> integer;  tVetor -> array of integer; tRegistro -> record_def...
        """
        tipo_atual = nome_tipo
        while True:
            alias_encontrado = None
            # Busca na tabela mestra se existe um símbolo 'tipo' com esse nome
            for s in self.tabela.tabela_mestra:
                if s.nome == tipo_atual and s.classificacao == 'tipo':
                    alias_encontrado = s
                    break
            
            if alias_encontrado:
                tipo_atual = alias_encontrado.tipo # Avança para a definição
            else:
                return tipo_atual # Retorna o tipo base encontrado
    
    def visitar_nos_filhos(self, no):
        for filho in no.filhos:
            self.visitar(filho)