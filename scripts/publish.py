"""Publish package to CodeArtifact."""

from duct import cmd

cmd('uv', 'build').run()
cmd('uv', 'publish', '--index', 'codeartifact').run()
