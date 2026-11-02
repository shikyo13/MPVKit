#!/usr/bin/env python3
"""Rebuild dav1d's iOS/tvOS device slices with ARM assembly enabled.

Requires Xcode, Python 3, Git, Meson and Ninja. Other platform slices and the
public headers are preserved from the checksum-verified upstream XCFramework.
"""

import argparse
import hashlib
import pathlib
import shutil
import subprocess
import tempfile
import urllib.request

SOURCE_REVISION = "b546257f770768b2c88258c533da38b91a06f737"
SOURCE_URL = "https://github.com/videolan/dav1d.git"
FRAMEWORK_URL = "https://github.com/mpvkit/libdav1d-build/releases/download/1.5.3/Libdav1d.xcframework.zip"
FRAMEWORK_SHA256 = "d1a32ae6a1f0193e9f05c44c9176844af7f6d2a58cb33843f6f1b8dfd9224083"


def run(*args, **kwargs):
    return subprocess.run(args, check=True, **kwargs)


def output(*args):
    return subprocess.check_output(args, text=True).strip()


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_slice(work, source, sdk, architecture, target):
    name = f"{sdk}-{architecture}"
    build = work / name
    cross = work / f"{name}.ini"
    compiler = output("xcrun", "--sdk", sdk, "--find", "clang")
    sysroot = output("xcrun", "--sdk", sdk, "--show-sdk-path")
    cross.write_text(
        "[binaries]\n"
        f"c = {[compiler, '-target', target, '-isysroot', sysroot]!r}\n"
        "ar = '/usr/bin/ar'\nstrip = '/usr/bin/strip'\n"
        "[host_machine]\nsystem = 'darwin'\ncpu_family = 'aarch64'\n"
        f"cpu = '{architecture}'\nendian = 'little'\n"
        "[built-in options]\ndefault_library = 'static'\n"
        "buildtype = 'release'\nb_staticpic = true\n"
    )
    run("meson", "setup", str(build), str(source), "--cross-file", str(cross),
        "-Denable_asm=true", "-Denable_tests=false", "-Denable_tools=false",
        "-Denable_examples=false")
    run("ninja", "-C", str(build), "-j", "6")
    archive = build / "src/libdav1d.a"
    symbols = output("nm", "-g", str(archive))
    if "_neon" not in symbols:
        raise RuntimeError(f"No NEON implementations found in {name}")
    return archive


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=pathlib.Path, required=True,
                        help="Destination directory for the release ZIP and checksum")
    args = parser.parse_args()
    destination = args.output.resolve()
    destination.mkdir(parents=True, exist_ok=True)
    archive = destination / "Libdav1d.xcframework.zip"
    if archive.exists():
        parser.error(f"Refusing to replace existing artifact: {archive}")
    for tool in ("xcrun", "git", "meson", "ninja", "ditto", "lipo", "nm"):
        if not shutil.which(tool):
            parser.error(f"Required tool is missing: {tool}")
    with tempfile.TemporaryDirectory(prefix="dav1d-build-") as directory:
        work = pathlib.Path(directory)
        upstream = work / "upstream.zip"
        urllib.request.urlretrieve(FRAMEWORK_URL, upstream)
        if sha256(upstream) != FRAMEWORK_SHA256:
            raise RuntimeError("Upstream XCFramework checksum does not match")
        package = work / "package"
        run("ditto", "-x", "-k", str(upstream), str(package))
        framework = package / "Libdav1d.xcframework"
        source = work / "source"
        run("git", "init", "-q", str(source))
        run("git", "-C", str(source), "fetch", "--depth=1", SOURCE_URL, SOURCE_REVISION)
        run("git", "-C", str(source), "checkout", "--detach", "FETCH_HEAD")
        if output("git", "-C", str(source), "rev-parse", "HEAD") != SOURCE_REVISION:
            raise RuntimeError("Unexpected dav1d source revision")
        ios = build_slice(work, source, "iphoneos", "arm64", "arm64-apple-ios15.0")
        tv = build_slice(work, source, "appletvos", "arm64", "arm64-apple-tvos15.0")
        tv_e = build_slice(work, source, "appletvos", "arm64e", "arm64e-apple-tvos15.0")
        shutil.copyfile(ios, framework / "ios-arm64/Libdav1d.framework/Libdav1d")
        run("lipo", "-create", str(tv), str(tv_e), "-output",
            str(framework / "tvos-arm64_arm64e/Libdav1d.framework/Libdav1d"))
        shutil.copyfile(source / "COPYING", framework / "LICENSE.dav1d")
        run("ditto", "-c", "-k", "--keepParent", "--norsrc", str(framework), str(archive))
    checksum = sha256(archive)
    (destination / "Libdav1d.xcframework.checksum.txt").write_text(checksum + "\n")
    print(f"{archive}\nSHA256 {checksum}")


if __name__ == "__main__":
    main()
