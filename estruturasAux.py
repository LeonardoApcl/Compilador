class Token:
    def __init__(self, lexema, token, linha):
        self.lexema = lexema
        self.token = token
        self.linha = linha

    def __str__(self):
        """Representação em string para facilitar a visualização"""
        return f"Token: {self.token}, Lexema: {self.lexema}, Linha: {self.linha}"
    
class No:
    def __init__(self, dado = None):
        self.dado = dado
        self.prox = None

class Lista:
    def __init__(self):
        self.cab = None

    def append(self, dado):
        """Adiciona um novo nó ao final da lista."""
        novo_no = No(dado)
        
        if not self.cab:
            self.cab = novo_no
            return
        ult_no = self.cab
        
        while ult_no.prox:
            ult_no = ult_no.prox
        ult_no.prox = novo_no

    def __str__(self):
        """Retorna uma representação em string (uma tabela) da lista para impressão."""
        # 1. Define o cabeçalho da tabela
        # Usamos f-strings para alinhar o texto à esquerda (<) em um espaço fixo.
        header = f"{'Token':<15}{'Lexema':<25}{'Linha'}"
        separator = "-" * 50  # Uma linha separadora
        
        # Lista que vai guardar todas as linhas da tabela
        linhas_tabela = [header, separator]

        # 2. Itera sobre cada nó da lista para formatar os tokens
        atual = self.cab
        while atual:
            token_obj = atual.dado
            # Formata cada linha para se alinhar com o cabeçalho
            linha_formatada = f"{token_obj.token:<15}{token_obj.lexema:<25}{token_obj.linha}"
            linhas_tabela.append(linha_formatada)
            atual = atual.prox
        
        # 3. Junta todas as linhas com uma quebra de linha ("\n")
        return "\n".join(linhas_tabela)