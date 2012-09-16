// Copyright (C) 2008  Murphy Lab
// Carnegie Mellon University
// 
// Written by Luís Pedro Coelho <lpc@cmu.edu>
//
// This program is free software; you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published
// by the Free Software Foundation; either version 3 of the License,
// or (at your option) any later version.
//
// This program is distributed in the hope that it will be useful, but
// WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
// General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program; if not, write to the Free Software
// Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
// 02110-1301, USA.
//
// For additional information visit http://murphylab.web.cmu.edu or
// send email to murphy@cmu.edu


#include <string>
#include <exception>
#include <stdexcept>
#include <Magick++.h>
#include <iostream>

extern "C" {
    #include <Python.h>
    #include <numpy/ndarrayobject.h>
}

using namespace Magick;
namespace {

struct holdref {
    holdref(PyObject* obj):obj(obj) { }
    holdref(PyArrayObject* obj):obj((PyObject*)obj) { }
    ~holdref() { Py_DECREF(obj); }
  
private:  
    PyObject* obj;
};

struct gil_release {
    gil_release() {
        _save = PyEval_SaveThread();
    }
    ~gil_release() {
        PyEval_RestoreThread(_save);
    }
    PyThreadState *_save;
};

PyObject* array_from_image(Magick::Image& img) {
    PyArrayObject* ret = 0;
    try {
        Geometry size = img.size();
        unsigned w = size.width();
        unsigned h = size.height();

        npy_intp dimensions[3];
        dimensions[0] = h;
        dimensions[1] = w;
        dimensions[2] = 3;

        bool colourimage = (img.type() != GrayscaleType);
        int type;
        StorageType pixeltype;
        if (QuantumDepth == 8 || img.depth() == 8 || img.depth() == 1) {
            type = PyArray_UBYTE;
            pixeltype = CharPixel;
        } else if (QuantumDepth == 16) {
            type = PyArray_USHORT;
            pixeltype = ShortPixel;
        } else {
            PyErr_SetString(PyExc_EOFError,"Magick++ issue: Quantum depth is neither 8 nor 16.\nDon't know how to handle that.");
            return 0;
        }
        ret = (PyArrayObject*)PyArray_SimpleNew(2+colourimage, dimensions, type);
        if (!ret) {
            PyErr_SetString(PyExc_MemoryError,"Out of Memory");
            return 0;
        }
        const char* write_format = (colourimage ? "RGB" : "I");
        img.write(0,0,w,h,write_format,pixeltype,ret->data);

        return PyArray_Return(ret);
    } catch ( std::exception& error_ ) {
        PyErr_SetString(PyExc_EOFError,error_.what());
        Py_DECREF(ret);
        return 0;
    }
}
PyObject* readimg(PyObject* self, PyObject* args) {
	PyObject* input;
	if (!PyArg_ParseTuple(args,"O",&input) || !PyString_Check(input) || PyString_Size(input) == 0) {
         PyErr_SetString(PyExc_TypeError,"readimg takes a filename as input");
         return 0;
    }
    try {
        std::string fname = PyString_AsString(input);
        Image img;
        try {
            gil_release nogil;
            img.read(fname);
        } catch ( WarningCoder &warning ) {
            // Issuing warnings turned the program too verbose
            //
            // int status = PyErr_WarnEx( 0, ( std::string("ImageMagick Warning: ") + warning.what() ).c_str(), 1 );
            // if (status < 0) return 0;
        }
        return array_from_image(img);
    } catch ( std::exception& error_ ) {
        PyErr_SetString(PyExc_EOFError,error_.what());
        return 0;
    }
}
PyObject* readimgfromblob(PyObject* self, PyObject* args) {
	PyObject* input;
	if (!PyArg_ParseTuple(args,"O",&input) || !PyString_Check(input) || PyString_Size(input) == 0) {
         PyErr_SetString(PyExc_TypeError,"readimgfromblob takes image data as input");
         return 0;
    }
    const char* inputstr = PyString_AsString(input);
    const unsigned long inputsize = PyString_Size(input);
    try {
        gil_release nogil;
        Image img;
        try {
            img.read(Blob(inputstr, inputsize));
        } catch ( WarningCoder &warning ) {
            // Issuing warnings turned the program too verbose
            //
            //int status = PyErr_WarnEx( 0, ( std::string("ImageMagick Warning: ") + warning.what() ).c_str(), 1 );
            //if (status < 0) return 0;
        }
        return array_from_image(img);
    } catch ( std::exception& error_ ) {
        PyErr_SetString(PyExc_EOFError,error_.what());
        return 0;
    }
}

PyObject* writeimg(PyObject* self, PyObject* args) {
	PyArrayObject* input;
	const char* output_filename;
	if (PyTuple_Size(args) != 2) {
         PyErr_Format(PyExc_TypeError,"writeimg takes two arguments (%d given)",(int)PyTuple_Size(args));
         return 0;
    }
	if (!PyArg_ParseTuple(args,"Os",&input,&output_filename)) {
         PyErr_SetString(PyExc_TypeError,"writeimg take two arguments: an array and a filename.");
         return 0;
    }
    try {
        if (!PyArray_Check(input)) {
            throw std::runtime_error("writeimg: Can only handle inputs of type numpy.ndarray.");
        }
        if (PyArray_NDIM(input) > 3 || PyArray_NDIM(input) < 2) {
            throw std::runtime_error("writeimg: Can only handle arrays of the form H x W  or H x W x 3.");
        }
        if (PyArray_NDIM(input) == 3 && PyArray_DIM(input,2) != 3) {
            throw std::runtime_error("writeimg: Can only handle arrays of the form H x W  or H x W x 3.");
        }
        input = PyArray_GETCONTIGUOUS(input);
        holdref input_ref_(input);
        {
            gil_release nogil_;
            const int height = PyArray_DIM(input,0);
            const int width = PyArray_DIM(input,1);
            const bool is_colour = (PyArray_NDIM(input) > 2);
            const char * const pixel_ordering = is_colour ? "RGB" : "I";
            StorageType storage_type;
            if (PyArray_TYPE(input) == PyArray_UBYTE) {
                storage_type = CharPixel;
            } else if (PyArray_TYPE(input) == PyArray_USHORT) {
                storage_type = ShortPixel;
            } else {
                throw std::runtime_error("writeimg: Cannot handle this type (only handles uint8 & uint16)");
            }
            Image img(width,height,pixel_ordering,storage_type,PyArray_DATA(input));
            img.write(output_filename);
        }
        Py_RETURN_NONE;
    } catch ( std::exception& error_ ) {
        PyErr_SetString(PyExc_ValueError,error_.what());
        return 0;
    }
}
        

const char * readimg_doc = 
    "img = readimg(fname)\n"
    "\n"
    "Read an image using Image Magick.\n"
    "\n"
    "The returned array is either a uint8, or a uint16 array, depending on the image type.\n"
    "\n"
    "If the image is reported to be a colour image, then a 3-dimensional array is returned. "
    "The last dimension encodes the red, green, and blue channels.\n"
    "\n"
    "@see readimgfromblob\n"
    ;

const char * readimgfromblob_doc = 
    "img = readimgfromblob(data)\n"
    "\n"
    "Read an image using Image Magick.\n"
    "\n"
    "The returned array is either a uint8, or a uint16 array, depending on the image type.\n"
    "\n"
    "If the image is reported to be a colour image, then a 3-dimensional array is returned. "
    "The last dimension encodes the red, green, and blue channels.\n"
    "\n"
    "@see readimg\n"
    ;

const char * writeimg_doc =
    "writeimg(array, filename)\n"
    "\n"
    "Writes image array to filename using Image Magick.\n"
    "\n"
    "Handles colour images (stored in HxWx3 format) or grey-scale (stored in HxW format).\n"
    "Handles images stored as either uint8 (in which case the output is 8-bit) or\n"
    "uint16 (in which case the output may be 16-bit if the output format supports it).\n"
    "\n"
    "Limitations\n"
    "-----------\n"
    "\n"
    "Currently only handles contiguous arrays.\n"
    ;

PyMethodDef methods[] = {
  {"readimg",readimg, METH_VARARGS , readimg_doc },
  {"readimgfromblob",readimgfromblob, METH_VARARGS , readimgfromblob_doc },
  {"writeimg",writeimg, METH_VARARGS , writeimg_doc},
  {NULL, NULL,0,NULL},
};

const char * module_doc = 
    "readimg: Read an image into a numpy array.\n"
    "\n"
    "The implementation of this module is based on ImageMagick. Therefore, it supports\n"
    "all image formats that ImageMagick supports.\n"
    "\n"
    "\n"
    "Functions\n"
    "---------\n"
    "\n"
    "This module provides three functions:\n"
    "   * readimg(filename): reads an image from a file\n"
    "   * readimgfromblob(blob): reads an image from a blog (character string)\n"
    "   * writeimg(img, filename): writes an image to a file (format is inferred from extension).\n"
    ;
}

extern "C"
void initreadmagick()
  {
    import_array();
    PyObject* module = Py_InitModule3("readmagick", methods, module_doc);
    PyModule_AddStringConstant(module,"__version__","1.0.1");
  }

