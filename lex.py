from estruturasAux import Token, No, Lista

class Lexico:
    def __init__(self, caminho_arquivo):
        try:
            with open(caminho_arquivo, 'r') as file:
                self.codigo_fonte = file.read()
        except FileNotFoundError:
            print(f"Erro: O arquivo '{caminho_arquivo}' não foi encontrado.")
            self.codigo_fonte = ""

        # Definições dos tokens:
        self.palavras_reservadas = {
            'program': 'Prog', 'begin': 'Begin', 'end': 'End',
            'const': 'Const', 'type': 'Type', 'var': 'Var',
            'function': 'Func', 'while': 'Loop', 'if': 'Se',
            'then': 'Entao', 'else': 'Senao', 'write': 'Escrita',
            'read': 'Leitura', 'integer': 'TipoSimples', 'real': 'TipoSimples',
            'array': 'Array', 'record': 'Record', 'of': 'Of'
        }
        self.simbolos = {
            ';': 'PontV', '=': 'OpLog', '<': 'OpLog', '>': 'OpLog', '!': 'OpLog',
            '+': 'OpMat', '-': 'OpMat', '*': 'OpMat', '/': 'OpMat',
            '[': 'AColch', ']': 'FColch', ':': 'DoisPt', ',': 'Virg',
            '(': 'AParent', ')': 'FParent', '\"': 'Aspas', '.': 'Pont'
        }
        self.simbolos_compostos = {':=': 'Atribuicao'}
    
    def analisar(self):
        tokens_encontrados = Lista()

        if not self.codigo_fonte :
            return tokens_encontrados
        
        pos = 0
        linha_atual = 1

        while pos < len(self.codigo_fonte):
            char_atual = self.codigo_fonte[pos]

            # 1. Ignorar espaços em branco e contar novas linhas
            if char_atual.isspace():
                if char_atual == '\n':
                    linha_atual += 1
                pos += 1
                continue

            # 2. Ignorar comentários (marcados do '#' até o próximo '#')
            if char_atual == '#':
                pos_inicial_comentario = pos
                pos += 1
                
                while pos < len(self.codigo_fonte) and self.codigo_fonte[pos] != '#':
                    # Ainda precisamos contar as novas linhas dentro do comentário
                    if self.codigo_fonte[pos] == '\n':
                        linha_atual += 1
                    pos += 1
                
                # Se saímos do laço, ou achamos o '#' final ou o arquivo acabou
                if pos < len(self.codigo_fonte):
                    pos += 1
                else:
                    # Se o arquivo terminar sem fechar o comentário, avisamos o erro
                    print(f"Erro lexico: Comentario iniciado na linha {linha_atual} nao foi fechado.")
                continue

             # 3. Checar símbolo composto (:=)
            if pos + 1 < len(self.codigo_fonte) and self.codigo_fonte[pos:pos+2] in self.simbolos_compostos:
                lexema = self.codigo_fonte[pos:pos+2]
                tipo = self.simbolos_compostos[lexema]
                tokens_encontrados.append(Token(lexema, tipo, linha_atual))
                pos += 2
                continue

            # 4. Checar símbolos simples
            if char_atual in self.simbolos:
                tipo = self.simbolos[char_atual]
                tokens_encontrados.append(Token(char_atual, tipo, linha_atual))
                pos += 1
                continue

            # 5. Checar por IDs e palavras reservadas
            if char_atual.isalpha():
                pos_inicial = pos
                pos += 1
                while pos < len(self.codigo_fonte) and self.codigo_fonte[pos].isalnum():
                    pos += 1
                
                lexema = self.codigo_fonte[pos_inicial:pos]
                # verifica se esse lexema é uma palavra reservada, caso não for, o lexema é classificado como ID
                tipo = self.palavras_reservadas.get(lexema.lower(), 'ID') 
                tokens_encontrados.append(Token(lexema, tipo, linha_atual))
                continue

            # 6. Checar por números
            if char_atual.isdigit():
                pos_inicial = pos
                ponto_encontrado = False
                pos += 1
                while pos < len(self.codigo_fonte):
                    char_seguinte = self.codigo_fonte[pos]
                    if char_seguinte.isdigit():
                        pos += 1
                    elif char_seguinte == '.' and not ponto_encontrado:
                        ponto_encontrado = True
                        pos += 1
                    else:
                        break # Encerra se encontrar algo que não seja dígito ou um segundo ponto
                
                lexema = self.codigo_fonte[pos_inicial:pos]
                tokens_encontrados.append(Token(lexema, 'Num', linha_atual))
                continue

            # Se nada corresponder, é um erro léxico
            print(f"Erro lexico: Caractere nao reconhecido '{char_atual}' na linha {linha_atual}.")
            pos += 1
    
        return tokens_encontrados