import os
import shutil
import zipfile
import requests
import tempfile
from datetime import datetime

# ---------------- CONFIG ----------------
PATCH_URL = "https://github.com/alcfv/patch-file-host/releases/download/V1/Java.Anims.+.Debloat.zip"

# Minecraft paths
PATH_UWP = r"%localappdata%\Packages\Microsoft.MinecraftUWP_8wekyb3d8bbwe\LocalCache\minecraftpe\packcache\resource"
PATH_GDK = None  # Will be added later

# ----------------------------------------

def expand(p):
    return os.path.expandvars(p)

def choose_version():
    print("=======================================")
    print("   Minecraft Resource Pack Patcher")
    print("=======================================")
    print("Choose your Minecraft installation type:")
    print("1) Minecraft Bedrock BEFORE 1.21.20 (UWP)")
    print("2) Minecraft Bedrock 1.21.20+ (GDK)")
    choice = input("Enter 1 or 2: ").strip()

    if choice == "1":
        return expand(PATH_UWP)
    elif choice == "2":
        if PATH_GDK is None:
            print("\nGDK path not set yet. Update script when known.")
            input("Press ENTER to exit.")
            exit()
        return expand(PATH_GDK)
    else:
        print("\nInvalid choice.")
        input("Press ENTER to exit.")
        exit()

def backup_folder(folder):
    now = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = folder + "_backup_" + now
    print("\nCreating backup:", backup)
    shutil.copytree(folder, backup)
    return backup

def clear_packcache(folder):
    print("\nClearing existing server resource packs...")
    for item in os.listdir(folder):
        path = os.path.join(folder, item)
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
    print("Packcache cleared.")

def download_patch(tmpdir):
    zip_path = os.path.join(tmpdir, "patch.zip")
    print("\nDownloading patch...")
    r = requests.get(PATCH_URL, stream=True)
    r.raise_for_status()
    with open(zip_path, "wb") as f:
        for chunk in r.iter_content(8192):
            f.write(chunk)
    print("Download complete.")
    return zip_path

def extract_patch(zip_path, tmpdir):
    patch_dir = os.path.join(tmpdir, "patch")
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(patch_dir)
    return patch_dir

def copy_packs(patch_root, target_root):
    print("\nApplying patch...")
    for pack in os.listdir(patch_root):
        pack_src = os.path.join(patch_root, pack)
        pack_dst = os.path.join(target_root, pack)
        shutil.copytree(pack_src, pack_dst)
        print("Copied:", pack)
    print("All packs applied successfully.")

def main():
    target = choose_version()
    print("\nTarget folder:", target)

    if not os.path.exists(target):
        print("\nERROR: Minecraft resource pack folder not found.")
        input("Press ENTER to exit.")
        return

    backup_folder(target)
    clear_packcache(target)

    tmpdir = tempfile.mkdtemp(prefix="patcher_")
    try:
        zip_path = download_patch(tmpdir)
        patch_root = extract_patch(zip_path, tmpdir)
        copy_packs(patch_root, target)
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

    print("\nPatch applied successfully!")
    input("\nPress ENTER to exit.")

if __name__ == "__main__":
    main()
