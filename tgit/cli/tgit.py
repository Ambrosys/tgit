import argparse
import os
import signal

from .. import Globals
from .. import App


def main():
    signal.signal( signal.SIGINT, signal.SIG_DFL )

    parser = argparse.ArgumentParser( description='tgit is a simple git GUI for tagging commits.' )
    parser.add_argument( 'root', nargs='?', type=str, default='.', help = 'root directory of the repository, default: %(default)s' )
    parser.add_argument( 'paths', nargs='*', type=str, default=[], help = 'restrict to given paths' )
    parser.add_argument( '-b', '--branch', type=str, default='master', help = 'branch name, default: %(default)s' )
    parser.add_argument( '-n', '--no-numstat', action='store_true', help = 'do not call git log --numstat (faster)' )
    parser.add_argument( '--full-numstat', action='store_true', help = 'call git log --numstat for excluded files (slower)' )
    parser.add_argument( '-c', '--config-dir', metavar='DIR', type=str, default='.', help = 'directory for config files, default: %(default)s' )
    parser.add_argument( '--tags', metavar='FILENAME', type=str, default='tgit-tags.json', help = 'tags config file, default: %(default)s' )
    parser.add_argument( '--authors', metavar='FILENAME', type=str, default='tgit-authors.json', help = 'authors config file, default: %(default)s' )
    parser.add_argument( '--commits', metavar='FILENAME', type=str, default='tgit-commits.json', help = 'commits config file, default: %(default)s' )
    parser.add_argument( '--repository', metavar='FILENAME', type=str, default='tgit-repository.json', help = 'repository config file, default: %(default)s' )
    parser.add_argument( '--cache', metavar='FILENAME', type=str, default='tgit-cache.json', help = 'cache for commit history, default: %(default)s' )
    parser.add_argument( '--no-diff', action='store_true', help = 'deactivate "automatically diff all files"' )
    parser.add_argument( '--no-cache', action='store_true', help = 'do not save cache file' )
    parser.add_argument( '-r', '--read-only', action='store_true', help = 'read-only mode' )
    parser.add_argument( '-d', '--diff-hash', action='store_true', help = 'calculate diff hashes in views' )
    parser.add_argument( '-s', '--space-tolerant', action='store_true', help = 'ignore blank lines and white space at EOL in diff hashes' )
    args = parser.parse_args()

    if args.no_numstat and args.full_numstat:
        print( 'Error: --no-numstat and --full-numstat are mutually exclusive.' )
        exit( 1 )

    if args.space_tolerant and not args.diff_hash:
        print( 'Error: --space-tolerant requires --diff-hash.' )
        exit( 1 )

    if not os.path.isdir( args.root ):
        print( 'Error: %s is not a directory.' % args.root )
        exit( 1 )

    if not os.path.isdir( args.config_dir ):
        print( 'Error: %s is not a directory.' % args.config_dir )
        exit( 1 )

    Globals.app = App.App( args )
    Globals.app.run()

if __name__ == '__main__':
    main()
