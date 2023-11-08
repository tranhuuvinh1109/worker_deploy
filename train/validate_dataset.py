import os

def validate_dataset(dataset_dir):
    print("dataset_dir: ", dataset_dir)
    # Check if the root folder (dataset_dir) exists
    if not os.path.exists(dataset_dir):
        return "Thư mục gốc không tồn tại."

    # Check if "train" and "valid" folders exist
    train_dir = os.path.join(dataset_dir, "train")
    valid_dir = os.path.join(dataset_dir, "valid")
    
    if not os.path.exists(train_dir):
        return "Thư mục 'train' không tồn tại."

    if not os.path.exists(valid_dir):
        return "Thư mục 'valid' không tồn tại."

    # List the folders within the "train" directory
    train_subfolders = os.listdir(train_dir)
    valid_subfolders = os.listdir(valid_dir)

    # Check if "train" and "valid" folders contain subfolders for object categories
    if not train_subfolders:
        return "Thư mục 'train' không chứa các thư mục đối tượng."
    if not valid_subfolders:
        return "Thư mục 'valid' không chứa các thư mục đối tượng."

    for object_folder in train_subfolders:
        if object_folder == "__MACOSX":
            continue  # Skip the "__MACOSX" folder

        object_folder_path = os.path.join(train_dir, object_folder)

        # Check if each object folder is a directory
        if not os.path.isdir(object_folder_path):
            return f"Thư mục '{object_folder}' trong 'train' không tồn tại hoặc không phải là thư mục."

        # Check if each object folder contains image files
        if not any(filename.endswith(('.jpg', '.jpeg', '.png', '.gif')) for filename in os.listdir(object_folder_path)):
            return f"Thư mục '{object_folder}' trong 'train' không chứa hình ảnh."

    for object_folder in valid_subfolders:
        if object_folder == "__MACOSX":
            continue  # Skip the "__MACOSX" folder

        object_folder_path = os.path.join(valid_dir, object_folder)

        # Check if each object folder is a directory
        if not os.path.isdir(object_folder_path):
            return f"Thư mục '{object_folder}' trong 'valid' không tồn tại hoặc không phải là thư mục."

        # Check if each object folder contains image files
        if not any(filename.endswith(('.jpg', '.jpeg', '.png', '.gif')) for filename in os.listdir(object_folder_path)):
            return f"Thư mục '{object_folder}' trong 'valid' không chứa hình ảnh."

    # If there are no errors, the dataset is valid
    return None
