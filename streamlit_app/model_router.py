import h5py

file_path = "models/pumpkin_wheat.h5"

with h5py.File(file_path, "r") as f:
    print("Keys at root:")
    for key in f.keys():
        print(" -", key)

    if "model_weights" in f:
        print("\nModel weights groups:")
        for layer in f["model_weights"].keys():
            print(layer)
