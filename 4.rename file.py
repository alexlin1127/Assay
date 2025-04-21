""

""
import os

def renumber_files(directory_path):
    files = [f for f in os.listdir(directory_path) if f.endswith('.txt')]
    files.sort(key=lambda x: int(os.path.splitext(x)[0]))

    new_filenames = [f"{i+1}.txt" for i in range(len(files))]
    old_to_new_mapping = dict(zip(files, new_filenames))

    for old_name, new_name in old_to_new_mapping.items():
        os.rename(os.path.join(directory_path, old_name),
                  os.path.join(directory_path, new_name))

    return old_to_new_mapping

directory_path = '/Users/alex/Desktop/0511assay data測試/0512 news sample'

renumbering_map = renumber_files(directory_path)
print(renumbering_map)
