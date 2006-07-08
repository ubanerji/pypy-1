from pypy.rpython.extregistry import ExtRegistryEntry
from pypy.annotation import model as annmodel
from pypy.rpython.ootypesystem import ootype

class Entry_oostring(ExtRegistryEntry):
    _about_ = ootype.oostring

    def compute_result_annotation(self, obj_s, base_s):
        assert isinstance(obj_s, (annmodel.SomeInteger,
                                  annmodel.SomeChar,
                                  annmodel.SomeFloat,
                                  annmodel.SomeOOInstance,
                                  annmodel.SomeString))
        assert isinstance(base_s, annmodel.SomeInteger)
        return annmodel.SomeOOInstance(ootype.String)

    def specialize_call(self, hop):
        assert isinstance(hop.args_s[0],(annmodel.SomeInteger,
                                         annmodel.SomeChar,
                                         annmodel.SomeString,
                                         annmodel.SomeFloat,
                                         annmodel.SomeOOInstance,
                                         annmodel.SomeString))
        assert isinstance(hop.args_s[1], annmodel.SomeInteger)
        return hop.genop('oostring', hop.args_v, resulttype = ootype.String)


class Entry_ootype_string(ExtRegistryEntry):
    _type_ = ootype._string

    def compute_annotation(self):
        return annmodel.SomeOOInstance(ootype=ootype.String)


class Entry_ooparse_int(ExtRegistryEntry):
    _about_ = ootype.ooparse_int

    def compute_result_annotation(self, str_s, base_s):
        assert isinstance(str_s, annmodel.SomeOOInstance)\
               and str_s.ootype is ootype.String
        assert isinstance(base_s, annmodel.SomeInteger)
        return annmodel.SomeInteger()

    def specialize_call(self, hop):
        assert isinstance(hop.args_s[0], annmodel.SomeOOInstance)\
               and hop.args_s[0].ootype is ootype.String
        assert isinstance(hop.args_s[1], annmodel.SomeInteger)
        hop.has_implicit_exception(ValueError)
        hop.exception_is_here()
        return hop.genop('ooparse_int', hop.args_v, resulttype = ootype.Signed)

class Entry_oohash(ExtRegistryEntry):
    _about_ = ootype.oohash

    def compute_result_annotation(self, str_s):
        assert isinstance(str_s, annmodel.SomeOOInstance)\
               and str_s.ootype is ootype.String
        return annmodel.SomeInteger()

    def specialize_call(self, hop):
        assert isinstance(hop.args_s[0], annmodel.SomeOOInstance)\
               and hop.args_s[0].ootype is ootype.String
        return hop.genop('oohash', hop.args_v, resulttype=ootype.Signed)
