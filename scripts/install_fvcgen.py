"""Install fvcgen from CodeArtifact."""

import os
from duct import cmd

password = os.environ['UV_INDEX_CODEARTIFACT_PASSWORD']
index_url = f'https://aws:{password}@flyvercity-368281077578.d.codeartifact.eu-west-3.amazonaws.com/pypi/tools/simple/'

cmd(
    'uv',
    'tool',
    'install',
    'fvcgen',
    '-i',
    index_url,
    '--prerelease=allow',
    '--extra-index-url',
    'https://pypi.org/simple',
).run()
