
class Foo():
    def __init__(self):
        self.string = "Ferry"
        self.list = ["a", "b", True, False]
        self.reference_to_type = list
        self.reference_to_class = Foo
        self.none = None
        self.reference_to_self = None

foo = Foo()
foo.reference_to_self = foo

my_data = {
    'a_list': [
        {
            'pos': 0
        },
        {
            'pos': 1
        }
    ],
    'a_dict': {
        'pos': 1,
        'a': 'a string',
        'b': 'b string',
    },
    "a_set": set(["a", "b", "c"]),
    "other_types": {
        'unicode string': u'a unicode string',
        'byte string': b'byte string',
        'boolean': True,
        "object instance": foo,
    }
}

import davis
davis.vis(my_data)
davis.vis(locals())
