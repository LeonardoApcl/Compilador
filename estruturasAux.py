from anytree import Node, RenderTree

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
    
class NoArvore:
    def __init__(self, valor):
        self.valor = valor
        self.filhos = []

    def adicionar_filho(self, no):
        self.filhos.append(no)

    def __str__(self, nivel=0):
        # Representação visual da árvore 
        prefixo = "  " * nivel
        
        # Verifica se o valor no nó é um objeto Token ou uma string
        if isinstance(self.valor, Token):
            # Se for um Token, imprime de forma mais detalhada
            valor_str = f"Token({self.valor.token}, '{self.valor.lexema}')"
        else:
            # Se for uma string (como 'PROGRAMA'), apenas a exibe
            valor_str = repr(self.valor)

        ret = prefixo + valor_str + "\n"
        for filho in self.filhos:
            ret += filho.__str__(nivel + 1)
        return ret
    
def visualizar_com_anytree(raiz_original):
    """
    Converte a árvore sintática (NoArvore) para uma árvore no formato da
    biblioteca anytree e a imprime no console.
    """
    if not raiz_original:
        print("Árvore está vazia.")
        return

    def _converter_arvore(no_original, parent=None):
        """
        Função recursiva que converte a estrutura NoArvore para anytree.Node.
        """
        # Formata o rótulo do nó
        if isinstance(no_original.valor, Token):
            label = f"{no_original.valor.token} ({no_original.valor.lexema})"
        else:
            label = str(no_original.valor)
        
        # Cria o nó no formato do anytree, especificando o pai
        novo_no = Node(label, parent=parent)

        # Chama recursivamente para os filhos
        for filho in no_original.filhos:
            _converter_arvore(filho, parent=novo_no)
        
        return novo_no

    # Inicia a conversão a partir da raiz
    raiz_anytree = _converter_arvore(raiz_original)

    # Usa o RenderTree para imprimir a árvore de forma bonita
    for pre, fill, node in RenderTree(raiz_anytree):
        print(f"{pre}{node.name}")