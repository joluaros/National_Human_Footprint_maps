# -*- coding: utf-8 -*-
"""
Module for creating the Human Footprint maps of Peru and Ecuador.

Version 2041001 (Preprint)

This script will read spatial datasets of pressures, prepared them by
converting them all to a raster format with identical dimensions, then
score them to reflect their expected human influence.
The scored pressures will then be added to calculate a Human Footprint map.

The structure of the module requires the following:
    - HF_main.py to control the higher level of the process.
    - HF_settings to control the general settings.
    - HF_tasks to call all functions according to the HF workflow.
    - HF_spatial to provide all spatial functions and classes.
    - HF_scores to provide scores of humnan influence.
    - HF_layers for the settings related to layers (e.g. paths).

This is part of the project Life on Land, with UNDP, the Ministries of the
Environment of each country, and funded by NASA.

Created on Thu Jun 18 18:26:00 2020

@author: Jose Aragon-Osejo aragon@unbc.ca / jose.luis.aragon.ec@gmail.com

"""

import numpy as np


# From pressure scoring template
Urban_area_score = 10
Densily_populated_areas_score = 10
Infrastructure_impervious_pollution_score = 10
Infrastructure_impervious_score = 9
Main_road_score = 8.75
Infrastructure_partially_impervious_score = 8.25
Secondary_road_score = 8.25
Partially_impervious_pollution = 7.25 #  mining
Settlement_score = 7.5
Artificial_water_score = 6
Country_road_score = 6
Pasture_score = 5.5
Agriculture_score = 5.25
Linear_infrastructure_pollution_score = 5.25
Linear_infrastructure_score = 5
Tree_plantation_score = 4.5
Land_use_change_score = 4
Trail_score = 1.25

# Other settings
Indirect_max_hours = 4


# GHF for scoring template adapted from the Global Human Footprint maps
GHF = {

    'road_scores_l1': {
        'func': 'bins',
        'scores_by_bins': (
            ((0, 2), Main_road_score),
            ((2, np.inf), 0)),
    },

    'road_scores_l2': {
        'func': 'bins',
        'scores_by_bins': (
            ((0, 2), Secondary_road_score),
            ((2, np.inf), 0)),
    },

    'road_scores_l3': {
        'func': 'bins',
        'scores_by_bins': (
            ((0, 2), Country_road_score),
            ((2, np.inf), 0)),
    },

    'road_scores_l4': {
        'func': 'bins',
        'scores_by_bins': (
            ((0, 2), Trail_score),
            ((2, np.inf), 0)),
    },

    'indirect_scores': {
        'func': 'exp',
        'direct_score': 0,
        'max_score_exp': Land_use_change_score,
        'min_score_exp': 0,
        'max_dist': Indirect_max_hours*36000, #  Times raster in 10s
    },

    'settlement_scores': {
        'func': 'exp',
        'direct_score': Settlement_score,
        'max_score_exp': Land_use_change_score,
        'min_score_exp': 0,
        'max_dist': 100,
    },

    'urban_scores': {
        'func': 'bins',
        'scores_by_bins': (
            ((0, 2), Urban_area_score),
            ((2, np.inf), 0)),
    },

    'pop_scores_INEC_INEI': {
        'func': 'log',
        'max_score': Densily_populated_areas_score,
        # Parameters from the Global HF "inflated" scores, 
        # so were improved to this:
        'mult_factor': 2.5,
        'min_threshold': 0,
        'max_threshold': 10000,
        'scaling_factor': 1,
        'resampling_method': 'bilinear',
    },


    'worldpop_scores': {
        'func': 'log',
        'max_score': Densily_populated_areas_score,
        'mult_factor': 5.41, ##  for reaching sc0re 10 at 60 of DN
        'min_threshold': 0,
        'max_threshold': 70,
        'scaling_factor': 1,
        'resampling_method': 'bilinear',
    },

    'built_Meta_scores': {
        'func': 'bins',
        'scores_by_bins': (
            ((0, .0001), 0),
            ((.0001, np.inf), Settlement_score)),
        'resampling_method': 'bilinear',
    },

    'Infr_imp_scores': {
        'func': 'bins',
        'scores_by_bins': (
            ((0, 2), Infrastructure_impervious_score),
            ((2, np.inf), 0)),
    },

    'Infr_imp_poll_scores_05': {
        # 'from': 'Infrastructure_impervious_pollution_score',
        'func': 'bins',
        'scores_by_bins': (
            ((0, 50), Infrastructure_impervious_pollution_score),
            ((50, np.inf), 0)),
    },

    'Infr_imp_poll_scores_15': {
        # 'from': 'Infrastructure_impervious_pollution_score',
        'func': 'bins',
        'scores_by_bins': (
            ((0, 150), Infrastructure_impervious_pollution_score),
            ((150, np.inf), 0)),
    },

    'Infr_imp_poll_scores_5': {
        # 'from': 'Infrastructure_impervious_pollution_score',
        'func': 'bins',
        'scores_by_bins': (
            ((0, 500), Infrastructure_impervious_pollution_score),
            ((500, np.inf), 0)),
    },

    'Part_imp_poll_05': {
        # 'from': 'Mining_score',
        'func': 'bins',
        'scores_by_bins': (
            ((0, 50), Partially_impervious_pollution),
            ((50, np.inf), 0)),
    },
    
    'Part_imp_poll': {
        # 'from': 'Mining_score',
        'func': 'bins',
        'scores_by_bins': (
            ((0, 2), Partially_impervious_pollution),
            ((2, np.inf), 0)),
    },

    'Inf_part_imp_05': {
        # 'from': 'Infrastructure_partially_impervious_score',
        'func': 'bins',
        'scores_by_bins': (
            ((0, 50), Infrastructure_partially_impervious_score),
            ((50, np.inf), 0)),
    },

    'Inf_part_imp_15': {
        # 'from': 'Infrastructure_partially_impervious_score',
        'func': 'bins',
        'scores_by_bins': (
            ((0, 150), Infrastructure_partially_impervious_score),
            ((150, np.inf), 0)),
    },

    'line_inf_poll_scores': {
        'func': 'bins',
        'scores_by_bins': (
            ((0, 2), Linear_infrastructure_pollution_score),
            ((2, np.inf), 0)),
    },
    
    'line_inf_scores': {
        'func': 'bins',
        'scores_by_bins': (
            ((0, 2), Linear_infrastructure_score),
            ((2, np.inf), 0)),
    },

    'ntl_VIIRS_scores': {
        'func': 'linear',
        'max_score': Densily_populated_areas_score,
        'max_threshold': 60, #  60 is Q3 from samples in urban areas
        'min_threshold': .5,
        'resampling_method': 'bilinear',
    },

    'plantations_scores': {
        'func': 'bins',
        'scores_by_bins': (
            ((0, 2), Tree_plantation_score),
            ((2, np.inf), 0),),
    },

    'agr_MINAGRI_scores': {
        'func': 'categories',
        # 'numb_categories': 1,
        'scores_by_categories': {
            'Not crops': (0, [0]),
            'Crops': (Agriculture_score, [1]),
        },
        'resampling_method': 'mode',
    },

    'bui_Mapbiopmas_scores': {
        'func': 'categories',
        # 'numb_categories': 1,
        'scores_by_categories': {
            'Formación boscosa': (0, (3, 4, 5, 6)),
            'Formación natural no boscosa': (0, (11, 12, 13)),
            'Pasto': (0, [15]),
            'Agricultura, Mosaico agropecuario': (0, (18, 21)),
            'Plantación forestal': (0, [9]),
            'Infraestructura': (Urban_area_score, [24]),
            'Minería': (0, [30]),
            'Otra área sin vegetación': (0, [25]),
            'Cuerpo de agua': (0, (33, 34)),
            'No observado': (0, [27]),
        },
        'resampling_method': 'mode',
    },

    'luc_Mapbiopmas_scores': {
        'func': 'categories',
        'scores_by_categories': {
            'Formación boscosa': (0, (3, 4, 5, 6)),
            'Formación natural no boscosa': (0, (11, 12, 13)),
            'Pasto': (Pasture_score, [15]),
            'Agricultura, Mosaico agropecuario': (Agriculture_score, (18, 21)),
            'Plantación forestal': (Tree_plantation_score, [9]),
            'Infraestructura': (0, [24]),
            'Minería': (0, [30]),
            'Otra área sin vegetación': (0, [25]),
            'Cuerpo de agua': (0, (33, 34)),
            'No observado': (0, [27]),
        },
        'resampling_method': 'mode',
    },

    'mining_Mapbiopmas_scores': {
        'func': 'categories',
        'scores_by_categories': {
            'Formación boscosa': (0, (3, 4, 5, 6)),
            'Formación natural no boscosa': (0, (11, 12, 13)),
            'Pasto': (0, [15]),
            'Agricultura, Mosaico agropecuario': (0, (18, 21)),
            'Plantación forestal': (0, [9]),
            'Infraestructura': (0, [24]),
            'Minería': (Partially_impervious_pollution, [30]),
            'Otra área sin vegetación': (0, [25]),
            'Cuerpo de agua': (0, (33, 34)),
            'No observado': (0, [27]),
        },
        'resampling_method': 'mode',
    },

    'luc_MAAE_scores': {
        'func': 'categories',
        'scores_by_categories': {
            # Class Grassland eliminated and Pastizal moved to Crops because
            # it does not exist in all time series
            'Forest': (0, ('BOSQUE', 'BOSQUE NATIVO', 'MANGLAR',)),
            'Shrubs, Herbaceous': (0,  ('PÁRAMO', 'PARAMO', 'PRAMO',
                                        'VEGETACIÓN HERBÁEAS',
                                        'VEGETACIN HERBEAS',
                                        'VEGETACIN HERBCEA',
                                        'VEGETACION ARBUSTIVA Y HERBACEA',
                                        'VEGETACIÓN ARBUSTIVA Y HERBÁCEA',
                                        'VEGETACIN ARBUSTIVA Y HERBCEA',
                                        'VEGETACIÓN ARBUSTIVA',
                                        'VEGETACIN ARBUSTIVA',
                                        'VEGETACION ARBUSTIVA',
                                        'VEGETACION HERBACEA',)),
            'Crops': (Agriculture_score, ('TIERRA AGROPECUARIA', 'MOSAICO AGROPECUARIO',
                          'CULTIVO PERMANENTE', 'CULTIVO ANUAL',
                          'CULTIVO SEMI PERMANENTE',
                          'PASTIZAL',
                          )),
            'Forestry': (Tree_plantation_score, ('PLANTACION FORESTAL', 'PLANTACIÓN FORESTAL',
                             'PLANTACIN FORESTAL')),
            'Human_water': (Agriculture_score, ('ESPEJOS DE AGUA ARTIFICIAL', 'ARTIFICIAL',
                                'CUERPO DE AGUA ARTIFICIAL')),
            'Infrastructure': (Agriculture_score, ('INFRAESTRUCTURA')),
            'Built': (0, ('ZONA ANTROPICA', 'ZONA ANTRÓPICA',
                          'ZONA ANTRPICA', 'AREA POBLADA')),
            'Water, Other': (0,  ('ESPEJOS DE AGUA NATURAL', 'CUERPO DE AGUA',
                                  'CUERPO DE AGUA NATURAL',
                                  'OTRAS TIERRAS', 'GLACIAR', 'NATURAL',
                                  'ÁREA SIN COBERTURA VEGETAL',
                                  'REA SIN COBERTURA VEGETAL',
                                  'AREA SIN COBERTURA VEGETAL',
                                  'SIN INFORMACIÓN',
                                  'SIN INFORMACIN',
                                  'SIN INFORMACION')),
        },
    },

    'bui_MAAE_scores': {
        'func': 'categories',
        'scores_by_categories': {
            'Forest': (0, ('BOSQUE', 'BOSQUE NATIVO', 'MANGLAR',)),
            'Shrubs, Herbaceous': (0, ('PÁRAMO', 'PARAMO', 'PRAMO',
                                        'VEGETACIÓN HERBÁEAS',
                                        'VEGETACIN HERBEAS',
                                        'VEGETACIN HERBCEA',
                                        'VEGETACION ARBUSTIVA Y HERBACEA',
                                        'VEGETACIÓN ARBUSTIVA Y HERBÁCEA',
                                        'VEGETACIN ARBUSTIVA Y HERBCEA',
                                        'VEGETACIÓN ARBUSTIVA',
                                        'VEGETACIN ARBUSTIVA',
                                        'VEGETACION ARBUSTIVA',
                                        'VEGETACION HERBACEA',)),
            'Crops': (0, ('TIERRA AGROPECUARIA', 'MOSAICO AGROPECUARIO',
                          'CULTIVO PERMANENTE', 'CULTIVO ANUAL',
                          'CULTIVO SEMI PERMANENTE',
                          'PASTIZAL',
                          )),
            'Forestry': (0, ('PLANTACION FORESTAL', 'PLANTACIÓN FORESTAL',
                              'PLANTACIN FORESTAL')),
            'Human_water': (0, ('ESPEJOS DE AGUA ARTIFICIAL', 'ARTIFICIAL',
                                'CUERPO DE AGUA ARTIFICIAL')),
            'Infrastructure': (0, ('INFRAESTRUCTURA')),
            'Built': (Urban_area_score, ('ZONA ANTROPICA', 'ZONA ANTRÓPICA',
                            'ZONA ANTRPICA', 'AREA POBLADA')),
            'Water, Other': (0, ('ESPEJOS DE AGUA NATURAL', 'CUERPO DE AGUA',
                                 'CUERPO DE AGUA NATURAL',
                                  'OTRAS TIERRAS', 'GLACIAR', 'NATURAL',
                                  'ÁREA SIN COBERTURA VEGETAL',
                                  'REA SIN COBERTURA VEGETAL',
                                  'AREA SIN COBERTURA VEGETAL',
                                  'SIN INFORMACIÓN',
                                  'SIN INFORMACIN',
                                  'SIN INFORMACION')),
        },
    },

    'mining_MINAM_scores': {
        'func': 'categories',
        'scores_by_categories': {
            'Forest': (0,  ('Bofedal',
                            'Bosque de colina alta', 'Bosque de colina alta con paca',
                            'Bosque de colina alta del Divisor', 'Bosque de colina baja',
                            'Bosque de colina baja con castaña', 'Bosque de colina baja con paca',
                            'Bosque de colina baja con shiringa', 'Bosque de llanura meándrica',
                            'Bosque de montaña', 'Bosque de montaña altimontano', 'Bosque de montaña basimontano',
                            'Bosque de montaña con paca',
                            'Bosque de montaña basimontano con paca',
                            'Bosque de montaña montano', 'Bosque de palmeras de montaña montano',
                            'Bosque de terraza alta', 'Bosque de terraza alta basimontano',
                            'Bosque de terraza alta con castaña', 'Bosque de terraza alta con paca',
                            'Bosque de terraza baja', 'Bosque de terraza baja basimontano',
                            'Bosque de terraza baja con castaña', 'Bosque de terraza baja con paca',
                            'Bosque de terraza inundable por agua negra', 'Bosque inundable de palmeras',
                            'Bosque inundable de palmeras basimontano', 'Bosque montano occidental andino',
                            'Bosque relicto altoandino', 'Bosque relicto mesoandino',
                            'Bosque relicto mesoandino de coníferas', 'Bosque seco de colina alta',
                            'Bosque seco de colina baja', 'Bosque seco de lomada', 'Bosque seco de montaña',
                            'Bosque seco de piedemonte', 'Bosque seco ribereño', 'Bosque seco tipo sabana',
                            'Bosque semideciduo de montaña', 'Bosque subhúmedo de montaña',
                            'Bosque xérico interandino', 'Cardonal', 'Herbazal hidrofítico',
                            'Jalca', 'Loma', 'Manglar', 'Matorral arbustivo', 'Matorral arbustivo altimontano',
                            'Matorral esclerófilo de montaña montano', 'Pacal', 'Pajonal andino',
                            'Páramo', 'Sabana hidrofítica con palmeras', 'Sabana xérica interandina',
                            'Tillandsial', 'Vegetación esclerófila de arena blanca')),
            'Crops': (0, ('Agricultura costera y andina', 'Areas de no bosque amazónico')),
            'Forestry': (0, ('Plantación Forestal')),
            'Natural vegetation': (0, ('Area altoandina con escasa y sin vegetación',
                                        'Desierto costero', 'Humedal costero',
                                        'Albúfera', 'Vegetación de isla')),
            'Water, Other': (0, ('Banco de arena', 'Glaciar', 'Río', 'Estero',
                                  'Lagunas, lagos y cochas', 'Canal internacional',
                                  'Estuario de virilla')),
            'Human_water': (0, ('Represa')),
            'Built': (0, ('Area urbana')),
            'Mining': (Partially_impervious_pollution, ('Centro minero')),
            'Infrastructure': (0, ('Infraestructura')),
        },
    },

}

#######################################################################
# Print layers by scoring method for documentation
if __name__ == "__main__":
#######################################################################
    from HF_layers import layers_settings#, multitemporal_layers
    # print(f'{GHF=}')
    # print(f'\n{multitemporal_layers=}')
    # print(f'\n{layers_settings=}')
    scoring_dict = {}
    for scoring_method in GHF:
        # print(scoring_method)
        scoring_dict[scoring_method] = []
        for layer in layers_settings:
            # print(layer, layers_settings[layer]['scoring'])
            if scoring_method==layers_settings[layer]['scoring']:
                # print(layer, layers_settings[layer]['scoring'])
                if 'from' in GHF[scoring_method]:
                    scoring_dict[scoring_method].append(layer)
                    # scoring_dict[scoring_method].append(['XXX from:'+GHF[scoring_method]['from']])
                else:
                    scoring_dict[scoring_method].append(layer)
                
    for scoring_method in scoring_dict:
        
        print('\n', scoring_method, scoring_dict[scoring_method])

    
