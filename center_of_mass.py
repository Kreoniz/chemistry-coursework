# Атомные массы (в атомных единицах массы)
ATOMIC_MASSES = {
    "H": 1.008,
    "C": 12.011,
    "S": 32.06,
    "O": 15.999,
    "Cl": 35.45,
    "N": 14.007,
    "P": 30.974,
}


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


# Загрузка атомов из файла и вычисление центра массы
atoms = load_xyz("./molecules/graphite.xyz")
center_x_molecule, center_y_molecule, center_z_molecule = calculate_center_of_mass(
    atoms
)

print(
    f"Центр массы X: {center_x_molecule}\nЦентр массы Y: {center_y_molecule}\nЦентр массы Z: {center_z_molecule}"
)
