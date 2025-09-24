import pgzrun
import random
import pygame
from pygame import Rect

WIDTH = 670
HEIGHT = 430
TAM_CELULA = 40
TITLE = "DogBomber"

tela_atual = 'menu'
som_habilitado = True

# Botões do menu
botao_iniciar = Rect((236, 120), (200, 50))
botao_som = Rect((236, 190), (200, 50))
botao_instrucao = Rect((236, 260), (200, 50))

def carregar_e_escalar(ator, largura, altura):
    ator._surf = pygame.transform.scale(ator._surf, (largura, altura))
    ator._update_pos()

# Atores e imagens
fundo_img = "floor"
parede_img = "parede"
heroi = Actor("heroi", (80, 80))
cachorro = Actor("cachorro", (120, 80))
chave_img = "chave"
ponto_img = "porta"
inimigo_img = "inimigo"

carregar_e_escalar(heroi, TAM_CELULA // 2, TAM_CELULA // 2)
carregar_e_escalar(cachorro, TAM_CELULA // 2, TAM_CELULA // 2)

# ================= CENÁRIO =================
cenario = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]

heroi_pos = [1, 7]
cachorro_pos = [2, 7]

def posicao_aleatoria_livre(excluir=[]):
    while True:
        x = random.randint(0, len(cenario[0]) - 1)
        y = random.randint(0, len(cenario) - 1)
        if cenario[y][x] == 0 and [x, y] not in excluir:
            return [x, y]

chave_pos = posicao_aleatoria_livre([heroi_pos])
ponto_pos = posicao_aleatoria_livre([heroi_pos, chave_pos])
tem_chave = False

NUM_INIMIGOS = 3
inimigos_pos = [posicao_aleatoria_livre([heroi_pos, chave_pos, ponto_pos]) for _ in range(NUM_INIMIGOS)]

def tocar_musica():
    if som_habilitado:
        music.play("musica_fundo.ogg")
        music.set_volume(0.1)

def pode_andar(x, y):
    if x < 0 or y < 0 or y >= len(cenario) or x >= len(cenario[0]):
        return False
    return cenario[y][x] != 1

def mover_heroi_para(x, y):
    global heroi_pos, tem_chave, tela_atual
    if pode_andar(x, y):
        heroi_pos = [x, y]
        if heroi_pos == chave_pos:
            tem_chave = True
        if tem_chave and heroi_pos == ponto_pos:
            tela_atual = 'vitoria'

def mover_heroi(key):
    x, y = heroi_pos
    if key == keys.RIGHT: mover_heroi_para(x + 1, y)
    elif key == keys.LEFT: mover_heroi_para(x - 1, y)
    elif key == keys.UP: mover_heroi_para(x, y - 1)
    elif key == keys.DOWN: mover_heroi_para(x, y + 1)

def resetar_jogo():
    global heroi_pos, cachorro_pos, chave_pos, ponto_pos, tem_chave, inimigos_pos
    heroi_pos = [1, 7]
    cachorro_pos = [2, 7]
    chave_pos = posicao_aleatoria_livre([heroi_pos])
    ponto_pos = posicao_aleatoria_livre([heroi_pos, chave_pos])
    tem_chave = False
    inimigos_pos = [posicao_aleatoria_livre([heroi_pos, chave_pos, ponto_pos]) for _ in range(NUM_INIMIGOS)]

cachorro_timer = 0
inimigos_timer = 0
VEL_CACHORRO = 35
VEL_INIMIGO = 30

def mover_cachorro():
    global cachorro_pos
    hx, hy = heroi_pos
    cx, cy = cachorro_pos
    inimigo_perto = any(abs(ix - cx) + abs(iy - cy) <= 3 for ix, iy in inimigos_pos)

    if inimigo_perto:
        possiveis = []
        for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
            nx, ny = cx + dx, cy + dy
            if pode_andar(nx, ny) and [nx, ny] not in inimigos_pos:
                possiveis.append([nx, ny])
        if possiveis:
            cachorro_pos[:] = random.choice(possiveis)
    else:
        if abs(cx - hx) + abs(cy - hy) > 1:
            if cx < hx and pode_andar(cx + 1, cy): cx += 1
            elif cx > hx and pode_andar(cx - 1, cy): cx -= 1
            elif cy < hy and pode_andar(cx, cy + 1): cy += 1
            elif cy > hy and pode_andar(cx, cy - 1): cy -= 1
            cachorro_pos[:] = [cx, cy]

def mover_inimigos():
    global inimigos_pos
    for i, (ix, iy) in enumerate(inimigos_pos):
        cachorro_perto = abs(ix - cachorro_pos[0]) + abs(iy - cachorro_pos[1]) <= 3
        if cachorro_perto:
            alvo = [ix + (ix - heroi_pos[0]), iy + (iy - heroi_pos[1])]  # afasta do herói
        else:
            alvo = heroi_pos

        possiveis = []
        for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
            nx, ny = ix+dx, iy+dy
            if pode_andar(nx, ny):
                possiveis.append([nx, ny])

        if possiveis:
            possiveis.sort(key=lambda pos: abs(pos[0]-alvo[0]) + abs(pos[1]-alvo[1]))
            inimigos_pos[i] = possiveis[0]

def draw():
    if tela_atual == 'menu':
        draw_menu()
    elif tela_atual == 'jogo':
        draw_jogo()
    elif tela_atual == 'vitoria':
        screen.fill((0, 200, 0))
        screen.draw.text("VOCÊ VENCEU!", center=(WIDTH//2, HEIGHT//2), fontsize=60, color="white")
        screen.draw.text("Pressione ESC para voltar ao menu", center=(WIDTH//2, HEIGHT//2+50), fontsize=30, color="white")
    elif tela_atual == 'gameover':
        screen.fill((200, 0, 0))
        screen.draw.text("GAME OVER!", center=(WIDTH//2, HEIGHT//2), fontsize=60, color="white")
        screen.draw.text("Pressione ESC para voltar ao menu", center=(WIDTH//2, HEIGHT//2+50), fontsize=30, color="white")

def draw_menu():
    screen.fill((100,100,100))
    screen.draw.filled_rect(botao_iniciar, (0,200,0))
    screen.draw.text("Iniciar Jogo", center=botao_iniciar.center, color="white", fontsize=30)
    cor_som = (0,0,200) if som_habilitado else (200,0,0)
    screen.draw.filled_rect(botao_som, cor_som)
    screen.draw.text("Som: ON" if som_habilitado else "Som: OFF",
                     center=botao_som.center, color="white", fontsize=30)
    screen.draw.filled_rect(botao_instrucao, (150, 75, 0))
    screen.draw.text("Instruções", center=botao_instrucao.center, color="white", fontsize=30)

def draw_jogo():
    screen.clear()
    screen.blit(fundo_img, (0, 0))
    for y, linha in enumerate(cenario):
        for x, celula in enumerate(linha):
            px, py = x*TAM_CELULA, y*TAM_CELULA
            if celula == 1:
                parede = Actor(parede_img, (px+TAM_CELULA//2, py+TAM_CELULA//2))
                carregar_e_escalar(parede, TAM_CELULA//2, TAM_CELULA//2)
                parede.draw()
    if not tem_chave:
        chave = Actor(chave_img, (chave_pos[0]*TAM_CELULA + TAM_CELULA//2,
                                  chave_pos[1]*TAM_CELULA + TAM_CELULA//2))
        carregar_e_escalar(chave, TAM_CELULA//2, TAM_CELULA//2)
        chave.draw()
    ponto = Actor(ponto_img, (ponto_pos[0]*TAM_CELULA + TAM_CELULA//2,
                              ponto_pos[1]*TAM_CELULA + TAM_CELULA//2))
    carregar_e_escalar(ponto, TAM_CELULA//2, TAM_CELULA//2)
    ponto.draw()
    for ix, iy in inimigos_pos:
        inimigo = Actor(inimigo_img, (ix*TAM_CELULA + TAM_CELULA//2, iy*TAM_CELULA + TAM_CELULA//2))
        carregar_e_escalar(inimigo, TAM_CELULA//2, TAM_CELULA//2)
        inimigo.draw()
    heroi.pos = (heroi_pos[0]*TAM_CELULA + TAM_CELULA//2, heroi_pos[1]*TAM_CELULA + TAM_CELULA//2)
    cachorro.pos = (cachorro_pos[0]*TAM_CELULA + TAM_CELULA//2, cachorro_pos[1]*TAM_CELULA + TAM_CELULA//2)
    cachorro.draw()
    heroi.draw()

def update():
    global cachorro_timer, inimigos_timer, tela_atual
    if tela_atual == 'jogo':
        cachorro_timer += 1
        inimigos_timer += 1
        if cachorro_timer >= VEL_CACHORRO:
            mover_cachorro()
            cachorro_timer = 0
        if inimigos_timer >= VEL_INIMIGO:
            mover_inimigos()
            inimigos_timer = 0
        if any([ix, iy] == heroi_pos for ix, iy in inimigos_pos):
            tela_atual = 'gameover'

def on_key_down(key):
    global tela_atual
    if tela_atual == 'jogo':
        mover_heroi(key)
    elif tela_atual in ('vitoria', 'gameover'):
        if key == keys.ESCAPE:
            tela_atual = 'menu'
            resetar_jogo()
    elif tela_atual == 'instrucoes':
        if key == keys.ESCAPE:
            tela_atual = 'menu'

def on_mouse_down(pos):
    global tela_atual, som_habilitado
    if tela_atual == 'menu':
        if botao_iniciar.collidepoint(pos):
            tela_atual = 'jogo'
            tocar_musica()
        elif botao_som.collidepoint(pos):
            som_habilitado = not som_habilitado
            if som_habilitado:
                tocar_musica()
            else:
                music.stop()
        elif botao_instrucao.collidepoint(pos):
            tela_atual = 'instrucoes'
    elif tela_atual == 'jogo':
        x = pos[0] // TAM_CELULA
        y = pos[1] // TAM_CELULA
        mover_heroi_para(x, y)

def draw_instrucoes():
    screen.fill((50, 50, 50))
    screen.draw.text("INSTRUÇÕES", center=(WIDTH//2, 50), fontsize=40, color="white")
    texto = [
        "Objetivo: Pegue a chave e vá até a porta.",
        "Os inimigos perseguem você.",
        "O cachorro vai te auxiliar!",
        "Se os inimigos se aproximarem do cachorro,",
        "ele tentará distraí-los fugindo.",
        "",
        "Pressione ESC para voltar ao menu."
    ]
    for i, linha in enumerate(texto):
        screen.draw.text(linha, midleft=(50, 120 + i*30), fontsize=25, color="white")

# Sobrescreve draw para incluir instruções
def draw():
    if tela_atual == 'menu':
        draw_menu()
    elif tela_atual == 'jogo':
        draw_jogo()
    elif tela_atual == 'vitoria':
        screen.fill((0, 200, 0))
        screen.draw.text("VOCÊ VENCEU!", center=(WIDTH//2, HEIGHT//2), fontsize=60, color="white")
        screen.draw.text("Pressione ESC para voltar ao menu", center=(WIDTH//2, HEIGHT//2+50), fontsize=30, color="white")
    elif tela_atual == 'gameover':
        screen.fill((200, 0, 0))
        screen.draw.text("GAME OVER!", center=(WIDTH//2, HEIGHT//2), fontsize=60, color="white")
        screen.draw.text("Pressione ESC para voltar ao menu", center=(WIDTH//2, HEIGHT//2+50), fontsize=30, color="white")
    elif tela_atual == 'instrucoes':
        draw_instrucoes()

tocar_musica()
pgzrun.go()
