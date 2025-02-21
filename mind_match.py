import pygame
import random
import os

pygame.init()

WIDTH, HEIGHT = 800, 600
GRID_SIZE = 4  # 4x4 grid
CARD_SIZE = min((WIDTH - 150) // GRID_SIZE, (HEIGHT - 150) // GRID_SIZE)
FPS = 30

YELLOW = (255, 255, 150)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
RED = (255, 0, 0)

font_path = pygame.font.match_font("courier")
FONT = pygame.font.Font(font_path, 20)
MESSAGE_FONT = pygame.font.Font(font_path, 30)

sound_folder = "sound"
start_sound = pygame.mixer.Sound(os.path.join(sound_folder, "game_start.mp3"))
flip_sound = pygame.mixer.Sound(os.path.join(sound_folder, "flip_card.mp3"))
small_win_sound = pygame.mixer.Sound(os.path.join(sound_folder, "small_win.mp3"))
win_sound = pygame.mixer.Sound(os.path.join(sound_folder, "win.mp3"))

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("MIND MATCH")

image_folder = "images"
animal_images_folder = os.path.join(image_folder, "animals")
bomb_images_folder = os.path.join(image_folder, "bombs")

animal_images = [
    pygame.image.load(os.path.join(animal_images_folder, img))
    for img in os.listdir(animal_images_folder)
    if img.endswith(".png")
]

bomb_image_path = os.path.join(bomb_images_folder, "bomb.png")
if not os.path.exists(bomb_image_path):
    raise ValueError("Bomb image not found in the 'bombs' folder!")

bomb_image = pygame.image.load(bomb_image_path)
bomb_image = pygame.transform.scale(bomb_image, (CARD_SIZE, CARD_SIZE))

unique_images_needed = (GRID_SIZE * GRID_SIZE) // 2 - 1
if len(animal_images) < unique_images_needed:
    raise ValueError(f"Not enough images! Add at least {unique_images_needed} images to the 'animals' folder.")

animal_images = [pygame.transform.scale(img, (CARD_SIZE, CARD_SIZE)) for img in animal_images[:unique_images_needed]]
card_values = animal_images * 2

# Ensure only two bomb cards are added
card_values.extend([bomb_image, bomb_image])

def create_grid():
    random.shuffle(card_values)
    cards = []
    index = 0
    for row in range(GRID_SIZE):
        row_data = []
        for col in range(GRID_SIZE):
            rect = pygame.Rect(
                col * CARD_SIZE + (WIDTH - GRID_SIZE * CARD_SIZE) // 2,
                75 + row * CARD_SIZE,
                CARD_SIZE,
                CARD_SIZE,
            )
            card = {
                "rect": rect,
                "image": card_values[index],
                "flipped": False,
                "matched": False,
                "is_bomb": card_values[index] == bomb_image,
            }
            row_data.append(card)
            index += 1
        cards.append(row_data)
    return cards

def reset_game():
    global cards, first_card, second_card, matched_pairs, game_over, start_time, message, mismatch_timer, showing_bombs, bomb_display_start
    cards = create_grid()
    first_card, second_card = None, None
    matched_pairs = 0
    game_over = False
    start_time = pygame.time.get_ticks()
    message = ""
    mismatch_timer = 0
    showing_bombs = True
    bomb_display_start = pygame.time.get_ticks()

cards = create_grid()
reset_game()

start_sound.play()

show_bomb_time = 3000  # 3 seconds

running = True
clock = pygame.time.Clock()
while running:
    screen.fill(YELLOW)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN and not game_over and mismatch_timer == 0 and not showing_bombs:
            pos = pygame.mouse.get_pos()
            for row in cards:
                for card in row:
                    if card["rect"].collidepoint(pos) and not card["flipped"] and not card["matched"]:
                        if card["is_bomb"]:
                            reset_game()
                            start_sound.play()
                            break

                        if first_card is None:
                            first_card = card
                            card["flipped"] = True
                            flip_sound.play()
                        elif second_card is None:
                            second_card = card
                            card["flipped"] = True
                            flip_sound.play()

    if first_card and second_card and mismatch_timer == 0:
        if first_card["image"] == second_card["image"]:
            first_card["matched"] = True
            second_card["matched"] = True
            matched_pairs += 1
            small_win_sound.play()
            message = "Matched!!"
            first_card, second_card = None, None
        else:
            mismatch_timer = pygame.time.get_ticks()

    if mismatch_timer > 0 and pygame.time.get_ticks() - mismatch_timer > 500:
        first_card["flipped"] = False
        second_card["flipped"] = False
        first_card, second_card = None, None
        mismatch_timer = 0

    if pygame.time.get_ticks() - bomb_display_start > show_bomb_time:
        showing_bombs = False

    for row in cards:
        for card in row:
            if card["flipped"] or card["matched"] or (showing_bombs and card["is_bomb"]):
                screen.blit(card["image"], card["rect"].topleft)
            else:
                pygame.draw.rect(screen, BLACK, card["rect"])
                pygame.draw.rect(screen, WHITE, card["rect"], 2)

    elapsed_time = (pygame.time.get_ticks() - start_time) // 1000 if not game_over else elapsed_time
    timer_text = FONT.render(f"Time: {elapsed_time}s", True, BLACK)
    screen.blit(timer_text, ((WIDTH - timer_text.get_width()) // 2, 10))

    if message:
        message_text = MESSAGE_FONT.render(message, True, GREEN)
        screen.blit(message_text, (WIDTH // 2 - message_text.get_width() // 2, HEIGHT - 50))

    if matched_pairs == (GRID_SIZE * GRID_SIZE - 2) // 2 and not game_over:
        game_over = True
        message = "You Won!!"
        win_sound.play()

    if game_over:
        win_text = MESSAGE_FONT.render("You Won!!", True, GREEN)
        screen.blit(win_text, (WIDTH // 2 - win_text.get_width() // 2, HEIGHT - 50))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
