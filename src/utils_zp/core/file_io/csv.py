from ._utils_file_io import *


def csv_load(filepath, encoding='utf-8'):
    filepath = load_dump_prepocess(
        filepath=filepath,
        is_load=True,
        valid_suffixes=['.csv'],
    )
    
    df = pd.read_csv(filepath)
    return df


def csv_dump(obj:pd.DataFrame, filepath, encoding='utf-8'):
    filepath = load_dump_prepocess(
        filepath=filepath,
        is_load=False,
        valid_suffixes=['.csv'],
    )
    
    obj.to_csv(filepath, index=False)

