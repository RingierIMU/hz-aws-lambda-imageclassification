"""Python wrappers around TensorFlow ops.

This file is MACHINE GENERATED! Do not edit.
Original C++ source file: gen_coder_ops.cc
"""

import collections as _collections
import six as _six

from tensorflow.python import pywrap_tensorflow as _pywrap_tensorflow
from tensorflow.python.eager import context as _context
from tensorflow.python.eager import core as _core
from tensorflow.python.eager import execute as _execute
from tensorflow.python.framework import dtypes as _dtypes
from tensorflow.python.framework import errors as _errors
from tensorflow.python.framework import tensor_shape as _tensor_shape

from tensorflow.core.framework import op_def_pb2 as _op_def_pb2
# Needed to trigger the call to _set_call_cpp_shape_fn.
from tensorflow.python.framework import common_shapes as _common_shapes
from tensorflow.python.framework import op_def_registry as _op_def_registry
from tensorflow.python.framework import ops as _ops
from tensorflow.python.framework import op_def_library as _op_def_library
from tensorflow.python.util.tf_export import tf_export


@tf_export('range_decode')
def range_decode(encoded, shape, cdf, precision, name=None):
  r"""Decodes a range-coded `code` into an int32 tensor of shape `shape`.

  This is the reverse op of RangeEncode. The shape of the tensor that was encoded
  should be known by the caller.

  Implementation notes:

  - If wrong input was given (e.g., corrupt `encoded` string, or `cdf` or
  `precision` do not match encoder), the decode is unsuccessful. Because of
  potential performance issues, the decoder does not return error status.

  Args:
    encoded: A `Tensor` of type `string`.
      A scalar string tensor from RangeEncode.
    shape: A `Tensor` of type `int32`.
      An int32 1-D tensor representing the shape of the data encoded by
      RangeEncode.
    cdf: A `Tensor` of type `int32`.
    precision: An `int` that is `>= 1`.
      The number of bits for probability quantization. Must be <= 16, and
      must match the precision used by RangeEncode that produced `encoded`.
    name: A name for the operation (optional).

  Returns:
    A `Tensor` of type `int16`. An int32 tensor with shape equal to `shape`.
  """
  _ctx = _context._context
  if _ctx is None or not _ctx._eager_context.is_eager:
    precision = _execute.make_int(precision, "precision")
    _, _, _op = _op_def_lib._apply_op_helper(
        "RangeDecode", encoded=encoded, shape=shape, cdf=cdf,
        precision=precision, name=name)
    _result = _op.outputs[:]
    _inputs_flat = _op.inputs
    _attrs = ("precision", _op.get_attr("precision"))
    _execute.record_gradient(
      "RangeDecode", _inputs_flat, _attrs, _result, name)
    _result, = _result
    return _result

  else:
    try:
      _result = _pywrap_tensorflow.TFE_Py_FastPathExecute(
        _ctx._context_handle, _ctx._eager_context.device_name, "RangeDecode",
        name, _ctx._post_execution_callbacks, encoded, shape, cdf,
        "precision", precision)
      return _result
    except _core._FallbackException:
      return range_decode_eager_fallback(
          encoded, shape, cdf, precision=precision, name=name, ctx=_ctx)
    except _core._NotOkStatusException as e:
      if name is not None:
        message = e.message + " name: " + name
      else:
        message = e.message
      _six.raise_from(_core._status_to_exception(e.code, message), None)


def range_decode_eager_fallback(encoded, shape, cdf, precision, name=None, ctx=None):
  r"""This is the slowpath function for Eager mode.
  This is for function range_decode
  """
  _ctx = ctx if ctx else _context.context()
  precision = _execute.make_int(precision, "precision")
  encoded = _ops.convert_to_tensor(encoded, _dtypes.string)
  shape = _ops.convert_to_tensor(shape, _dtypes.int32)
  cdf = _ops.convert_to_tensor(cdf, _dtypes.int32)
  _inputs_flat = [encoded, shape, cdf]
  _attrs = ("precision", precision)
  _result = _execute.execute(b"RangeDecode", 1, inputs=_inputs_flat,
                             attrs=_attrs, ctx=_ctx, name=name)
  _execute.record_gradient(
      "RangeDecode", _inputs_flat, _attrs, _result, name)
  _result, = _result
  return _result

_ops.RegisterShape("RangeDecode")(None)


@tf_export('range_encode')
def range_encode(data, cdf, precision, name=None):
  r"""Using the provided cumulative distribution functions (CDF) inside `cdf`, returns

  a range-code of `data`.

  The shape of `cdf` should have one more axis than the shape of `data`, and the
  prefix `cdf.shape[:-1]` should be broadcastable to `data.shape`. That is, for
  every `i = 0,...,rank(data) - 1`, the op requires that either
  `cdf.shape[i] == 1` or `cdf.shape[i] == data.shape[i]`. Note that this
  broadcasting is limited in the sense that the number of axes must match, and
  broadcasts only `cdf` but not `data`.

  `data` should have an upper bound `m > 0` such that each element is an integer
  in range `[0, m)`. Then the last dimension size of `cdf` must be `m + 1`. For
  each element of `data`, the innermost strip of `cdf` is a vector representing a
  CDF. For each k = 0,...,m, `cdf[..., k] / 2^precision` is the probability that
  an outcome is less than `k` (not less than or equal to).

  ```
     cdf[..., 0] / 2^precision = Pr(data[...] < 0)
     cdf[..., 1] / 2^precision = Pr(data[...] < 1) = Pr(data[...] <= 0)
     cdf[..., 2] / 2^precision = Pr(data[...] < 2) = Pr(data[...] <= 1)
     ...
     cdf[..., m] / 2^precision = Pr(data[...] < m) = 1
  ```

  Therefore each element of `cdf` must be in `[0, 2^precision]`.

  Ideally `cdf[..., m]` should equal to `2^precision` but this is not a hard
  requirement as long as `cdf[..., m] <= 2^precision`.

  The encoded string neither contains the shape information of the encoded data
  nor a termination symbol. Therefore the shape of the encoded data must be
  explicitly provided to the decoder.

  Implementation notes:

  - Because of potential performance issues, the op does not check whether
  elements of `data` is in the correct range `[0, m)`, or if `cdf` satisfies
  monotonic increase property.

  - For the range coder to decode the encoded string correctly, the decoder should
  be able to reproduce the internal states of the encoder precisely. Otherwise,
  the decoding would fail and once an error occur, all subsequent decoded values
  are incorrect. For this reason, the range coder uses integer arithmetics and
  avoids using any floating point operations internally, and `cdf` should contain
  integers representing quantized probability mass rather than floating points.

  Args:
    data: A `Tensor` of type `int16`. An int32 tensor.
    cdf: A `Tensor` of type `int32`.
      An int32 tensor representing the CDF's of `data`. Each integer is divided
      by `2^precision` to represent a fraction.
    precision: An `int` that is `>= 1`.
      The number of bits for probability quantization. Must be <= 16.
    name: A name for the operation (optional).

  Returns:
    A `Tensor` of type `string`. A range-coded scalar string.
  """
  _ctx = _context._context
  if _ctx is None or not _ctx._eager_context.is_eager:
    precision = _execute.make_int(precision, "precision")
    _, _, _op = _op_def_lib._apply_op_helper(
        "RangeEncode", data=data, cdf=cdf, precision=precision, name=name)
    _result = _op.outputs[:]
    _inputs_flat = _op.inputs
    _attrs = ("precision", _op.get_attr("precision"))
    _execute.record_gradient(
      "RangeEncode", _inputs_flat, _attrs, _result, name)
    _result, = _result
    return _result

  else:
    try:
      _result = _pywrap_tensorflow.TFE_Py_FastPathExecute(
        _ctx._context_handle, _ctx._eager_context.device_name, "RangeEncode",
        name, _ctx._post_execution_callbacks, data, cdf, "precision",
        precision)
      return _result
    except _core._FallbackException:
      return range_encode_eager_fallback(
          data, cdf, precision=precision, name=name, ctx=_ctx)
    except _core._NotOkStatusException as e:
      if name is not None:
        message = e.message + " name: " + name
      else:
        message = e.message
      _six.raise_from(_core._status_to_exception(e.code, message), None)


def range_encode_eager_fallback(data, cdf, precision, name=None, ctx=None):
  r"""This is the slowpath function for Eager mode.
  This is for function range_encode
  """
  _ctx = ctx if ctx else _context.context()
  precision = _execute.make_int(precision, "precision")
  data = _ops.convert_to_tensor(data, _dtypes.int16)
  cdf = _ops.convert_to_tensor(cdf, _dtypes.int32)
  _inputs_flat = [data, cdf]
  _attrs = ("precision", precision)
  _result = _execute.execute(b"RangeEncode", 1, inputs=_inputs_flat,
                             attrs=_attrs, ctx=_ctx, name=name)
  _execute.record_gradient(
      "RangeEncode", _inputs_flat, _attrs, _result, name)
  _result, = _result
  return _result

_ops.RegisterShape("RangeEncode")(None)

def _InitOpDefLibrary(op_list_proto_bytes):
  op_list = _op_def_pb2.OpList()
  op_list.ParseFromString(op_list_proto_bytes)
  _op_def_registry.register_op_list(op_list)
  op_def_lib = _op_def_library.OpDefLibrary()
  op_def_lib.add_op_list(op_list)
  return op_def_lib
# op {
#   name: "RangeDecode"
#   input_arg {
#     name: "encoded"
#     type: DT_STRING
#   }
#   input_arg {
#     name: "shape"
#     type: DT_INT32
#   }
#   input_arg {
#     name: "cdf"
#     type: DT_INT32
#   }
#   output_arg {
#     name: "decoded"
#     type: DT_INT16
#   }
#   attr {
#     name: "precision"
#     type: "int"
#     has_minimum: true
#     minimum: 1
#   }
# }
# op {
#   name: "RangeEncode"
#   input_arg {
#     name: "data"
#     type: DT_INT16
#   }
#   input_arg {
#     name: "cdf"
#     type: DT_INT32
#   }
#   output_arg {
#     name: "encoded"
#     type: DT_STRING
#   }
#   attr {
#     name: "precision"
#     type: "int"
#     has_minimum: true
#     minimum: 1
#   }
# }
_op_def_lib = _InitOpDefLibrary(b"\nQ\n\013RangeDecode\022\013\n\007encoded\030\007\022\t\n\005shape\030\003\022\007\n\003cdf\030\003\032\013\n\007decoded\030\005\"\024\n\tprecision\022\003int(\0010\001\nC\n\013RangeEncode\022\010\n\004data\030\005\022\007\n\003cdf\030\003\032\013\n\007encoded\030\007\"\024\n\tprecision\022\003int(\0010\001")
