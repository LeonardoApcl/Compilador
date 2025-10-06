#Código criado para realizar testes na análise léxica

from lex import Lexico
from sint import Sintatico

arquivos_teste = {
    "teste_basico.txt",
    "teste_completo.txt",
    "teste_comentarios.txt",
    "teste_com_erros.txt",
    "teste_especial.txt"
}

def executar():
    for nome_arquivo in arquivos_teste:
        print(f">>> ANALISANDO ARQUIVO: {nome_arquivo} <<<\n")
        
        analisador = Lexico(nome_arquivo)
        lista_de_tokens = analisador.analisar()
        
        # Imprime a lista de tokens (ou mensagens de erro que o analisador gerou)
        print(lista_de_tokens)
        
        print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    # executar()
    print("Analise lexica!! \n")
    analisadorLex = Lexico("teste_sint_comandos.txt")
    lista_de_tokens = analisadorLex.analisar()

    print(lista_de_tokens)
    print("\n" + "="*50 + "\n")

    print("Analise sintatica!! \n")
    analisadorSint = Sintatico(lista_de_tokens)
    arvore_sintatica = analisadorSint.analisar()

    print(arvore_sintatica)
    print("\n" + "="*50 + "\n")