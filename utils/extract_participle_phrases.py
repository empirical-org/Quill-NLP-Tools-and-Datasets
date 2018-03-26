"""Extract participle phrases from a text file or directory of text files"""
import argparse
import logging


def _extract_from_file(inputfile, outputfile=None):
    pass

def _extract_from_directory(inputdir, outputdir='qfragment'):
    pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extract participle phrases '
            'from arbitrary text.')
    parser.add_argument('-i', '--inputfile', help='Extract participle phrases '
            'from here.')
    parser.add_argument('-I', '--inputdir', help='Extract participle phrases '
            'from files in this input directory.')
    parser.add_argument('-o', '--outputfile', help='write output to this file')
    parser.add_argument('-O', '--outputdir', help='write output to this '
            'directory.')
    args = parser.parse_args()



    if args.inputdir and args.outputdir:
        _extract_from_directory(args.inputdir, args.outputdir)
    elif args.inputdir:
        _extract_from_directory(args.inputdir) 
    elif args.inputfile and args.outputfile:
        _extract_from_file(args.inputfile, args.outputfile)
    elif args.inputfile:
        _extract_from_file(args.inputfile)

    # Generate ignore messages
    if args.inputdir and (args.inputfile or args.outputfile):
        logging.warning('inputfile and outputfile unused when directory is '
                'specified.')
    if args.outputdir and not args.inputdir:
        logging.warning('inputdir required with outputdir.')
    
    if args.outputfile and not args.inputfile:
        logging.warning('inputfile required with outputfile.')
