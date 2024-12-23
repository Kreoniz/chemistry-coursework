import pygame
import math
import random

# C2C2 C2H C2S

# Цвета для элементов и осей
COLORS = {
    "H": (255, 255, 255),  # Белый для водорода
    "C": (50, 50, 50),  # Серый для углерода
    "S": (255, 223, 0),  # Желтый для серы
    "O": (255, 0, 0),  # Красный для кислорода
    "Cl": (0, 255, 0),  # Зеленый для хлора
    "N": (0, 0, 255),  # Синий для азота
    "P": (255, 165, 0),  # Оранжевый для фосфора
    "Other": (
        128,
        0,
        0,
    ),  # Темно-красный/Розовый/Марун для других элементов
    "X_axis": (255, 0, 0),  # Красный для оси X
    "Y_axis": (0, 255, 0),  # Зеленый для оси Y
    "Z_axis": (0, 0, 255),  # Синий для оси Z
}

# Коэффициенты радиусов атомов
ATOM_SIZES = {
    "H": 0.53,
    "C": 0.77,
    "S": 1.04,
    "O": 0.60,
    "Cl": 0.99,
    "N": 0.65,
    "P": 1.10,
    "Other": 1.00,
}

ATOMIC_MASSES = {
    "H": 1.008,
    "C": 12.011,
    "S": 32.06,
    "O": 15.999,
    "Cl": 35.45,
    "N": 14.007,
    "P": 30.974,
}

# Параметры окна
WIDTH, HEIGHT = 1280, 780
FPS = 60


# Загрузка данных из XYZ файла
def load_xyz(file_path):
    atoms = []

    with open(file_path, "r") as file:
        lines = file.readlines()[2:]  # Пропускаем первые две строки
        for line in lines:
            parts = line.split()
            if len(parts) == 4:
                element, x, y, z = (
                    parts[0],
                    float(parts[1]),
                    float(parts[2]),
                    float(parts[3]),
                )
                atoms.append({"element": element, "x": x, "y": y, "z": z})
    return atoms


# Вычисление центра молекулы
def calculate_center_of_mass(atoms):
    total_mass = 0
    x_mass, y_mass, z_mass = 0, 0, 0

    for atom in atoms:
        element = atom["element"]
        mass = ATOMIC_MASSES[element]
        total_mass += mass
        x_mass += atom["x"] * mass
        y_mass += atom["y"] * mass
        z_mass += atom["z"] * mass

    center_x = x_mass / total_mass
    center_y = y_mass / total_mass
    center_z = z_mass / total_mass
    return center_x, center_y, center_z


# Функции вращения
def rotate_z(x, y, angle):
    cos_angle = math.cos(angle)
    sin_angle = math.sin(angle)
    x_rot = x * cos_angle - y * sin_angle
    y_rot = x * sin_angle + y * cos_angle
    return x_rot, y_rot


def rotate_x(y, z, angle):
    cos_angle = math.cos(angle)
    sin_angle = math.sin(angle)
    y_rot = y * cos_angle - z * sin_angle
    z_rot = y * sin_angle + z * cos_angle
    return y_rot, z_rot


def rotate_y(x, z, angle):
    cos_angle = math.cos(angle)
    sin_angle = math.sin(angle)
    x_rot = x * cos_angle + z * sin_angle
    z_rot = -x * sin_angle + z * cos_angle
    return x_rot, z_rot


# Вращение вокруг всех осей
def rotate_around_axis(x, y, z, angle_x, angle_y, angle_z):
    # Вращение вокруг X, Y и Z
    y, z = rotate_x(y, z, angle_x)
    x, z = rotate_y(x, z, angle_y)
    x, y = rotate_z(x, y, angle_z)
    return x, y, z


# Инициализация Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Молекула графита")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

# Загрузка атомов из файла и вычисление центра
atoms = load_xyz("./molecules/graphite.xyz")
center_x_molecule, center_y_molecule, center_z_molecule = calculate_center_of_mass(
    atoms
)

# Центр экрана и начальные параметры масштабирования и перемещения
center_x, center_y = WIDTH // 2, HEIGHT // 2
scale = 40  # Начальный масштаб
offset_x, offset_y = 0, 0  # Смещение

temperature = 0  # Начальная температура

# Углы вращения
angle_x = 135  # Поворот вокруг оси X
angle_y = 0  # Поворот вокруг оси Y
angle_z = 90  # Поворот вокруг оси Z
# Рисование атомов с сортировкой по глубине

# Параметры слайдера
slider_x = 10
slider_y = HEIGHT - 120  # Положение под легендой
slider_width = 300
slider_height = 10
slider_padding = 20

# Новые переменные для отслеживания состояния перетаскивания
dragging = False
mouse_start_x, mouse_start_y = 0, 0
initial_offset_x, initial_offset_y = offset_x, offset_y

# Дополнительные параметры для ползунка оптимизации
slider_opt_x = 10
slider_opt_y = HEIGHT - 165
slider_opt_width = 300
slider_opt_height = 10

checkbox_rect = pygame.Rect(10, HEIGHT - 240, 20, 20)
optimize_enabled = False
optimization_steps = 0

initial_atoms = []

frame_counter = 0
frame_delay = 1  # Задержка обновления оптимизации (каждые 10 кадров)


def minimize_energy(atoms):
    for atom in atoms:
        atom["x"] += random.uniform(-0.02, 0.02)
        atom["y"] += random.uniform(-0.02, 0.02)
        atom["z"] += random.uniform(-0.02, 0.02)


# Основной цикл
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # ЛКМ для перетаскивания
                mouse_x, mouse_y = pygame.mouse.get_pos()

                if (
                    slider_x <= mouse_x <= slider_x + slider_width
                    and slider_y <= mouse_y <= slider_y + slider_height
                ):
                    # Установка температуры по положению курсора на слайдере
                    temperature = int(100 * (mouse_x - slider_x) / slider_width)

                else:
                    # Начало перетаскивания: фиксируем начальные координаты
                    dragging = True
                    mouse_start_x, mouse_start_y = pygame.mouse.get_pos()
                    initial_offset_x, initial_offset_y = offset_x, offset_y
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # ЛКМ
                # Завершаем перетаскивание
                dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if dragging:
                # Если происходит перетаскивание, обновляем смещение
                mouse_x, mouse_y = pygame.mouse.get_pos()
                offset_x = initial_offset_x + (mouse_x - mouse_start_x)
                offset_y = initial_offset_y + (mouse_y - mouse_start_y)

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_o:
                optimize_enabled = not optimize_enabled

    # Управление вращением и масштабированием
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        angle_y -= 0.05  # Поворот против часовой стрелки вокруг Z
    if keys[pygame.K_RIGHT]:
        angle_y += 0.05  # Поворот по часовой стрелке вокруг Z
    if keys[pygame.K_UP]:
        angle_x += 0.05  # Поворот против часовой стрелки вокруг X
    if keys[pygame.K_DOWN]:
        angle_x -= 0.05  # Поворот по часовой стрелке вокруг X
    if keys[pygame.K_q]:
        angle_z += 0.05  # Поворот против часовой стрелки вокруг Y
    if keys[pygame.K_e]:
        angle_z -= 0.05  # Поворот по часовой стрелке вокруг Y
    if keys[pygame.K_PLUS] or keys[pygame.K_EQUALS]:  # Увеличить масштаб
        scale += 2
    if keys[pygame.K_MINUS] or keys[pygame.K_UNDERSCORE]:  # Уменьшить масштаб
        scale = max(10, scale - 2)
    if keys[pygame.K_w]:  # Перемещение вверх
        offset_y -= 5
    if keys[pygame.K_s]:  # Перемещение вниз
        offset_y += 5
    if keys[pygame.K_a]:  # Перемещение влево
        offset_x -= 5
    if keys[pygame.K_d]:  # Перемещение вправо
        offset_x += 5

    # Очистка экрана
    screen.fill((0, 0, 0))

    if optimize_enabled:
        if frame_counter % frame_delay == 0:
            if optimization_steps >= 100:
                optimization_steps = 0
                print(initial_atoms)
                atoms = initial_atoms.copy()
            else:
                minimize_energy(atoms)
                optimization_steps += 1

    if optimization_steps == 0 and not initial_atoms:
        initial_atoms = atoms.copy()

    frame_counter += 1  # Увеличиваем счетчик кадров

    # Draw checkbox
    pygame.draw.rect(screen, (255, 255, 255), checkbox_rect, 2)
    if optimize_enabled:
        pygame.draw.rect(screen, (0, 255, 0), checkbox_rect.inflate(-4, -4))

    checkbox_label = font.render(
        f"Оптимизация {'' if optimize_enabled else 'не'} запущена",
        True,
        (255, 255, 255),
    )
    screen.blit(checkbox_label, (checkbox_rect.x + 30, checkbox_rect.y + 2))

    # Рисование атомов с сортировкой по глубине
    atoms_to_draw = []

    for atom in atoms:
        # Сдвигаем атом относительно центра молекулы
        x_shifted = atom["x"] - center_x_molecule
        y_shifted = atom["y"] - center_y_molecule
        z_shifted = atom["z"] - center_z_molecule

        # Вращаем атом вокруг всех осей
        x_rot, y_rot, z_rot = rotate_around_axis(
            x_shifted, y_shifted, z_shifted, angle_x, angle_y, angle_z
        )

        # Координаты на экране
        x_screen = int(center_x + offset_x + x_rot * scale)
        y_screen = int(center_y + offset_y - y_rot * scale)

        jitter = temperature / 50
        x_screen += int(random.uniform(-jitter, jitter))
        y_screen += int(random.uniform(-jitter, jitter))

        # Добавляем в список с учетом глубины для сортировки
        atoms_to_draw.append((z_rot, atom["element"], x_screen, y_screen))

    # Сортировка по глубине, чтобы ближние атомы рендерились поверх дальних
    atoms_to_draw.sort(reverse=True, key=lambda atom: atom[0])

    # Рисование атомов
    for _, element, x_screen, y_screen in atoms_to_draw:
        # Получаем цвет атома
        color = COLORS.get(element, COLORS["Other"])

        # Вычисляем радиус атома с учетом масштаба и типа атома
        base_size = ATOM_SIZES.get(
            element, ATOM_SIZES["Other"]
        )  # Если элемент не указан, используем 0.2 как базовый размер
        atom_radius = int(scale * base_size)

        BORDER_COLOR = (0, 0, 0)  # Черный цвет для обводки
        pygame.draw.circle(screen, BORDER_COLOR, (x_screen, y_screen), atom_radius + 2)

        # Отображаем атом как круг
        pygame.draw.circle(screen, color, (x_screen, y_screen), atom_radius)

    # Координаты осей относительно центра для вращения
    axes = {"X_axis": (30, 0, 0), "Y_axis": (0, 30, 0), "Z_axis": (0, 0, 30)}

    # Вращение осей
    for axis, (x, y, z) in axes.items():
        # Поворачиваем сначала вокруг оси X, затем вокруг оси Y и Z
        y_rot_x, z_rot_x = rotate_x(y, z, angle_x)
        x_rot_y, z_rot_y = rotate_y(x, z_rot_x, angle_y)
        x_rot, y_rot = rotate_z(x_rot_y, y_rot_x, angle_z)

        # Отрисовка осей в левом верхнем углу экрана
        axis_offset = 40  # Смещение осей от верхнего левого угла
        x_screen = int(axis_offset + x_rot)
        y_screen = int(axis_offset - y_rot)

        # Отрисовка осей
        pygame.draw.line(
            screen,
            COLORS[axis],
            (axis_offset, axis_offset),
            (x_screen, y_screen),
            2,  # Сделаем оси тоньше
        )

    # Легенда управления внизу
    legend_text = [
        "Управление:",
        "Вверх/Вниз - вращение вокруг X",
        "Влево/Вправо - вращение вокруг Y",
        "Q/E - вращение вокруг Z",
        "+/- - масштабирование",
        "W/A/S/D - перемещение",
    ]
    for i, text in enumerate(legend_text):
        label = font.render(text, True, (255, 255, 255))
        screen.blit(label, (10, HEIGHT - 100 + i * 20))

    # Рисование горизонтального слайдера температуры
    pygame.draw.rect(
        screen, (150, 150, 150), (slider_x, slider_y, slider_width, slider_height)
    )
    temp_x = slider_x + int(slider_width * (temperature / 100))
    pygame.draw.rect(screen, (255, 0, 0), (temp_x, slider_y, 10, slider_height))
    temp_label = font.render(f"Температура: {temperature}°C", True, (255, 255, 255))
    screen.blit(temp_label, (slider_x, slider_y - slider_padding))

    # Рисуем слайдер оптимизации
    pygame.draw.rect(
        screen,
        (150, 150, 150),
        (slider_opt_x, slider_opt_y, slider_opt_width, slider_opt_height),
    )
    opt_x = slider_opt_x + int(slider_opt_width * (optimization_steps / 100))
    pygame.draw.rect(screen, (0, 0, 255), (opt_x, slider_opt_y, 10, slider_opt_height))
    opt_label = font.render(
        f"Шаги оптимизации: {optimization_steps}.\nнажмите O, чтобы запустить",
        True,
        (255, 255, 255),
    )
    screen.blit(opt_label, (slider_opt_x, slider_opt_y - 40))

    # Обновление экрана
    pygame.display.flip()
    clock.tick(FPS)

# Завершение Pygame
pygame.quit()
