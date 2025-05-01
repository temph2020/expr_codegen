import sys
from io import StringIO

import polars as pl

from expr_codegen import codegen_exec


def _code_block_1():
    # 因子编辑区，可利用IDE的智能提示在此区域编辑因子
    LOG_MC_ZS = cs_mad_zscore(log1p(market_cap))


def _code_block_2():
    # 模板中已经默认导入了from polars_ta.prefix下大量的算子，但
    # talib在模板中没有默认导入。这种写法可实现在生成的代码中导入
    from polars_ta.prefix.talib import ts_LINEARREG_SLOPE  # noqa

    # 1. 下划线开头的变量只是中间变量,会被自动更名，最终输出时会被剔除
    # 2. 下划线开头的变量可以重复使用。多个复杂因子多行书写时有重复中间变时不再冲突
    _avg = ts_mean(corr, 20)
    _std = ts_std_dev(corr, 20)
    _beta = ts_LINEARREG_SLOPE(corr, 20)

    # 3. 下划线开头的变量有环循环赋值。在调试时可快速用注释进行切换
    _avg = cs_mad_zscore_resid(_avg, LOG_MC_ZS, ONE)
    _std = cs_mad_zscore_resid(_std, LOG_MC_ZS, ONE)
    # _beta = cs_mad_zscore_resid(_beta, LOG_MC_ZS, ONE)

    _corr = cs_zscore(_avg) + cs_zscore(_std)
    CPV = cs_zscore(_corr) + cs_zscore(_beta)


code = codegen_exec(None, _code_block_1, _code_block_2, over_null='partition_by', output_file=sys.stdout)  # 打印代码
code = codegen_exec(None, _code_block_1, _code_block_2, over_null='partition_by', output_file="output.py")  # 保存到文件
code = codegen_exec(None, _code_block_1, _code_block_2, over_null='partition_by')  # 只执行，不保存代码

code = StringIO()
codegen_exec(None, _code_block_1, _code_block_2, over_null='partition_by', output_file=code)  # 保存到字符串
code.seek(0)
code.read()  # 读取代码

# TODO 替换成合适的数据
df = pl.DataFrame()
df = codegen_exec(df.lazy(), _code_block_1, _code_block_2, over_null='partition_by').collect()  # Lazy CPU
df = codegen_exec(df.lazy(), _code_block_1, _code_block_2, over_null='partition_by').collect(engine="gpu")  # Lazy GPU
