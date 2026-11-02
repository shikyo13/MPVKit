> **Fork note (shikyo13/MPVKit):** based on MPVKit 1.0.0. `Libmpv` is rebuilt with two
> patches in [`Sources/BuildScripts/patch/libmpv`](Sources/BuildScripts/patch/libmpv):
> - `0004-audiounit-survive-route-changes.patch` keeps mpv's AudioUnit output (iOS/tvOS) from crashing
>   when the audio route changes (HDMI renegotiation, AirPlay, HomePod, AirPods).
> - `0005-avfoundation-pace-feeding-and-latency.patch` paces the AVFoundation output
>   (AVSampleBufferAudioRenderer) so it keeps only the output latency plus half a second queued instead
>   of draining mpv's buffer (which caused underruns and stutter), and schedules audio no earlier than
>   the route can play it.
>
> `Libavformat` is also rebuilt from the same FFmpeg n8.1.2 source with the VobSub demuxer
> enabled for iOS, tvOS and their simulators, so external `.idx`/`.sub` pairs can be read.
> Its macOS, Mac Catalyst and visionOS slices remain upstream.
>
> `Libdav1d` 1.5.3 is rebuilt with ARM assembly optimizations enabled for iOS and tvOS
> devices. This accelerates software AV1 decoding on devices without an AV1 hardware
> decoder. Its simulator, macOS, Mac Catalyst and visionOS slices remain upstream.
> All other binaries remain upstream.

# MPVKit

[![mpv](https://img.shields.io/badge/mpv-v0.41.0-blue.svg)](https://github.com/mpv-player/mpv)
[![ffmpeg](https://img.shields.io/badge/ffmpeg-n8.1.2-blue.svg)](https://github.com/FFmpeg/FFmpeg)
[![license](https://img.shields.io/github/license/mpvkit/MPVKit)](https://github.com/mpvkit/MPVKit/main/LICENSE)

> MPVKit is only suitable for learning `libmpv` and will not be maintained too frequently.

`MPVKit` is a collection of tools to use `mpv` in `iOS`, `macOS`, `tvOS` applications.

It includes scripts to build `mpv` native libraries.

Forked from [kingslay/FFmpegKit](https://github.com/kingslay/FFmpegKit)

## About Metal support

Metal support only a patch version ([#7857](https://github.com/mpv-player/mpv/pull/7857)) and does not officially support it yet. Encountering any issues is not strange. 

## Installation

### Swift Package Manager

```
https://github.com/mpvkit/MPVKit.git
```

### Choose which version

| Version | License | Note |
|---|---|---|
| MPVKit | LGPL | [FFmpeg details](https://github.com/FFmpeg/FFmpeg/blob/master/LICENSE.md) , [mpv details](https://github.com/mpv-player/mpv/blob/master/Copyright) |
| MPVKit-GPL | GPL | Support samba protocol, same as old MPVKit version |


## How to build

To build the optimized iOS/tvOS dav1d release artifact, install Meson and Ninja,
select a full Xcode installation, and run:

```bash
python3 Tools/build-dav1d.py --output /path/to/release-artifacts
```

The script pins dav1d's source revision and verifies the upstream archive's SHA-256.
It replaces only the iOS arm64 and tvOS arm64/arm64e binaries, preserving the other
XCFramework slices and headers. It writes the ZIP and its checksum to the selected
directory. Builds use the selected Xcode SDK; use the emitted checksum when updating
the Swift package's binary target.

```bash
make build
# specified platforms (ios,macos,tvos,tvsimulator,isimulator,maccatalyst,xros,xrsimulator)
make build platform=ios,macos
# build GPL version
make build enable-gpl
# clean all build temp files and cache
make clean
# see help
make help
```

## Make demo app using the local build version

If you want the demo app to use the local build version, you need to modify `Package.swift` to reference the local build xcframework file.

<details>
<summary>Click here for more information.</summary>
  
```
.binaryTarget(
    name: "Libmpv-GPL",
    path: "dist/release/Libmpv.xcframework.zip"
),
.binaryTarget(
    name: "Libavcodec-GPL",
    path: "dist/release/Libavcodec.xcframework.zip"
),
.binaryTarget(
    name: "Libavdevice-GPL",
    path: "dist/release/Libavdevice.xcframework.zip"
),
.binaryTarget(
    name: "Libavformat-GPL",
    path: "dist/release/Libavformat.xcframework.zip"
),
.binaryTarget(
    name: "Libavfilter-GPL",
    path: "dist/release/Libavfilter.xcframework.zip"
),
.binaryTarget(
    name: "Libavutil-GPL",
    path: "dist/release/Libavutil.xcframework.zip"
),
.binaryTarget(
    name: "Libswresample-GPL",
    path: "dist/release/Libswresample.xcframework.zip"
),
.binaryTarget(
    name: "Libswscale-GPL",
    path: "dist/release/Libswscale.xcframework.zip"
),
```

</details>

## Run default mpv player

```bash
./mpv.sh --input-commands='script-message display-stats-toggle' [url]
./mpv.sh --list-options
```

> Use <kbd>Shift</kbd>+<kbd>i</kbd> to show stats overlay

## Related Projects

* [moltenvk-build](https://github.com/mpvkit/moltenvk-build)
* [libplacebo-build](https://github.com/mpvkit/libplacebo-build)
* [libdovi-build](https://github.com/mpvkit/libdovi-build)
* [libshaderc-build](https://github.com/mpvkit/libshaderc-build)
* [libluajit-build](https://github.com/mpvkit/libluajit-build)
* [libass-build](https://github.com/mpvkit/libass-build)
* [libbluray-build](https://github.com/mpvkit/libbluray-build)
* [libsmbclient-build](https://github.com/mpvkit/libsmbclient-build)
* [gnutls-build](https://github.com/mpvkit/gnutls-build)
* [openssl-build](https://github.com/mpvkit/openssl-build)

## Donation

If you appreciate my current work, you can buy me a cup of coffee ☕️.

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/C0C410P7UN)

## License

`MPVKit` source alone is licensed under the LGPL v3.0.

`MPVKit` bundles (`frameworks`, `xcframeworks`), which include both `libmpv` and `FFmpeg` libraries, are also licensed under the LGPL v3.0. However, if the source code is built using the optional `enable-gpl` flag or prebuilt binaries with `-GPL` postfix are used, then `MPVKit` bundles become subject to the GPL v3.0.
