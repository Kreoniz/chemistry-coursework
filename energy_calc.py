import numpy as np
from scipy.optimize import minimize


# Функция для расчёта энергии с использованием координат
def energy_with_coords(coords, bonds, r_eq):
    coords = coords.reshape(-1, 3)  # Преобразуем в 2D массив (количество атомов, 3)
    E_bond = bond_energy(coords, bonds, r_eq)
    E_vdw = vdw_energy(coords)
    return E_bond + E_vdw


# Оптимизация геометрии
def optimize_geometry(xyz_file, bonds, r_eq):
    atoms, coords = read_xyz(xyz_file)
    initial_coords = coords.flatten()  # Преобразуем в 1D массив для оптимизатора

    # Функция минимизации
    result = minimize(
        energy_with_coords,  # Целевая функция
        initial_coords,  # Начальное приближение
        args=(bonds, r_eq),  # Дополнительные аргументы функции
        method="BFGS",  # Метод оптимизации
        options={"disp": True},
    )

    # Результаты
    optimized_coords = result.x.reshape(-1, 3)
    return atoms, optimized_coords, result.fun


# Константы (можно заменить реальными значениями)
K_bond = 1.0  # Жесткость связи, [ккал/(моль*Å^2)]
K_theta = 1.0  # Деформационная сила, [ккал/(моль*рад^2)]
epsilon = 0.2  # Глубина потенциальной ямы, [ккал/моль]
sigma = 3.5  # Радиус взаимодействия, [Å]


# Функция для чтения XYZ файла
def read_xyz(filename):
    with open(filename, "r") as file:
        lines = file.readlines()
        atom_count = int(lines[0].strip())
        atoms = []
        coordinates = []
        for line in lines[2:]:
            parts = line.split()
            atoms.append(parts[0])
            coordinates.append([float(x) for x in parts[1:4]])
        return np.array(atoms), np.array(coordinates)


# Расчет энергии по связи
def bond_energy(coords, bonds, r_eq):
    E_bond = 0.0
    for i, j in bonds:
        r = np.linalg.norm(coords[i] - coords[j])
        E_bond += 0.5 * K_bond * (r - r_eq) ** 2
    return E_bond


# Расчет ван-дер-ваальсовой энергии
def vdw_energy(coords):
    E_vdw = 0.0
    num_atoms = len(coords)
    for i in range(num_atoms):
        for j in range(i + 1, num_atoms):
            r = np.linalg.norm(coords[i] - coords[j])
            if r == 0:
                continue  # Пропускать вычисления, если расстояние равно нулю
            E_vdw += 4 * epsilon * ((sigma / r) ** 12 - (sigma / r) ** 6)
    return E_vdw


# Основная функция для расчета энергии молекулы
def calculate_energy(xyz_file, bonds, r_eq):
    atoms, coords = read_xyz(xyz_file)

    # Энергия по связи
    E_bond = bond_energy(coords, bonds, r_eq)

    # Ван-дер-ваальсово взаимодействие
    E_vdw = vdw_energy(coords)

    # Суммарная энергия
    total_energy = E_bond + E_vdw
    return total_energy


if __name__ == "__main__":
    xyz_file = "./molecules/graphite.xyz"
    bonds = [(0, 1), (1, 2)]
    r_eq = 1.0

    atoms, optimized_coords, final_energy = optimize_geometry(xyz_file, bonds, r_eq)
    print(f"Optimized Energy: {final_energy:.3f} kcal/mol")
    print("Optimized Coordinates:")
    print(optimized_coords)
