from pathlib import Path as path

for i in range(1,7):
    with open(path(__file__).parent/ f'~test{i}.py','w')as f:
        f.write('')