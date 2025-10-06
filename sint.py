from estruturasAux import NoArvore

class Sintatico:
    def __init__(self, lista_tokens):
        self.lista_tokens = lista_tokens
        self.token_atual = lista_tokens.cab if lista_tokens else None

        # Conjuntos First de cada não-terminal

        self.FIRST = {
            'PROGRAMA'    : {'Prog'},
            'CORPO'       : {'Const', 'Type', 'Var', 'Func', 'Begin'},
            'DECLARACOES' : {'Const', 'Type', 'Var', 'Func'},
            'DEF_CONST'   : {'Const'},
            'LISTA_CONST' : {'ID'},
            'LISTA_CONST_': {'PontV'},
            'CONSTANTE'   : {'ID'},
            'CONST_VALOR' : {'Aspas', 'ID', 'Num', 'AParent'},
            'DEF_TIPOS'   : {'Type'},
            'LISTA_TIPOS' : {'ID'},
            'LISTA_TIPOS_': {'PontV'},
            'TIPO'        : {'ID'},
            'TIPO_DADO'   : {'TipoSimples', 'Array', 'Record', 'ID'},
            'DEF_VAR'     : {'Var'},
            'LISTA_VAR'   : {'ID'},
            'LISTA_VAR_'  : {'PontV'},
            'VARIAVEL'    : {'ID'},
            'LISTA_ID'    : {'ID'},
            'LISTA_ID_'   : {','},
            'LISTA_FUNC'  : {'Func'},
            'FUNCAO'      : {'Func'},
            'NOME_FUNCAO' : {'Func'},
            'BLOCO_FUNCAO': {'Var', 'Begin', 'ID', 'Loop', 'Se', 'Escrita', 'Read'},
            'BLOCO'       : {'Begin', 'ID', 'Loop', 'Se', 'Escrita', 'Read'},
            'LISTA_COM'   : {'ID', 'Loop', 'Se', 'Escrita', 'Read'},
            'COMANDO'     : {'ID', 'Loop', 'Se', 'Escrita', 'Read'},
            'ELSE'        : {'Senão'},
            'VALOR'       : {'ID', 'Num', 'AParent'},
            'LISTA_PARAM' : {'AParent'},
            'LISTA_NOME'  : {'ID', 'Num', 'AParent'},
            'LISTA_NOME_' : {','},
            'EXP_LOGICA'  : {'ID', 'Num', 'AParent'},
            'EXP_LOGICA_' : {'OpLog'},
            'EXP_MAT'     : {'ID', 'Num', 'AParent'},
            'EXP_MAT_'    : {'OpMat'},
            'PARAMETRO'   : {'ID', 'Num', 'AParent'},
            'OP_LOGICO'   : {'OpLog'},
            'OP_MAT'      : {'OpMat'},
            'NOME'        : {'ID'},
            'NOME_'       : {'AParent', 'AColch'},
        }
        
        self.FOLLOW = {
            'PROGRAMA'    : {'$'},
            'CORPO'       : {'$'},
            'DECLARACOES' : {'Begin'},
            'DEF_CONST'   : {'Type', 'Var', 'Func', 'Begin'},
            'LISTA_CONST' : {'Type', 'Var', 'Func', 'Begin'},
            'LISTA_CONST_': {'Type', 'Var', 'Func', 'Begin'},
            'CONSTANTE'   : {'PontV', 'Type', 'Var', 'Func', 'Begin'},
            'CONST_VALOR' : {'PontV'},
            'DEF_TIPOS'   : {'Var', 'Func', 'Begin'},
            'LISTA_TIPOS' : {'Var', 'Func', 'Begin'},
            'LISTA_TIPOS_': {'Var', 'Func', 'Begin'},
            'TIPO'        : {'PontV', 'Var', 'Func', 'Begin'},
            'TIPO_DADO'   : {'PontV', 'FParent', 'End'},
            'DEF_VAR'     : {'Func', 'Begin', 'ID', 'Loop', 'Se', 'Escrita', 'Read'},
            'LISTA_VAR'   : {'Func', 'Begin', 'End'},
            'LISTA_VAR_'  : {'Func', 'Begin', 'End'},
            'VARIAVEL'    : {'PontV', 'Func', 'Begin', 'End'},
            'LISTA_ID'    : {'DoisPt'},
            'LISTA_ID_'   : {'DoisPt'},
            'LISTA_FUNC'  : {'Begin'},
            'FUNCAO'      : {'Func', 'Begin'},
            'NOME_FUNCAO' : {'Var', 'Begin', 'ID', 'Loop', 'Se', 'Escrita', 'Read'},
            'BLOCO_FUNCAO': {'Func', 'Begin'},
            'BLOCO'       : {'PontV', 'End', 'Senão', '$'},
            'LISTA_COM'   : {'End'},
            'COMANDO'     : {'PontV', 'End'},
            'ELSE'        : {'PontV', 'End'},
            'VALOR'       : {'PontV', 'End'},
            'LISTA_PARAM' : {'PontV', 'OpMat', 'OpLog', 'FColch', 'FParent', 'Então', 'Begin', 'ID', 'Loop', 'Se', 'Escrita', 'Read', 'End'},
            'LISTA_NOME'  : {'FParent'},
            'LISTA_NOME_' : {'FParent'},
            'EXP_LOGICA'  : {'Então', 'Begin', 'ID', 'Loop', 'Se', 'Escrita', 'Read'},
            'EXP_LOGICA_' : {'Então', 'Begin', 'ID', 'Loop', 'Se', 'Escrita', 'Read'},
            'EXP_MAT'     : {'OpLog', 'PontV', 'FColch', 'FParent', 'Então', 'Begin', 'ID', 'Loop', 'Se', 'Escrita', 'Read', 'End'},
            'EXP_MAT_'    : {'OpLog', 'PontV', 'FColch', 'FParent', 'Então', 'Begin', 'ID', 'Loop', 'Se', 'Escrita', 'Read', 'End'},
            'PARAMETRO'   : {'OpMat', 'OpLog', 'PontV', 'FColch', 'FParent', 'Então', 'Begin', 'ID', 'Loop', 'Se', 'Escrita', 'Read', 'End'},
            'OP_LOGICO'   : {'ID', 'Num', 'AParent'},
            'OP_MAT'      : {'ID', 'Num', 'AParent'},
            'NOME'        : {'Atribuição', 'PontV', 'OpMat', 'OpLog', 'FColch', 'FParent', 'Então', 'Begin', 'ID', 'Loop', 'Se', 'Escrita', 'Read', 'End'},
            'NOME_'       : {'Atribuição', 'PontV', 'OpMat', 'OpLog', 'FColch', 'FParent', 'Então', 'Begin', 'ID', 'Loop', 'Se', 'Escrita', 'Read', 'End'},
        }

    def erro(self, esperado):
        if self.token_atual:
            raise SyntaxError(
                f"Erro Sintatico na linha {self.token_atual.dado.linha}: "
                f"Esperado {esperado}, mas encontrou '{self.token_atual.dado.lexema}'"
            )
        else:
            raise SyntaxError(f"Erro Sintatico: Esperado {esperado}, mas o arquivo terminou.")

    def avancar(self):
        if self.token_atual:
            self.token_atual = self.token_atual.prox

    def processarTerminal(self, token_esperado):
        if self.token_atual and self.token_atual.dado.token == token_esperado:
            objeto_token = self.token_atual.dado
            no = NoArvore(objeto_token)
            self.avancar()
            return no
        else:
            self.erro(token_esperado)

    def analisar(self):
        """ Ponto de entrada da análise sintática. """
        arvore = self.programa()
        if self.token_atual is not None:
            raise SyntaxError(f"Erro Sintatico: Tokens inesperados no final do arquivo.")
        return arvore
    
    #Métodos da gramática

    def programa(self):
        # [PROGRAMA] -> (program) [ID] (;) [CORPO]

        no = NoArvore('PROGRAMA')
        no.adicionar_filho(self.processarTerminal('Prog'))
        no.adicionar_filho(self.processarTerminal('ID'))
        no.adicionar_filho(self.processarTerminal('PontV'))
        no.adicionar_filho(self.corpo())
        
        return no
    
    def corpo(self):
        # [CORPO] -> [DECLARACOES] (begin) [LISTA_COM] (end) | (begin) [LISTA_COM] (end)

        no = NoArvore('CORPO')
        
        if self.token_atual and self.token_atual.dado.token in self.FIRST['DECLARACOES']:
            no.adicionar_filho(self.declaracoes())
        no.adicionar_filho(self.processarTerminal('Begin'))
        no.adicionar_filho(self.lista_com())
        no.adicionar_filho(self.processarTerminal('End'))
        
        return no


    def declaracoes(self):
        # [DECLARACOES] -> [DEF_CONST] [DEF_TIPOS] [DEF_VAR] [LISTA_FUNC] | Є

        no = NoArvore('DECLARACOES')
        
        if self.token_atual and self.token_atual.dado.token in self.FIRST['DEF_CONST']:
            no.adicionar_filho(self.def_const())
        if self.token_atual and self.token_atual.dado.token in self.FIRST['DEF_TIPOS']:
            no.adicionar_filho(self.def_tipos())
        if self.token_atual and self.token_atual.dado.token in self.FIRST['DEF_VAR']:
            no.adicionar_filho(self.def_var())
        if self.token_atual and self.token_atual.dado.token in self.FIRST['LISTA_FUNC']:
            no.adicionar_filho(self.lista_func())
        
        return no
    
    def def_const(self):
        # [DEF_CONST] -> (const) [LISTA_CONST] | Є

        no = NoArvore('DEF_CONST')
        
        if self.token_atual and self.token_atual.dado.token in self.FIRST['DEF_CONST']:
            no.adicionar_filho(self.processarTerminal('Const'))
            no.adicionar_filho(self.lista_const())
        
        return no
    
    def lista_const(self):
        """
        Processa [LISTA_CONST] -> [CONSTANTE] [LISTA_CONST']
        e [LISTA_CONST'] -> (;) [LISTA_CONST] | Є de forma iterativa.
        """
        no = NoArvore('LISTA_CONST')

        no.adicionar_filho(self.constante())

        while self.token_atual and self.token_atual.dado.token == 'PontV':
            no.adicionar_filho(self.processarTerminal('PontV'))
            no.adicionar_filho(self.constante())
        
        return no
    
    def constante(self):
        # [CONSTANTE] -> [ID] (:=) [CONST_VALOR] (;)

        no = NoArvore('CONSTANTE')
        
        no.adicionar_filho(self.processarTerminal('ID'))
        no.adicionar_filho(self.processarTerminal('Atribuicao'))
        no.adicionar_filho(self.const_valor())
        no.adicionar_filho(self.processarTerminal('PontV'))
        
        return no
    
    def const_valor(self):
        # [CONST_VALOR] -> (“) sequência alfanumérica (“) | [EXP_MATEMATICA]

        no = NoArvore('CONST_VALOR')
        token_type = self.token_atual.dado.token if self.token_atual else None
        
        if token_type == 'Aspas': 
            no.adicionar_filho(self.processarTerminal('Aspas'))

            # No léxico, a sequência alfanumérica é reconhecida como uma série de IDs e Nums
            # Foi criado um pseudo não-terminal 'STRING_LITERAL' para agrupar essa sequência
            no_str = NoArvore('STRING_LITERAL')
            while self.token_atual and self.token_atual.dado.token != 'Aspas':
                if self.token_atual.dado.token in ['ID', 'Num']:
                    no_str.adicionar_filho(NoArvore(self.token_atual.dado))
                    self.avancar()
                else:
                    self.erro("'ID', 'Num' ou 'Aspas' para fechar a string")
            no.adicionar_filho(no_str)
            
            no.adicionar_filho(self.processarTerminal('Aspas'))
        
        elif token_type in self.FIRST['EXP_MAT']:
            no.adicionar_filho(self.exp_mat())

        else:
            self.erro(f"uma string(comecando por \") ou uma expressão matemática (comecando por ID, Num ou \'(\' )")    
        
        return no
    
    def def_tipos(self):
        # [DEF_TIPOS] -> (type) [LISTA_TIPOS] | Є

        no = NoArvore('DEF_TIPOS')
        token_type = self.token_atual.dado.token if self.token_atual else None

        if token_type == 'Type':
            no.adicionar_filho(self.processarTerminal('Type'))
            no.adicionar_filho(self.lista_tipos())
        
        return no

    def lista_com(self):
        # Este método é iterativo
        # [LISTA_COM] -> [COMANDO] (;) [LISTA_COM] | Є  

        no = NoArvore('LISTA_COM')
        token_type = self.token_atual.dado.token if self.token_atual else None

        if token_type in self.FIRST['COMANDO']:
            no.adicionar_filho(self.comando())

            while self.token_atual and self.token_atual.dado.token == 'PontV':
                no.adicionar_filho(self.processarTerminal('PontV'))
                no.adicionar_filho(self.comando())
        
        return no