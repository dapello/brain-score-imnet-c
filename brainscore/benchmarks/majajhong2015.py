import brainscore
from brainscore.benchmarks._neural_common import NeuralBenchmark, average_repetition
from brainscore.metrics.ceiling import InternalConsistency, RDMConsistency
from brainscore.metrics.rdm import RDMCrossValidated
from brainscore.metrics.regression import CrossRegressedCorrelation, mask_regression, ScaledCrossRegressedCorrelation, \
    pls_regression, pearsonr_correlation
from brainscore.utils import LazyLoad

VISUAL_DEGREES = 8
NUMBER_OF_TRIALS = 50


def _DicarloMajajHong2015Region(region, identifier_metric_suffix, similarity_metric, ceiler):
    assembly_repetition = LazyLoad(lambda region=region: load_assembly(average_repetitions=False, region=region))
    assembly = LazyLoad(lambda region=region: load_assembly(average_repetitions=True, region=region))
    return NeuralBenchmark(identifier=f'dicarlo.MajajHong2015.{region}-{identifier_metric_suffix}', version=3,
                           assembly=assembly, similarity_metric=similarity_metric,
                           visual_degrees=VISUAL_DEGREES, number_of_trials=NUMBER_OF_TRIALS,
                           ceiling_func=lambda: ceiler(assembly_repetition),
                           parent=region, paper_link='http://www.jneurosci.org/content/35/39/13402.short')


def DicarloMajajHong2015V4PLS():
    return _DicarloMajajHong2015Region('V4', identifier_metric_suffix='pls',
                                       similarity_metric=CrossRegressedCorrelation(
                                           regression=pls_regression(), correlation=pearsonr_correlation(),
                                           crossvalidation_kwargs=dict(stratification_coord='object_name')),
                                       ceiler=InternalConsistency())


def DicarloMajajHong2015ITPLS():
    return _DicarloMajajHong2015Region('IT', identifier_metric_suffix='pls',
                                       similarity_metric=CrossRegressedCorrelation(
                                           regression=pls_regression(), correlation=pearsonr_correlation(),
                                           crossvalidation_kwargs=dict(stratification_coord='object_name')),
                                       ceiler=InternalConsistency())


def DicarloMajajHong2015V4Mask():
    return _DicarloMajajHong2015Region('V4', identifier_metric_suffix='mask',
                                       similarity_metric=ScaledCrossRegressedCorrelation(
                                           regression=mask_regression(), correlation=pearsonr_correlation(),
                                           crossvalidation_kwargs=dict(splits=2, stratification_coord='object_name')),
                                       ceiler=InternalConsistency())


def DicarloMajajHong2015ITMask():
    return _DicarloMajajHong2015Region('IT', identifier_metric_suffix='mask',
                                       similarity_metric=ScaledCrossRegressedCorrelation(
                                           regression=mask_regression(), correlation=pearsonr_correlation(),
                                           crossvalidation_kwargs=dict(splits=2, stratification_coord='object_name')),
                                       ceiler=InternalConsistency())


def DicarloMajajHong2015V4RDM():
    return _DicarloMajajHong2015Region('V4', identifier_metric_suffix='rdm',
                                       similarity_metric=RDMCrossValidated(
                                           crossvalidation_kwargs=dict(stratification_coord='object_name')),
                                       ceiler=RDMConsistency())


def DicarloMajajHong2015ITRDM():
    return _DicarloMajajHong2015Region('IT', identifier_metric_suffix='rdm',
                                       similarity_metric=RDMCrossValidated(
                                           crossvalidation_kwargs=dict(stratification_coord='object_name')),
                                       ceiler=RDMConsistency())


def load_assembly(average_repetitions, region, access='private'):
    assembly = brainscore.get_assembly(name=f'dicarlo.MajajHong2015.{access}')
    assembly = assembly.sel(region=region)
    assembly['region'] = 'neuroid', [region] * len(assembly['neuroid'])
    assembly = assembly.squeeze("time_bin")
    assembly.load()
    assembly = assembly.transpose('presentation', 'neuroid')
    if average_repetitions:
        assembly = average_repetition(assembly)
    return assembly
