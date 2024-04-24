import os


blender_path = '/Applications/Blender.app/Contents/MacOS/Blender'
gen_stator_script_path = 'gen_stator.py'
gen_rotor_script_path = 'gen_rotor.py'
stator_cmd = f'{blender_path} --background --python {gen_stator_script_path}'
rotor_cmd = f'{blender_path} --background --python {gen_rotor_script_path}'


def main():
    print('Generating Stator')
    os.system(stator_cmd)
    print('Generating Rotor')
    os.system(rotor_cmd)


if __name__ == '__main__':
    main()
