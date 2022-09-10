import os
from rede_neural import Rede_Neural
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import random
import shelve
import time
import numpy as np

'''
    Função para importar arquivos (imagens) do diretório temporario
    (serve para quando o .exe do programa é criado)
'''
def resource_path(relative_path):
    try:
        # O PyInstaller cria uma pasta chamada _MEIPASS no temp
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Constantes globais

# Sprite de onde saem todas as imagens
sprite = pygame.image.load(resource_path('Imagens/sprites_jogo.png'))

# Altura do chao
GND_HEIGHT = 10
 
# Colors
COR_PRETO = (0, 0, 0)
COR_BRANCO = (255, 255, 255)
COR_AZUL = (0,162,232)
COR_CINZA = (86, 86, 86)
COR_CINZA_2 = (37, 37, 37)
COR_AMARELO = (240,200,40)
COR_ROXO = (163,73,164)
COR_MARROM = (128,64,0)
COR_LARANJA = (255,128,0) 
COR_VERDE = (34,177,76)
COR_VERMELHO = (255,0,0)

# Tamanho da tela
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 300

# Fontes
pygame.font.init()
FONT_MAIN = 'consolas'
FONT_MENU_1 = pygame.font.SysFont(FONT_MAIN, 30)
FONT_MENU_2 = pygame.font.SysFont(FONT_MAIN, 26)
FONT_SCORE = pygame.font.SysFont(FONT_MAIN, 20)



'''
    Altera a cor de uma imagem
    Parâmetros:
        image - surface para ser colorida
        new_color - tupple com a nova cor RGB
    Retorna:
        A surface já colorida
'''
def chg_color(image, new_color):
    image = image.copy()

    image.fill(new_color, None, pygame.BLEND_MAX)

    return image


class Dino(pygame.sprite.Sprite): 
    def __init__(self, speed): 
        # Construtor da estrutura pai (Sprite)
        super().__init__()

        # Sprites de referência
        self.image_jump = sprite.subsurface((1338, 2, 88, 94))
        self.image_1 = sprite.subsurface((1338+88*2, 2, 88, 94))
        self.image_2 = sprite.subsurface((1338+88*3, 2, 88, 94))
        self.image_dead = sprite.subsurface((1338+88*5+1, 2, 88, 94))
        self.image_crouch_1 = sprite.subsurface((1866, 36, 118, 60))
        self.image_crouch_2 = sprite.subsurface((1984, 36, 118, 60))

        # Altera a cor da imagem randomicamente
        cores = [COR_CINZA,
                 COR_AMARELO,
                 COR_ROXO,
                 COR_AZUL,
                 COR_VERMELHO,
                 COR_VERDE,
                 COR_LARANJA,
                 COR_MARROM,
                 COR_PRETO
                 ]
        
        rand = random.randint(0,len(cores)-1)
        self.image_jump = chg_color(self.image_jump, cores[rand])
        self.image_1 = chg_color(self.image_1, cores[rand])
        self.image_2 = chg_color(self.image_2, cores[rand])
        self.image_dead = chg_color(self.image_dead, cores[rand])
        self.image_crouch_1 = chg_color(self.image_crouch_1, cores[rand])
        self.image_crouch_2 = chg_color(self.image_crouch_2, cores[rand])
 
        # Cria a imagem do dinossauro e o hitbox
        self.image = self.image_1
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

        # Muda a posição do dinossauro
        self.rect.x = 80
        self.rect.y = SCREEN_HEIGHT - self.rect.height - GND_HEIGHT

        # Variavel para auxiliar na movimentação
        self.change_y = 0

        # Contador interno (animação de andar)
        self.cont = 0

        # Lista dos sprites para colidir
        self.lista_sprites = None

        # Parâmetros gerais do dinossauro
        self.speed = speed
        self.score = 0
        self.sensors = [0, 0, 0]

        self.onground = True # Informa se está no chão
        self.crouched = False # Informa se está agachado
    
        self.dead = False # Informa que colidiu em algo

        self.rede_neural = Rede_Neural()

        #self.framerate = 60

    def load_neural_network(self, weights):
        self.rede_neural.weights = weights.copy()

    def update(self, framerate):
        """ Atualiza o movimento do jogador. """
        if not self.dead:
            # Toma uma decisão
            self.take_action()
            
            # Aumenta o score do player
            self.score += framerate/360
            
            # Gravidade
            self.calc_grav()
     
            # Mover cima/baixo
            self.rect.y += self.change_y

            # Controla a animação de andar (em pé e agachado)    
            if (self.onground):
                if(not self.crouched):
                    if self.cont == 8:
                        self.image = self.image_2
                    elif self.cont >= 16:
                        self.cont = 0
                        self.image = self.image_1
                else:
                    if self.cont == 8:
                        self.image = self.image_crouch_1
                    elif self.cont >= 16:
                        self.cont = 0
                        self.image = self.image_crouch_2

                self.rect = self.image.get_rect()
                self.mask = pygame.mask.from_surface(self.image)
                self.rect.x, self.rect.y = 80, SCREEN_HEIGHT - self.rect.height - GND_HEIGHT
                
                self.cont += 1
            
            # Verifica a colisao
            aux = pygame.sprite.Group(self.lista_sprites)
            block_hit_list = pygame.sprite.spritecollide(self, aux, False, pygame.sprite.collide_mask)
            for block in block_hit_list:
                self.dead = True
                self.image = self.image_dead
                
                y = self.rect.y
                self.rect = self.image.get_rect()
                self.rect.x, self.rect.y = 80, y

                if(self.crouched):
                    self.rect.x += 30
                    self.rect.y -= 30
        else:
            if self.rect.x > -150:
                self.rect.x -= self.speed
        
    def calc_grav(self):
        """ Calcula o efeito da gravidade """
        
        if self.change_y != 0:
            if(not self.crouched):
                self.change_y += 1.2
            else:
                self.change_y += 5
 
        # Verifica se está no chão e não está pulando
        if self.rect.y >= SCREEN_HEIGHT - self.rect.height - GND_HEIGHT and self.change_y >= 0:
            self.change_y = 0
            self.rect.y = SCREEN_HEIGHT - self.rect.height - GND_HEIGHT
            self.onground = True

    """ Ações do jogador """
    def take_action(self):
        #x = [on_ground, self.speed, self.sensors[0], self.sensors[1], self.sensors[2]]
        dist = self.sensors[0]-self.rect.x
        #dist = dist if dist > 0 else 600
        x = [self.onground, self.speed, dist, self.sensors[1], self.sensors[2]]
        act = self.rede_neural.fast_forward(x)

        if(act[0] >= 0.5):
            self.action_jump()
        if(act[1] >= 0.5):
            self.crouched = True
        else:
            self.crouched = False
            
    def action_jump(self):
        # Só consegue pular se estiver no chão e não estiver agachado
        if (self.onground and not self.crouched):
            self.change_y = -22
            self.image = self.image_jump
            
            self.onground = False


class Ground(pygame.sprite.Sprite): 
    def __init__(self, speed): 
        # Construtor da estrutura pai (Sprite)
        super().__init__()

        # Cria a imagem do chão e o hitbox
        self.image = sprite.subsurface((0, 104, SCREEN_WIDTH, 26))
        self.rect = self.image.get_rect()

        # Altera a posição do chão
        self.rect.x = 0
        self.rect.y = SCREEN_HEIGHT - self.rect.height

        # Posição do chão no sprite
        self.posicao = 0
        # Velocidade da animação do chão
        self.speed = speed

    # Cria a animação do chão
    def update(self, framerate):
        self.image = sprite.subsurface((self.posicao, 104, SCREEN_WIDTH, 26))
        self.posicao += self.speed
        
        if self.posicao + SCREEN_WIDTH >= 2100:
            self.posicao = 0


class Cloud(pygame.sprite.Sprite): 
    def __init__(self, count = 400): 
        # Construtor da estrutura pai (Sprite)
        super().__init__()

        # Cria a imagem e o hitbox
        self.image_day = sprite.subsurface((166, 2, 92, 27))
        self.image_night = chg_color(self.image_day, COR_CINZA_2)

        self.image = self.image_day
        self.rect = self.image.get_rect()

        self.rect.x = -self.rect.width - 10

        # Velocidade da nuvem
        self.speed = 1

        self.count = count

        self.randomize()

    def randomize(self):
        if self.count > random.randint(300,400):
            self.rect.y = random.randint(10,150)
            self.rect.x = SCREEN_WIDTH
        else:
            self.count += 1

    # Cria a animação da nuvem
    def update(self, framerate):      
        if self.rect.x <= -self.rect.width - 10:
            self.randomize()
        else:
            self.rect.x -= self.speed

    def change_image(self, night):
        if(not night):
            self.image = self.image_day
        else:
            self.image = self.image_night
            
            
class Cactus(pygame.sprite.Sprite): 
    def __init__(self, speed): 
        # Construtor da estrutura pai (Sprite)
        super().__init__()

        # Sprites de referência
        self.images = [sprite.subsurface((448 + 34*x, 4, 30, 66))
                       for x in range(0,6)]
        self.images += [sprite.subsurface((654 + 50*x, 4, 46, 96))
                       for x in range(0,4)]
        self.images.append(sprite.subsurface((852, 4, 98, 96)))

        for i in self.images.copy():
            color_image = chg_color(i, COR_BRANCO)
            self.images.append(color_image)

        # Velocidade do movimento do cacto
        self.speed = speed

        # Se está de noite ou não (para mudar a cor das imagens
        self.night = False

        # Cria a imagem do cacto e o hitbox
        self.randomize()

    # Randomiza a imagem do cacto e altera o hitbox
    def randomize(self):
        if(not self.night):
            rand = random.randint(0,10)
        else:
            rand = random.randint(11,21)
            
        self.image = self.images[rand]
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

        self.rect.x = SCREEN_WIDTH + self.rect.width + random.randint(10,100)
        self.rect.y = SCREEN_HEIGHT - self.rect.height - GND_HEIGHT + 2

    # Cria o movimento do cacto
    def update(self, framerate):
        self.rect.x -= self.speed
        
        if self.rect.x <= -self.rect.width - 10:
            self.randomize()


class Screens():
    def __init__(self):
        size = [SCREEN_WIDTH, SCREEN_HEIGHT]

        flags = pygame.DOUBLEBUF | pygame.HWSURFACE
        self.screen = pygame.display.set_mode(size, flags)
        
        # Variaveis importantes no controle do jogo
        self.framerate = 60
        
        self.clock = pygame.time.Clock()

        self.cur_screen = "Menu"

        '''
            A velocidade global será aumentada a cada 500
            de score em 2 unidades e ela começa em 10            
        '''
        self.global_speed = 10

        self.night = False

        self.auto_advance = False

        self.mutation_factor = 0 # Calculado automaticamente na função create_menu_elements

        # Carrega o melhor agente a partir do arquivo
        with shelve.open('best_dinos') as db:
            try:
                self.best_dinos = db['best']
                self.train_generation = db['gen']
            except:
                self.best_dinos = []
                self.train_generation = 0

        # Cria o menu
        self.create_menu_elements()

    # Cria os elementos do menu
    def create_menu_elements(self):
        self.screen.fill(COR_BRANCO)
        
        titulo = FONT_MENU_1.render('Dinossauro do Google Inteligente', True, (0, 0, 0))
        self.screen.blit(titulo, (SCREEN_WIDTH/2 - titulo.get_rect().width/2, 20))

        self.elements = [[SCREEN_WIDTH/2-240, 100, 230, 40, 'Testar agentes:'],
                         [SCREEN_WIDTH/2-240, 150, 230, 40, 'Treinar agentes:'],
                         [SCREEN_WIDTH/2-125, 200, 250, 40, 'Reiniciar agentes', 'reiniciar']
                         ]
        self.elements += [[SCREEN_WIDTH/2 + 10 + 70*x, 100, 50, 40, str(10**x), "testar"] for x in range(0,3)]
        self.elements += [[SCREEN_WIDTH/2 + 10 + 70*x, 150, 50, 40, str(10*(x==0)+20*x), "treinar"] for x in range(0,3)]

        for i in self.elements[:2]:
            texto = FONT_MENU_2.render(i[4], True, (0, 0, 0))
            self.screen.blit(texto, (i[0]+i[2]/2 - texto.get_rect().width/2,
                                       i[1]+i[3]/2 - texto.get_rect().height/2))

        for i in self.elements[2:]:
            pygame.draw.rect(self.screen, COR_CINZA, (i[0], i[1], i[2], i[3]))

            texto = FONT_MENU_2.render(i[4], True, (255, 255, 255))
            self.screen.blit(texto, (i[0]+i[2]/2 - texto.get_rect().width/2,
                                       i[1]+i[3]/2 - texto.get_rect().height/2))

    # Cria os elementos do jogo
    def create_run_elements(self, agents_size):
        # Variaveis importantes no controle do jogo
        self.active_sprite_list = pygame.sprite.Group()

        self.score = 0
        self.night = False
        
        # Cria o dinossauro, o chão e o cacto
        self.dinos = []

        self.cloud_1 = Cloud(0)
        self.cloud_2 = Cloud()
        self.ground = Ground(self.global_speed)
        self.cactus = Cactus(self.global_speed)
        
        
        self.active_sprite_list.add(self.ground, self.cactus, self.cloud_1, self.cloud_2)

        # O fator de mutação começa em 1.0 e a cada 20 gerações
        # ele cai pela metade
        self.mutation_factor = 1/(2**(self.train_generation//10))

        # Com 10 dinos ou sem a lista dos melhores, o programa apenas:
        # Teste: Cria os dinos iguais ao melhor
        # Treino: Cria os dinos com base no último melhor (mutando um pouco),
        # mas mantém 1 original
        if agents_size <= 10 or not self.best_dinos:
            for i in range(agents_size):
                dino = Dino(self.global_speed)
                self.active_sprite_list.add(dino)
                dino.lista_sprites = [self.cactus]
                self.dinos.append(dino)
                # Teste: Todos os dinos são iguais ao original
                # Treino: O dino 0 é igual ao original e o resto sofre mutação                    
                if self.best_dinos:
                    dino.load_neural_network(self.best_dinos[0])                   
                    if self.cur_screen == "RunTrain":
                        dino.rede_neural.mutate(self.mutation_factor)

        # Aplicável só ao treino:
        # Com mais de 10 dinos e com a lista dos melhores:
        # 1/10 dos dinos são iguais aos ultimos melhores
        # 1/10 dos dinos são selecionados aleatoriamente dos últimos
        # 8/10 dos dinos são mutações dos últimos melhores
        elif self.best_dinos:
            # Cria 1/10 melhores
            for i in range(agents_size//10):
                dino = Dino(self.global_speed)
                self.active_sprite_list.add(dino)
                dino.lista_sprites = [self.cactus]
                self.dinos.apend(dino)

                dino.load_neural_network(self.best_dinos[i])

            # Cria 1/10 escolhidos aleatórios
            for i in range(agents_size//10):
                dino = Dino(self.global_speed)
                self.active_sprite_list.add(dino)
                dino.lista_sprites = [self.cactus]
                self.dinos.append(dino)

                dino.load_neural_network(random.sample(self.best_dinos, 1)[0])

            # Mutação dos 1/10 melhores para formar os outros 8/10 dinos
            rest = agents_size-2*agents_size//10
            
            for i in range(rest):
                dino = Dino(self.global_speed)
                self.active_sprite_list.add(dino)
                dino.lista_sprites = [self.cactus]
                self.dinos.append(dino)

                dino.load_neural_network(self.best_dinos[i//((10*rest)//agents_size)])
                if self.cur_screen == "RunTrain":
                    dino.rede_neural.mutate(self.mutation_factor)
                    
    # Deleta os elementos do jogo
    def delete_run_elements(self):
        for i in self.dinos:
            i.kill()
        self.dinos = []
        self.ground.kill()
        self.cactus.kill()

    '''
        Loop de atualização
    '''
    def draw(self, events):            
        # CÓDIGOS QUE ENVOLVEM O DESENHO NA TELA
        if self.cur_screen == "Menu":
            self.screen_menu(events)
        elif self.cur_screen == "RunTest" or\
             self.cur_screen == "RunTrain":            
            self.screen_run(events)
        # ---------------------------------------

        # Força o framerate
        self.clock.tick_busy_loop(self.framerate)
        #self.clock.tick(self.framerate)
 
        # Atualiza a tela
        pygame.display.flip()
        

    '''
        Procedimentos do menu
    '''
    def screen_menu(self, events):
        # Verifica se algum botão foi pressionado
        if events:
            if events[0].type == pygame.MOUSEBUTTONUP:
                pos = events[0].pos
        
                for i in self.elements[2:]:
                    if i[0] < pos[0] < i[0] + i[2] \
                       and i[1] < pos[1] < i[1] + i[3]:
                        if(i[5] == "reiniciar"):
                            self.best_dinos = []
                            self.train_generation = 0
                            print("Agentes reiniciados")
                            pygame.draw.rect(self.screen, COR_BRANCO, (i[0], i[1], i[2], i[3]))
                            self.elements.remove(i)
                            
                        if(i[5] == "testar"):
                            self.cur_screen = "RunTest"
                            self.create_run_elements(int(i[4]))
                            self.framerate = 60
                            
                        elif(i[5] == "treinar"):
                            self.cur_screen = "RunTrain"
                            self.create_run_elements(int(i[4]))
                            self.framerate = 60
                            self.auto_advance = False
    
      
    '''
        Procedimentos do jogo
    '''
    def screen_run(self, events):        
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    if self.cur_screen == "RunTest":
                        self.screen_end_game_test()
                        return
                    elif self.cur_screen == "RunTrain":
                        self.screen_end_game_train()
                        return
                if event.key == pygame.K_RIGHT:
                    self.framerate += 20
                if (event.key == pygame.K_LEFT) and (self.framerate > 20):
                    self.framerate -= 20
                # Troca o modo de auto avanço do treino
                if event.key == pygame.K_x:
                    self.auto_advance = not self.auto_advance
                
        # Atualiza os movimentos do jogador
        self.active_sprite_list.update(self.framerate)

        if(int(self.score)%1000 == 0 and int(self.score) != 0):
            self.night = not self.night
            self.cactus.night = self.night
            self.cloud_1.change_image(self.night)
            self.cloud_2.change_image(self.night)

            self.score += 1 # Força o score a pular 1 unidade (não repetir este if vezes seguidas)

        if(not self.night):
            self.screen.fill(COR_BRANCO)
            text_color = COR_PRETO
        else:
            self.screen.fill(COR_PRETO)
            text_color = COR_BRANCO
            
        self.active_sprite_list.draw(self.screen)

        # Escreve o score        
        self.score += self.framerate/360
        score_text = FONT_SCORE.render("%05d"%self.score, True, text_color)
        self.screen.blit(score_text, (SCREEN_WIDTH - score_text.get_rect().width, 0))

        # Escreve o texto do framerate
        frate_text = FONT_SCORE.render("FPS: %03d"%self.framerate, True, text_color)
        self.screen.blit(frate_text, (0, 20))

        # Escreve o texto da geração atual
        if self.cur_screen == "RunTrain":
            gen_text = FONT_SCORE.render("Geração: %d"%self.train_generation, True, text_color)
            self.screen.blit(gen_text, (220, 0))

            # Escreve o texto do fator de mutação
            mut_text = FONT_SCORE.render("Fator de mutação: %.4f"%self.mutation_factor, True, text_color)
            self.screen.blit(mut_text, (220, 20))
            
            # Escreve o texto do auto avanço
            avan_text = FONT_SCORE.render("Automático: %s"%('x' if self.auto_advance else '-'), True, text_color)
            self.screen.blit(avan_text, (380, 0))

        # Atualiza os "sensores" dos dinossauros
        for i in self.dinos:
            i.sensors[0] = self.cactus.rect.x
            i.sensors[1] = self.cactus.rect.width
            i.sensors[2] = self.cactus.rect.height

        # Atualiza a velocidade
        if (int(self.score) % 500 == 0):
            self.global_speed = int(10 + 2*self.score/500)
            self.cactus.speed = self.global_speed
            self.ground.speed = self.global_speed
            for i in self.dinos:
                i.speed = self.global_speed

        # Indicação de que acabou o jogo
        collide = True
        dinos_alive = len(self.dinos)
        for i in self.dinos:
            if i.dead == False:
                collide = False
            else:
                dinos_alive -= 1

        # Escreve o texto dos dinos vivos
        alive_text = FONT_SCORE.render(str("Dinos vivos: %02d/%02d"%(dinos_alive,len(self.dinos))), True, text_color)
        self.screen.blit(alive_text, (0, 0))

        if collide:
            if self.cur_screen == "RunTest":
                self.screen_end_game_test()
            elif self.cur_screen == "RunTrain":
                self.screen_end_game_train()

    # Procedimentos de quando todos os dinossauros morrem
    # no modo de teste
    def screen_end_game_test(self):
        self.active_sprite_list.draw(self.screen)

        # Lista os melhores dinos
        self.best_dinos, scores = self.select_best_dinos()
        
        print("Melhores scores:", scores[:10])

        cont = 0
        while 1:
            cont += 1
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()

            if(cont >= 1000):
                self.cur_screen = "Menu"
                self.create_menu_elements()
                self.delete_run_elements()
                break
            
    # Procedimentos de quando todos os dinossauros morrem
    # no modo de treino
    def screen_end_game_train(self):
        self.active_sprite_list.draw(self.screen)

        # Lista os melhores dinos
        new_best_dinos, scores = self.select_best_dinos()

        print("Melhores scores:", scores[:10])

        igual = True
        if(self.best_dinos):
            for i in range(len(new_best_dinos[0])):
                if (new_best_dinos[0][i] != self.best_dinos[0][i]).any():
                    igual = False
                
            if(not igual):
                print("Um novo gene prosperou: ", new_best_dinos[0], end="\n\n")
        else:
            print("Um novo gene prosperou: ", new_best_dinos[0], end="\n\n")

        self.best_dinos = new_best_dinos.copy()

        # Desenha os botões na tela
        elements = [[SCREEN_WIDTH/2-150, 50, 100, 40, 'Voltar'],
                   [SCREEN_WIDTH/2+40, 50, 140, 40, 'Continuar'],
                   [SCREEN_WIDTH/2-50, 110, 100, 40, 'Salvar']]

        for i in elements:
            pygame.draw.rect(self.screen, COR_CINZA, (i[0], i[1], i[2], i[3]))
            texto = FONT_MENU_2.render(i[4], True, (0, 0, 0))
            self.screen.blit(texto, (i[0]+i[2]/2 - texto.get_rect().width/2,
                                       i[1]+i[3]/2 - texto.get_rect().height/2))

        # Aguarda algum botão ser pressionado
        stuck = True
        while stuck:            
            pygame.display.flip()

            events = pygame.event.get()

            # Verifica se algum evento ocorreu ou algum botão foi pressionado
            if events:
                if events[0].type == pygame.QUIT:
                    pygame.quit()
                
                elif events[0].type == pygame.MOUSEBUTTONUP:
                    pos = events[0].pos
            
                    for i in elements:
                        if i[0] < pos[0] < i[0] + i[2] \
                           and i[1] < pos[1] < i[1] + i[3]:
                            if(i[4] == "Voltar"):
                                self.cur_screen = "Menu"
                                self.create_menu_elements()
                                self.delete_run_elements()

                                stuck = False

                            elif(i[4] == "Salvar"):
                                self.save_best_dinos()
                                pygame.draw.rect(self.screen, COR_BRANCO, (i[0], i[1], i[2], i[3]))
                                elements.remove(i)

                                print("Pesos salvos")
                                    
                            elif(i[4] == "Continuar"):
                                self.save_best_dinos()
                                self.train_generation += 1
                                
                                self.delete_run_elements()
                                n = len(self.best_dinos)
                                self.create_run_elements(n)
                                stuck = False
            # Avança automaticamente                    
            if self.auto_advance:
                self.save_best_dinos()
                self.train_generation += 1
                
                self.delete_run_elements()
                n = len(self.best_dinos)
                self.create_run_elements(n)
                stuck = False
                    
    # Retorna os melhores dinos para o próximo treino                    
    def select_best_dinos(self):        
        # Cria uma lista com os melhores scores
        best_dinos = []
        for i in self.dinos:
            best_dinos.append([i.rede_neural.weights, int(i.score)])

        best_dinos.sort(reverse=True, key=lambda x: x[1])

        return [x[0] for x in best_dinos], [x[1] for x in best_dinos]

    # Salva os melhores dinos no arquivo
    def save_best_dinos(self):
        # Salva o melhor dino no arquivo
        with shelve.open('best_dinos') as db:
            db['best'] = self.best_dinos
            db['gen'] = self.train_generation 


def main():
    """ Main Program """
    pygame.init()
    pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.MOUSEBUTTONUP])
    
    # Muda a posição da tela
    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (900,500)    

    # CONFIGURAÇÕES INICIAIS 
    pygame.display.set_caption("Dinossauro inteligente")
    icon = pygame.image.load(resource_path('Imagens/google_dino.png'))
    pygame.display.set_icon(icon)

    # Cria as telas
    screens = Screens()   

    # Variavel de controle do termino do jogo
    done = False

 
    # -------- Loop principal -----------
    while not done:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                done = True

        screens.draw(events)
 
    pygame.quit()

main()
