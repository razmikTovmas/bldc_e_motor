import os


blender_path = 'path_to_blender'
gen_stator_script_path = 'gen_stator.py'
cmd = f'{blender_path} --background  --python {gen_stator_script_path}'


def main():
    os.system(cmd)


if __name__ == '__main__':
    main()
