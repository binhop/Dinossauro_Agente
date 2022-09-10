import numpy as np

class Rede_Neural():
    '''
        Parâmetro:
            layers - array com a quantidade de neuronio em cada camada
            ex: [5, 4, 2] (5 inputs, 4 neuronios iniciais e 2 de saida
    '''
    def __init__(self, layers = [5, 10, 2]):
        self.weights = []

        # Cria uma matriz do tipo:
        # x linhas por y colunas
        # sendo que x indica qual o peso
        # e y indica qual o neuronio
        # Esta matriz é criada para cada camada da rede
        for i in range(len(layers)-1):
            #self.weights.append(np.random.normal(0.0, layers[i]**-0.5, (layers[i], layers[i+1])))
            self.weights.append(np.random.uniform(-3, 3, (layers[i], layers[i+1])))

        #self.weights = np.asarray(self.weights)

        # Função de ativação (sigmoid)
        self.activation_function = lambda x : 1/(1+np.exp(-x))

        # Ordem dos inputs:
        # on_ground, speed, cactus_pos, cactus_width, cactus_height
        self.normalized_input = (1, 20, 662, 100, 99)
        #self.normalized_input = (20, 500, 100, 99)

    def activation(self, z):
        return 1/(1 + np.exp(-z))

    def normalize_input(self, x):
        return np.divide(x, self.normalized_input)

    def fast_forward(self, x):
        # Normaliza as entradas
        x = self.normalize_input(x)
        
        for i in self.weights:
            output = []

            z = np.dot(x, i)
            a = self.activation_function(z)
            x = a

        return x

    def mutate(self, mutation_factor = 0.5):
        for i in range(len(self.weights)):
            a = np.random.uniform(-1,1, self.weights[i].shape)*mutation_factor

            self.weights[i] = np.add(self.weights[i], a)



