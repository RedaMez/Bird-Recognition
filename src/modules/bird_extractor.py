import multiprocessing
import cv2
import numpy as np
import os
from rembg import remove

# Methode avec la library RemBG
def extract_bird(filename,img_path,output_path):
    print(f"extract_bird: \033[1;34m{filename}\033[m")
    input = cv2.imread(img_path)
    output = remove(input)
    output_filename = os.path.splitext(filename)[0] + ".png"
    cv2.imwrite(os.path.join(output_path, output_filename), output)

def process_file(file, input_dir, output_dir):
    input_file = os.path.join(input_dir, file)
    extract_bird(file, input_file, output_dir)

# extrait tout les oiseaux dans le dossier birds vers le dossiers Results
def extract_all(input_dir,output_dir):
    print("\nBird extracting...")
    # on parcours tout les fichier de birds
    # on verifie que le nom correspond à un fichier et que ca ne commence pas par un point
    files = [file for file in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, file)) and not file.startswith('.')]
    pool = multiprocessing.Pool()
    pool.starmap(process_file, [(file, input_dir, output_dir) for file in files])
    print("\nBird extraction completed.")

def main():
    print("Vous êtes censés lancer le programme via le main.")

if __name__ == "__main__":
    main()
