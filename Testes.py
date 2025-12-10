#Código criado para realizar testes na análise léxica

from estruturasAux import visualizar_com_anytree, gerar_visualizacao_graphviz
from lex import Lexico
from sint import Sintatico
from seman import Semantico
from icode import CodigoIntermediario

arquivos_teste_lexico = {
    #"Testes/Lexico/teste_basico.txt",
    "Testes/Lexico/teste_completo.txt",
    #"Testes/Lexico/teste_comentarios.txt",
    #"Testes/Lexico/teste_com_erros.txt",
    #"Testes/Lexico/teste_especial.txt",
    #"Testes/Sintatico/teste_declaracoes.txt",
}
arquivos_teste_sintatico = {
    #"Testes/Sintatico/teste_acessos.txt",
    #"Testes/Sintatico/teste_declaracoes.txt",
    "Testes/Sintatico/teste_estruturas_controle.txt",
    #"Testes/Sintatico/teste_sintaxe_invalida.txt",
}
arquivos_teste_semantico = {
    "Testes/Semantico/teste_sucesso_completo.txt",
    #"Testes/Semantico/teste_semantico_interme.txt",
    #"Testes/Semantico/teste_alias.txt",
    #"Testes/Semantico/teste_erros_estruturas.txt",
    #"Testes/Semantico/teste_erro_tipos_func.txt",
}

def executar():
    for nome_arquivo in arquivos_teste_semantico:
        print(f">>> ANALISANDO ARQUIVO: {nome_arquivo} <<<\n")
        
        print("Analise lexica!! \n")
        analisadorLex = Lexico(nome_arquivo)
        lista_de_tokens = analisadorLex.analisar()
        #print(lista_de_tokens)
        print("\n" + "="*50 + "\n")

        print("Analise sintatica!! \n")
        analisadorSint = Sintatico(lista_de_tokens)
        arvore_sintatica = analisadorSint.analisar()
        #visualizar_com_anytree(arvore_sintatica)
        print("\n" + "="*50 + "\n")

        if not arvore_sintatica:
            print("Árvore sintática não gerada devido a erros.")
            continue

        print("Analise semantica!! \n")
        analisadorSem = Semantico(arvore_sintatica)
        tabela_de_simbolos = analisadorSem.analisar()
        
        if tabela_de_simbolos:
            print(tabela_de_simbolos)
        else:
            print("Erro na análise semântica. Código Intermediário abortado.")
            continue # Não gera código se tiver erro semântico
        
        print("\n" + "="*50 + "\n")
        
        print("Geração de Cod. intermediário !! \n")

        gerador = CodigoIntermediario(arvore_sintatica)
        instrucoes = gerador.gerar()

        print("Lista de Instruções Gerada:")
        print("-" * 30)
        for i, instr in enumerate(instrucoes):
            print(f"{i}: {instr}")
        print("-" * 30)
        
        print("\n" + "="*50 + "\n")

        try:
            gerar_visualizacao_graphviz(arvore_sintatica, 'arvore_simples')
        
        except SyntaxError as e:
            print(e)
        except Exception as e:
            print(f"Ocorreu um erro inesperado: {e}")

if __name__ == "__main__":
    executar()