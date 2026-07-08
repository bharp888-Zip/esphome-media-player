#!/usr/bin/env python3
"""Host-side smoke tests for artwork URL rewriting helpers."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory


ROOT = Path(__file__).resolve().parent.parent

SOURCE = r'''
#include "components/artwork_image/artwork_url.h"

#include <iostream>
#include <string>

using esphome::artwork_image::cap_artwork_url;
using esphome::artwork_image::decode_url_param;

void expect_eq(const std::string &label, const std::string &actual, const std::string &expected) {
  if (actual != expected) {
    std::cerr << label << " failed\nexpected: " << expected << "\nactual:   " << actual << "\n";
    std::exit(1);
  }
}

int main() {
  expect_eq("decode_url_param", decode_url_param("https%3A%2F%2Fexample.test%2Fa+b.jpg"), "https://example.test/a b.jpg");

  expect_eq(
      "proxy_template",
      cap_artwork_url("http://homeassistant.local/api/media_player_proxy/media_player.kitchen?cache=https%3A%2F%2Fis1-ssl.mzstatic.com%2Fimage%2Fthumb%2FMusic116%2Fv4%2Fab%2Fcd%2Fef%2Fsource%2F%7Bw%7Dx%7Bh%7Dbb.jpg&token=abc"),
      "https://is1-ssl.mzstatic.com/image/thumb/Music116/v4/ab/cd/ef/source/600x600bb.jpg");

  expect_eq(
      "proxy_concrete",
      cap_artwork_url("http://homeassistant.local/api/media_player_proxy/media_player.kitchen?cache=https%3A%2F%2Fis1-ssl.mzstatic.com%2Fimage%2Fthumb%2FMusic116%2Fv4%2Fab%2Fcd%2Fef%2F3000x3000bb.jpg"),
      "https://is1-ssl.mzstatic.com/image/thumb/Music116/v4/ab/cd/ef/600x600bb.jpg");

  expect_eq(
      "proxy_concrete_heic",
      cap_artwork_url("http://homeassistant.local/api/media_player_proxy/media_player.kitchen?cache=https%3A%2F%2Fis1-ssl.mzstatic.com%2Fimage%2Fthumb%2FMusic116%2Fv4%2Fab%2Fcd%2Fef%2F3000x3000bb.heic"),
      "https://is1-ssl.mzstatic.com/image/thumb/Music116/v4/ab/cd/ef/600x600bb.jpg");

  expect_eq(
      "standalone_template",
      cap_artwork_url("https://is1-ssl.mzstatic.com/image/thumb/Music116/v4/ab/cd/ef/{w}x{h}bb.jpg"),
      "https://is1-ssl.mzstatic.com/image/thumb/Music116/v4/ab/cd/ef/600x600bb.jpg");

  expect_eq(
      "standalone_concrete_large",
      cap_artwork_url("https://is1-ssl.mzstatic.com/image/thumb/Music116/v4/ab/cd/ef/3000x3000bb.jpg"),
      "https://is1-ssl.mzstatic.com/image/thumb/Music116/v4/ab/cd/ef/600x600bb.jpg");

  expect_eq(
      "standalone_concrete_png_large",
      cap_artwork_url("https://is1-ssl.mzstatic.com/image/thumb/Music116/v4/ab/cd/ef/3000x3000bb.png"),
      "https://is1-ssl.mzstatic.com/image/thumb/Music116/v4/ab/cd/ef/600x600bb.jpg");

  const std::string small = "https://is1-ssl.mzstatic.com/image/thumb/Music116/v4/ab/cd/ef/300x300bb.jpg";
  expect_eq("standalone_concrete_small", cap_artwork_url(small), small);

  const std::string unrelated = "https://example.test/artwork.png";
  expect_eq("unrelated_url", cap_artwork_url(unrelated), unrelated);

  std::cout << "Artwork URL checks passed.\n";
  return 0;
}
'''


def main() -> int:
    compiler = os.environ.get("CXX", "c++")
    with TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        source = tmp_path / "check_artwork_url.cpp"
        binary = tmp_path / "check_artwork_url"
        source.write_text(SOURCE)
        subprocess.run(
            [compiler, "-std=c++17", "-I", str(ROOT), str(source), "-o", str(binary)],
            cwd=ROOT,
            check=True,
        )
        subprocess.run([str(binary)], cwd=ROOT, check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
