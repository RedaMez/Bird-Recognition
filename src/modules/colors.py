import cv2
import numpy as np
import os

def rgb_to_hsv(color):
    return cv2.cvtColor(color, cv2.COLOR_RGB2HSV)

# compte le nombre de pixels de chaque couleur en rgb
# puis converti le tout en hsv avant de regrouper
# les couleurs par leur hue (teinte)
def color_count_dict(img, dir):
    # print(f"color_count_dict: file = {img}")
    image = cv2.imread(dir + img, cv2.IMREAD_UNCHANGED)
    total_pixels = 0
    color_counts = {}

    for i in range(len(image)):
        for j in range(len(image[0])):
            rgba_color = image[i][j]
            # transparence
            alpha = rgba_color[3]
            if alpha != 0:  # Si non transparent
                total_pixels += 1
                # rgb sans canal alpha (sans la transparence)
                rgb_color = rgba_color[:3]
                # conversion en hsv
                hsv_color = cv2.cvtColor(
                    np.uint8([[rgb_color]]), cv2.COLOR_BGR2HSV)[0][0]
                # On récupére la teinte
                hue = hsv_color[0]

                # print(f"Hue: {hue}, RGB Color: {rgb_color}")
                for color_range, color_name in (
                    (range(0, 29), 'Rouge'),
                    (range(150, 180), 'Rouge'),
                    (range(30, 59), 'Jaune'),
                    (range(60, 89), 'Vert'),
                    (range(90, 119), 'Cyan'),
                    (range(120, 149), 'Bleu'),
                ):
                    if hue in color_range:
                        if color_name in color_counts:
                            color_counts[color_name] += 1
                        else:
                            color_counts[color_name] = 1
                        break
    colors_to_remove = []
    # On converti tout ce comptage en pourcentage de présence de chaque couleur (groupé par teinte)
    for color, count in color_counts.items():
        color_counts[color] = round((count / total_pixels) * 100, 2)
        if(color_counts[color] == 0.0):
        # On stocke dans une liste pour éviter de modifier le dict en pleine itération
            colors_to_remove.append(color)

    # Si on a 0.0, on supprime de notre dictionnaire car négligeable (3 chiffres après la virgule et on a 0.0...)
    for color in colors_to_remove:
        color_counts.pop(color)
    return color_counts

# applique color_count pour tout les fichiers dans le dossier results
def color_count_all(dir):
    for file in os.listdir(dir):
        if os.path.isfile(os.path.join(dir, file)) and not file.startswith('.'):
            color_count_dict(file, dir)


def main():
    print("Vous êtes censés lancer le programme via le main.")

if __name__ == "__main__":
    main()
