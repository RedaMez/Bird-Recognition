import os
import shutil
import time
from src.modules.dimensions import birdRealArea, pixel_area
from src.modules.colors import color_count_dict
from multiprocessing import Pool, Manager

manager = Manager()
images_data = manager.dict()
valid_data = manager.dict()

# img1 et img2 deux images différentes ou non
# focal et dist comme décrit dans la méthode birdRealArea
# Return un coefficient de similarité entre les deux aires
# On décidera plus tard de ce qu'un coefficient correct vaut
def compare_two_images_Area(img1, img2,dist,focal,dir1,dir2):
    if(img1 in images_data):       
        c_area_1 = images_data[img1][0]
    else:
        p_area_1 = pixel_area(img1,dir1)
        c_area_1 = birdRealArea(p_area_1,dist,focal)

    if(img2 in images_data):
        c_area_2 = images_data[img2][0]
    else:
        p_area_2 = pixel_area(img2,dir2)
        c_area_2 = birdRealArea(p_area_2,dist,focal)

    max_area = max(c_area_1, c_area_2)
    min_area = min(c_area_1, c_area_2)
    if(max_area == 0):
        if(min_area == 0):
            return 1
        else:
            return 0
    return (min_area/max_area)

# calcul de la médiane après avoir trier le dictionnaire de couleurs
def get_median_color_percentage(color_dict):
    sorted_dict = {k: v for k, v in sorted(color_dict.items(), key=lambda item: item[1])}
    values = list(sorted_dict.values())
    length = len(values)
    if length <= 1:
        return values[0] if length == 1 else 0
    median_index = (length - 1)//2
    if length % 2 == 0:
        median_value = (values[median_index] + values[median_index + 1]) / 2
    else:
        median_value = values[median_index]
    return median_value


# img1 et img2 deux images différentes ou non
# Return un coefficient de similarité entre les deux dictionnaires
# de couleurs (une moyenne entre tous les coeff de couleurs 2 à 2)
# On décidera plus tard de ce qu'un coefficient correct vaut
def compare_two_images_Colors(img1, img2,dir1,dir2):
    if(img1 in images_data):       
        c_dict_1 = images_data[img1][1]
    else:
        c_dict_1 = color_count_dict(img1,dir1)
    if(img2 in images_data):       
        c_dict_2 = images_data[img2][1]
    else:
        c_dict_2 = color_count_dict(img2,dir2)

    # if not c_dict_1 and not c_dict_2:
    #     # les deux images sont blanches, donc 100% de similarité
    #     # les 2 dicts sont vides
    #     return 1
    
    # On fusionne utilise les clefs des deux dicts pour avoir notre
    # dictionnaire finale
    keys = list(c_dict_1.keys() | c_dict_2.keys())
    result_dict = dict.fromkeys(keys, 0)
    for colors in result_dict.keys():
        if colors in c_dict_1 and colors in c_dict_2:
            color1 = c_dict_1[colors]
            color2 = c_dict_2[colors]
            max_color = max(color1, color2)
            min_color = min(color1, color2)
            result_dict[colors] = min_color / max_color 
        else:
            result_dict[colors] = 0
    threshold = get_median_color_percentage(result_dict)
    total_colors = 0
    count_colors = 0
    count_all = 0
    for val in result_dict.values():
        if val >= threshold:
            total_colors += val
            count_colors += 1
        else:
            count_all += 1
    if count_colors == 0:
        return 0
    else:
        return total_colors/count_colors

#fait une comparaison de l'aire et des couleurs de 2 images
def compare_two_images(img1,img2, dist,focal , dir1,dir2,threshold):
    print(f"\nComparing two images: \033[1;34m{img1}\033[0m & \033[1;34m{img2}\033[0m")
    color_similarities = compare_two_images_Colors(img1,img2,dir1,dir2)
    area_similarities = compare_two_images_Area(img1,img2,dist,focal,dir1,dir2)
    moyenne = (0.20*area_similarities) + (0.80*color_similarities)
    print(f"couleurs: {color_similarities}")
    print(f"aires: {area_similarities}")
    if(moyenne>threshold):
        print(f"\033[32mmoyenne: {moyenne}\033[0m")
        return True,moyenne
    else:
        print(f"\033[31mmoyenne: {moyenne}\033[0m")
        return False,moyenne

# Utilisée pour comparer file avec tous les fichiers deja rajoutés dans results
def percentage_in_sub_dir(file_name,file_dir,sub_dir,dist,focal,threshold):
    png_files = []
    for root,dirs,files in os.walk(sub_dir):
        for file_i in files:
            if file_i.endswith(".png"):
                file_path = os.path.join(root,file_i)
                png_files.append(file_path)
    average_similarity = 0
    count = 0
    total_similarity = 0
    for i in range(len(png_files)):
        dir_i = os.path.dirname(png_files[i])
        filename_i = os.path.basename(png_files[i])
        better,similarity_percentage = compare_two_images(file_name,filename_i,dist,focal,file_dir,dir_i+"/",threshold)
        total_similarity += similarity_percentage
        count += 1
    average_similarity = total_similarity / count
    print(average_similarity)
    return average_similarity

def percentages_in_dir(file,file_dir,dirs_4,dist,focal,threshold):
    subdirectories = [os.path.join(dirs_4, sub_dir) for sub_dir in os.listdir(dirs_4) if os.path.isdir(os.path.join(dirs_4, sub_dir))]
    max_value= 0
    sub_dir = ""
    for subdirectory in subdirectories:
        print(subdirectory)
        current_percent = percentage_in_sub_dir(file,file_dir,subdirectory,dist,focal,threshold)
        if current_percent > max_value:
            max_value = current_percent
            sub_dir = subdirectory
    print(f"max :{max_value} and dir: {sub_dir}")
    return max_value,sub_dir

def process_file(file,dist,focal,directory,isValid):
    print(f"Loading image: {file}")
    p_area = pixel_area(file, directory)
    images_data[file] = (birdRealArea(p_area, dist, focal), color_count_dict(file, directory))
    if isValid:
        valid_data[file] = (birdRealArea(p_area, dist, focal), color_count_dict(file, directory))

#charger les images dans images_data
def load_image(dist,focal,directory,isValid):
    file_list = [file for file in os.listdir(directory) if os.path.isfile(os.path.join(directory,file)) and not file.startswith('.') and file.endswith(".png")]
    pool = Pool()
    pool.starmap(process_file, [(file, dist, focal, directory,isValid) for file in file_list])
    pool.close()
    pool.join()

def unsupervised_model(dist,focal,dirs_3,dirs_4,threshold):
    print("\nUnsupervised training...")
    # On commence par regrouper toutes les images à 80% similaires présentes dans extracted_bird_to_validate
    bird_list = []
    for file in os.listdir(dirs_3):
        if os.path.isfile(os.path.join(dirs_3, file)) and not file.startswith('.') and file.endswith(".png"):
            # On commence par mettre toutes les images dans une même liste
            bird_list.append(file)
    while len(bird_list) > 0:
        # On fait une nouvelle liste à manipuler
        copy_bird_list = bird_list[1:]
        pivot = bird_list[0]

        # On retire de copy_bird_list tout oiseau avec un taux de similitude >=70% avec notre pivot qu'on déplacera donc dans un dossier avec le nom du pivot
        for bird in bird_list[1:]:
            better,value = compare_two_images(pivot,bird,dist,focal,dirs_3,dirs_3,threshold)
            if not better:
                copy_bird_list.remove(bird)
        
        # On se retrouve dans copy_bird_list avec uniquement les oiseaux similaires à notre pivot
        # On déplace tout le contenu de copy_bird_list ainsi que notre pivot dans un nouveau sous-dossier du même nom que notre pivot
        pivot_name, extension = os.path.splitext(os.path.basename(pivot))
        folder = dirs_4+pivot_name+"/"
        if not os.path.exists(folder):
            os.makedirs(folder)
        shutil.move(dirs_3+pivot,folder)
        bird_list.remove(pivot)
        for bird in copy_bird_list:
            shutil.move(dirs_3+bird, folder)
            bird_list.remove(bird)
        time.sleep(3)
    print("\nUnsupervised training completed.")

def supervised_model(dist,focal,dirs_1,dirs_4,threshold):
    print("\nSupervised training...")
    # Pour chaque sous-dossier de dirs[4]
    # Créer deux dossiers Valid et Invalid
    # Pour chaque image .png dans ces sous-dossiers
    # Si l'image correspond à 80% à une image présente dans le s valid_images
    # Rajouter dans valid, sinon invalid
    for subfolder in os.listdir(dirs_4):
        subfolder_path = os.path.join(dirs_4, subfolder)
        if os.path.isdir(subfolder_path):
            # On crée les sous-dossiers valid et invalid dans chaque sous-dossier de results
            valid_folder = os.path.join(subfolder_path, "valid")
            invalid_folder = os.path.join(subfolder_path, "invalid")
            os.makedirs(valid_folder, exist_ok=True)
            os.makedirs(invalid_folder, exist_ok=True)
            # On doit maintenant distribuer les images présentes dans ce sous-dossier dans valid et invalid
            # On parcours donc chaque image présente dans notre sous-dossier courant dans results
            for file in os.listdir(subfolder_path):
                if file.endswith(".png"):
                    file_path = os.path.join(subfolder_path,file)
                    moved = -1
                    for valid in valid_data:
                        better,value = compare_two_images(file,valid,dist,focal,subfolder_path,dirs_1,threshold)
                        if better:
                            shutil.move(file_path,valid_folder)
                            print(f"\n{file} was moved to {valid_folder}")
                            moved = 1
                            break
                    if(moved == -1):
                        shutil.move(file_path,invalid_folder)
                        print(f"\n{file} was moved to {invalid_folder}")
                time.sleep(1)
    print("\nSupervised training completed.")

def model_rasp_image(dist,focal,dir_6,threshold,dir_1,dir_4):
    print("\nAnalysing the freshly taken pictures...")
    for file in os.listdir(dir_6):
        if file.endswith(".png"):
            file_path = os.path.join(dir_6,file)
            moved = -1
            isValid = "invalid"
            # On vérifie d'abord si notre image est valide
            for valid in valid_data:
                better,value = compare_two_images(file,valid,dist,focal,dir_6,dir_1,threshold)
                if better:
                    isValid = "valid"
                    break
            # On cherche maintenant le sous-dossier adéquat dans results
            maxValue, directory = percentages_in_dir(file,dir_6,dir_4,dist,focal,threshold)
            if maxValue > threshold:
                shutil.move(file_path,directory+"/"+isValid)
                print(f"\n{file} was moved to {directory}/{isValid}")
            else:
                valid_folder = os.path.join(dir_4+file+"/", "valid")
                invalid_folder = os.path.join(dir_4+file+"/", "invalid")
                os.makedirs(valid_folder, exist_ok=True)
                os.makedirs(invalid_folder, exist_ok=True)
                shutil.move(file_path,dir_4+file+"/"+isValid)
                print(f"\n{file} was moved to {dir_4}{file}/{isValid}")

def main():
    print("Vous êtes censés lancer le programme via le main.")

if __name__ == "__main__":
    main()
