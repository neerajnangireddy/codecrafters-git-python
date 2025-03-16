import argparse
import os
import sys
import zlib
import hashlib
from pathlib import Path


def init(_):
    os.mkdir(".git")
    os.mkdir(".git/objects")
    os.mkdir(".git/refs")
    with open(".git/HEAD", "w") as f:
        f.write("ref: refs/heads/main\n")
    print("Initialized git directory")


def cat_file(blob_sha, p=False):
    object_path = Path(".git/objects") / blob_sha[:2] / blob_sha[2:]
    if not object_path.is_file():
        print("Object not found.")
        return
    with open(object_path, "rb") as f:
        compressed_obj = f.read()
    decompressed_obj = zlib.decompress(compressed_obj)
    header, content = decompressed_obj.split(b"\0", maxsplit=1)
    # obj_type, size = header.decode().split(" ")
    sys.stdout.write(content.decode())


def ls_tree(tree_sha, name_only=True):
    sub_dir = tree_sha[:2]
    object_sha = tree_sha[2:]
    object_path = Path(".git/objects") / sub_dir / object_sha
    if not object_path.is_file():
        print("Object not found.")
        return None, None
    with open(object_path, "rb") as f:
        contents = zlib.decompress(f.read())
    header, contents = contents.split(b"\0", maxsplit=1)
    i = 0
    while i < len(contents):
        temp = []
        while contents[i] != 0:
            temp.append(chr(contents[i]))
            i += 1
        mode, name = "".join(temp).split(maxsplit=1)
        i += 1
        obj_raw_sha = contents[i : i + 20]
        i += 20
        if name_only:
            print(name)
        else:
            print(mode, name, obj_raw_sha)


def hash_object(filepath, write_enabled=False):
    filepath = Path(filepath)
    if not filepath.is_file():
        print("Object not found.")
        raise FileNotFoundError
    with open(filepath, "rb") as f:
        contents = f.read()
    size = len(contents)
    header = f"blob {size}"
    blob = header.encode() + b"\0" + contents
    raw_sha = hashlib.sha1(blob)
    sha_hash = raw_sha.hexdigest()
    if write_enabled:
        compressed_blob = zlib.compress(blob)
        sub_dir = sha_hash[:2]
        obj_name = sha_hash[2:]
        if not (Path(".git/objects") / sub_dir).is_dir():
            Path.mkdir(Path(".git/objects") / sub_dir)
        with open(Path(".git/objects") / sub_dir / obj_name, "wb") as f:
            f.write(compressed_blob)
    return (raw_sha.digest()[:20], sha_hash)


def write_tree(loc: Path):
    tree_contents = b""
    for file in sorted(list(loc.iterdir())):
        if file.name == ".git":
            continue
        elif file.is_file():
            mode = "100644"
            raw_sha, _ = hash_object(file)
        else:
            mode = "40000"
            raw_sha, _ = write_tree(file)
        tree_contents += f"{mode} {file.name}".encode() + b"\0" + raw_sha
        # print(mode, file.name, raw_sha)

    tree_sha = hashlib.sha1(tree_contents)
    tree_sha_hash = tree_sha.hexdigest()
    if not (Path(".git/objects") / tree_sha_hash[:2]).is_dir():
        Path.mkdir(Path(".git/objects") / tree_sha_hash[:2])
    with open(Path(".git/objects") / tree_sha_hash[:2] / tree_sha_hash[2:], "wb") as f:
        tree_obj = f"tree {len(tree_contents)}".encode() + b"\0" + tree_contents
        compressed_tree_obj = zlib.compress(tree_obj)
        f.write(compressed_tree_obj)
    return tree_sha.digest()[:20], tree_sha_hash


def main():
    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers(dest="subparser_name")

    init_parser = subparser.add_parser("init")

    cat_file_parser = subparser.add_parser("cat-file")
    cat_file_parser.add_argument("blob_sha")
    cat_file_parser.add_argument("-p", action="store_true")

    hash_object_parser = subparser.add_parser("hash-object")
    hash_object_parser.add_argument("filepath")
    hash_object_parser.add_argument("-w", action="store_true")

    ls_tree_parser = subparser.add_parser("ls-tree")
    ls_tree_parser.add_argument("tree_sha")
    ls_tree_parser.add_argument("--name-only", action="store_true")

    write_tree_parser = subparser.add_parser("write-tree")

    args = parser.parse_args()
    sub_command = args.subparser_name
    if sub_command == "init":
        init(args)
    elif sub_command == "cat-file":
        cat_file(args.p)
    elif sub_command == "hash-object":
        _, hash = hash_object(args.filepath, args.write_enabled)
        print(hash)
    elif sub_command == "ls-tree":
        ls_tree(args.tree_sha, args.name_only)
    elif sub_command == "write-tree":
        _, tree_hash = write_tree(Path.cwd())
        print(tree_hash)


if __name__ == "__main__":
    main()
