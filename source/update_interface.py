import os
os.environ.update({"PYGAME_HIDE_SUPPORT_PROMPT" : "PYGAME_HIDE_SUPPORT_PROMPT"})

import pygame, time, sys
import pathlib
import subprocess
import updates_renderer



def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)








pygame.init()
#pygame.display.set_icon(pygame.image.load(resource_path("icon.png")))
pygame.display.set_caption("Quantify Updater")


screen_size = (500, 500)
surface = pygame.display.set_mode(screen_size)
bg_gray = (215*0.8, 215*0.8, 230*0.8)
black = (0, 0, 0)
arial = pygame.font.SysFont("Arial", int(screen_size[0] * 0.039), bold=True)
pat_font = pygame.font.SysFont("Arial", int(screen_size[0] * 0.02))



already_rendered = False
txt_height = 110

def event_loop(updates):
    global txt_height, already_rendered, updates_surf
    if len(updates) and not already_rendered:
        def render_updates(txt):
            updates_surf = pat_font.render(txt, antialias=True, color=black, wraplength=490)
            return updates_surf
        start_time = time.time()
        update_text_thread = subprocess.Popen("python source\\updates_renderer.py", creationflags=subprocess.CREATE_NO_WINDOW)
        cur_time = start_time
        poll = None
        while (cur_time - start_time < 4):
            poll = update_text_thread.poll()
            cur_time = time.time()
            if poll == 0:
                updates_surf = render_updates(updates)
                break
        else:
            updates_surf = pat_font.render("File changes are too big to render.", antialias=True, color=black, wraplength=490)
        update_text_thread.terminate()
        already_rendered = True
            




    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                return 1
            elif event.key == pygame.K_ESCAPE:
                return 2
        if event.type == pygame.MOUSEWHEEL:
            txt_height -= event.y * 15
            if txt_height > 130:
                txt_height += event.y *15
            elif txt_height <  -updates_surf.size[1] + 410:
                txt_height += event.y * 15
    surface.fill(bg_gray)
    surface.blit(updates_surf, (10, txt_height))
    pygame.draw.rect(surface, bg_gray, pygame.Rect(0, 0, 550, 110))

    surface.blit(arial.render("Updates are available for quantify. Press Enter to update. Press ESC to skip update. Detailed changes below. (scroll)", antialias=True, color=black, wraplength=490), (10, 10))
    pygame.display.update()
    return False



def finished():
    surface.fill(bg_gray)
    surface.blit(arial.render("Finished updating. Opening VSCode.", antialias=True, color=black, wraplength=490), (10, 10))
    pygame.display.update()
    time.sleep(3)

def install_vscode():
    surface.fill(bg_gray)
    surface.blit(arial.render("VSCode is not detected on your computer. Install VSCode to let Quantify automatically open the scripting folder on launch.", antialias=True, color=black, wraplength=490), (10, 10))
    pygame.display.update()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    sys.exit()