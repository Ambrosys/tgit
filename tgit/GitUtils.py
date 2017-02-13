import site
import re
import hashlib
import collections

import ansi2html

from . import Utils
from . import  Globals


def _calculateDiffHash( commitHash, paths ):
    cmd = ['git', 'show', '--format=', commitHash, '--']
    cmd.extend( paths )
    diff = Utils.call( cmd, cwd=Globals.repositoryDir )
    # replace patterns like "index 5504aae..f60cf6b 100755" or
    # "index 5504aae..f60cf6b" with "index 0000000..0000000 100755"
    # or "index 0000000..0000000" respectively
    regex = re.compile("^index [a-z0-9]+\.\.[a-z0-9]+( [0-9]+)?$")
    diff[:] = [regex.sub( 'index 0000000..0000000\\1', line ) for line in diff]
    if Globals.calculateDiffHashesSpaceTolerant:
        # remove blank lines and white space at EOL
        diff[:] = [line.rstrip() for line in diff if line.strip()]

    m = hashlib.sha1()
    m.update( '\n'.join( diff ).encode('utf-8') )
    return m.digest().hex()[:7]

def getDiffHash( commitHash, paths, forceGeneration ):
    pathsString = ':'.join( sorted( paths ) )

    if Globals.calculateDiffHashesSpaceTolerant:
        hash_commit_filenames_diffHash = Globals.hash_commit_filenames_spaceTolerantDiffHash
    else:
        hash_commit_filenames_diffHash = Globals.hash_commit_filenames_diffHash

    if commitHash in hash_commit_filenames_diffHash:
        if pathsString in hash_commit_filenames_diffHash[commitHash]:
            return hash_commit_filenames_diffHash[commitHash][pathsString]

    if not forceGeneration:
        return ''

    if not commitHash in hash_commit_filenames_diffHash:
        hash_commit_filenames_diffHash[commitHash] = collections.OrderedDict()

    diffHash = _calculateDiffHash( commitHash, paths )
    hash_commit_filenames_diffHash[commitHash][pathsString] = diffHash
    return diffHash

def getDiffHtml( commitHash, paths ):
    cmd = ['git', 'show', '--format=', commitHash, '--color-words', '--']
    cmd.extend( paths )
    diff = Utils.call( cmd, cwd=Globals.repositoryDir )
    conv = ansi2html.Ansi2HTMLConverter( font_size="9pt" )
    ansi = '\n'.join( diff )
    html = conv.convert( ansi )
    #html = '\n'.join( Utils.call( ['ansi2html.sh', '--bg=dark'], input=ansi ) )
    return html
