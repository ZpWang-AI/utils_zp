from pathlib import Path as path


def get_info_from_script_file(file, id_sep='-', desc_sep='_'):
    file_name = path(file).stem
    return {
        'id': file_name.split(id_sep)[0],
        'desc': file_name.split(desc_sep)[-1],
    }    
    

if __name__ == '__main__':
    print(get_info_from_script_file('001-test_script_testabc'))