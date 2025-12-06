from utils_zp import *

rdb_dir = path(__file__).parent/'~test_rdb'

rdb = FileDict(rdb_dir,)
rdb.clear()
for i in tqdm.tqdm(range(5000)):
    d = random.randint(0,20)
    if random.random() < 0.6:
        rdb[d] = d
    else:
        val = rdb[d]
        assert val == d or val is None
print(sorted(rdb,key=lambda x:int(x[0])))
    
shutil.rmtree(rdb_dir)
