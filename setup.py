#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2012-2014 Danilo de Jesus da Silva Bellini
#                         danilo [dot] bellini [at] gmail [dot] com
#
# Musical Mines is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# Created on Tue Jun 10 22:50:17 2014
""" Musical Mines setup file """

from setuptools import setup
import os, ast, re

# Functions based on AudioLazy setup.py

def locals_from_exec(code):
  """ Run code in a qualified exec, returning the resulting locals dict """
  namespace = {}
  exec(code, {}, namespace)
  return namespace

def pseudo_import(fname):
  """ Namespace dict with direct dunder assignments """
  is_dunder = lambda n: isinstance(n, ast.Name) and re.match("__\S*__", n.id)
  has_dunder_target = lambda n: any(map(is_dunder, n.targets))
  is_d_assign = lambda n: isinstance(n, ast.Assign) and has_dunder_target(n)
  with open(fname, "r") as f:
    astree = ast.parse(f.read(), filename=fname)
  astree.body = [node for node in astree.body if is_d_assign(node)]
  return locals_from_exec(compile(astree, fname, mode="exec"))

def read_rst_and_process(fname):
  """
  The reStructuredText string in file ``fname``, without the starting ``..``
  comment and with ``line_process`` function applied to every line.
  """
  with open(fname, "r") as f:
    data = f.read().splitlines()
  first_idx = next(idx for idx, line in enumerate(data) if line.strip())
  if data[first_idx].strip() == "..":
    next_idx = first_idx + 1
    first_idx = next(idx for idx, line in enumerate(data[next_idx:], next_idx)
                         if line.strip() and not line.startswith(" "))
  return "\n".join(data[first_idx:])

def read_description(readme_file):
  readme_data = read_rst_and_process(readme_file)
  title, descr, sections_and_ending = readme_data.split("\n\n", 2)
  sects = sections_and_ending.rsplit("----", 1)[0]
  return descr, "\n".join(block.strip() for block in ["", title, "", sects])


path = os.path.split(__file__)[0]

fname_init = os.path.join(path, "mmines.py")
fname_readme = os.path.join(path, "README.rst")

metadata = {k.strip("_") : v for k, v in pseudo_import(fname_init).items()}
metadata["description"], metadata["long_description"] = \
  read_description(fname_readme)
metadata["classifiers"] = """
Development Status :: 3 - Alpha
Environment :: Win32 (MS Windows)
Environment :: X11 Applications
Intended Audience :: Education
Intended Audience :: End Users/Desktop
Intended Audience :: Other Audience
License :: OSI Approved :: GNU General Public License v3 (GPLv3)
Natural Language :: English
Operating System :: Microsoft :: Windows
Operating System :: POSIX :: Linux
Programming Language :: Python
Programming Language :: Python :: 2
Programming Language :: Python :: 2.7
Programming Language :: Python :: 2 :: Only
Topic :: Artistic Software
Topic :: Education
Topic :: Games/Entertainment
Topic :: Games/Entertainment :: Puzzle Games
Topic :: Multimedia
""".strip().splitlines()
metadata["author_email"] = "danilo.bellini@gmail.com"
metadata["url"] = "https://github.com/danilobellini/mmines"
metadata["license"] = "GPLv3"
metadata["name"] = "mmines"
metadata["packages"] = ["_mmines"]
metadata["py_modules"] = ["mmines"]
metadata["entry_points"] = {"console_scripts": ["mmines=mmines:main"]}
metadata["install_requires"] = ["audiolazy"]

setup(**metadata)
