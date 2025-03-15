import os
from pathlib import Path
import argparse
import zlib
import sys

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


def main():
    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers()

    init_parser = subparser.add_parser("init")
    parser.set_defaults(func=init)

    cat_file_parser = subparser.add_parser("cat-file")
    cat_file_parser.add_argument("blob_sha")
    cat_file_parser.add_argument("-p", action="store_true")
    cat_file_parser.set_defaults(func=cat_file)

    args = parser.parse_args()
    if args.func:
        args.func(args)


if __name__ == "__main__":
    main()
