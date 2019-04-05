import pygame
import sys
from time import sleep
from bullet import Bullet
from meteor import Meteor


def check_keydown_events(event, ai_settings, screen, ship, bullets):
    """
    Responde ao pressionamento da tecla
    """
    if event.key == pygame.K_ESCAPE:
        sys.exit()

    if event.key == pygame.K_RIGHT:
        ship.moving_right = True
    elif event.key == pygame.K_LEFT:
        ship.moving_left = True
    elif event.key == pygame.K_UP:
        ship.moving_up = True
    elif event.key == pygame.K_DOWN:
        ship.moving_down = True

    elif event.key == pygame.K_SPACE:
        fire_bullet(ai_settings, screen, ship, bullets)


def fire_bullet(ai_settings, screen, ship, bullets):
    """
    Dispara um projétil seo limite não foi alcançado
    """
    # Cria um novo projétil e o adiciona ao grupo projéteis
    if len(bullets) < ai_settings.bullets_allowed:
        new_bullet = Bullet(ai_settings, screen, ship)
        bullets.add(new_bullet)


def check_keyup_events(event, ship):
    """
    Responde a soltura da tecla
    """
    if event.key == pygame.K_RIGHT:
        ship.moving_right = False
    elif event.key == pygame.K_LEFT:
        ship.moving_left = False
    elif event.key == pygame.K_UP:
        ship.moving_up = False
    elif event.key == pygame.K_DOWN:
        ship.moving_down = False


def check_events(ai_settings, screen, ship, bullets):
    """
    Responde a eventos do teclado e do mouse
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        # Responde aos movimentos
        elif event.type == pygame.KEYDOWN:
            check_keydown_events(event, ai_settings, screen, ship, bullets)

        elif event.type == pygame.KEYUP:
            check_keyup_events(event, ship)


def update_screen(ai_settings, screen, ship, meteors, bullets):
    """
    Atualiza a imagem da tela
    """

    # Redesenha a tela a cada passagem de laço
    screen.fill(ai_settings.bg_color)

    # Redesenha todos os projéteis da espaçonave
    for bullet in bullets.sprites():
        bullet.draw_bullet()

    ship.blitme()
    meteors.draw(screen)

    # Deixa apenas a tela mais recente visível
    pygame.display.flip()


def update_bullets(ai_settings, screen, ship, meteors, bullets):
    """
    Atualiza a posição dos projéteis e se livra dos antigos
    """
    bullets.update()
    for bullet in bullets.copy():
        if bullet.rect.bottom <= 0:
            bullets.remove(bullet)

    check_bullet_meteor_collision(ai_settings, screen, ship, meteors, bullets)


def check_bullet_meteor_collision(ai_settings, screen, ship, meteors, bullets):
    """Responde a colisões entre projéteis e meteors"""

    # Verifica se algum projétil atingiu meteor
    collisions = pygame.sprite.groupcollide(bullets, meteors, True, True)

    if len(meteors) == 0:

        # Destrói os projéteis e cria nova frota
        bullets.empty()
        create_fleet(ai_settings, screen, ship, meteors)


def get_number_meteors_x(ai_settings, meteor_width):
    """
    Determina o número de meteoros
    """
    available_space_x = ai_settings.screen_width - 2 * meteor_width
    number_meteors_x = int(available_space_x / (2 * meteor_width))
    return number_meteors_x


def create_meteor(ai_settings, screen, meteors, meteor_number, row_number):
    # Cria um meteoro e o posiciona
    meteor = Meteor(ai_settings, screen)
    meteor_width = meteor.rect.width
    meteor.x = meteor_width + 2 * meteor_width * meteor_number
    meteor.rect.x = meteor.x
    meteor.rect.y = meteor.rect.height + 2 * meteor.rect.height * row_number
    meteors.add(meteor)


def create_fleet(ai_settings, screen, ship, meteors):
    """
    Cria os meteoros
    """

    # Cria um meteoro e calcula o número
    meteor = Meteor(ai_settings, screen)
    number_meteors_x = get_number_meteors_x(ai_settings, meteor.rect.width)
    number_rows = get_number_rows(ai_settings, ship.rect.height, meteor.rect.height)

    # Cria a frota de meteoros
    for row_number in range(number_rows):
        for meteor_number in range(number_meteors_x):
            create_meteor(ai_settings, screen, meteors, meteor_number, row_number)


def get_number_rows(ai_settings, ship_height, meteor_height):
    """Determina o número de linhas de meteoros"""
    available_space_y = (ai_settings.screen_height - (3*meteor_height) - ship_height)
    number_rows = int(available_space_y / (2 * meteor_height))
    return number_rows


def ship_hit(ai_settings, stats, screen, ship, meteors, bullets):
    """Responde ao fato de a espaçonave ter sido atingida por meteor"""

    # decrementa ships_left
    if stats.ships_left > 0:
        stats.ships_left -= 1

        # esvazia a lista de meteors e projéteis
        meteors.empty()
        bullets.empty()

        # Cria uma nova frota e centraliza a nave
        create_fleet(ai_settings, screen, ship, meteors)
        ship.center_ship()

        # Faz uma pausa
        sleep(0.5)
    else:
        stats.game_active = False


def update_meteors(ai_settings, stats, screen, ship, meteors, bullets):
    """Atualiza a posição dos meteors"""
    check_fleet_edges(ai_settings, meteors)
    meteors.update()

    # Verifica se houve colisão entre meteor e ship
    if pygame.sprite.spritecollideany(ship, meteors):
        print('Nave atingida')
        ship_hit(ai_settings, stats, screen, ship, meteors, bullets)

    # Verifica se há meteor que atingiu a parte inferior da tela
    check_meteors_bottom(ai_settings, stats, screen, ship, meteors, bullets)


def check_meteors_bottom(ai_settings, stats, screen, ship, meteors, bullets):
    """Verifica se o meteor atingiu a base da tela"""
    screen_rect = screen.get_rect()
    for meteor in meteors.sprites():
        if meteor.rect.bottom >= screen_rect.bottom:

            # Trata esse caso do mesmo modo quando a nave é atingida
            ship_hit(ai_settings, stats, screen, ship, meteors, bullets)
            break


def check_fleet_edges(ai_settings, meteors):
    """responde quando atinge a borda"""
    for meteor in meteors.sprites():
        if meteor.check_edges():
            change_fleet_direction(ai_settings, meteors)
            break


def change_fleet_direction(ai_settings, meteors):
    """Faz a frota descer e mudar a direção"""
    for meteor in meteors.sprites():
        meteor.rect.y += ai_settings.fleet_drop_speed
    ai_settings.fleet_direction *= -1

