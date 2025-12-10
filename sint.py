from estruturasAux import NoArvore

class Sintatico:
    def __init__(self, lista_tokens):
        self.lista_tokens = lista_tokens
        self.token_atual = lista_tokens.cab if lista_tokens else None

        # --- DEFINIÇÃO DOS CONJUNTOS FIRST ---
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
            'BLOCO_FUNCAO': {'Var', 'Begin', 'ID', 'Loop', 'Se', 'Escrita', 'Leitura'},
            'BLOCO'       : {'Begin', 'ID', 'Loop', 'Se', 'Escrita', 'Leitura'},
            'LISTA_COM'   : {'ID', 'Loop', 'Se', 'Escrita', 'Leitura'},
            'COMANDO'     : {'ID', 'Loop', 'Se', 'Escrita', 'Leitura'},
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
            'NOME_'       : {'Pont', 'AColch', 'AParent'},
        }
        
        # O self.FOLLOW não precisa ser alterado para fazer o código funcionar,
        # pois o analisador atual não implementa recuperação de erro (Modo Pânico).
        self.FOLLOW = {} 

    def erro(self, esperado, NT):
        if self.token_atual:
            print(
                f"Erro Sintatico na linha {self.token_atual.dado.linha}: "
                f"Esperado {esperado}, mas encontrou '{self.token_atual.dado.lexema}'"
            )
        else:
            print(f"Erro Sintatico: Esperado {esperado}, mas o arquivo terminou.")

    def avancar(self):
        if self.token_atual:
            self.token_atual = self.token_atual.prox

    def processarTerminal(self, token_esperado, NT):
        if self.token_atual and self.token_atual.dado.token == token_esperado:
            objeto_token = self.token_atual.dado
            no = NoArvore(objeto_token)
            self.avancar()
            return no
        else:
            self.erro(token_esperado, NT)

    def analisar(self):
        """ Ponto de entrada da análise sintática. """
        arvore = self.programa()
        if self.token_atual is not None:
            print(f"Erro Sintatico: Tokens inesperados no final do arquivo ({self.token_atual.dado.lexema}).\n")
        return arvore
    
    # --- MÉTODOS DA GRAMÁTICA ---

    def programa(self):
        no = NoArvore('PROGRAMA')
        no.adicionar_filho(self.processarTerminal('Prog','PROGRAMA'))
        no.adicionar_filho(self.processarTerminal('ID','PROGRAMA'))
        no.adicionar_filho(self.processarTerminal('PontV','PROGRAMA'))
        no.adicionar_filho(self.corpo())
        return no
    
    def corpo(self):
        no = NoArvore('CORPO')
        if self.token_atual and self.token_atual.dado.token in self.FIRST['DECLARACOES']:
            no.adicionar_filho(self.declaracoes())
        no.adicionar_filho(self.processarTerminal('Begin','CORPO'))
        no.adicionar_filho(self.lista_com())
        no.adicionar_filho(self.processarTerminal('End','CORPO'))
        return no

    def declaracoes(self):
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
        no = NoArvore('DEF_CONST')
        if self.token_atual and self.token_atual.dado.token in self.FIRST['DEF_CONST']:
            no.adicionar_filho(self.processarTerminal('Const','DEF_CONST'))
            no.adicionar_filho(self.lista_const())
        return no
    
    def lista_const(self):
        no = NoArvore('LISTA_CONST')
        no.adicionar_filho(self.constante())
        while self.token_atual and self.token_atual.dado.token == 'PontV':
            no.adicionar_filho(self.processarTerminal('PontV','LISTA_CONST'))
            if self.token_atual and self.token_atual.dado.token in self.FIRST['CONSTANTE']:
                no.adicionar_filho(self.constante())
            else:
                break
        return no
    
    def constante(self):
        no = NoArvore('CONSTANTE')
        no.adicionar_filho(self.processarTerminal('ID','CONSTANTE'))
        no.adicionar_filho(self.processarTerminal('Atribuicao','CONSTANTE'))
        no.adicionar_filho(self.const_valor())
        return no
    
    def const_valor(self):
        no = NoArvore('CONST_VALOR')
        token_type = self.token_atual.dado.token if self.token_atual else None
        
        if token_type == 'Aspas': 
            no.adicionar_filho(self.processarTerminal('Aspas','CONST_VALOR'))
            no_str = NoArvore('STRING_LITERAL')
            while self.token_atual and self.token_atual.dado.token != 'Aspas':
                if self.token_atual.dado.token in ['ID', 'Num']:
                    no_str.adicionar_filho(NoArvore(self.token_atual.dado))
                    self.avancar()
                else:
                    self.erro("'ID', 'Num' ou 'Aspas'", 'CONST_VALOR')
            no.adicionar_filho(no_str)
            no.adicionar_filho(self.processarTerminal('Aspas','CONST_VALOR'))
        
        elif token_type in self.FIRST['EXP_MAT']:
            no.adicionar_filho(self.exp_mat())
        else:
            self.erro(f"string ou expressao", 'CONST_VALOR')    
        return no
    
    def def_tipos(self):
        no = NoArvore('DEF_TIPOS')
        if self.token_atual and self.token_atual.dado.token == 'Type':
            no.adicionar_filho(self.processarTerminal('Type','DEF_TIPOS'))
            no.adicionar_filho(self.lista_tipos())
        return no
    
    def lista_tipos(self):
        no = NoArvore('LISTA_TIPOS')
        no.adicionar_filho(self.tipo())
        while self.token_atual and self.token_atual.dado.token == 'PontV':
            no.adicionar_filho(self.processarTerminal('PontV','LISTA_TIPOS'))
            if self.token_atual and self.token_atual.dado.token in self.FIRST['TIPO']:
                no.adicionar_filho(self.tipo())
            else:
                break
        return no
    
    def tipo(self):
        no = NoArvore('TIPO')
        no.adicionar_filho(self.processarTerminal('ID','TIPO'))
        no.adicionar_filho(self.processarTerminal('Atribuicao','TIPO'))
        no.adicionar_filho(self.tipo_dado())
        return no
    
    def tipo_dado(self):
        no = NoArvore('TIPO_DADO')
        token_type = self.token_atual.dado.token if self.token_atual else None
        
        if token_type == 'TipoSimples': 
            no.adicionar_filho(self.processarTerminal('TipoSimples', 'TIPO_DADO'))
        elif token_type == 'Array':
            no.adicionar_filho(self.processarTerminal('Array', 'TIPO_DADO'))
            no.adicionar_filho(self.processarTerminal('AColch', 'TIPO_DADO'))
            no.adicionar_filho(self.processarTerminal('Num', 'TIPO_DADO'))
            no.adicionar_filho(self.processarTerminal('FColch', 'TIPO_DADO'))
            no.adicionar_filho(self.processarTerminal('Of', 'TIPO_DADO'))
            no.adicionar_filho(self.tipo_dado())
        elif token_type == 'Record': 
            no.adicionar_filho(self.processarTerminal('Record', 'TIPO_DADO'))
            no.adicionar_filho(self.lista_var())
            no.adicionar_filho(self.processarTerminal('End', 'TIPO_DADO'))
        elif token_type == 'ID': 
            no.adicionar_filho(self.processarTerminal('ID', 'TIPO_DADO'))
        else:
            self.erro(f"tipo simples, array, record ou ID", 'TIPO_DADO')
        return no

    def def_var(self):
        no = NoArvore('DEF_VAR')
        if self.token_atual and self.token_atual.dado.token == 'Var':
            no.adicionar_filho(self.processarTerminal('Var','DEF_VAR'))
            no.adicionar_filho(self.lista_var())
        return no
    
    def lista_var(self):
        no = NoArvore('LISTA_VAR')
        no.adicionar_filho(self.variavel())
        while self.token_atual and self.token_atual.dado.token == 'PontV':
            no.adicionar_filho(self.processarTerminal('PontV', 'LISTA_VAR'))
            if self.token_atual and self.token_atual.dado.token in self.FIRST['VARIAVEL']:
                no.adicionar_filho(self.variavel())
            else:
                break
        return no
    
    def variavel(self):
        no = NoArvore('VARIAVEL')
        no.adicionar_filho(self.lista_id())
        no.adicionar_filho(self.processarTerminal('DoisPt','VARIAVEL'))
        no.adicionar_filho(self.tipo_dado())
        return no
    
    def lista_id(self):
        no = NoArvore('LISTA_ID')
        no.adicionar_filho(self.processarTerminal('ID','LISTA_ID'))
        while self.token_atual and self.token_atual.dado.token == 'Virg':
            no.adicionar_filho(self.processarTerminal('Virg','LISTA_ID'))
            if self.token_atual and self.token_atual.dado.token == 'ID':
                no.adicionar_filho(self.processarTerminal('ID','LISTA_ID'))
            else:
                break
        return no

    def lista_com(self):
        no = NoArvore('LISTA_COM')
        if self.token_atual and self.token_atual.dado.token in self.FIRST['COMANDO']:
            no.adicionar_filho(self.comando())
            while self.token_atual and self.token_atual.dado.token == 'PontV':
                no.adicionar_filho(self.processarTerminal('PontV','LISTA_COM'))
                if self.token_atual and self.token_atual.dado.token in self.FIRST['COMANDO']:
                    no.adicionar_filho(self.comando())
                else:
                    break
        return no
        
    def lista_func(self):
        no = NoArvore('LISTA_FUNC')  
        while self.token_atual and self.token_atual.dado.token in self.FIRST['FUNCAO']:
            no.adicionar_filho(self.funcao())
        return no
    
    def funcao(self):
        no = NoArvore('FUNCAO')
        no.adicionar_filho(self.nome_funcao())
        no.adicionar_filho(self.bloco_funcao())
        return no
    
    def nome_funcao(self):
        no = NoArvore('NOME_FUNCAO')
        no.adicionar_filho(self.processarTerminal('Func', 'NOME_FUNCAO'))
        no.adicionar_filho(self.processarTerminal('ID', 'NOME_FUNCAO'))
        no.adicionar_filho(self.processarTerminal('AParent', 'NOME_FUNCAO'))
        no.adicionar_filho(self.lista_var())
        no.adicionar_filho(self.processarTerminal('FParent', 'NOME_FUNCAO'))
        no.adicionar_filho(self.processarTerminal('DoisPt', 'NOME_FUNCAO'))
        no.adicionar_filho(self.tipo_dado())
        return no
    
    def bloco_funcao(self):
        no = NoArvore('BLOCO_FUNCAO')
        token_type = self.token_atual.dado.token if self.token_atual else None
        if token_type == 'Var':
            no.adicionar_filho(self.def_var())
        no.adicionar_filho(self.bloco())
        return no
    
    def bloco(self):
        no = NoArvore('BLOCO')
        token_type = self.token_atual.dado.token if self.token_atual else None
        if token_type in self.FIRST['BLOCO']:
            if token_type == 'Begin':
                no.adicionar_filho(self.processarTerminal('Begin','BLOCO'))
                no.adicionar_filho(self.lista_com())
                no.adicionar_filho(self.processarTerminal('End','BLOCO'))
            else:
                no.adicionar_filho(self.comando())
        else:
            self.erro(f"'begin' ou comando", 'BLOCO')
        return no
    
    def comando(self):
        no = NoArvore('COMANDO')
        token_type = self.token_atual.dado.token if self.token_atual else None
        
        if token_type == 'ID':
            no.adicionar_filho(self.nome())
            no.adicionar_filho(self.processarTerminal('Atribuicao', 'COMANDO'))
            no.adicionar_filho(self.valor())
        elif token_type == 'Loop':
            no.adicionar_filho(self.processarTerminal('Loop', 'COMANDO'))
            no.adicionar_filho(self.exp_logica())
            no.adicionar_filho(self.bloco())
        elif token_type == 'Se':
            no.adicionar_filho(self.processarTerminal('Se', 'COMANDO'))
            no.adicionar_filho(self.exp_logica())
            no.adicionar_filho(self.processarTerminal('Entao', 'COMANDO'))
            no.adicionar_filho(self.bloco())
            no.adicionar_filho(self.senao()) #else
        elif token_type == 'Escrita':
            no.adicionar_filho(self.processarTerminal('Escrita', 'COMANDO'))
            no.adicionar_filho(self.const_valor())
        elif token_type == 'Leitura':
            no.adicionar_filho(self.processarTerminal('Leitura', 'COMANDO'))
            no.adicionar_filho(self.nome())
        else:
            self.erro(f"Comando invalido", 'COMANDO')
        return no
        
    def senao(self):
        no = NoArvore('ELSE')
        if self.token_atual and self.token_atual.dado.token == 'Senao':
            no.adicionar_filho(self.processarTerminal('Senao','ELSE'))
            no.adicionar_filho(self.bloco())
        return no
    
    def valor(self):
        # [VALOR] -> [EXP_MAT]
        # Nota: Simplificado para chamar exp_mat direto, pois exp_mat agora cobre ID e Funções
        no = NoArvore('VALOR')
        token_type = self.token_atual.dado.token if self.token_atual else None
        
        if token_type in self.FIRST['EXP_MAT']:
            no.adicionar_filho(self.exp_mat())
        else:
            self.erro(f"expressao", 'VALOR')
        return no
        
    def lista_param(self):
        no = NoArvore('LISTA_PARAM')
        no.adicionar_filho(self.processarTerminal('AParent','LISTA_PARAM'))   
        no.adicionar_filho(self.lista_nome())
        no.adicionar_filho(self.processarTerminal('FParent','LISTA_PARAM'))
        return no
        
    def lista_nome(self):
        no = NoArvore('LISTA_NOME')
        token_type = self.token_atual.dado.token if self.token_atual else None
        
        # MUDANÇA: Aceita EXP_MAT (para argumentos como n-1)
        if token_type in self.FIRST['EXP_MAT']:
            no.adicionar_filho(self.exp_mat()) # Chama exp_mat em vez de parametro

            while self.token_atual and self.token_atual.dado.token == 'Virg':
                no.adicionar_filho(self.processarTerminal('Virg','LISTA_NOME'))
                if self.token_atual and self.token_atual.dado.token in self.FIRST['EXP_MAT']:
                    no.adicionar_filho(self.exp_mat())
                else:
                    self.erro(f"argumento valido", 'LISTA_NOME')
        return no
    
    def exp_logica(self):
        no = NoArvore('EXP_LOGICA')
        no.adicionar_filho(self.exp_mat())
        while self.token_atual and self.token_atual.dado.token == 'OpLog':
            no.adicionar_filho(self.op_logico())
            no.adicionar_filho(self.exp_mat())
        return no
        
    def exp_mat(self):
        no = NoArvore('EXP_MAT')
        no.adicionar_filho(self.parametro())
        while self.token_atual and self.token_atual.dado.token == 'OpMat':
                no.adicionar_filho(self.op_mat())
                no.adicionar_filho(self.parametro())
        return no
        
    def parametro(self):
        # [PARAMETRO] -> [NOME] | [NUMERO] | ( [EXP_MAT] )
        no = NoArvore('PARAMETRO')
        token_type = self.token_atual.dado.token if self.token_atual else None
        
        if token_type == 'AParent': # MUDANÇA: Suporte a parenteses (a+b)
            no.adicionar_filho(self.processarTerminal('AParent', 'PARAMETRO'))
            no.adicionar_filho(self.exp_mat())
            no.adicionar_filho(self.processarTerminal('FParent', 'PARAMETRO'))
        elif token_type in self.FIRST['NOME']:
            no.adicionar_filho(self.nome())
        elif token_type == 'Num':
            no.adicionar_filho(self.processarTerminal('Num','PARAMETRO'))
        else:
            self.erro(f"ID, numero ou '('", 'PARAMETRO')
        return no
        
    def op_logico(self):
        no = NoArvore('OP_LOGICO')
        no.adicionar_filho(self.processarTerminal('OpLog','OP_LOGICO'))
        return no
        
    def op_mat(self):
        no = NoArvore('OP_MAT')
        no.adicionar_filho(self.processarTerminal('OpMat','OP_MAT'))
        return no
        
    def nome(self):
        # [NOME]  -> [ID] [NOME’]
        # [NOME’] -> .[NOME] | ([) [PARAMETRO] (]) | ( [LISTA_PARAM] ) | Є
        no = NoArvore('NOME')
        no.adicionar_filho(self.processarTerminal('ID','NOME'))
        
        while self.token_atual and self.token_atual.dado.token in self.FIRST['NOME_']:
            token_type = self.token_atual.dado.token
            no_nome_linha = NoArvore('NOME_LINHA')

            if token_type == 'Pont':
                no_nome_linha.adicionar_filho(self.processarTerminal('Pont','NOME'))
                no_nome_linha.adicionar_filho(self.processarTerminal('ID','NOME'))
                no.adicionar_filho(no_nome_linha)
            elif token_type == 'AColch':
                no_nome_linha.adicionar_filho(self.processarTerminal('AColch','NOME'))
                no_nome_linha.adicionar_filho(self.parametro())
                no_nome_linha.adicionar_filho(self.processarTerminal('FColch','NOME'))
                no.adicionar_filho(no_nome_linha)
            elif token_type == 'AParent': # MUDANÇA: Suporte a chamada de função f()
                no_nome_linha.adicionar_filho(self.lista_param())
                no.adicionar_filho(no_nome_linha)
                
        return no