import os
import json

def validate_dataset(dataset_dir):
    result = {"valid": True, "message": ""}

    if not os.path.exists(dataset_dir):
        result["valid"] = False
        result["message"] = "The dataset directory does not exist."
        return json.dumps(result)

    train_dir = os.path.join(dataset_dir, "train")
    valid_dir = os.path.join(dataset_dir, "valid")

    if not os.path.exists(train_dir):
        if not os.path.exists(valid_dir):
            result["valid"] = False
            result["message"] = "The 'train' and 'valid' directories must exist in the dataset."
            return json.dumps(result)

    if not os.path.exists(train_dir):
        result["valid"] = False
        result["message"] = "The 'train' directory must exist in the dataset."
        return json.dumps(result)

    if not os.path.exists(valid_dir):
        result["valid"] = False
        result["message"] = "The 'valid' directory must exist in the dataset."
        return json.dumps(result)

    train_subfolders = [f for f in os.listdir(train_dir) if not f.startswith(".")]
    valid_subfolders = [f for f in os.listdir(valid_dir) if not f.startswith(".")]

    if not train_subfolders or not valid_subfolders:
        result["valid"] = False
        result["message"] = "The 'train' and 'valid' directories must contain at least one image folder."
        return json.dumps(result)

    return json.dumps(result)