import argparse
import subprocess

import dfhack.ci.util.git as git
from dfhack.ci.util.github_parse import PullRequestRef

def make_parser():
    def _parse_pull_request(arg):
        # wrapper to produce better error messages
        try:
            return PullRequestRef.from_string(arg)
        except ValueError as e:
            raise argparse.ArgumentTypeError(str(e)) from e

    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--url', required=True,
        help='URL of the repository to clone')
    parser.add_argument('-d', '--destination', required=True,
        help='Directory to clone into (must be empty or nonexistent)')
    parser.add_argument('-a', '--full-depth', action='store_true',
        help='Include entire history (default is a shallow clone)')
    parser.add_argument('--pull-request', type=_parse_pull_request,
        help='Update submodules based on the specified pull request')
    return parser

def main():
    args = make_parser().parse_args()
    try:
        git.clone(url=args.url, destination=args.destination, shallow=not args.full_depth)
    except subprocess.CalledProcessError as e:
        print('ERROR: %s' % e)
        exit(1)

if __name__ == '__main__':
    main()
