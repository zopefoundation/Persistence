/*

 Copyright (c) 2003 Zope Foundation and Contributors.
 All Rights Reserved.

 This software is subject to the provisions of the Zope Public License,
 Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
 THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
 WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
 FOR A PARTICULAR PURPOSE.

*/
static char _Persistence_module_documentation[] =
"Persistent ExtensionClass\n"
;

#include "ExtensionClass/ExtensionClass.h"
#include "ExtensionClass/_compat.h"
#include "persistent/cPersistence.h"


/* convert_name() returns a new reference to a string name
   or sets an exception and returns NULL.
*/

static PyObject *
convert_name(PyObject *name)
{
#ifdef Py_USING_UNICODE
    /* The Unicode to string conversion is done here because the
       existing tp_setattro slots expect a string object as name
       and we wouldn't want to break those. */
    if (PyUnicode_Check(name)) {
		name = PyUnicode_AsEncodedString(name, NULL, NULL);
    }
    else
#endif
    if (!NATIVE_CHECK(name)) {
		PyErr_SetString(PyExc_TypeError, "attribute name must be a string");
	return NULL;
    } else
		Py_INCREF(name);
    return name;
}

/* Returns true if the object requires unghostification.

   There are several special attributes that we allow access to without
   requiring that the object be unghostified:
   __class__
   __del__
   __dict__
   __of__
   __setstate__
*/

static int
unghost_getattr(const char *s)
{
    if (*s++ != '_')
	return 1;
    if (*s == 'p') {
	s++;
	if (*s == '_')
	    return 0; /* _p_ */
	else
	    return 1;
    }
    else if (*s == '_') {
	s++;
	switch (*s) {
	case 'c':
	    return strcmp(s, "class__");
	case 'd':
	    s++;
	    if (!strcmp(s, "el__"))
		return 0; /* __del__ */
	    if (!strcmp(s, "ict__"))
		return 0; /* __dict__ */
	    return 1;
	case 'o':
	    return strcmp(s, "of__");
	case 's':
	    return strcmp(s, "setstate__");
	default:
	    return 1;
	}
    }
    return 1;
}

static PyObject *
P_getattr(cPersistentObject *self, PyObject *name)
{
  PyObject *v=NULL;

  char *s;

  PyObject* as_bytes = convert_name(name);
  if (!as_bytes)
    return NULL;

  s = PyBytes_AS_STRING(as_bytes);

  if (s[0] != '_' || unghost_getattr(s))
    {
      if (PER_USE(self))
        {
          v = Py_FindAttr((PyObject*)self, name);
          PER_ALLOW_DEACTIVATION(self);
          PER_ACCESSED(self);
        }
    }
  else
    v = Py_FindAttr((PyObject*)self, name);

  Py_DECREF(as_bytes);

  return v;
}


/*
 *  Module state
 */

typedef struct {
    PyObject *MetaClass;
    PyTypeObject *Persistent;
} _Persistence_module_state;

static int
_Persistence_module_traverse(PyObject *module, visitproc visit, void *arg)
{
    _Persistence_module_state* state = PyModule_GetState(module);
    if (state == NULL)
        return -1;
    Py_VISIT(state->MetaClass);
    Py_VISIT(state->Persistent);
    return 0;
}

static int
_Persistence_module_clear(PyObject *module)
{
    _Persistence_module_state* state = PyModule_GetState(module);
    if (state == NULL)
        return -1;
    Py_CLEAR(state->Persistent);
    Py_CLEAR(state->MetaClass);
    return 0;
}


/*
 *  ExtensionClass's attribute-set discipline for our heap types.
 *
 *  The historical static 'Persistence.Persistent' barred dunder
 *  attribute names (like '__foo__') on the class object, through the
 *  static branch of ExtensionClass's 'EC_setattro'.  Heap types are
 *  routed to that function's permissive heap branch instead, so the
 *  metaclass created in '_Persistence_module_exec' applies this guard,
 *  replacing the static-check behavior.
 */

static int
MetaClass_setattro(PyObject *cls, PyObject *name, PyObject *value)
{
    PyObject *as_bytes = convert_name(name);
    if (as_bytes == NULL) {
        return -1;
    }
    {
        const char *cname = PyBytes_AS_STRING(as_bytes);
        Py_ssize_t len = PyBytes_GET_SIZE(as_bytes);

        if (len >= 4
            && cname[0] == '_' && cname[1] == '_'
            && cname[len - 1] == '_' && cname[len - 2] == '_')
        {
            const char *underscore = strchr(cname + 2, '_');
            if (underscore != NULL && (underscore - cname) >= (len - 2)) {
                Py_DECREF(as_bytes);
                PyErr_Format(PyExc_TypeError,
                             "can't set attributes of built-in/extension "
                             "type '%s' if the attribute name begins and "
                             "ends with __ and contains only 4 _ characters",
                             ((PyTypeObject *)cls)->tp_name);
                return -1;
            }
        }
    }
    Py_DECREF(as_bytes);

    /* Same delegation ExtensionClass's 'EC_setattro' makes for heap
       types.
    */
    if (PyType_Type.tp_setattro(cls, name, value) < 0) {
        return -1;
    }
    PyType_Modified((PyTypeObject *)cls);
    return 0;
}


/*
 *  Module initialization
 */

static int
_Persistence_module_exec(PyObject *module)
{
    PyObject *name = NULL, *modname = NULL, *doc = NULL, *bases = NULL;
    PyObject *slots = NULL, *dict = NULL, *args = NULL;
    PyObject *metaname = NULL, *metabases = NULL, *metadict = NULL;
    PyObject *metaargs = NULL, *meta = NULL;
    PyObject *klass, *getattr_descr = NULL;
    _Persistence_module_state* state;

    /* Match the static definition's method signature:  METH_O, so
       that 'PyDescr_NewMethod' below produces a descriptor calling it
       as (self, name).
    */
    static PyMethodDef P_getattr_methoddef = {
        "__getattribute__", (PyCFunction)P_getattr, METH_O,
        "Ghost-aware attribute fetch, defined for Persistence.Persistent.",
    };

    if (!ExtensionClassImported)
        return -1;  /* capsule import has already set the exception */

    /* The PER_* macros used in this TU read the CAPI struct through
       this static, so it must be populated before any instance-level
       work happens.  As with the persistent modules, it is refreshed
       on each module exec.
    */
    cPersistenceCAPI = (cPersistenceCAPIstruct *)PyCapsule_Import(
                            "persistent.cPersistence.CAPI", 0);
    if (cPersistenceCAPI == NULL)
        return -1;

    state = (_Persistence_module_state*)PyModule_GetState(module);
    if (state == NULL)
        return -1;

    modname = PyUnicode_FromString("Persistence");
    if (modname == NULL)
        goto error;

    /* The metaclass:  an ExtensionClass metaclass subclass.  Its
       instances are the classes created below (and, through normal
       metaclass resolution, every Python class deriving from them);
       the overridden 'tp_setattro' restores ExtensionClass's
       class-attribute discipline for heap types (see
       'MetaClass_setattro').
    */
    metaname = PyUnicode_FromString("MetaClass");
    if (metaname == NULL)
        goto error;

    metabases = Py_BuildValue("(O)", ECExtensionClassType);
    if (metabases == NULL)
        goto error;

    metadict = PyDict_New();
    if (metadict == NULL
        || PyDict_SetItemString(metadict, "__module__", modname) < 0)
        goto error;

    metaargs = PyTuple_Pack(3, metaname, metabases, metadict);
    if (metaargs == NULL)
        goto error;

    meta = PyObject_CallObject((PyObject *)ECExtensionClassType, metaargs);
    if (meta == NULL)
        goto error;

    ((PyTypeObject *)meta)->tp_setattro = MetaClass_setattro;
    PyType_Modified((PyTypeObject *)meta);

    state->MetaClass = meta;

    if (PyModule_AddObjectRef(module, "MetaClass", meta) < 0)
        goto error;

    /* Create the type through the same path the 'class' statement uses:
       invoke the metaclass with (name, bases, dict), letting EC_new /
       EC_init run.  The result is a heap type, with the metaclass just
       created as its metaclass, the (heap-allocated)
       persistent.Persistent as its tp_base, and ECBaseType carried in
       tp_bases for the MRO.  ExtensionClass.Base is shaped like
       'object', so persistent.Persistent wins as the strongest base,
       matching the tp_base pinned by the previous static definition.
    */
    name = PyUnicode_FromString("Persistent");
    if (name == NULL)
        goto error;

    bases = Py_BuildValue("(OO)", cPersistenceCAPI->pertype, ECBaseType);
    if (bases == NULL)
        goto error;

    doc = PyUnicode_FromString("Persistent ExtensionClass");
    if (doc == NULL)
        goto error;

    /* Declaring '__slots__: ()' keeps 'type_new' from adding an
       instance dict / weakref to the type itself, matching the layout
       of the static definition:  without it, the empty-dict base would
       gain a managed instance dict, which class-level '__slots__'
       users would inherit (breaking 'x.__dict__' and '__getstate__'
       behavior).  Subclasses without '__slots__' still get their own
       instance dict, exactly as with the static type.
    */
    slots = PyTuple_New(0);
    if (slots == NULL)
        goto error;

    dict = PyDict_New();
    if (dict == NULL
        || PyDict_SetItemString(dict, "__module__", modname) < 0
        || PyDict_SetItemString(dict, "__doc__", doc) < 0
        || PyDict_SetItemString(dict, "__slots__", slots) < 0)
        goto error;

    args = PyTuple_Pack(3, name, bases, dict);
    if (args == NULL)
        goto error;

    klass = PyObject_CallObject(state->MetaClass, args);
    if (klass == NULL)
        goto error;

    state->Persistent = (PyTypeObject *)klass;

    /* Same slot as the static definition carried:  ghost-aware
       attribute access.  The class dict defines no
       __getattr__ / __getattribute__, so no slot wrappers intervene.
    */
    state->Persistent->tp_getattro = (getattrofunc)P_getattr;

    /* Same tp_new as the static definition inherited (via
       'persistent.Persistent') before persistent heap-allocated its
       own type:  instances ignore constructor arguments, and the
       'cls.__new__(cls)' calls made by '__basicnew__' / pickling's
       '__newobj__' resolve to 'ExtensionClass.Base.__new__', which
       uses the same function, satisfying CPython's tp_new-wrapper
       safety check.
    */
    state->Persistent->tp_new = PyType_GenericNew;

    /* Bind P_getattr into the type dict as '__getattribute__', so that
       the slot-fixup machinery resolves our function (rather than the
       wrapper descriptor inherited from 'persistent.Persistent',
       which wraps 'Per_getattro') for this type and every subclass.
    */
    getattr_descr = PyDescr_NewMethod(state->Persistent, &P_getattr_methoddef);
    if (getattr_descr == NULL)
        goto error;

    /* Written directly into the type dict (the metaclass guard would
       refuse a dunder attribute write).  Subclasses resolve this entry
       at their own creation, restoring 'P_getattr' for the whole
       subtree.
    */
    if (PyDict_SetItemString(((PyTypeObject *)klass)->tp_dict,
                             "__getattribute__", getattr_descr) < 0)
        goto error;

    PyType_Modified((PyTypeObject *)klass);
    Py_CLEAR(getattr_descr);

    if (PyModule_AddObjectRef(module, "Persistent", klass) < 0)
        goto error;

    Py_DECREF(args);
    Py_DECREF(dict);
    Py_DECREF(doc);
    Py_DECREF(modname);
    Py_DECREF(bases);
    Py_DECREF(slots);
    Py_DECREF(name);

    return 0;

  error:
    Py_CLEAR(getattr_descr);
    Py_CLEAR(state->Persistent);
    Py_CLEAR(state->MetaClass);
    Py_XDECREF(metaargs);
    Py_XDECREF(metadict);
    Py_XDECREF(metabases);
    Py_XDECREF(metaname);
    Py_XDECREF(args);
    Py_XDECREF(dict);
    Py_XDECREF(doc);
    Py_XDECREF(slots);
    Py_XDECREF(modname);
    Py_XDECREF(bases);
    Py_XDECREF(name);
    return -1;
}

/* Slot definitions for multi-phase initialization
 *
 * See: https://docs.python.org/3/c-api/module.html#multi-phase-initialization
 * and: https://peps.python.org/pep-0489
 */
static PyModuleDef_Slot _Persistence_module_slots[] = {
    {Py_mod_exec,       _Persistence_module_exec},
    {0,                 NULL}
};

static struct PyModuleDef moduledef =
{
    PyModuleDef_HEAD_INIT,
    .m_name         = "_Persistence",                    /* m_name */
    .m_doc          = _Persistence_module_documentation, /* m_doc */
    .m_size         = sizeof(_Persistence_module_state),
    .m_methods      = NULL,
    .m_traverse     = _Persistence_module_traverse,
    .m_clear        = _Persistence_module_clear,
    .m_slots        = _Persistence_module_slots,
};

static PyObject*
_Persistence_module_init(void)
{
    return PyModuleDef_Init(&moduledef);
}

PyMODINIT_FUNC
PyInit__Persistence(void)
{
    return _Persistence_module_init();
}
