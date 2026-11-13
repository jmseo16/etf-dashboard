import json, sys
import vb_units
views = [f() for f in vb_units.UNIT_VIEWS]
try:
    import vb_blocks
    views = [f() for f in vb_blocks.BLOCK_VIEWS] + views + [f() for f in getattr(vb_blocks, 'EXTRA_UNIT_VIEWS', [])]
except ImportError as e:
    print('no block views yet', e)
json.dump(views, open('views.json', 'w'), indent=0)
print(len(views), 'views')
