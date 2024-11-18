from pathlib import Path as path


target_dirpath = path(__file__).parent
# target_dirpath = path('')
for i in range(1,7):
    with open(target_dirpath/ f'~test{i}.py','w')as f:
        f.write('')
