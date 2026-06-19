from pathlib import Path

# user = input("enter: ")
# def recur(path: str):
#     folder_path = Path(path)
#     for file_path in folder_path.iterdir():
#         if file_path.is_file():
#             print(f"\n\n===== file name: {file_path.name} =====")
#             content = file_path.read_text(encoding="utf8", errors="ignore")
#             print(f"\ncontent:\n{content}")
        
#         if file_path.is_dir():
#             recur(file_path)

# recur(user)


user = input("Enter folder path: ")

seen_folders = set()

def recur(path: str):
    folder_path = Path(path).resolve()
    
    if folder_path in seen_folders:
        return
    
    seen_folders.add(folder_path)

    try:
        for file_path in folder_path.iterdir():
            real_file_path = file_path.resolve()
            
            if real_file_path.is_file():
                print(f"\n\n===== file name: {real_file_path.name} =====")
                content = real_file_path.read_text(encoding="utf8", errors="ignore")
                print(f"\ncontent:\n{content}")
            
            elif real_file_path.is_dir():
                recur(str(real_file_path))
                
    except PermissionError:
        print(f"Access Denied to: {folder_path.name}")


recur(user)
