from estruturasAux import Simbolo

class TabelaSimbolos:
    def __init__(self):
        # Armazenamento Permanente (Tabela Mestra)
        self.tabela_mestra = [] 
        
        # Controle de Visibilidade (Pilha de Escopos)
        # Começa com o escopo Global
        self.pilha_escopos = [{
            "nome": "Global",
            "simbolos": [] 
        }]

    def entrar_escopo(self, nome_escopo):
        """ Empilha um novo contexto de visibilidade. """
        self.pilha_escopos.append({
            "nome": nome_escopo,
            "simbolos": []
        })

    def sair_escopo(self):
        """ Desempilha o contexto atual. """
        if len(self.pilha_escopos) > 1:
            self.pilha_escopos.pop()
        else:
            print("Erro Interno: Tentativa de fechar o escopo Global.")

    def obter_escopo_atual_nome(self):
        return self.pilha_escopos[-1]["nome"]

    def declarar(self, token_id, classificacao, tipo, qtd=None, ordem=None, params_tipos=None):
        """
        Regra 1: Não declarar mais de 1 ID com mesmo nome no mesmo escopo.
        """
        lexema = token_id.lexema
        escopo_atual = self.pilha_escopos[-1]
        
        # Verifica duplicidade no escopo atual
        for simb in escopo_atual["simbolos"]:
            if simb.nome == lexema:
                print(f"Erro Semântico (Regra 1): '{lexema}' já declarado em '{escopo_atual['nome']}' (Linha {token_id.linha}).")
                return None 

        # Cria o Símbolo
        novo_simbolo = Simbolo(
            nome=lexema,
            classificacao=classificacao,
            tipo=tipo,
            escopo=escopo_atual["nome"],
            Qtd=qtd,
            ordem=ordem,
            linha=token_id.linha
        )
        
        # Hack para guardar tipos dos parâmetros (para validação da Regra 6)
        if params_tipos:
            novo_simbolo.params_tipos = params_tipos

        # Salva nas duas estruturas
        self.tabela_mestra.append(novo_simbolo)
        escopo_atual["simbolos"].append(novo_simbolo)
        
        return novo_simbolo

    def consultar(self, token_id):
        """
        Regra 2: Declaração de Id no escopo antes do uso.
        Busca do escopo atual até o Global.
        """
        lexema = token_id.lexema
        for escopo in reversed(self.pilha_escopos):
            for simb in escopo["simbolos"]:
                if simb.nome == lexema:
                    return simb
        return None

    # --- ESTE É O MÉTODO QUE ESTAVA FALTANDO ---
    def consultar_campo_record(self, nome_campo, nome_tipo_record):
        """
        Regra 9 e 10: Busca um campo dentro de um escopo específico de record/classe.
        """
        # Precisamos buscar na tabela mestra símbolos cujo escopo seja igual ao nome do record (ex: record_def_linha_10)
        # E cujo nome seja o nome do campo (ex: 'id' ou 'vetor')
        for simb in self.tabela_mestra:
            if simb.escopo == nome_tipo_record and simb.nome == nome_campo:
                return simb
        return None
    # -------------------------------------------
    
    def atualizar_qtd_params(self, nome_funcao, nova_qtd, lista_tipos):
        """ Atualiza info da função na tabela mestra após processar os parâmetros """
        # Busca no escopo Global (ou atual)
        for simb in reversed(self.tabela_mestra):
            if simb.nome == nome_funcao and simb.classificacao == 'funcao':
                simb.qtd = nova_qtd
                simb.params_tipos = lista_tipos 
                return

    def __str__(self):
        # 1. Definir os cabeçalhos das colunas
        headers = ["Nome", "Classificacao", "Tipo", "Escopo", "Qtd", "Ordem"]

        # 2. Coletar todos os dados em formato de lista de strings (Matriz de dados)
        rows = []
        for simb in self.tabela_mestra:
            # Tratamento de valores nulos para visualização (None vira "-")
            qtd_str = str(simb.qtd) if simb.qtd is not None else "-"
            ordem_str = str(simb.ordem) + "º" if simb.ordem is not None else "-"
            
            row = [
                str(simb.nome),
                str(simb.classificacao),
                str(simb.tipo),
                str(simb.escopo),
                qtd_str,
                ordem_str
            ]
            rows.append(row)

        # 3. Calcular a largura máxima necessária para cada coluna automaticamente
        # Começamos com a largura do próprio cabeçalho
        col_widths = [len(h) for h in headers]

        for row in rows:
            for i, val in enumerate(row):
                # Se o dado for maior que a largura atual, atualizamos a largura da coluna
                if len(val) > col_widths[i]:
                    col_widths[i] = len(val)

        # 4. Criar a string de formatação dinâmica
        # Ex: "{:<20} | {:<15} | ..."
        # O ":<" alinha à esquerda. Adicionamos o width calculado.
        format_string = " | ".join([f"{{:<{w}}}" for w in col_widths])

        # 5. Montar a tabela final para impressão
        output = []
        
        # Calcula o tamanho total da linha para fazer o separador
        # (Soma das larguras + 3 caracteres " | " para cada separação)
        total_width = sum(col_widths) + (3 * (len(headers) - 1))
        separator = "-" * total_width

        # Montagem visual
        output.append("TABELA DE SÍMBOLOS")
        output.append(separator)
        output.append(format_string.format(*headers)) # Imprime Cabeçalho alinhado
        output.append(separator)

        for row in rows:
            output.append(format_string.format(*row)) # Imprime cada linha alinhada

        output.append(separator)

        return "\n".join(output)