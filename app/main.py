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


def cat_file(args):
    _ = args.p
    blob_sha = args.blob_sha
    object_path = (Path(".git/objects")/blob_sha[:2]/blob_sha[2:])
    if not object_path.is_file():
        print("Object not found.")
        return
    with open(object_path, "rb") as f:
        compressed_obj = f.read()
    decompressed_obj = zlib.decompress(compressed_obj)
    header, content = decompressed_obj.split(b"\0", maxsplit=1)
    # obj_type, size = header.decode().split(" ")
    sys.stdout.write(content.decode())


def hash_object(args):
    write_enabled = args.w
    filepath = Path(args.filepath)

    if not filepath.is_file():
        print("Object not found.")
        return
    with open(filepath, "rb") as f:
        contents = f.read()
    size = len(contents)
    header = f"blob {size}"
    blob = header.encode() + b"\0" + contents
    sha_hash = hashlib.sha1(blob).hexdigest()
    print(sha_hash)
    if write_enabled:
        compressed_blob = zlib.compress(blob)
        sub_dir = sha_hash[:2]
        obj_name = sha_hash[2:]
        if not (Path(".git/objects")/sub_dir).is_dir():
            Path.mkdir(Path(".git/objects")/sub_dir)
        with open(Path(".git/objects")/sub_dir/obj_name, "wb") as f:
            f.write(compressed_blob)


def main():
    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers()

    init_parser = subparser.add_parser("init")
    parser.set_defaults(func=init)

    cat_file_parser = subparser.add_parser("cat-file")
    cat_file_parser.add_argument("blob_sha")
    cat_file_parser.add_argument("-p", action="store_true")
    cat_file_parser.set_defaults(func=cat_file)

    cat_file_parser = subparser.add_parser("hash-object")
    cat_file_parser.add_argument("filepath")
    cat_file_parser.add_argument("-w", action="store_true")
    cat_file_parser.set_defaults(func=hash_object)

    args = parser.parse_args()
    if args.func:
        args.func(args)


if __name__ == "__main__":
    main()
