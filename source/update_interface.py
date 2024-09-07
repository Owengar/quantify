import pygame, time, sys
import pathlib

pygame.init()
pygame.display.set_icon(pygame.image.load(str(pathlib.Path().resolve())+"\\source\\icon.png"))
pygame.display.set_caption("Quantify Updater")


screen_size = (500, 500)
surface = pygame.display.set_mode(screen_size)
bg_gray = (215*0.8, 215*0.8, 230*0.8)
black = (0, 0, 0)
arial = pygame.font.SysFont("Arial", int(screen_size[0] * 0.039), bold=True)
pat_font = pygame.font.SysFont("Arial", int(screen_size[0] * 0.02))
stime = time.time()



txt_height = 110

def event_loop(updates):
    global txt_height
    updates_surf = pat_font.render(updates, antialias=True, color=black, wraplength=490)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                return True
            elif event.key == pygame.K_ESCAPE:
                sys.exit()
        if event.type == pygame.MOUSEWHEEL:
            txt_height -= event.y * 15
            if txt_height + 110 > 140:
                txt_height += event.y *15
            elif txt_height <  -updates_surf.size[1] + 410:
                txt_height += event.y * 15
    surface.fill(bg_gray)
    surface.blit(updates_surf, (10, txt_height))
    pygame.draw.rect(surface, bg_gray, pygame.Rect(0, 0, 550, 110))

    surface.blit(arial.render("Updates are available for quantify. Press enter to update. Detailed changes below. (scroll)", antialias=True, color=black, wraplength=490), (10, 10))
    pygame.display.update()
    return False
