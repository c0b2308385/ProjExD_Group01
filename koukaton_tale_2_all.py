import os
import time
import random
import sys
import pygame as pg
import math

def start_screen(screen):
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    screen.fill((0, 0, 0))

    font_path = "meiryo.ttc"
    if os.path.exists(font_path):
        title_font = pg.font.Font(font_path, 100)
        button_font = pg.font.Font(font_path, 60)
    else:
        title_font = pg.font.SysFont("msgothic", 100)
        button_font = pg.font.SysFont("msgothic", 60)

    title_text = title_font.render("コウカトンテイル", True, (255, 0, 0))
    title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
    screen.blit(title_text, title_rect)

    button_text = button_font.render("スタート", True, (255, 0, 0))
    button_rect = button_text.get_rect(center=(WIDTH // 2, HEIGHT * 2 // 3))
    screen.blit(button_text, button_rect)

    pg.display.update()
    
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.KEYDOWN and event.key == pg.K_RETURN:
                return

WIDTH, HEIGHT = 1100, 650
DELTA = {
    pg.K_UP: (0, -7),
    pg.K_DOWN: (0, +7),
    pg.K_LEFT: (-7, 0),
    pg.K_RIGHT: (+7, 0),
}
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def check_bound(rct: pg.Rect) -> tuple[bool, bool]:
    yoko, tate = True, True
    if rct.left < 0 or WIDTH < rct.right:
        yoko = False
    if rct.top < 0 or HEIGHT < rct.bottom:
        tate = False
    return yoko, tate

def init_bb_imgs() -> tuple[list[pg.Surface], list[int]]:
    bb_imgs = []
    bb_accs = [a for a in range(1, 11)]
    for r in range(1, 11):
        bb_img = pg.Surface((20 * r, 20 * r), pg.SRCALPHA)
        pg.draw.circle(bb_img, (255, 0, 0), (10 * r, 10 * r), 10 * r)
        bb_imgs.append(bb_img)
    return bb_imgs, bb_accs

def get_kk_img(sum_mv: tuple[int, int]) -> pg.Surface:
    kk_images = {
        (0, -7): pg.transform.rotozoom(pg.image.load("fig/3.png"), -90, 1),
        (0, 7): pg.transform.rotozoom(pg.image.load("fig/3.png"), 90, 1),
        (-7, 0): pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 1),
        (7, 0): pg.transform.flip(pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 1), True, False),
        (7, -7): pg.transform.flip(pg.transform.rotozoom(pg.image.load("fig/3.png"), -45, 1), True, False),
        (-7, 7): pg.transform.rotozoom(pg.image.load("fig/3.png"), 45, 1),
        (-7, -7): pg.transform.rotozoom(pg.image.load("fig/3.png"), -45, 1),
        (7, 7): pg.transform.flip(pg.transform.rotozoom(pg.image.load("fig/3.png"), 45, 1), True, False),
    }
    return kk_images.get(sum_mv, pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 1))

def calc_orientation(org: pg.Rect, dst: pg.Rect, current_xy: tuple[float, float]) -> tuple[float, float]:
    dx = dst.centerx - org.centerx
    dy = dst.centery - org.centery
    norm = math.sqrt(dx**2 + dy**2)
    if norm != 0:
        vx = dx / norm * 5
        vy = dy / norm * 5
    else:
        vx, vy = 0, 0
    return vx, vy

def gameover(screen: pg.Surface) -> None:
    font = pg.font.SysFont("msgothic", 80)
    text = font.render("留年確定", True, (255, 0, 0))
    text_rect = text.get_rect(center=(WIDTH / 2, HEIGHT / 2))
    screen.blit(text, text_rect)
    pg.display.update()
    pg.time.wait(5000)

def draw_hp_gauge(screen: pg.Surface, hp: int) -> None:
    gauge_width = 200
    gauge_height = 20
    fill_width = int((hp / 100) * gauge_width)
    pg.draw.rect(screen, (255, 255, 255), (20, 20, gauge_width, gauge_height), 2)
    pg.draw.rect(screen, (0, 255, 0), (20, 20, fill_width, gauge_height))

def draw_pause_count(screen: pg.Surface, pause_count: int, pause_limit: int) -> None:
    font = pg.font.SysFont("msgothic", 20)
    text = font.render(f"停止機能: {pause_limit - pause_count}回", True, (255, 255, 255))
    screen.blit(text, (20, 50))

def draw_score_time(screen: pg.Surface, score: int, elapsed_time: int) -> None:
    font = pg.font.SysFont("msgothic", 40)
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    time_text = font.render(f"Time: {elapsed_time // 50} s", True, (255, 255, 255))
    screen.blit(score_text, (WIDTH - 250, 20))
    screen.blit(time_text, (WIDTH - 250, 60))

def random_non_overlapping_position(kk_rct: pg.Rect, size: int) -> tuple[int, int]:
    while True:
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        rct = pg.Rect(x - size // 2, y - size // 2, size, size)
        if not kk_rct.colliderect(rct):
            return (x, y)

def rotate_towards(target: pg.Rect, source: pg.Rect, image: pg.Surface) -> pg.Surface:
    dx = target.centerx - source.centerx
    dy = target.centery - source.centery
    angle = math.degrees(math.atan2(-dy, dx))
    rotated_img = pg.transform.rotozoom(image, angle, 1)
    return rotated_img

def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200
    bb_imgs, bb_accs = init_bb_imgs()

    score = 0
    hp = 100
    paused = False
    pause_timer = 0
    pause_limit = 3
    pause_count = 0

    mode = random.choice(["bomb", "beam"])
    print("Selected mode:", mode)

    bombs = []
    if mode == "bomb":
        for i in range(3):
            bb_size = bb_imgs[0].get_width()
            x, y = random_non_overlapping_position(kk_rct, bb_size)
            bb_rct = bb_imgs[0].get_rect()
            bb_rct.centerx = x
            bb_rct.centery = y
            vx, vy = +5, -5
            bombs.append({'rct': bb_rct, 'vx': vx, 'vy': vy})

    beam_img_original = pg.image.load("fig/beam.png") if mode == "beam" else None
    beams = []
    if mode == "beam":
        next_beam_time = 15
        beam_size = beam_img_original.get_width()

    flash_counter = 0
    clock = pg.time.Clock()
    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.KEYDOWN and event.key == pg.K_t:
                if not paused and pause_count < pause_limit:
                    paused = True
                    pause_timer = 150
                    pause_count += 1
                    print(f"停止機能を使用しました。残り回数: {pause_limit - pause_count}")
                elif pause_count >= pause_limit:
                    print("停止機能はこれ以上使用できません！")

        if paused:
            pause_timer -= 1
            if pause_timer <= 0:
                paused = False

        screen.fill((0, 0, 0))

        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        for key, tpl in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += tpl[0]
                sum_mv[1] += tpl[1]

        current_kk_img = get_kk_img(tuple(sum_mv))
        kk_rct.move_ip(sum_mv)
        if check_bound(kk_rct) != (True, True):
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])

        idx = min(tmr // 250 + 1, 9)

        if mode == "bomb" and not paused:
            for bomb in bombs:
                bb_rct = bomb['rct']
                vx = bomb['vx']
                vy = bomb['vy']

                bb_img = bb_imgs[idx]
                bb_acc = bb_accs[idx]
                avx = vx * bb_acc
                avy = vy * bb_acc
                bb_rct.move_ip(avx, avy)

                yoko, tate = check_bound(bb_rct)
                if not yoko:
                    bomb['vx'] *= -1
                if not tate:
                    bomb['vy'] *= -1

                screen.blit(bb_img, bb_rct)

                if flash_counter == 0:
                    kk_mask = pg.mask.from_surface(current_kk_img)
                    bb_mask = pg.mask.from_surface(bb_img)
                    offset = (bb_rct.x - kk_rct.x, bb_rct.y - kk_rct.y)
                    if kk_mask.overlap(bb_mask, offset):
                        hp = max(hp - 10, 0)
                        new_bb_size = bb_img.get_width()
                        x, y = random_non_overlapping_position(kk_rct, new_bb_size)
                        bb_rct.centerx = x
                        bb_rct.centery = y
                        bomb['vx'] = +5
                        bomb['vy'] = -5
                        flash_counter = 100
                        score += 10

        if mode == "beam" and not paused:
            if tmr > next_beam_time:
                x, y = random_non_overlapping_position(kk_rct, beam_size)
                beam_rct = beam_img_original.get_rect()
                beam_rct.centerx = x
                beam_rct.centery = y
                beams.append({
                    'rct': beam_rct,
                    'state': 'spawned',
                    'spawn_time': tmr,
                    'vx': 0,
                    'vy': 0,
                    'img': beam_img_original
                })
                next_beam_time = tmr + 15

            for beam in beams[:]:
                if beam['state'] == 'spawned':
                    if tmr - beam['spawn_time'] > 25:
                        vx, vy = calc_orientation(beam['rct'], kk_rct, (0, 0))
                        vx *= 3
                        vy *= 3
                        beam['vx'] = vx
                        beam['vy'] = vy
                        beam['img'] = rotate_towards(kk_rct, beam['rct'], beam['img'])
                        beam['state'] = 'fired'

                if beam['state'] == 'fired':
                    beam['rct'].move_ip(beam['vx'], beam['vy'])

                screen.blit(beam['img'], beam['rct'])

                if flash_counter == 0:
                    kk_mask = pg.mask.from_surface(current_kk_img)
                    beam_mask = pg.mask.from_surface(beam['img'])
                    offset = (beam['rct'].x - kk_rct.x, beam['rct'].y - kk_rct.y)
                    if kk_mask.overlap(beam_mask, offset):
                        hp = max(hp - 10, 0)
                        beams.remove(beam)
                        flash_counter = 100
                        continue

                if (beam['rct'].right < 0 or beam['rct'].left > WIDTH or
                    beam['rct'].bottom < 0 or beam['rct'].top > HEIGHT):
                    beams.remove(beam)

        if hp <= 0:
            gameover(screen)
            return

        if flash_counter > 0:
            flash_counter -= 1
            if (flash_counter // 5) % 2 == 0:
                screen.blit(current_kk_img, kk_rct)
        else:
            screen.blit(current_kk_img, kk_rct)

        draw_hp_gauge(screen, hp)
        draw_pause_count(screen, pause_count, pause_limit)
        draw_score_time(screen, score, tmr)
        pg.display.update()
        tmr += 1
        clock.tick(50)

if __name__ == "__main__":
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    start_screen(screen)
    main()
    pg.quit()
    sys.exit()