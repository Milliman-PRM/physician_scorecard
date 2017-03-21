"""
### CODE OWNERS: Michael Reisz
### OBJECTIVE:
  Read in PUDD/PUAD parquet files and output to reporting SQLite database for
  the Physician Scorecard tool.
### DEVELOPER NOTES:
"""

import logging

import pyspark.sql
import pyspark.sql.functions as spark_funcs

import prm.meta.project
from prm.spark.app import SparkApp
from prm.meta.output_datamart import DataMart

LOGGER = logging.getLogger(__name__)
PRM_META = prm.meta.project.parse_project_metadata()


# pylint: disable=no-member

# =============================================================================
# LIBRARIES, LOCATIONS, LITERALS, ETC. GO ABOVE HERE
# =============================================================================


def main() -> int:
    """A function to enclose the execution of business logic."""
    LOGGER.info('About to do something awesome.')
    sparkapp = SparkApp(PRM_META['pipeline_signature'])

    # Create the dataframes:
    dataframes = [('puad01_member', 180),
                  ('puad02_risk_cond', 180),
                  ('puad03_risk_cond_grp', 180),
                  ('puad04_risk_other', 180),
                  ('puad05_comp_quality', 180),
                  ('puad05ref_comp_quality', 180),
                  ('puad06_comp_rx', 180),
                  ('puad07_hist_flight', 180),
                  ('puad08_hcc_feat', 180),
                  ('puad10_modeling_windows', 180),
                  ('puad11_predictions', 180),
                  ('puad12_member_excluded', 180),
                  ('puad13_cond_uncoded', 180),
                  ('puad14_pred_therap_class', 180),
                  ('decor_case', 73),
                  ('outclaims_PRM', 73),
                  ('outpharmacy_PRM', 73),
                  ('member', 35),
                  ('member_time', 35),
                  ('providers', 25),
                  ('prm_line_agg', 15)]

    df_raw = dict()
    df_temp = dict()
    df_out = dict()

    for table, dir in dataframes:
        parquet_name = table + '.parquet'
        df_raw[table] = sparkapp.load_df(PRM_META[dir, 'out'] / parquet_name)



    """
        Provider Table
    """
    df_temp['providers'] = df_raw['providers'].select('prv_id', 'prv_name', 'prv_hier_1', 'prv_hier_2', 'prv_id_npi').filter('prv_type = "Physician"').withColumnRenamed('prv_taxonomy_cd', 'prv_id_tin')
    df_temp['provider_memcnt'] = df_raw['member'].groupBy('mem_prv_id_align').agg({'member_id': 'count'}).withColumnRenamed('count(member_id)', 'member_count')
    df_out['providers'] = df_temp['providers'].join(df_temp['provider_memcnt'], df_temp['providers'].prv_id == df_temp['provider_memcnt'].mem_prv_id_align, 'inner').drop(df_temp['provider_memcnt'].mem_prv_id_align).orderBy('mem_prv_id_align')

    # Get a distinct list of assigned providers to use in limiting later dataframes
    df_temp['provider_distinct'] = df_out['providers'].select('prv_id').distinct()
    df_temp['prv_mem_align'] = df_raw['member'].select('member_id', 'mem_prv_id_align').distinct().orderBy('member_id', 'mem_prv_id_align').withColumnRenamed('mem_prv_id_align', 'prv_id')


    """
        Provider_Time Table
    """
    for line in ['medical', 'rx']:
        df_temp['provider_time_' + line] = df_raw['member_time'].select(
            'mem_prv_id_align',
            'elig_month',
            # 'cover_medical',
            'memmos'
        ).filter(
            "cover_"  + line + " = 'Y'"
        ).groupBy(
            'mem_prv_id_align',
            'elig_month'
        ).agg(
            {'memmos': 'sum'}
        ).drop(
            'cover_' + line
        ).withColumnRenamed(
            'sum(memmos)', 'memmos_' + line
        ).withColumnRenamed(
            'mem_prv_id_align', 'prv_id'
        ).orderBy(
            'prv_id',
            'elig_month'
        )

    df_temp['provider_time'] = df_temp['provider_time_medical'].join(
        df_temp['provider_time_rx'],
        ['prv_id', 'elig_month'],
        'outer'
    ).orderBy(
        'prv_id',
        'elig_month'
    )

    df_out['provider_time'] = df_temp['provider_time'].join(
        df_temp['provider_distinct'],
        ['prv_id'],
        'right_outer'
    )


    """
        Cost/Utilization Table
    """
    df_temp['member_util_medical'] = df_raw['outclaims_PRM'].select(
        'member_id',
        'prm_yearmo_fromdate_claim',
        'prm_line',
        'prm_util_type',
        'prm_costs',
        'prm_util'
    ).groupBy(
        'member_id',
        'prm_yearmo_fromdate_claim',
        'prm_line',
        'prm_util_type'
    ).agg(
        {'prm_costs': 'sum',
         'prm_util': 'sum'}
    ).withColumnRenamed(
        'prm_yearmo_fromdate_claim', 'from_date'
    ).withColumnRenamed(
        'sum(prm_costs)', 'costs'
    ).withColumnRenamed(
        'sum(prm_util)', 'utilization'
    ).orderBy(
        'member_id',
        'prm_yearmo_fromdate_claim',
        'prm_line',
        'prm_util_type'
    )

    df_temp['member_util_rx'] = df_raw['outpharmacy_PRM'].select(
        'member_id',
        'prm_yearmo_fromdate',
        'prm_line',
        'prm_util_type',
        'prm_costs',
        'prm_util'
    ).groupBy(
        'member_id',
        'prm_yearmo_fromdate',
        'prm_line',
        'prm_util_type'
    ).agg(
        {'prm_costs': 'sum',
         'prm_util': 'sum'}
    ).withColumnRenamed(
        'prm_yearmo_fromdate', 'from_date'
    ).withColumnRenamed(
        'sum(prm_costs)', 'costs'
    ).withColumnRenamed(
        'sum(prm_util)', 'utilization'
    ).orderBy(
        'member_id',
        'prm_yearmo_fromdate',
        'prm_line',
        'prm_util_type'
    )

    df_temp['member_util'] = df_temp['member_util_medical'].union(
        df_temp['member_util_rx']
    ).orderBy(
        'member_id',
        'from_date',
        'prm_line',
        'prm_util_type'
    )

    df_out['cost_util'] = df_temp['member_util'].join(
        df_temp['prv_mem_align'],
        'member_id',
        'inner'
    ).drop(
        'member_id'
    ).groupBy(
        'prv_id',
        'from_date',
        'prm_line',
        'prm_util_type'
    ).agg(
        {'costs': 'sum',
         'utilization': 'sum'}
    ).withColumnRenamed(
        'sum(costs)', 'costs'
    ).withColumnRenamed(
        'sum(utilization)', 'utilization'
    ).orderBy(
        'prv_id',
        'from_date',
        'prm_line',
        'prm_util_type'
    )


    """
        Cost/Utilization Table
    """
    df_out['ref_service_cat'] = df_raw['prm_line_agg'].select(
        'prm_line_agg',
        'hist_time_service_ind',
        'hist_time_service',
        'prm_coverage_type'
    ).withColumnRenamed(
        'hist_time_service_ind', 'hist_time_service_dual'
    ).orderBy(
        'hist_time_service_ind'
    )


    """
        Quality Measures Table
    """
    df_temp['member_quality_measures'] = df_raw['puad05_comp_quality'].select(
        'member_id',
        'comp_quality_short',
        'comp_quality_numerator',
        'comp_quality_denominator'
    ).groupBy(
        'member_id',
        'comp_quality_short'
    ).agg(
        {'comp_quality_numerator': 'sum',
         'comp_quality_denominator': 'sum'}
    ).withColumnRenamed(
        'sum(comp_quality_numerator)', 'comp_quality_numerator'
    ).withColumnRenamed(
        'sum(comp_quality_denominator)', 'comp_quality_denominator'
    ).orderBy(
        'member_id',
        'comp_quality_short'
    )

    df_out['quality_measures'] = df_temp['member_quality_measures'].join(
        df_temp['prv_mem_align'],
        'member_id',
        'inner'
    ).groupBy(
        'prv_id',
        'comp_quality_short'
    ).agg(
        {'comp_quality_numerator': 'sum',
         'comp_quality_denominator': 'sum'}
    ).withColumnRenamed(
        'sum(comp_quality_numerator)', 'comp_quality_numerator'
    ).withColumnRenamed(
        'sum(comp_quality_denominator)', 'comp_quality_denominator'
    ).orderBy(
        'prv_id',
        'comp_quality_short'
    )


    """
        Quality Measures Reference Table
    """
    df_out['ref_member_quality_measures'] = df_raw['puad05ref_comp_quality'].select(
        'comp_quality_short',
        'comp_quality_dual',
        'comp_quality',
        'comp_quality_direction',
        'comp_quality_target_value',
        'comp_quality_format_code'
    ).orderBy(
        'comp_quality_dual'
    )


    return 0


if __name__ == '__main__':
    # pylint: disable=wrong-import-position, wrong-import-order, ungrouped-imports
    import sys
    import prm.utils.logging_ext
    import prm.spark.defaults_prm

    prm.utils.logging_ext.setup_logging_stdout_handler()
    SPARK_DEFAULTS_PRM = prm.spark.defaults_prm.get_spark_defaults(PRM_META)

    with SparkApp(PRM_META['pipeline_signature'], **SPARK_DEFAULTS_PRM):
        RETURN_CODE = main()

    sys.exit(RETURN_CODE)

