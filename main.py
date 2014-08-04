import sys
import os
import argparse
import imp
import subprocess

import scadgen

def launch_openscad(output_path):
    if output_path is None:
        raise ValueError('Cannot launch openscad without output file.')
    
    subprocess.Popen(['openscad', output_path])

def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('input_script', help='Input Python script with model.')
    parser.add_argument('-f', '--output-format', default='openscad', help='Output format.')
    parser.add_argument('-o', '--output-file', type=argparse.FileType('w'), help='Write OpenSCAD output to this file.')
    parser.add_argument('-s', '--openscad', action='store_true', help='Open output in OpenSCAD GUI.')
    args = parser.parse_args()
    
    script = imp.load_source('the_script', args.input_script)
    
    model = script.model()
    
    scad_src = scadgen.build_output(model, args.output_format)
    
    output_path = None
    
    if args.output_file is not None:
        output = args.output_file
        output_path = os.path.abspath(output.name)
        output.write(scad_src)
        output.close()
    else:
        sys.stdout.write(scad_src)
    
    if args.openscad:
        launch_openscad(output_path)
    
if __name__ == '__main__':
    main()
