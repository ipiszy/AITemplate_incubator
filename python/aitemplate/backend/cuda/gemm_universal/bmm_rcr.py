#  Copyright (c) Meta Platforms, Inc. and affiliates.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

"""
Codegen for bmm_rcr, which computes A @ B + bias.
A[RowMajor], B[ColMajor], bias[RowMajor]
"""

from ... import registry
from . import bmm_common, common
from .layout import RCR

# pylint: disable=C0103,C0415,W0613,C0301,R1705,R1703


PROBLEM_ARGS = {
    "bias_ptr": "c_ptr",
    "a_batch_stride": "M * K",
    "b_batch_stride": "N * K",
    "bias_batch_stride": "M * N",
    "c_batch_stride": "M * N",
    "lda": "K",
    "ldb": "K",
    "ldbias": "N",
    "ldc": "N",
}


@registry.reg("cuda.bmm_rcr.config")
def bmm_rcr_config(func_attrs, dtype="float16"):
    common.make_fproc(func_attrs, RCR)


@registry.reg("cuda.bmm_rcr.gen_profiler")
def gen_profiler(func_attrs, workdir, profiler_filename, dim_info_dict):
    return bmm_common.default_gen_profiler(
        func_attrs,
        workdir,
        profiler_filename,
        dim_info_dict,
        PROBLEM_ARGS,
    )


@registry.reg("cuda.bmm_rcr.gen_function")
def gen_function(
    func_attrs,
    exec_cond_template,
    dim_info_dict,
):
    default_mm_info = bmm_common.get_default_problem_info(
        PROBLEM_ARGS,
        alpha_value=func_attrs.get("alpha", 1),
    )
    (
        problem_args,
        input_addr_calculator,
        output_addr_calculator,
    ) = bmm_common.make_function_strided_args(
        func_attrs, dim_info_dict, default_mm_info, is_permute=False
    )

    return bmm_common.gen_function(
        func_attrs,
        exec_cond_template,
        problem_args,
        dim_info_dict,
        input_addr_calculator,
        output_addr_calculator,
    )


@registry.reg("cuda.bmm_rcr.func_decl")
def gen_function_decl(func_attrs):
    return bmm_common.gen_function_decl(func_attrs)


@registry.reg("cuda.bmm_rcr.func_call")
def gen_function_call(func_attrs, indent="  "):
    return bmm_common.gen_function_call(func_attrs, indent)


@registry.reg("cuda.bmm_rcr.filter")
def function_filter(cfg, func_attrs, ab_alignment):
    """Generates function filter.

    Parameters
    ----------
    cfg: str
        The filename generated for profiler.
    func_attrs : Dict
        Stores the operation attributes.
    ab_alignment:
        Input alignments.

    Returns
    -------
    bool
        If input cfg should be filtered.
    """
    return common.function_filter(cfg, func_attrs, ab_alignment)
