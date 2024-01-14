import cv2

# On imagine qu'on n'a que des images d'oiseaux avec fond transparent
# distance_from_objective est en millimètres, focal_length en pixels²
# apparent_size en pixel et le resultat en millimètre²
def birdRealArea(apparent_area, distance_from_objective, focal_length):
    return (apparent_area * (distance_from_objective**2))/(focal_length**2)

def pixel_area(image_path, dir):
    # On charge l'image en conservant la couche de transparence
    img = cv2.imread(dir+image_path, cv2.IMREAD_UNCHANGED)

    # On extrait le canal alpha (transparence pour chaque pixel)
    alpha = img[:,:,3]

    # On compte les pixels non transparents
    area = cv2.countNonZero(alpha)

    return area


def main():
    print("Vous êtes censés lancer le programme via le main.")

if __name__ == "__main__":
    main()
