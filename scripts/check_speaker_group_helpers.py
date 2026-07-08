#!/usr/bin/env python3
"""Host-side smoke tests for speaker grouping parsing helpers."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory


ROOT = Path(__file__).resolve().parent.parent

SOURCE = r'''
#include "common/addon/speaker_group_helpers.h"

#include <iostream>
#include <string>
#include <vector>

using esphome::speaker_group::parse_group_members;

void expect_members(
    const std::string &label,
    const std::string &raw,
    const std::vector<std::string> &expected) {
  const std::vector<std::string> actual = parse_group_members(raw);
  if (actual != expected) {
    std::cerr << label << " failed\nexpected:";
    for (const auto &member : expected) std::cerr << " [" << member << "]";
    std::cerr << "\nactual:  ";
    for (const auto &member : actual) std::cerr << " [" << member << "]";
    std::cerr << "\n";
    std::exit(1);
  }
}

int main() {
  expect_members(
      "plain_csv",
      "media_player.kitchen, media_player.lounge",
      {"media_player.kitchen", "media_player.lounge"});

  expect_members(
      "python_single_quote_list",
      "['media_player.kitchen', 'media_player.lounge']",
      {"media_player.kitchen", "media_player.lounge"});

  expect_members(
      "python_double_quote_list",
      "[\"media_player.kitchen\", \"media_player.lounge\"]",
      {"media_player.kitchen", "media_player.lounge"});

  expect_members(
      "spaces_and_empty_tokens",
      "  media_player.kitchen, , 'media_player.lounge'  ",
      {"media_player.kitchen", "media_player.lounge"});

  expect_members("empty", "", {});
  expect_members("empty_list", "[]", {});
  expect_members("none", "None", {});
  expect_members("upper_none", "NONE", {});
  expect_members("unknown", "unknown", {});
  expect_members("mixed_unknown", "Unknown", {});
  expect_members("unavailable", "unavailable", {});
  expect_members("upper_unavailable", "UNAVAILABLE", {});

  std::cout << "Speaker group helper checks passed.\n";
  return 0;
}
'''


def main() -> int:
    compiler = os.environ.get("CXX", "c++")
    with TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        source = tmp_path / "check_speaker_group_helpers.cpp"
        binary = tmp_path / "check_speaker_group_helpers"
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
