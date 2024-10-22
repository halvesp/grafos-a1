import numpy as np
import json
import networkx as nx
import matplotlib.pyplot as plt

class Usuario:
    def __init__(self, id_usuario, nome, idade_conta, atividade_media):
        self.id_usuario = id_usuario
        self.nome = nome
        self.idade_conta = idade_conta  # em dias
        self.atividade_media = atividade_media  # interações por dia

    def atualizar(self, nome=None, idade_conta=None, atividade_media=None):
        if nome:
            self.nome = nome
        if idade_conta:
            self.idade_conta = idade_conta
        if atividade_media:
            self.atividade_media = atividade_media

    def to_dict(self):
        return {
            'id_usuario': self.id_usuario,
            'nome': self.nome,
            'idade_conta': self.idade_conta,
            'atividade_media': self.atividade_media
        }

    @staticmethod
    def from_dict(data):
        return Usuario(
            data['id_usuario'],
            data['nome'],
            data['idade_conta'],
            data['atividade_media']
        )

    def __str__(self):
        return f"ID: {self.id_usuario}, Nome: {self.nome}, Idade da Conta: {self.idade_conta} dias, Atividade Média: {self.atividade_media} interações/dia"

class GrafoRedeSocial:
    def __init__(self):
        self.usuarios = {}
        self.matriz_adj = np.array([[]])
        self.is_digrafo = True
        self.is_ponderado = True
        self.id_to_index = {}
        self.index_to_id = []

    def carregar_grafo(self, arquivo):
        try:
            with open(arquivo, 'r') as f:
                data = json.load(f)
            self.usuarios = {int(k): Usuario.from_dict(v) for k, v in data['usuarios'].items()}
            self.matriz_adj = np.array(data['matriz_adj'])
            self.id_to_index = {int(k): v for k, v in data['id_to_index'].items()}
            self.index_to_id = [int(id_) for id_ in data['index_to_id']]
        except Exception as e:
            print(f"Erro ao carregar o grafo: {e}")
            raise e 

    def salvar_grafo(self, arquivo):
        try:
            data = {
                'usuarios': {k: v.to_dict() for k, v in self.usuarios.items()},
                'matriz_adj': self.matriz_adj.tolist(),
                'id_to_index': self.id_to_index,
                'index_to_id': self.index_to_id
            }
            with open(arquivo, 'w') as f:
                json.dump(data, f, indent=4)
            print(f"Grafo salvo com sucesso em {arquivo}.")
        except Exception as e:
            print(f"Erro ao salvar o grafo: {e}")

    def exportar_grafo(self, arquivo):
        try:
            with open(arquivo, 'w') as f:
                f.write("id_usuario,nome,idade_conta,atividade_media\n")
                for usuario in self.usuarios.values():
                    f.write(f"{usuario.id_usuario},{usuario.nome},{usuario.idade_conta},{usuario.atividade_media}\n")
                f.write("\nMatriz de Adjacência:\n")
                np.savetxt(f, self.matriz_adj, fmt='%d')
            print(f"Grafo exportado com sucesso para {arquivo}.")
        except Exception as e:
            print(f"Erro ao exportar o grafo: {e}")

    def adicionar_usuario(self, usuario):
        if usuario.id_usuario in self.usuarios:
            print(f"Usuário com ID {usuario.id_usuario} já existe. Atualizando informações.")
            self.atualizar_usuario(usuario.id_usuario, nome=usuario.nome, idade_conta=usuario.idade_conta, atividade_media=usuario.atividade_media)
        else:
            self.usuarios[usuario.id_usuario] = usuario
            self.index_to_id.append(usuario.id_usuario)
            self.id_to_index[usuario.id_usuario] = len(self.index_to_id) - 1
            tamanho = len(self.index_to_id)
            if self.matriz_adj.size == 0:
                self.matriz_adj = np.zeros((1,1))
            else:
                nova_matriz = np.zeros((tamanho, tamanho))
                nova_matriz[:tamanho-1, :tamanho-1] = self.matriz_adj
                self.matriz_adj = nova_matriz

    def remover_usuario(self, id_usuario):
        if id_usuario in self.usuarios:
            indice = self.id_to_index[id_usuario]
            self.matriz_adj = np.delete(self.matriz_adj, indice, axis=0)
            self.matriz_adj = np.delete(self.matriz_adj, indice, axis=1)
            del self.usuarios[id_usuario]
            del self.id_to_index[id_usuario]
            self.index_to_id.pop(indice)
            # Atualizar índices dos usuários seguintes
            for idx in range(indice, len(self.index_to_id)):
                user_id = self.index_to_id[idx]
                self.id_to_index[user_id] = idx
        else:
            print("Usuário não encontrado.")

    def adicionar_aresta(self, id_origem, id_destino, peso=1):
        if id_origem in self.usuarios and id_destino in self.usuarios:
            indice_origem = self.id_to_index[id_origem]
            indice_destino = self.id_to_index[id_destino]
            self.matriz_adj[indice_origem][indice_destino] = peso
        else:
            print("Um dos usuários não existe.")

    def remover_aresta(self, id_origem, id_destino):
        if id_origem in self.usuarios and id_destino in self.usuarios:
            indice_origem = self.id_to_index[id_origem]
            indice_destino = self.id_to_index[id_destino]
            self.matriz_adj[indice_origem][indice_destino] = 0
        else:
            print("Um dos usuários não existe.")

    def atualizar_usuario(self, id_usuario, **kwargs):
        if id_usuario in self.usuarios:
            self.usuarios[id_usuario].atualizar(**kwargs)
        else:
            print("Usuário não encontrado.")

    def consultar_usuario(self, id_usuario):
        if id_usuario in self.usuarios:
            print(self.usuarios[id_usuario])
        else:
            print("Usuário não encontrado.")

    def consultar_aresta(self, id_origem, id_destino):
        if id_origem in self.usuarios and id_destino in self.usuarios:
            indice_origem = self.id_to_index[id_origem]
            indice_destino = self.id_to_index[id_destino]
            peso = self.matriz_adj[indice_origem][indice_destino]
            if peso != 0:
                print(f"Aresta de {id_origem} para {id_destino} com peso {peso}")
            else:
                print("Não existe aresta entre os usuários especificados.")
        else:
            print("Um dos usuários não existe.")

    def listar_dados_grafo(self):
        print("Grafo é um dígrafo.") if self.is_digrafo else print("Grafo não é um dígrafo.")
        print("Grafo é ponderado.") if self.is_ponderado else print("Grafo não é ponderado.")
        print("Grafo tem laços.") if np.trace(self.matriz_adj) > 0 else print("Grafo não tem laços.")
        print("Grau de cada vértice:")
        for id_usuario in self.usuarios:
            indice = self.id_to_index[id_usuario]
            grau = np.count_nonzero(self.matriz_adj[indice])
            print(f"Usuário {id_usuario} tem grau {grau}")

    def detectar_bots(self):
        print("Usuários suspeitos de serem bots:")
        for usuario in self.usuarios.values():
            indice_usuario = self.id_to_index[usuario.id_usuario]
            interacoes_recebidas = np.count_nonzero(self.matriz_adj[:, indice_usuario])
            condicao1 = usuario.idade_conta < 7 and usuario.atividade_media >= 500
            condicao2 = usuario.atividade_media >= 1000 and interacoes_recebidas < 10
            if condicao1 or condicao2:
                print(f"ID: {usuario.id_usuario}, Nome: {usuario.nome}, Atividade Média: {usuario.atividade_media}, Idade da Conta: {usuario.idade_conta} dias, Interações Recebidas: {interacoes_recebidas}")

    def visualizar_grafo(self):
        print("Matriz de Adjacência:")
        print(self.matriz_adj)

    def gerar_relatorio(self):
        total_usuarios = len(self.usuarios)
        total_arestas = np.count_nonzero(self.matriz_adj)
        print(f"Total de usuários: {total_usuarios}")
        print(f"Total de interações: {total_arestas}")
        graus = [np.count_nonzero(self.matriz_adj[i]) for i in range(total_usuarios)]
        grau_medio = sum(graus) / total_usuarios if total_usuarios > 0 else 0
        print(f"Grau médio: {grau_medio}")

    def simular_alteracao(self):
        while True:
            print("\nSimulando alteração na rede...")
            print("Escolha uma opção:")
            print("1. Adicionar usuário")
            print("2. Remover usuário")
            print("3. Adicionar aresta")
            print("4. Remover aresta")
            print("5. Atualizar usuário")
            print("6. Atualizar aresta")
            print("7. Consultar usuário")
            print("8. Consultar aresta")
            print("9. Gerar relatório")
            print("10. Visualizar grafo")
            print("11. Detectar potenciais bots")
            print("12. Sair da simulação")
            opcao = input("Opção: ")
            
            if opcao == '1':
                id_usuario = int(input("ID do novo usuário: "))
                if id_usuario in self.usuarios:
                    print("ID já existe. Escolha outro ID.")
                    continue
                nome = input("Nome: ")
                idade_conta = int(input("Idade da conta (dias): "))
                atividade_media = int(input("Atividade média (interações/dia): "))
                usuario = Usuario(id_usuario, nome, idade_conta, atividade_media)
                self.adicionar_usuario(usuario)
                print("Usuário adicionado.")
            
            elif opcao == '2':
                id_usuario = int(input("ID do usuário a ser removido: "))
                self.remover_usuario(id_usuario)
                print("Usuário removido.")
            
            elif opcao == '3':
                id_origem = int(input("ID do usuário de origem: "))
                id_destino = int(input("ID do usuário de destino: "))
                peso = int(input("Peso da aresta: "))
                self.adicionar_aresta(id_origem, id_destino, peso)
                print("Aresta adicionada.")
            
            elif opcao == '4':
                id_origem = int(input("ID do usuário de origem: "))
                id_destino = int(input("ID do usuário de destino: "))
                self.remover_aresta(id_origem, id_destino)
                print("Aresta removida.")
            
            elif opcao == '5':
                id_usuario = int(input("ID do usuário a atualizar: "))
                if id_usuario in self.usuarios:
                    nome = input("Novo nome (pressione Enter para manter): ")
                    idade_conta = input("Nova idade da conta (dias) (pressione Enter para manter): ")
                    atividade_media = input("Nova atividade média (interações/dia) (pressione Enter para manter): ")
                    
                    nome = nome if nome else None
                    idade_conta = int(idade_conta) if idade_conta else None
                    atividade_media = int(atividade_media) if atividade_media else None
                    
                    self.atualizar_usuario(id_usuario, nome=nome, idade_conta=idade_conta, atividade_media=atividade_media)
                    print("Usuário atualizado.")
                else:
                    print("Usuário não encontrado.")
            
            elif opcao == '6':
                id_origem = int(input("ID do usuário de origem: "))
                id_destino = int(input("ID do usuário de destino: "))
                if id_origem in self.usuarios and id_destino in self.usuarios:
                    indice_origem = self.id_to_index[id_origem]
                    indice_destino = self.id_to_index[id_destino]
                    peso_atual = self.matriz_adj[indice_origem][indice_destino]
                    if peso_atual == 0:
                        print("Não existe aresta entre os usuários especificados.")
                    else:
                        print(f"Aresta atual de {id_origem} para {id_destino} com peso {peso_atual}")
                        novo_peso = int(input("Novo peso da aresta: "))
                        self.adicionar_aresta(id_origem, id_destino, novo_peso)
                        print("Aresta atualizada.")
                else:
                    print("Um dos usuários não existe.")
            
            elif opcao == '7':
                id_usuario = int(input("ID do usuário a consultar: "))
                self.consultar_usuario(id_usuario)
            
            elif opcao == '8':
                id_origem = int(input("ID do usuário de origem: "))
                id_destino = int(input("ID do usuário de destino: "))
                self.consultar_aresta(id_origem, id_destino)
            
            elif opcao == '9':
                self.gerar_relatorio()
            
            elif opcao == '10':
                self.visualizar_grafo()
            
            elif opcao == '11':
                self.detectar_bots()
            
            elif opcao == '12':
                print("Saindo da simulação.")
                break
            
            else:
                print("Opção inválida.")

    def calcular_porcentagem_preenchimento(self):
        total_vertices = len(self.usuarios)
        total_possiveis_arestas = total_vertices * (total_vertices - 1)
        total_arestas_existentes = np.count_nonzero(self.matriz_adj)
        porcentagem = (total_arestas_existentes / total_possiveis_arestas) * 100
        print(f"Porcentagem da matriz de adjacências preenchida: {porcentagem:.2f}%")
        return porcentagem
    
    def gerar_imagem_grafo(self, arquivo_imagem='grafo.png'):
        G = nx.DiGraph() if self.is_digrafo else nx.Graph()

        # Adicionando os vértices
        for usuario in self.usuarios.values():
            G.add_node(usuario.id_usuario, label=usuario.nome)

        # Adicionando as arestas com pesos
        for i, id_origem in enumerate(self.index_to_id):
            for j, id_destino in enumerate(self.index_to_id):
                peso = self.matriz_adj[i][j]
                if peso > 0:
                    G.add_edge(id_origem, id_destino, weight=peso)

        pos = nx.spring_layout(G)  # Layout do grafo

        # Desenhando os nós
        nx.draw_networkx_nodes(G, pos, node_size=500)

        # Desenhando as arestas com pesos
        edges = G.edges()
        weights = [G[u][v]['weight'] for u, v in edges]
        nx.draw_networkx_edges(G, pos, edgelist=edges, arrowstyle='->', arrowsize=20, width=2)

        # Desenhando os rótulos dos nós
        labels = {usuario.id_usuario: usuario.nome for usuario in self.usuarios.values()}
        nx.draw_networkx_labels(G, pos, labels, font_size=10)

        # Desenhando os pesos das arestas
        edge_labels = nx.get_edge_attributes(G, 'weight')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

        plt.axis('off')
        plt.savefig(arquivo_imagem)
        plt.show()
        print(f"Imagem do grafo salva como {arquivo_imagem}.")

if __name__ == "__main__":
    grafo = GrafoRedeSocial()

    try:
        grafo.carregar_grafo('grafo.json')
        print("Grafo carregado com sucesso de grafo.json.")
        grafo_existe = True
    except Exception as e:
        grafo_existe = False

    if not grafo_existe:
        usuarios = [
            Usuario(1, "Ana", 30, 50),
            Usuario(2, "Bruno", 5, 1500),
            Usuario(3, "Carla", 60, 20),
            Usuario(4, "Diego", 10, 300),
            Usuario(5, "Eduarda", 15, 450),
            Usuario(6, "Felipe", 25, 600),
            Usuario(7, "Gabriela", 35, 700),
            Usuario(8, "Henrique", 45, 800),
            Usuario(9, "Isabela", 55, 900),
            Usuario(10, "João", 65, 1000)
        ]

        for usuario in usuarios:
            grafo.adicionar_usuario(usuario)

        grafo.adicionar_aresta(1, 2, peso=5)
        grafo.adicionar_aresta(2, 3, peso=3)
        grafo.adicionar_aresta(3, 4, peso=2)
        grafo.adicionar_aresta(4, 5, peso=4)
        grafo.adicionar_aresta(5, 6, peso=6)
        grafo.adicionar_aresta(6, 7, peso=1)
        grafo.adicionar_aresta(7, 8, peso=7)
        grafo.adicionar_aresta(8, 9, peso=8)
        grafo.adicionar_aresta(9, 10, peso=9)
        grafo.adicionar_aresta(10, 1, peso=10)
        grafo.adicionar_aresta(2, 5, peso=2)
        grafo.adicionar_aresta(3, 6, peso=3)
        grafo.adicionar_aresta(4, 7, peso=4)
        grafo.adicionar_aresta(5, 8, peso=5)
        grafo.adicionar_aresta(6, 9, peso=6)
        grafo.adicionar_aresta(7, 10, peso=7)
        grafo.adicionar_aresta(8, 1, peso=8)
        grafo.adicionar_aresta(9, 2, peso=9)
        grafo.adicionar_aresta(10, 3, peso=10)

        # Chamando o método para calcular a porcentagem de preenchimento
        porcentagem = grafo.calcular_porcentagem_preenchimento()
        if porcentagem < 20:
            print("A porcentagem de preenchimento está abaixo de 20%. Considere adicionar mais arestas.")
        else:
            print("A porcentagem de preenchimento atende ao requisito mínimo de 20%.")

    # O restante do seu código continua aqui...
    grafo.consultar_usuario(2)
    grafo.consultar_aresta(1, 2)
    grafo.listar_dados_grafo()
    grafo.detectar_bots()
    grafo.visualizar_grafo()
    grafo.gerar_relatorio()
    grafo.simular_alteracao()

    # Gerando a imagem do grafo
    grafo.gerar_imagem_grafo('grafo.png')

    grafo.salvar_grafo('grafo.json')
    grafo.exportar_grafo('grafo_exportado.csv')
