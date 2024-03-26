import os

FROM_PROJECT = "heavy_stack"
FROM_PROJECT_DASH_NAME = "heavy-stack"
FROM_PROJECT_PROPER_NAME = "Heavy Stack"
FROM_PROJECT_FORMAL_TITLE = "The Heavy Stack"

OTHER_PATHS = [
    ".devcontainer",
    ".vscode",
    "brython",
    "dev_scripts",
    "dockerfiles",
    "static",
    "tests",
]

OTHER_FILES = [
    ".gitignore",
    "alembic.ini",
    "docker-compose.yaml",
    "LICENSE",
    "pyproject.toml",
]

STRINGS_TO_REMOVE = ["The Heavy Stack used by Heavy Resume", "Heavy Resume"]


def main() -> None:
    new_project_name = None
    while not new_project_name or " " in new_project_name:
        print("Enter the project name in snake_case (e.g. my_module)")
        new_project_name = input("Enter the new project name: ").lower()
    new_project_dash_name = new_project_name.replace("_", "-").lower()
    new_project_default_proper_name = new_project_name.replace("_", " ").title()
    new_project_proper_name = input(f"Confirm proper name ({new_project_default_proper_name}): ")
    if not new_project_proper_name:
        new_project_proper_name = new_project_default_proper_name
    new_project_formal_title = new_project_proper_name

    print(f"{FROM_PROJECT} -> {new_project_name}")
    print(f"{FROM_PROJECT_DASH_NAME} -> {new_project_dash_name}")
    print(f"{FROM_PROJECT_PROPER_NAME} -> {new_project_proper_name}")
    print(f"{FROM_PROJECT_FORMAL_TITLE} -> {new_project_formal_title}")
    confirm = input("Confirm rename? ")
    if confirm and confirm.lower()[0] == "y":
        rename_project(new_project_name, new_project_dash_name, new_project_proper_name, new_project_formal_title)
        print("Renamed project")
    else:
        print("Aborted")


def substitute_file_content(
    path: str,
    new_project_name: str,
    new_project_dash_name: str,
    new_project_proper_name: str,
    new_project_formal_title: str,
) -> None:
    with open(path, "r") as f:
        try:
            content = f.read()
        except UnicodeDecodeError:
            # binary file
            return
    for s in STRINGS_TO_REMOVE:
        content = content.replace(s, "")
    with open(path, "w") as f:
        f.write(
            content.replace(FROM_PROJECT, new_project_name)
            .replace(FROM_PROJECT_DASH_NAME, new_project_dash_name)
            .replace(FROM_PROJECT_PROPER_NAME, new_project_proper_name)
            .replace(FROM_PROJECT_FORMAL_TITLE, new_project_formal_title)
        )


def rename_project(
    new_project_name: str, new_project_dash_name: str, new_project_proper_name: str, new_project_formal_title: str
) -> None:
    # Rename project directory
    os.rename(FROM_PROJECT, new_project_name)

    # Rename project files
    for dir_name in [new_project_name] + OTHER_PATHS:
        for root, dirs, files in os.walk(dir_name):
            for name in files:
                path = os.path.join(root, name)
                substitute_file_content(
                    path, new_project_name, new_project_dash_name, new_project_proper_name, new_project_formal_title
                )

    # Rename project files
    for root, dirs, files in os.walk(new_project_name):
        for name in dirs:
            path = os.path.join(root, name)
            new_path = path.replace(FROM_PROJECT, new_project_name)
            os.rename(path, new_path)

    # Rename project files
    for root, dirs, files in os.walk(new_project_name):
        for name in files:
            path = os.path.join(root, name)
            new_path = path.replace(FROM_PROJECT, new_project_name)
            os.rename(path, new_path)

    for file in OTHER_FILES:
        substitute_file_content(
            file, new_project_name, new_project_dash_name, new_project_proper_name, new_project_formal_title
        )


if __name__ == "__main__":
    main()
