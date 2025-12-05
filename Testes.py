#Código criado para realizar testes na análise léxica

from estruturasAux import visualizar_com_anytree, gerar_visualizacao_graphviz
from lex import Lexico
from sint import Sintatico

arquivos_teste_lexico = {
    #"Testes/Lexico/teste_basico.txt",
    #"Testes/Lexico/teste_completo.txt",
    #"Testes/Lexico/teste_comentarios.txt",
    #"Testes/Lexico/teste_com_erros.txt",
    #"Testes/Lexico/teste_especial.txt",
    "Testes/Sintatico/teste_declaracoes.txt",
}
arquivos_teste_sintatico = {
    #"Testes/Sintatico/teste_acessos.txt",
    "Testes/Sintatico/teste_declaracoes.txt",
    #"Testes/Sintatico/teste_estruturas_controle.txt",
    #"Testes/Sintatico/teste_sintaxe_invalida.txt",
}

def executar():
    for nome_arquivo in arquivos_teste_sintatico:
        print(f">>> ANALISANDO ARQUIVO: {nome_arquivo} <<<\n")
        
        #print("Analise lexica!! \n")
        analisador = Lexico(nome_arquivo)
        lista_de_tokens = analisador.analisar()
        
        # Imprime a lista de tokens (ou mensagens de erro que o analisador gerou)
        print(lista_de_tokens)
        
        print("\n" + "="*50 + "\n")

        print("Analise sintatica!! \n")
        analisadorSint = Sintatico(lista_de_tokens)
        arvore_sintatica = analisadorSint.analisar()

        visualizar_com_anytree(arvore_sintatica)
        print("\n" + "="*50 + "\n")

        try:
            gerar_visualizacao_graphviz(arvore_sintatica, 'arvore_simples')
        
        except SyntaxError as e:
            print(e)
        except Exception as e:
            print(f"Ocorreu um erro inesperado: {e}")

if __name__ == "__main__":
    executar()