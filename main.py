import pygame
import sys
import random


def draw_floor(screen, floor_surface, floor_x_pos) -> None:
    screen.blit(floor_surface, (floor_x_pos, 900))
    screen.blit(floor_surface, (floor_x_pos + 576, 900))


def create_pipe(pipe_surface, pipe_height):
    random_pipe_pos = random.choice(pipe_height)
    bottom_pipe = pipe_surface.get_rect(midtop=(700, random_pipe_pos))
    top_pipe = pipe_surface.get_rect(midbottom=(700, random_pipe_pos - 300))
    return bottom_pipe, top_pipe


def move_pipes(pipes: list) -> list:
    for pipe in pipes:
        pipe.centerx -= 5
    return pipes


def draw_pipes(screen, pipes: list[pygame.Rect], pipe_surface) -> None:
    for pipe in pipes:
        if pipe.bottom >= 1024:
            screen.blit(pipe_surface, pipe)
        else:
            screen.blit(pygame.transform.flip(pipe_surface, False, True), pipe)


def check_collision(pipes, bird_rect, death_sound: pygame.mixer.Sound) -> bool:
    for pipe in pipes:
        if bird_rect.colliderect(pipe):
            death_sound.play()
            return False
    if bird_rect.top <= -100 or bird_rect.bottom >= 900:
        death_sound.play()
        return False
    return True


def rotate_bird(bird, bird_rotation: float):
    rotation_factor = 3
    return pygame.transform.rotozoom(bird, -bird_rotation * rotation_factor, 1)


def bird_animation(bird_frames: list, bird_index: int, previous_bird_rect):
    new_bird = bird_frames[bird_index]
    new_bird_rect = new_bird.get_rect(center=(100, previous_bird_rect.centery))
    return new_bird, new_bird_rect


def score_display(game_font: pygame.font.Font, score: int, high_score: int, game_active: bool, screen) -> None:
    score_surface = game_font.render(f"Score: {int(score)}", True, (255, 255, 255))
    score_rect = score_surface.get_rect(center=(288, 100))
    screen.blit(score_surface, score_rect)
    if not game_active:
        high_score_surface = game_font.render(f"High Score: {int(high_score)}", True, (255, 255, 255))
        high_score_rect = high_score_surface.get_rect(center=(288, 850))
        screen.blit(high_score_surface, high_score_rect)


def update_score(score: int, high_score: int) -> int:
    if score > high_score:
        high_score = score
    return high_score


def main() -> None:
    # Initialize
    pygame.mixer.pre_init(size=32, channels=1, buffer=512)
    pygame.init()
    pygame.display.set_caption("Flappy Bird")
    screen = pygame.display.set_mode((576, 1024))
    clock = pygame.time.Clock()
    game_font = pygame.font.Font('04B_19.ttf', 50)

    # Game Variables
    gravity = 0.25
    bird_movement = 0
    game_active = True
    score = 0
    high_score = 0

    bg_surface = pygame.transform.scale2x(pygame.image.load('assets/background-day.png').convert())
    floor_surface = pygame.transform.scale2x(pygame.image.load('assets/base.png').convert())
    floor_x_pos = 0

    bird_frames = [pygame.transform.scale2x(pygame.image.load(f'assets/bluebird-{x}flap.png')) for x in ["down", "mid",
                                                                                                         "up"]]
    bird_index = 0
    bird_surface = bird_frames[bird_index]
    bird_rect = bird_surface.get_rect(center=(100, 512))

    BIRD_FLAP = pygame.USEREVENT + 1
    pygame.time.set_timer(BIRD_FLAP, 200)
    
    pipe_surface = pygame.transform.scale2x(pygame.image.load('assets/pipe-green.png'))
    pipe_list = []
    SPAWN_PIPE = pygame.USEREVENT
    pygame.time.set_timer(SPAWN_PIPE, 1200)
    pipe_height = [400, 600, 800]

    game_over_surface = pygame.transform.scale2x(pygame.image.load('assets/message.png').convert_alpha())
    game_over_rect = game_over_surface.get_rect(center=(288, 512))

    flap_sound = pygame.mixer.Sound('sound/sfx_wing.wav')
    death_sound = pygame.mixer.Sound('sound/sfx_hit.wav')
    score_sound = pygame.mixer.Sound('sound/sfx_point.wav')
    score_sound_countdown = 100

    # game loop
    while True:
        # event loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and game_active:
                    bird_movement = -12
                    flap_sound.play()
                if event.key == pygame.K_SPACE and not game_active:
                    game_active = True
                    pipe_list.clear()
                    bird_rect.center = (100, 512)
                    bird_movement = 0
                    score = 0

            if event.type == SPAWN_PIPE:
                pipe_list.extend(create_pipe(pipe_surface, pipe_height))

            if event.type == BIRD_FLAP:
                bird_index = (bird_index + 1) % 3
                bird_surface, bird_rect = bird_animation(bird_frames, bird_index, bird_rect)

        screen.blit(bg_surface, (0, 0))

        if game_active:
            # Bird
            bird_movement += gravity
            rotated_bird = rotate_bird(bird_surface, bird_movement)
            bird_rect.centery += bird_movement
            screen.blit(rotated_bird, bird_rect)
            game_active = check_collision(pipe_list, bird_rect, death_sound)

            # Pipes
            pipe_list = move_pipes(pipe_list)
            draw_pipes(screen, pipe_list, pipe_surface)
            score += 0.01
            score_sound_countdown -= 1
            if score_sound_countdown <= 0:
                score_sound.play()
                score_sound_countdown = 100
        else:
            screen.blit(game_over_surface, game_over_rect)
            high_score = update_score(score, high_score)
            score_sound_countdown = 100

        score_display(game_font, score, high_score, game_active, screen)

        # Floor
        floor_x_pos -= 1
        draw_floor(screen, floor_surface, floor_x_pos)
        if floor_x_pos <= -576:
            floor_x_pos = 0
        pygame.display.update()
        clock.tick(120)


if __name__ == '__main__':
    main()
