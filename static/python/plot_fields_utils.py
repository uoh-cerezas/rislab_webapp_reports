import utm

import numpy as np
import matplotlib.pyplot as plt

from sklearn.neighbors import KNeighborsRegressor

import matplotlib.colors as colors

POINTS_TORRE = np.array(
    [[-34.396485, -70.806297], [-34.392485, -70.810373], [-34.394304, -70.811798], [-34.397501, -70.807738],
     [-34.396485, -70.806297]])
PAIRS_TORRE = np.array([[[1, 0], [2, 3]]])

POINTS_GRANEROS = np.array(
    [[-34.055773, -70.699803], [-34.055687, -70.700160], [-34.055632, -70.700395], [-34.055154, -70.702150],
     [-34.055247, -70.702164],
     [-34.055145, -70.702573], [-34.058063, -70.703465], [-34.058161, -70.703105], [-34.058630, -70.701286],
     [-34.056989, -70.700522],
     [-34.057089, -70.700196], [-34.055773, -70.699803]])

PAIRS_GRANEROS = np.array([[[0, 1], [10, 9]], [[1, 2], [9, 8]], [[2, 3], [8, 7]], [[4, 5], [7, 6]]])

PAIRS_NELTUME_PAINE_C1 = np.array([[[0, 1], [9, 8]],
                                   [[1, 2], [8, 7]],
                                   [[2, 3], [7, 6]],
                                   [[3, 4], [6, 5]],
                                   ])

POINTS_NELTUME_PAINE_C1 = np.array([[-33.789081, -70.629085], [-33.788746, -70.629804],
                                    [-33.787574, -70.630545], [-33.787021, -70.632304],
                                    [-33.786415, -70.635131], [-33.789763, -70.634262],
                                    [-33.789651, -70.632921], [-33.789955, -70.630974],
                                    [-33.789990, -70.630888], [-33.790030, -70.630062]])

POINTS_DONA_JAVIERA_SPA_C2 = np.array([[-34.400775, -70.889872], [-34.401602, -70.889915],
                                       [-34.401313, -70.888217], [-34.401201, -70.887501],
                                       [-34.401019, -70.887446],
                                       [-34.400734, -70.887007], [-34.400379, -70.887186],
                                       [-34.400214, -70.887544], [-34.400173, -70.888217],
                                       [-34.400775, -70.889872],
                                       ])

PAIRS_DONA_JAVIERA_SPA_C2 = np.array([[[1, 2], [9, 8]],
                                      [[2, 3], [8, 7]],
                                      [[4, 5], [7, 6]],
                                      ])

POINTS_EL_TOTORAL_C2 = np.array([[-34.380474, -70.858648], [-34.380935, -70.857989],
                                 [-34.382081, -70.858548], [-34.382796, -70.856743],
                                 [-34.383216, -70.855662], [-34.381331, -70.854839],
                                 [-34.380604, -70.855476], [-34.379865, -70.857381],
                                 [-34.379569, -70.858118]])

PAIRS_EL_TOTORAL_C2 = np.array([[[0, 1], [8, 7]], [[2, 3], [7, 6]], [[3, 4], [6, 5]]])

POINTS_EL_PERAL_RUCANAHUE_C3 = np.array([[-34.352715, -70.920438], [-34.353051, -70.920642],
                                         [-34.354575, -70.921790], [-34.355195, -70.922241],
                                         [-34.355753, -70.922627], [-34.357799, -70.924172],
                                         [-34.357471, -70.928882], [-34.355903, -70.927959],
                                         [-34.355372, -70.927605], [-34.354903, -70.926339],
                                         [-34.354318, -70.926242], [-34.352626, -70.925030],
                                         [-34.352334, -70.924740]])

PAIRS_EL_PERAL_RUCANAHUE_C3 = np.array(
    [[[0, 1], [12, 11]], [[1, 2], [11, 10]], [[2, 3], [10, 9]], [[3, 4], [9, 8]], [[4, 5], [8, 7]]])


def plot_polygon(pos, color="c"):
    for last_pos, new_pos in zip(pos[:-1], pos[1:]):
        plt.plot([last_pos[0], new_pos[0]], [last_pos[1], new_pos[1]], color)


def get_interpolation_array(positions, max_length):
    if len(positions) == max_length:
        return positions
    else:
        indices_x = np.floor(np.linspace(0, len(positions), max_length)).astype(np.int32)
        indices_x[-1] = len(positions) - 1
        return positions[indices_x]


def generate_positions(x1, x2, space):
    factor = space
    if x1 > x2:
        factor = -space
    positions = np.arange(x1, x2 + factor, factor)
    return positions


def calculate_sub_positions(positions, pairs, delta_factor=10):
    total_coordinates = []
    space_x = 0
    space_y = 0
    for i, pos in enumerate(positions[1:]):
        s_x = np.abs(positions[i, 0] - pos[0])
        s_y = np.abs(positions[i, 1] - pos[1])
        if s_x > space_x:
            space_x = s_x

        if s_y > space_y:
            space_y = s_y

    space_x /= delta_factor
    space_y /= delta_factor

    for pair_matrix in pairs:
        # coordinates = np.zeros([delta_factor,delta_factor,2])
        coordinates = []
        p1 = pair_matrix[0]
        p2 = pair_matrix[1]

        linx1 = generate_positions(positions[p1[0], 0], positions[p1[1], 0], space_x)
        linx2 = generate_positions(positions[p2[0], 0], positions[p2[1], 0], space_x)

        liny1 = generate_positions(positions[p1[0], 1], positions[p1[1], 1], space_y)
        liny2 = generate_positions(positions[p2[0], 1], positions[p2[1], 1], space_y)
        max_lenght = max(len(linx1), len(linx2), len(liny1), len(liny2))
        linx1 = get_interpolation_array(linx1, max_lenght)
        linx2 = get_interpolation_array(linx2, max_lenght)
        liny1 = get_interpolation_array(liny1, max_lenght)
        liny2 = get_interpolation_array(liny2, max_lenght)

        for i, (sub_posx1, sub_posx2, sub_posy1, sub_posy2) in enumerate(zip(linx1, linx2, liny1, liny2)):
            intermediate_pos_x = generate_positions(sub_posx1, sub_posx2, space_x)
            intermediate_pos_y = generate_positions(sub_posy1, sub_posy2, space_y)
            max_lenght = max(len(intermediate_pos_x), len(intermediate_pos_y))
            intermediate_pos_x = get_interpolation_array(intermediate_pos_x, max_lenght)
            intermediate_pos_y = get_interpolation_array(intermediate_pos_y, max_lenght)

            total_coordinates += [np.concatenate([intermediate_pos_x[:, None], intermediate_pos_y[:, None]], axis=1)]

    total_coordinates = np.concatenate(total_coordinates, axis=(0)).reshape([-1, 2])
    # total_coordinates = np.array(total_coordinates)
    return total_coordinates


def calculate_subpositions(points_border, pairs, delta_factor=50):
    coordinates_field = transform_locations(points_border)
    # plot_polygon(coordinates_field)

    internal_positions = calculate_sub_positions(coordinates_field, pairs, delta_factor=delta_factor)
    return coordinates_field, internal_positions


def calculate_sub_positions(positions, pairs, delta_factor=10):
    total_coordinates = []
    space_x = 0
    space_y = 0
    for i, pos in enumerate(positions[1:]):
        s_x = np.abs(positions[i, 0] - pos[0])
        s_y = np.abs(positions[i, 1] - pos[1])
        if s_x > space_x:
            space_x = s_x

        if s_y > space_y:
            space_y = s_y

    space_x /= delta_factor
    space_y /= delta_factor

    for pair_matrix in pairs:
        # coordinates = np.zeros([delta_factor,delta_factor,2])
        coordinates = []
        p1 = pair_matrix[0]
        p2 = pair_matrix[1]

        linx1 = generate_positions(positions[p1[0], 0], positions[p1[1], 0], space_x)
        linx2 = generate_positions(positions[p2[0], 0], positions[p2[1], 0], space_x)

        liny1 = generate_positions(positions[p1[0], 1], positions[p1[1], 1], space_y)
        liny2 = generate_positions(positions[p2[0], 1], positions[p2[1], 1], space_y)
        max_lenght = max(len(linx1), len(linx2), len(liny1), len(liny2))
        linx1 = get_interpolation_array(linx1, max_lenght)
        linx2 = get_interpolation_array(linx2, max_lenght)
        liny1 = get_interpolation_array(liny1, max_lenght)
        liny2 = get_interpolation_array(liny2, max_lenght)

        for i, (sub_posx1, sub_posx2, sub_posy1, sub_posy2) in enumerate(zip(linx1, linx2, liny1, liny2)):
            factorx = np.rint(np.abs(sub_posx1 - sub_posx2) / space_x).astype(np.int32)
            factory = np.rint(np.abs(sub_posy1 - sub_posy2) / space_y).astype(np.int32)
            factor = max(factorx, factory)
            intermediate_pos_x = np.linspace(sub_posx1, sub_posx2, factor)
            intermediate_pos_y = np.linspace(sub_posy1, sub_posy2, factor)
            total_coordinates += [np.concatenate([intermediate_pos_x[:, None], intermediate_pos_y[:, None]], axis=1)]

    total_coordinates = np.concatenate(total_coordinates, axis=(0)).reshape([-1, 2])
    # total_coordinates = np.array(total_coordinates)
    return total_coordinates


def plot_data_in_field(data_pos, values, positions, name_save='',
                       neighbors=4, type_display='density'):
    maturity = 'maturity' == type_display
    knn_regressor = KNeighborsRegressor(n_neighbors=neighbors, weights="distance")

    knn_regressor.fit(data_pos, values)
    # print("data_pos: ",data_pos[0,:])
    # print("positions: ",positions[0,:])
    values_pred = knn_regressor.predict(positions)

    # color1 = np.array((0,0, 1.0))
    # color2 = np.array((1.0,0,0.0))
    min_var = np.min(values_pred)
    max_var = np.max(values_pred)

    if maturity:
        # color_extreme = [(0.1,1.0,0.1),(0.3,0.8,0.2),(1.0,0.10,0.10)]
        color_extreme = [(0.1, 1.0, 0.1), (0.3, 0.9, 0.2), (1.0, 0.0, 0.00)]
    else:
        color_extreme = ['b', 'c', 'g', 'y', 'r']
    cmap_value = colors.LinearSegmentedColormap.from_list("", color_extreme)
    # plt.figure(figsize=(9,9))

    sc = plt.scatter(positions[:, 0], positions[:, 1], c=values_pred, vmin=round(min_var), vmax=round(max_var),
                     s=24, cmap=cmap_value, )
    cbar = plt.colorbar(sc, anchor=(0.7, 0.9))

    # plot_polygon(border_poses)

    if maturity:
        cbar.set_label('Madurez [%]', rotation=270, labelpad=20)
    else:
        cbar.set_label('Conteos', rotation=270, labelpad=20)
    plt.scatter(data_pos[:, 0], data_pos[:, 1], color='y', edgecolor='k',
                marker='*', s=150, label='Arboles de Control')
    plt.legend()

    if name_save:
        plt.savefig(name_save, bbox_inches='tight')


def transform_locations(locations):
    lat, lon = locations[:, 0], locations[:, 1]
    x, y, *_ = utm.from_latlon(lat, lon)
    locations = np.concatenate([x[:, None], y[:, None]], axis=1)
    return locations


def plot_border_field(points_field):
    coordinates_field = transform_locations(points_field)
    plot_polygon(coordinates_field)
    plt.axis("off")


def plot_field(points_border, pairs_border, delta_factor=25):
    coordinates_field = transform_locations(points_border)
    # plot_polygon(coordinates_field)

    internal_positions = calculate_sub_positions(coordinates_field, pairs_border, delta_factor=delta_factor)
    plt.scatter(internal_positions[:, 0], internal_positions[:, 1])
    plt.axis("off")


def get_la_torre_points():
    return calculate_subpositions(POINTS_TORRE, PAIRS_TORRE)


def get_graneros_points():
    return calculate_subpositions(POINTS_GRANEROS, PAIRS_GRANEROS)


def get_el_peral_rengo_C3():
    return calculate_subpositions(POINTS_EL_PERAL_RUCANAHUE_C3, PAIRS_EL_PERAL_RUCANAHUE_C3, delta_factor=50)


def get_el_totoral_rengo_c2():
    return calculate_subpositions(POINTS_EL_TOTORAL_C2, PAIRS_EL_TOTORAL_C2, delta_factor=50)


def get_dona_javiera_rengo_c2():
    return calculate_subpositions(POINTS_DONA_JAVIERA_SPA_C2, PAIRS_DONA_JAVIERA_SPA_C2, delta_factor=35)


def get_neltume_paine_c1():
    return calculate_subpositions(POINTS_NELTUME_PAINE_C1, PAIRS_NELTUME_PAINE_C1, delta_factor=35)
