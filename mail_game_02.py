#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简述（中文）：一个用 Pygame 实现的极简 2D 横版跳跃示例：左右移动 + 跳跃 + 平台碰撞。
Kurzbeschreibung (Deutsch): Ein minimalistisches 2D-Jump’n’Run-Beispiel mit Pygame:
Links/Rechts-Bewegung, Springen und Plattform-Kollision.
"""

import sys
import pygame


# ========= 全局常量 / Globale Konstanten =========
# 画面尺寸（中文）：窗口宽度与高度
# Bildschirmgröße (Deutsch): Fensterbreite und -höhe
W, H = 1500, 800

# 颜色（中文）：用于背景、平台、玩家方块
# Farben (Deutsch): Für Hintergrund, Plattformen, Spielerrechteck
FARBE_STUFE = (150,200,150 )
FARBE_Hintergrund = (150, 100, 100)
FARBE_SPIELER  = (50, 0, 40)

# 物理与移动参数（中文）：重力、水平速度、起跳初速度、最大下落速度
# Physik & Bewegung (Deutsch): Schwerkraft, Horizontaltempo, Start-Aufwärtsgeschwindigkeit, max. Fallgeschwindigkeit
Schwerkraft = 0.6
MOVE_SPEED = 6
JUMP_VELOCITY = -17
MAX_FALL_SPEED = 25

# 帧率（中文）：目标每秒帧数
# Bildrate (Deutsch): Ziel-FPS
FPS = 60


def move_and_collide(rect: pygame.Rect, dx: float, dy: float, solids: list[pygame.Rect]) -> bool:
    """
    简易 AABB 碰撞：先处理水平方向，再处理垂直方向；返回是否着地。
    Einfache AABB-Kollision: erst horizontal, dann vertikal; gibt zurück, ob man auf dem Boden steht.
    """
    # 水平移动 / Horizontalbewegung
    rect.x += dx
    for s in solids:
        if rect.colliderect(s):
            if dx > 0:
                rect.right = s.left   # 从右侧碰到平台 / Kollision von rechts
            elif dx < 0:
                rect.left = s.right   # 从左侧碰到平台 / Kollision von links

    # 垂直移动 / Vertikalbewegung
    rect.y += dy
    grounded = False
    for s in solids:
        if rect.colliderect(s):
            if dy > 0:
                # 从上方落到平台 / Landung auf die Plattform
                rect.bottom = s.top
                grounded = True
            elif dy < 0:
                # 头部顶到平台 / Kopf stößt oben an
                rect.top = s.bottom
    return grounded


def handle_input(on_ground: bool, vel_y: float) -> tuple[int, float]:
    """
    读取键盘输入：左右移动与跳跃。
    Tastatureingaben lesen: Links/Rechts und Springen.
    """
    keys = pygame.key.get_pressed()

    # 左右方向键（或 A/D） / Links/Rechts (oder A/D)
    vel_x = (keys[pygame.K_RIGHT] or keys[pygame.K_d]) * MOVE_SPEED - \
            (keys[pygame.K_LEFT]  or keys[pygame.K_a]) * MOVE_SPEED

    # 跳跃（空格 / W / 上箭头），仅在着地时生效
    # Springen (Space / W / Pfeil hoch), nur wenn am Boden
    if (keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]) and on_ground:
        vel_y = JUMP_VELOCITY
        jump_sound.play()  # Play the jump sound

    return vel_x, vel_y


# Load the player image and scale it to 40x30
player_image = pygame.image.load("house-03_gold.png")
player_image = pygame.transform.scale(player_image, (40, 30))
# Set the white color in the player image to be transparent
player_image.set_colorkey((255, 255, 255))

# Load the background image and scale it to the screen size
background_image = pygame.image.load("hintergrund-1.png")
background_image = pygame.transform.scale(background_image, (W, H))

# Load the jump sound
pygame.mixer.init()
jump_sound = pygame.mixer.Sound("pony_jump-1.mp3")

# Modify the draw_scene function to draw the background image
def draw_scene(screen: pygame.Surface, player: pygame.Rect, platforms: list[pygame.Rect]) -> None:
    """
    渲染场景：背景、平台、玩家。
    Szene zeichnen: Hintergrund, Plattformen, Spieler.
    """
    screen.blit(background_image, (0, 0))  # Draw the background image
    for s in platforms:
        pygame.draw.rect(screen, FARBE_STUFE, s)     # 平台 / Plattformen
    screen.blit(player_image, player.topleft)  # Draw the player image


def main() -> None:
    """
    程序主入口：初始化、主循环、事件处理、物理与渲染。
    Haupteinstieg: Initialisierung, Hauptschleife, Events, Physik & Rendering.
    """
    pygame.init()
    

    # 创建窗口与时钟 / Fenster & Uhr
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Pygame 2D Mario-like Demo")
    clock = pygame.time.Clock()

    # 玩家初始状态 / Spielerzustand
    player = pygame.Rect(100, 100, 40, 30)  # 简易矩形代替角色 / Rechteck als Platzhalter
    vel_x, vel_y = 0, 0
    on_ground = False

    # 关卡平台（地面 + 台阶） / Levelplattformen (Boden + Stufen)
    platforms = [
        pygame.Rect(0,   H - 40, W,     40),  # 地面 / Boden
        pygame.Rect(100, H - 200, 100,  20),  # 台阶1 / Stufe 1
        pygame.Rect(300, H - 650, 130,  20),  # 台阶2 / Stufe 2
        pygame.Rect(350, H - 280, 100,  20),  # 台阶3 / Stufe 3
        pygame.Rect(500, H - 450, 100, 20),  # 台阶4 / Stufe 4
        pygame.Rect(650, H - 700, 20, 250),  # 台阶4 / Stufe 4
        pygame.Rect(750, H - 550, 150, 20),
        pygame.Rect(900, H - 300, 200, 20),  # 台阶5 / Stufe 6
        pygame.Rect(1350, H - 200, 100, 20),  # 台阶6 / Stufe 7
    ]

    # 游戏主循环 / Haupt-Spielschleife
    while True:
        # 事件处理（退出）/ Events (Beenden)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # 输入处理（左右 + 跳跃）/ Eingaben (Links/Rechts + Springen)
        vel_x, vel_y = handle_input(on_ground, vel_y)

        # 重力叠加与限制最大下落速度
        # Schwerkraft addieren & maximale Fallgeschwindigkeit begrenzen
        vel_y += Schwerkraft
        if vel_y > MAX_FALL_SPEED:
            vel_y = MAX_FALL_SPEED

        # 位移 + 碰撞 / Bewegung + Kollision
        on_ground = move_and_collide(player, vel_x, vel_y, platforms)
        if on_ground:
            vel_y = 0

        # 渲染 / Rendern
        draw_scene(screen, player, platforms)
        pygame.display.flip()

        # 帧率控制 / Bildrate steuern
        clock.tick(FPS)


if __name__ == "__main__":
    # 仅当脚本被直接执行时运行 main（而不是被导入）
    # main() nur ausführen, wenn dieses Skript direkt gestartet wird (nicht importiert)
    main()
