import os
import shutil
import sys
from src.modules.modele import load_image, unsupervised_model, supervised_model, model_rasp_image
from src.modules.bird_extractor import extract_all
from datetime import datetime
import paramiko


def main(dist, focal):
    res = "resources/"
    dirs = [res+"accepted_birds/", res+"model_trainer/", res+"birds_to_validate/", res +
            "extracted_birds_to_validate/", res+"results/", res+"raspberry_birds/", res+"extracted_raspberry_birds/"]
    for dir in dirs:
        os.makedirs(dir, exist_ok=True)
    extract_all(dirs[0],dirs[1])
    extract_all(dirs[2],dirs[3])
    print("Loading images for the \033[1;34munsupervised model\033[0m...")
    load_image(dist, focal, dirs[3],False)
    print(
        "Images loaded succesfully for the \033[1;34munsupervised model\033[0m...")
    print("Loading images for the \033[1;34msupervised model\033[0m...")
    load_image(dist, focal, dirs[1],True)
    print(
        "Images loaded succesfully for the \033[1;34msupervised model\033[0m...")
    sys.stdin.flush()  # Vider le tampon d'entrée
    input(
        "Appuyez sur Entrée pour lancer le modèle \033[1;34mnon supervisé\033[0m...")
    unsupervised_model(dist, focal, dirs[3], dirs[4],0.80)
    sys.stdin.flush()  # Vider le tampon d'entrée
    input("Appuyez sur Entrée pour lancer le modèle supervisé...")
    supervised_model(dist, focal, dirs[1], dirs[4],0.70)

    # Paramètres de connexion SSH
    HOST = 'raspberrypi.local'
    USERNAME = 'pi'
    PASSWORD = 'mezianehafid2023'
    # Paramètres de la caméra (je penses qu'on prend une photo entiere et qu'on la traite après avec resize non?)
    # CAMERA_WIDTH = 640
    # CAMERA_HEIGHT = 480
    # SI on garde les height est width, on doit rajouter -h {CAMERA_HEIGHT} -w {CAMERA_WIDTH} dans la "command" avec un f avant

    # Initialisation de la connexion SSH
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, username=USERNAME, password=PASSWORD)
    sys.stdin.flush()  # Vider le tampon d'entrée
    input("Appuyez sur Entrée pour lancer la prise de photo avec le raspberry...")
    # try finally pour que même si le programme crash ou est interrompu, la connection ssh est fermée
    try:
        # Prise de photos en boucle
        while True:
            # Commande pour prendre une photo avec la caméra Raspberry Pi
            command = 'raspistill -t 10000 -o /home/pi/photo.png'

            # Exécution de la commande sur le Raspberry Pi
            stdin, stdout, stderr = client.exec_command(command)

            # Transférer le fichier photo.png vers l'ordinateur
            now = datetime.now()
            heure_actuelle = now.strftime("%Y-%m-%d_%H-%M-%S")

            # transport = client.get_transport()
            sftp = client.open_sftp()
            sftp.get('/home/pi/photo.png', f'{dirs[5]}{heure_actuelle}.png')
            sftp.close()
            # Traitement de la photo rajoutée dans le dossier birds_to_validate
            extract_all(dirs[5], dirs[6])
            load_image(dist, focal, dirs[6],False)
            model_rasp_image(dist,focal,dirs[6],0.75,dirs[1],dirs[4])
            # On vide raspberry_bird
            shutil.rmtree(dirs[5])
            os.makedirs(dirs[5], exist_ok=True)

    finally:
        # Fermeture de la connexion SSH
        client.close()


if __name__ == '__main__':
    main(100, 1000)
