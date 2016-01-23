__version__ = '0.4.1-alpha'
__all__ = ['Schema', 'And', 'Or', 'Optional', 'SchemaError', 'JSONSchema']


class SchemaError(Exception):

    """Error during Schema validation."""

    def __init__(self, autos, errors):
        self.autos = autos if type(autos) is list else [autos]
        self.errors = errors if type(errors) is list else [errors]
        Exception.__init__(self, self.code)

    @property
    def code(self):
        def uniq(seq):
            seen = set()
            seen_add = seen.add
            # This way removes duplicates while preserving the order.
            return [x for x in seq if x not in seen and not seen_add(x)]
        a = uniq(i for i in self.autos if i is not None)
        e = uniq(i for i in self.errors if i is not None)
        if e:
            return '\n'.join(e)
        return '\n'.join(a)


class And(object):

    def __init__(self, *args, **kw):
        self._args = args
        assert list(kw) in (['error'], [])
        self._error = kw.get('error')

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__,
                           ', '.join(repr(a) for a in self._args))

    def validate(self, data):
        for s in [Schema(s, error=self._error) for s in self._args]:
            data = s.validate(data)
        return data


class Or(And):

    def validate(self, data):
        x = SchemaError([], [])
        for s in [Schema(s, error=self._error) for s in self._args]:
            try:
                return s.validate(data)
            except SchemaError as _x:
                x = _x
        raise SchemaError(['%r did not validate %r' % (self, data)] + x.autos,
                          [self._error] + x.errors)


class Use(object):

    def __init__(self, callable_, error=None):
        assert callable(callable_)
        self._callable = callable_
        self._error = error

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self._callable)

    def validate(self, data):
        try:
            return self._callable(data)
        except SchemaError as x:
            raise SchemaError([None] + x.autos, [self._error] + x.errors)
        except BaseException as x:
            f = _callable_str(self._callable)
            raise SchemaError('%s(%r) raised %r' % (f, data, x), self._error)


COMPARABLE, CALLABLE, VALIDATOR, TYPE, DICT, ITERABLE = range(6)


def _priority(s):
    """Return priority for a given object."""
    if type(s) in (list, tuple, set, frozenset):
        return ITERABLE
    if type(s) is dict:
        return DICT
    if issubclass(type(s), type):
        return TYPE
    if hasattr(s, 'validate'):
        return VALIDATOR
    if callable(s):
        return CALLABLE
    else:
        return COMPARABLE


class Schema(object):

    def __init__(self, schema, error=None):
        self._schema = schema
        self._error = error

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self._schema)

    @staticmethod
    def _dict_key_priority(s):
        """Return priority for a given key object."""
        if isinstance(s, Optional):
            return _priority(s._schema) + 0.5
        return _priority(s)

    def validate(self, data):
        s = self._schema
        e = self._error
        flavor = _priority(s)
        if flavor == ITERABLE:
            data = Schema(type(s), error=e).validate(data)
            o = Or(*s, error=e)
            return type(data)(o.validate(d) for d in data)
        if flavor == DICT:
            data = Schema(dict, error=e).validate(data)
            new = type(data)()  # new - is a dict of the validated values
            coverage = set()  # matched schema keys
            # for each key and value find a schema entry matching them, if any
            sorted_skeys = sorted(s, key=self._dict_key_priority)
            for key, value in data.items():
                for skey in sorted_skeys:
                    svalue = s[skey]
                    try:
                        nkey = Schema(skey, error=e).validate(key)
                    except SchemaError:
                        pass
                    else:
                        nvalue = Schema(svalue, error=e).validate(value)
                        new[nkey] = nvalue
                        coverage.add(skey)
                        break
            required = set(k for k in s if type(k) is not Optional)
            if not required.issubset(coverage):
                missing_keys = required - coverage
                s_missing_keys = ", ".join(repr(k) for k in missing_keys)
                raise SchemaError('Missing keys: ' + s_missing_keys, e)
            if len(new) != len(data):
                wrong_keys = set(data.keys()) - set(new.keys())
                s_wrong_keys = ', '.join(repr(k) for k in sorted(wrong_keys,
                                                                 key=repr))
                raise SchemaError('Wrong keys %s in %r' % (s_wrong_keys, data),
                                  e)

            # Apply default-having optionals that haven't been used:
            defaults = set(k for k in s if type(k) is Optional and
                           hasattr(k, 'default')) - coverage
            for default in defaults:
                new[default.key] = default.default

            return new
        if flavor == TYPE:
            if isinstance(data, s):
                return data
            else:
                raise SchemaError('%r should be instance of %r' %
                                  (data, s.__name__), e)
        if flavor == VALIDATOR:
            try:
                return s.validate(data)
            except SchemaError as x:
                raise SchemaError([None] + x.autos, [e] + x.errors)
            except BaseException as x:
                raise SchemaError('%r.validate(%r) raised %r' % (s, data, x),
                                  self._error)
        if flavor == CALLABLE:
            f = _callable_str(s)
            try:
                if s(data):
                    return data
            except SchemaError as x:
                raise SchemaError([None] + x.autos, [e] + x.errors)
            except BaseException as x:
                raise SchemaError('%s(%r) raised %r' % (f, data, x),
                                  self._error)
            raise SchemaError('%s(%r) should evaluate to True' % (f, data), e)
        if s == data:
            return data
        else:
            raise SchemaError('%r does not match %r' % (s, data), e)


class Optional(Schema):

    """Marker for an optional part of Schema."""

    _MARKER = object()

    def __init__(self, *args, **kwargs):
        default = kwargs.pop('default', self._MARKER)
        super(Optional, self).__init__(*args, **kwargs)
        if default is not self._MARKER:
            # See if I can come up with a static key to use for myself:
            if _priority(self._schema) != COMPARABLE:
                raise TypeError(
                    'Optional keys with defaults must have simple, '
                    'predictable values, like literal strings or ints. '
                    '"%r" is too complex.' % (self._schema,))
            self.default = default
            self.key = self._schema


def _callable_str(callable_):
    if hasattr(callable_, '__name__'):
        return callable_.__name__
    return str(callable_)


class JSONSchema(object):

    def __init__(self, schema, data, error=None):
        import copy
        self.schema = schema
        self._data = copy.deepcopy(data)    # origin data
        self.data = data    # validated data, only valid data included
        self.error = error  # custom error message for entire schema
        self.valid = True   # valid or not
        self.errors = {}    # errors with the same hierarchy against origin data

    def validate(self):
        """
        validate data against schema
        :return:
        """
        schema = self.schema
        data = self.data

        # validate if is a dict
        if isinstance(schema, dict) and isinstance(data, dict):
            new = dict()
            # validate data against each key-validator pair specified in schema
            for sk, sv in schema.iteritems():
                # process Optional schema
                if isinstance(sk, Optional):
                    sk = sk._schema
                    # escape not filled keys
                    if sk not in data:
                        continue
                    # escape any other Optional object
                    if sk in (basestring, unicode, str):
                        continue
                dv = data.get(sk)
                js = JSONSchema(sv, dv).validate()
                if sk in data:
                    self.errors[sk] = js.errors
                else:
                    self.errors[sk] = "Missing key: {0}".format(sk)
                self.valid = self.valid and js.valid
                if js.valid:
                    new[sk] = js.data
            self.data = new
            return self

        # validate if is a list
        if isinstance(schema, list) and isinstance(data, list):
            js_list = []
            for ss in schema:
                for dv in data:
                    js = JSONSchema(ss, dv).validate()
                    js_list.append(js)
            self.errors = [js.errors for js in js_list]
            self.valid = all([js.valid for js in js_list])
            self.data = [js.data for js in js_list if js.valid]
            return self

        else:
            try:
                new = Schema(schema).validate(data)
                self.data = new
                self.errors = None
            except SchemaError as e:
                self.valid = False
                self.errors = e.message
                self.data = None
            return self
