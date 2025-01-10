import sys
from lilbinboy.lbb_common import make_unique_name

print(make_unique_name(sys.argv[1], ["me", "me.01", "you", "us.1", "us01", "us.02"], default_index_padding=5))