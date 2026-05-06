"""Publish package to CodeArtifact."""

from duct import cmd

cmd('uv', 'publish', '--index', 'codeartifact').run()
