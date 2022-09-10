import pygame
from os import environ as os_environ
import random

# Constantes globais

# Sprite de onde saem todas as imagens
sprite = pygame.image.load('Imagens/sprites_jogo.png')

# Altura do chao
GND_HEIGHT = 10
 
# Colors
COR_PRETO = (0, 0, 0)
COR_BRANCO = (255, 255, 255)
COR_AZUL = (0, 0, 150)

# Tamanho da tela
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 300

# Framerate
FRAMERATE = 60

# Fontes
pygame.font.init()
FONT_MAIN = 'consolas'
FONT_MENU_1 = pygame.font.SysFont(FONT_MAIN, 30)
FONT_MENU_2 = pygame.font.SysFont(FONT_MAIN, 26)
FONT_SCORE = pygame.font.SysFont(FONT_MAIN, 20)
 
class Dino(pygame.sprite.Sprite): 
    def __init__(self): 
        # Construtor da estrutura pai (Sprite)
        super().__init__()

        # Sprites de referência
        self.image_jump = sprite.subsurface((1338, 0, 88, 96))
        self.image_1 = sprite.subsurface((1338+88*2+1, 0, 88, 96))
        self.image_2 = sprite.subsurface((1338+88*3+1, 0, 88, 96))
        self.image_dead = sprite.subsurface((1338+88*5+1, 0, 88, 96))
 
        # Cria a imagem do dinossauro e o hitbox
        self.image = self.image_1
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

        # Muda a posição do dinossauro
        self.rect.x = 80
        self.rect.y = SCREEN_HEIGHT - self.rect.height - GND_HEIGHT
 
        # Velocidade do dinossauro
        self.change_y = 0

        # Contador interno (animação de andar)
        self.cont = 0

        # Lista dos sprites para colidir
        self.lista_sprites = None

        # Informa que colidiu em algo
        self.collide = False

        # Score
        self.score = 0
 
 
    def update(self):
        """ Atualiza o movimento do jogador. """
        # Aumenta o score do player
        self.score += 10/FRAMERATE
        
        # Gravidade
        self.calc_grav()
 
        # Mover cima/baixo
        self.rect.y += self.change_y
 
        # Verifica a colisao
        aux = pygame.sprite.Group(self.lista_sprites)
        block_hit_list = pygame.sprite.spritecollide(self, aux, False, pygame.sprite.collide_mask)
        for block in block_hit_list:
            self.collide = True

        # Controla a animação de andar    
        if (self.rect.bottom >= SCREEN_HEIGHT - GND_HEIGHT):
            
            if self.cont == 8:
                self.image = self.image_2
            elif self.cont >= 16:
                self.cont = 0
                self.image = self.image_1

            self.cont += 1
        
    def calc_grav(self):
        """ Calcula o efeito da gravidade """
        
        if self.change_y != 0:
            self.change_y += 1.2
 
        # Verifica se está no chão e não está pulando
        if self.rect.y >= SCREEN_HEIGHT - self.rect.height - GND_HEIGHT and self.change_y >= 0:
            self.change_y = 0
            self.rect.y = SCREEN_HEIGHT - self.rect.height - GND_HEIGHT

    def dead(self):
        self.image = self.image_dead
        print(int(self.score))

    """ Ações do jogador """
    def jump(self):
        # Verifica se está no chão
        if self.rect.bottom >= SCREEN_HEIGHT - GND_HEIGHT:
            self.change_y = -22
            self.image = self.image_jump
 

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
    def update(self):
        self.image = sprite.subsurface((self.posicao, 104, SCREEN_WIDTH, 26))
        self.posicao += self.speed
        
        if self.posicao + SCREEN_WIDTH >= 2100:
            self.posicao = 0


class Cactus(pygame.sprite.Sprite): 
    def __init__(self, speed): 
        # Construtor da estrutura pai (Sprite)
        super().__init__()

        # Sprites de referência
        self.images = [sprite.subsurface((447 + 34*x, 1, 34, 72))
                       for x in range(0,6)]
        self.images += [sprite.subsurface((652 + 50*x, 1, 49, 99))
                       for x in range(0,4)]
        self.images.append(sprite.subsurface((851, 1, 100, 99)))

        # Cria a imagem do cacto e o hitbox
        self.randomize()

        # Velocidade do movimento do cacto
        self.speed = speed

    # Randomiza a imagem do cacto e altera o hitbox
    def randomize(self):
        rand = random.randint(0,10)
        self.image = self.images[rand]
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

        self.rect.x = SCREEN_WIDTH + self.rect.width + 10
        self.rect.y = SCREEN_HEIGHT - self.rect.height - GND_HEIGHT

    # Cria o movimento do cacto
    def update(self):
        self.rect.x -= self.speed
        
        if self.rect.x <= -self.rect.width - 10:
            self.randomize()



class Screens():
    def __init__(self):
        size = [SCREEN_WIDTH, SCREEN_HEIGHT]
        self.screen = pygame.display.set_mode(size)
        
        # Variaveis importantes no controle do jogo
        self.clock = pygame.time.Clock()

        self.cur_screen = "Menu"

        '''
            A velocidade global será aumentada a cada 500
            de score em 2 unidades e ela começa em 10            
        '''
        self.global_speed = 10

    # Cria os elementos do jogo
    def create_run_elements(self):
        # Variaveis importantes no controle do jogo
        self.active_sprite_list = pygame.sprite.Group()

        self.score = 0
        
        # Cria o dinossauro, o chão e o cacto 
        self.dino = Dino()
        self.ground = Ground(self.global_speed)
        self.cactus = Cactus(self.global_speed)
        
        self.active_sprite_list.add(self.dino, self.ground, self.cactus)

        self.dino.lista_sprites = [self.cactus]

    # Deleta os elementos do jogo
    def delete_run_elements(self):
        self.dino.kill()
        self.ground.kill()
        self.cactus.kill()

    def draw(self, events):            
        # CÓDIGOS QUE ENVOLVEM O DESENHO NA TELA
        if self.cur_screen == "Menu":
            self.screen_menu()
        elif self.cur_screen == "Run":            
            self.screen_run(events)
        # ---------------------------------------

        # 60 fps
        self.clock.tick(FRAMERATE)
 
        # Atualiza a tela
        pygame.display.flip()
        

    '''
        Procedimentos do menu
    '''
    def screen_menu(self):
        self.screen.fill(COR_BRANCO)
        
        titulo = FONT_MENU_1.render('Dinossauro do Google Inteligente', True, (0, 0, 0))
        self.screen.blit(titulo, (SCREEN_WIDTH/2 - titulo.get_rect().width/2, 20))

        botao = [SCREEN_WIDTH/2-40, 100, 80, 40]
        pygame.draw.rect(self.screen, COR_AZUL, (botao[0], botao[1], botao[2], botao[3]))

        texto_botao = FONT_MENU_2.render('Jogar', True, (255, 255, 255))
        self.screen.blit(texto_botao, (botao[0]+botao[2]/2 - texto_botao.get_rect().width/2,
                                       botao[1]+botao[3]/2 - texto_botao.get_rect().height/2))

        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()

        if botao[0] < mouse[0] < botao[0] + botao[2] \
           and botao[1] < mouse[1] < botao[1] + botao[3] \
           and click[0]:
            self.create_run_elements()
            self.cur_screen = "Run"
            

    '''
        Procedimentos do jogo
    '''
    def screen_run(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.dino.jump()
                if event.key == pygame.K_DOWN:
                    pass

            if event.type == pygame.KEYUP:
                pass
                
        # Atualiza os movimentos do jogador
        self.active_sprite_list.update()
        
        self.screen.fill(COR_BRANCO)
        self.active_sprite_list.draw(self.screen)

        # Atualiza o score
        self.score += 10/FRAMERATE
        score_text = FONT_SCORE.render(str("%05d"%self.score), True, (0, 0, 0))
        self.screen.blit(score_text, (SCREEN_WIDTH - score_text.get_rect().width, 0))

        # Atualiza a velocidade
        if (int(self.score) % 500 == 0):
            self.global_speed = int(10 + 2*self.score/500)
            self.cactus.speed = self.global_speed
            self.ground.speed = self.global_speed

        # Indicação de que acabou o jogo
        if self.dino.collide == True:
            self.dino.dead()
            self.active_sprite_list.draw(self.screen)

            cont = 0
            while 1:
                cont += 1
                
                pygame.display.flip()
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()

                if(cont >= 1000):
                    self.cur_screen = "Menu"
                    self.delete_run_elements()
                    break

        

def main():
    """ Main Program """
    pygame.init()
    
    # Muda a posição da tela
    os_environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (900,500)    

    # CONFIGURAÇÕES INICIAIS 
    pygame.display.set_caption("Dinossauro inteligente")
    icon = pygame.image.load('Imagens/google_dino.png')
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
