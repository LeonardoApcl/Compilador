from anytree import Node, RenderTree
import graphviz

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

def gerar_visualizacao_graphviz(raiz, nome_arquivo='arvore_sintatica'):
    """
    Percorre a árvore sintática e gera uma visualização usando Graphviz.
    Salva o resultado em um arquivo .gv e renderiza uma imagem (ex: .png).
    """
    if not raiz:
        print("Árvore está vazia.")
        return

    # Cria um novo grafo direcionado
    dot = graphviz.Digraph(comment='Árvore Sintática', format='svg')
    dot.attr('node', shape='ellipse', style='rounded')
    dot.attr(rankdir='TB', size='8,5') # Top to Bottom layout

    # Contador global para garantir IDs únicos para cada nó
    node_counter = 0

    def _adicionar_nos_e_arestas(no_atual):
        """
        Função auxiliar recursiva para percorrer a árvore e adicionar
        nós e arestas (conexões) ao grafo do Graphviz.
        """
        nonlocal node_counter
        id_no_atual = f'node_{node_counter}'
        node_counter += 1

        # Formata o rótulo do nó
        if isinstance(no_atual.valor, Token):
            # Para nós terminais (folhas), mostra o tipo e o lexema
            label = f"{no_atual.valor.token}\n({no_atual.valor.lexema})"
            dot.node(id_no_atual, label, shape='box') # Nós de token com formato diferente
        else:
            # Para nós não-terminais, mostra o nome da regra
            label = str(no_atual.valor)
            dot.node(id_no_atual, label)

        # Para cada filho, adiciona o nó e a aresta que o conecta ao pai
        for filho in no_atual.filhos:
            id_filho = _adicionar_nos_e_arestas(filho)
            dot.edge(id_no_atual, id_filho)
        
        return id_no_atual

    # Inicia a recursão a partir da raiz
    _adicionar_nos_e_arestas(raiz)
    
    # Renderiza o grafo
    try:
        dot.render(nome_arquivo, view=True, cleanup=True)
        print(f"Árvore renderizada e salva como '{nome_arquivo}.svg'.")
    except graphviz.backend.ExecutableNotFound:
        print("\nERRO: O executável do Graphviz não foi encontrado.")
        print("Verifique se o Graphviz está instalado e se o seu diretório 'bin' está no PATH do sistema.")
        print(f"Arquivo DOT gerado: '{nome_arquivo}.gv'")
        dot.save(nome_arquivo + '.gv')