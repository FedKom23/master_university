#include <Python.h>
#include <string.h>
#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>

void skip_ws(const char *s, int *i) {
    while (isspace((unsigned char)s[*i])) {
        (*i)++;
    }
}

static PyObject *parse_string_slice(const char *s, int start, int end) {
    if (end - start < 2 || s[start] != '"' || s[end - 1] != '"') {
        PyErr_SetString(PyExc_ValueError, "expected string");
        return NULL;
    }

    return PyUnicode_FromStringAndSize(
        s + start + 1,
        (end - start) - 2
    );
}

static PyObject *parse_int_slice(const char *s, int start, int end) {
    char buf[64];
    char *eptr;
    long val;
    int len = end - start;

    if (len <= 0 || len >= (int)sizeof(buf)) {
        PyErr_SetString(PyExc_ValueError, "invalid integer");
        return NULL;
    }

    memcpy(buf, s + start, len);
    buf[len] = '\0';

    val = strtol(buf, &eptr, 10);
    if (*eptr != '\0') {
        PyErr_SetString(PyExc_ValueError, "invalid integer");
        return NULL;
    }

    return PyLong_FromLong(val);
}

PyObject *loads(PyObject *self, PyObject *args) {
    PyObject *input;
    const char *s;
    PyObject *dict;
    PyObject *key = NULL, *value = NULL;

    if (!PyArg_ParseTuple(args, "U", &input))
        return NULL;

    s = PyUnicode_AsUTF8(input);
    if (!s)
        return NULL;

    dict = PyDict_New();
    if (!dict)
        return NULL;

    int i = 0;
    int left = 0;
    int key_count = 0, value_count = 0;

    skip_ws(s, &i);

    if (s[i] != '{') {
        PyErr_SetString(PyExc_ValueError, "Expected '{'");
        Py_DECREF(dict);
        return NULL;
    }
    i++;
    skip_ws(s, &i);
    if (s[i] == '}') {
        i++;
        skip_ws(s, &i);
        if (s[i] != '\0') {
            PyErr_SetString(PyExc_ValueError, "Trailing garbage");
            Py_DECREF(dict);
            return NULL;
        }
        return dict;
    }

    left = i;

    while (s[i] != '\0') {
        skip_ws(s, &i);

        if (s[i] == ':') {
            Py_XDECREF(key);
            
            int key_start = left;
            int key_end = i;
            

            while (key_end > key_start && isspace((unsigned char)s[key_end - 1])) {
                key_end--;
            }
            
            key = parse_string_slice(s, key_start, key_end);
            if (!key) {
                Py_XDECREF(value);
                Py_DECREF(dict);
                return NULL;
            }

            i++;
            skip_ws(s, &i);
            left = i;
            key_count++;
        }
        else if (s[i] == ',' || s[i] == '}') {
            Py_XDECREF(value);
            value = NULL;

            int value_start = left;
            int value_end = i;
            

            while (value_end > value_start && isspace((unsigned char)s[value_end - 1])) {
                value_end--;
            }
            
            if (value_start >= value_end) {
                PyErr_SetString(PyExc_ValueError, "empty value");
                Py_XDECREF(key);
                Py_DECREF(dict);
                return NULL;
            }

            if (s[value_start] == '"') {
                value = parse_string_slice(s, value_start, value_end);
            }
            else if (s[value_start] == '-' || isdigit((unsigned char)s[value_start])) {
                value = parse_int_slice(s, value_start, value_end);
            }
            else {
                PyErr_SetString(PyExc_ValueError, "expected string or number");
                Py_XDECREF(key);
                Py_XDECREF(value);
                Py_DECREF(dict);
                return NULL;
            }

            if (!value) {
                Py_XDECREF(key);
                Py_DECREF(dict);
                return NULL;
            }

            value_count++;

            if (key_count != value_count) {
                PyErr_SetString(PyExc_ValueError, "key!=value ");
                Py_XDECREF(key);
                Py_XDECREF(value);
                Py_DECREF(dict);
                return NULL;
            }

            if (PyDict_SetItem(dict, key, value) < 0) {
                Py_XDECREF(key);
                Py_XDECREF(value);
                Py_DECREF(dict);
                return NULL;
            }

            Py_DECREF(key);
            Py_DECREF(value);
            key = value = NULL;

            if (s[i] == '}') {
                i++;
                skip_ws(s, &i);
                if (s[i] != '\0') {
                    PyErr_SetString(PyExc_ValueError, "trailing garbage");
                    Py_DECREF(dict);
                    return NULL;
                }
                return dict;
            }

            i++;
            skip_ws(s, &i);
            left = i;
        }
        else {
            i++;
        }
    }

    if (key_count != value_count) {
        PyErr_SetString(PyExc_ValueError, "key/value mismatch");
        Py_XDECREF(key);
        Py_XDECREF(value);
        Py_DECREF(dict);
        return NULL;
    }

    PyErr_SetString(PyExc_ValueError, "unterminated object");
    Py_XDECREF(key);
    Py_XDECREF(value);
    Py_DECREF(dict);
    return NULL;
}

PyObject *dumps(PyObject *self, PyObject *args) {
    PyObject *dict;
    PyObject *key, *value;
    Py_ssize_t pos = 0;
    int first = 1;
    PyObject *result = NULL;
    PyObject *temp = NULL;

    if (!PyArg_ParseTuple(args, "O!", &PyDict_Type, &dict))
        return NULL;

    result = PyUnicode_FromString("{");
    if (!result)
        return NULL;

    while (PyDict_Next(dict, &pos, &key, &value)) {
        if (!PyUnicode_Check(key)) {
            PyErr_SetString(PyExc_ValueError, "keys  strings");
            Py_DECREF(result);
            return NULL;
        }

        if (!first) {
            temp = PyUnicode_FromFormat("%U, ", result);
            Py_DECREF(result);
            result = temp;
            if (!result)
                return NULL;
        }
        first = 0;

        temp = PyUnicode_FromFormat("%U\"%U\": ", result, key);
        Py_DECREF(result);
        result = temp;
        if (!result)
            return NULL;

        if (PyUnicode_Check(value)) {
            temp = PyUnicode_FromFormat("%U\"%U\"", result, value);
            Py_DECREF(result);
            result = temp;
            if (!result)
                return NULL;
        }
        else if (PyLong_Check(value)) {
            temp = PyUnicode_FromFormat("%U%S", result, value);
            Py_DECREF(result);
            result = temp;
            if (!result)
                return NULL;
        }
        else {
            PyErr_SetString(PyExc_ValueError, "values strings or int");
            Py_DECREF(result);
            return NULL;
        }
    }

    temp = PyUnicode_FromFormat("%U}", result);
    Py_DECREF(result);
    return temp;
}


static PyMethodDef custom_json_methods[] = {
    {"loads", loads, METH_VARARGS, "Parse JSON string"},
    {"dumps", dumps, METH_VARARGS, "Serialize to JSON string"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef custom_json_module = {
    PyModuleDef_HEAD_INIT,
    "custom_json",
    "Custom JSON parser module",
    -1,
    custom_json_methods
};

PyMODINIT_FUNC PyInit_custom_json(void) {
    return PyModule_Create(&custom_json_module);
}