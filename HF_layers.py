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

# import numpy as np

# multitemporal_layers indicates which layers should be treated as multitemporal.
# The script will look first here and decide the closest layer in time according
# to the year being processed. If the layer is not here, it will look directly
# in the layers

multitemporal_layers = {

    'ntl_VIIRS': {
        'datasets': (
            'ntl_VIIRS_12',
            'ntl_VIIRS_13',
            'ntl_VIIRS_14',
            'ntl_VIIRS_15',
            'ntl_VIIRS_16',
            'ntl_VIIRS_17',
            'ntl_VIIRS_18',
            'ntl_VIIRS_19',
            'ntl_VIIRS_20',
            'ntl_VIIRS_21',
            'ntl_VIIRS_22',
        ),
        'purp_scores': {
            'accu_input': 'high',  # comparison to previous version
            'sustained_input': 'high',
            'well_docmted_input': 'high', 
            'user_friendly_input': 'high',
            'offi': 'low',
            'comparable': 'high',
            'source': 'VIIRS',
            'finer':
                {
                    'scale': None,
                    'res': 458,
                    'unit': 'm',
                },
        },
        'years_datasets': list(range(2012, 2022 + 1)),
    },

    'Ec_cut_MAAE': {
        'datasets': (
            'Ec_cut_MAAE_90',
            'Ec_cut_MAAE_00',
            'Ec_cut_MAAE_08',
            'Ec_cut_MAAE_14',
            'Ec_cut_MAAE_16',
            'Ec_cut_MAAE_18',
            'Ec_cut_MAAE_20',
            'Ec_cut_MAAE_22',
        ),
        'purp_scores': {
            'accu_input': 'high',
            'sustained_input': 'high',
            'well_docmted_input': 'med',
            'user_friendly_input': 'high',
            'offi': 'high',
            'comparable': 'low',
            'source': 'CUT_MAATE',
            'finer':
                {
                    'scale': 100000,
                    'res': None,
                    'unit': None,
                },
        },
        'years_datasets': [1990, 2000, 2008, 2014, 2016, 2018, 2020, 2022],
    },

    'Ec_bui_MAAE': {
        'datasets': (
            'Ec_bui_MAAE_90',
            'Ec_bui_MAAE_00',
            'Ec_bui_MAAE_08',
            'Ec_bui_MAAE_14',
            'Ec_bui_MAAE_16',
            'Ec_bui_MAAE_18',
            'Ec_bui_MAAE_20',
            'Ec_bui_MAAE_22',
        ),
        'purp_scores': {
            'accu_input': 'high',
            'sustained_input': 'high',
            'well_docmted_input': 'med',
            'user_friendly_input': 'high',
            'offi': 'high',
            'comparable': 'low',
            'source': 'CUT_MAATE',
            'finer':
                {
                    'scale': 100000,
                    'res': None,
                    'unit': None,
                },
        },
        'years_datasets': [1990, 2000, 2008, 2014, 2016, 2018, 2020, 2022],
    },


    'Pe_bui_Mapbiopmas': {
        'datasets': (
            # 'Pe_bui_Mapbiopmas_00',
            # 'Pe_bui_Mapbiopmas_10',
            'Pe_bui_Mapbiopmas_12',
            'Pe_bui_Mapbiopmas_13',
            'Pe_bui_Mapbiopmas_14',
            'Pe_bui_Mapbiopmas_15',
            'Pe_bui_Mapbiopmas_16',
            'Pe_bui_Mapbiopmas_17',
            'Pe_bui_Mapbiopmas_18',
            'Pe_bui_Mapbiopmas_19',
            'Pe_bui_Mapbiopmas_20',
            'Pe_bui_Mapbiopmas_21',
            'Pe_bui_Mapbiopmas_22',
        ),
        'purp_scores': {
            'accu_input': 'high',
            'sustained_input': 'high',
            'well_docmted_input': 'high',
            'user_friendly_input': 'high',
            'offi': 'med',
            'comparable': 'high',
            'source': 'MapBiomas',
            'finer':
                {
                    'scale': None,
                    'res': 30,
                    'unit': 'm',
                },
        },
        'years_datasets': list(range(1985, 2022 + 1)),
    },

    'Pe_luc_Mapbiopmas': {
        'datasets': (
            # 'Pe_luc_Mapbiopmas_00',
            # 'Pe_luc_Mapbiopmas_10',
            'Pe_luc_Mapbiopmas_12',
            'Pe_luc_Mapbiopmas_13',
            'Pe_luc_Mapbiopmas_14',
            'Pe_luc_Mapbiopmas_15',
            'Pe_luc_Mapbiopmas_16',
            'Pe_luc_Mapbiopmas_17',
            'Pe_luc_Mapbiopmas_18',
            'Pe_luc_Mapbiopmas_19',
            'Pe_luc_Mapbiopmas_20',
            'Pe_luc_Mapbiopmas_21',
            'Pe_luc_Mapbiopmas_22',
        ),
        'purp_scores': {
            'accu_input': 'high',
            'sustained_input': 'high',
            'well_docmted_input': 'high',
            'user_friendly_input': 'high',
            'offi': 'med',
            'comparable': 'high',
            'source': 'MapBiomas',
            'finer':
                {
                    'scale': None,
                    'res': 30,
                    'unit': 'm',
                },
        },
        'years_datasets': list(range(1985, 2022 + 1)),
    },

    'Pe_mining_Mapbiopmas': {
        # 'datasets': (f'Pe_mining_Mapbiopmas_{i}' for i in range(12, 23)),
        'datasets': (
            # 'Pe_mining_Mapbiopmas_00',
            # 'Pe_mining_Mapbiopmas_10',
            'Pe_mining_Mapbiopmas_12',
            'Pe_mining_Mapbiopmas_13',
            'Pe_mining_Mapbiopmas_14',
            'Pe_mining_Mapbiopmas_15',
            'Pe_mining_Mapbiopmas_16',
            'Pe_mining_Mapbiopmas_17',
            'Pe_mining_Mapbiopmas_18',
            'Pe_mining_Mapbiopmas_19',
            'Pe_mining_Mapbiopmas_20',
            'Pe_mining_Mapbiopmas_21',
            'Pe_mining_Mapbiopmas_22',
        ),
        'purp_scores': {
            'accu_input': 'high',
            'sustained_input': 'high',
            'well_docmted_input': 'high',
            'user_friendly_input': 'high',
            'offi': 'med',
            'comparable': 'high',
            'source': 'MapBiomas',
            'finer':
                {
                    'scale': None,
                    'res': 30,
                    'unit': 'm',
                },
        },
        'years_datasets': list(range(1985, 2022 + 1)),
    },

}


layers_settings = {  # Multitemporal, official, current

    # VIIRS NTL
    'ntl_VIIRS_12': {'path': [
        "No_Oficial/NTL/VIIRS_v21/201204-201303_PEC.tif",
    ],
        'scoring': 'ntl_VIIRS_scores',
        'year': 2012,
        'units': 'Digital number',
    },

    'ntl_VIIRS_13': {'path': [
        "No_Oficial/NTL/VIIRS_v21/2013_PEC.tif",
    ],
        'scoring': 'ntl_VIIRS_scores',
        'year': 2013,
        'units': 'Digital number',
    },

    'ntl_VIIRS_14': {'path': [
        "No_Oficial/NTL/VIIRS_v21/2014_PEC.tif",
    ],
        'scoring': 'ntl_VIIRS_scores',
        # 'scoring': 'pop_VIIRS_scores',
        'year': 2014,
        'units': 'Digital number',
        # 'offi': 'low',
        # 'comparable': 'high',
    },

    'ntl_VIIRS_15': {'path': [
        "No_Oficial/NTL/VIIRS_v21/2015_PEC.tif",
    ],
        'scoring': 'ntl_VIIRS_scores',
        # 'scoring': 'pop_VIIRS_scores',
        'year': 2015,
        'units': 'Digital number',
        # 'offi': 'low',
        # 'comparable': 'high',
    },

    'ntl_VIIRS_16': {'path': [
        "No_Oficial/NTL/VIIRS_v21/2016_PEC.tif",
    ],
        'scoring': 'ntl_VIIRS_scores',
        # 'scoring': 'pop_VIIRS_scores',
        'year': 2016,
        'units': 'Digital number',
        # 'offi': 'low',
        # 'comparable': 'high',
    },

    'ntl_VIIRS_17': {'path': [
        "No_Oficial/NTL/VIIRS_v21/2017_PEC.tif",
    ],
        'scoring': 'ntl_VIIRS_scores',
        # 'scoring': 'pop_VIIRS_scores',
        'year': 2017,
        'units': 'Digital number',
        # 'offi': 'low',
        # 'comparable': 'high',
    },

    'ntl_VIIRS_18': {'path': [
        "No_Oficial/NTL/VIIRS_v21/2018_PEC.tif",
    ],
        'scoring': 'ntl_VIIRS_scores',
        # 'scoring': 'pop_VIIRS_scores',
        'year': 2018,
        'units': 'Digital number',
        # 'offi': 'low',
        # 'comparable': 'high',
    },

    'ntl_VIIRS_19': {'path': [
        "No_Oficial/NTL/VIIRS_v21/2019_PEC.tif",
    ],
        'scoring': 'ntl_VIIRS_scores',
        # 'scoring': 'pop_VIIRS_scores',
        'year': 2019,
        'units': 'Digital number',
        # 'offi': 'low',
        # 'comparable': 'high',
    },

    'ntl_VIIRS_20': {'path': [
        "No_Oficial/NTL/VIIRS_v21/2020_PEC.tif",
    ],
        'scoring': 'ntl_VIIRS_scores',
        # 'scoring': 'pop_VIIRS_scores',
        'year': 2020,
        'units': 'Digital number',
        # 'offi': 'low',
        # 'comparable': 'high',
    },

    'ntl_VIIRS_21': {'path': [
        "No_Oficial/NTL/VIIRS_v21/2021_PEC.tif",
    ],
        'scoring': 'ntl_VIIRS_scores',
        # 'scoring': 'pop_VIIRS_scores',
        'year': 2021,
        'units': 'Digital number',
        # 'offi': 'low',
        # 'comparable': 'high',
    },

    'ntl_VIIRS_22': {'path': [
        "No_Oficial/NTL/VIIRS_v22/2022_PEC.tif",
    ],
        'scoring': 'ntl_VIIRS_scores',
        'year': 2022,
        'units': 'Digital number',
    },

    # Official Ecuador
    'bui_Ec_poblados_IGM_10': {
        'path': ['Oficial/IGM/poblado_p.shp'],
        'scoring': 'settlement_scores',
        'year': 2010,
        'units': 'meters',
        'accu_input': 'high',
        'sustained_input': 'med',
        'well_docmted_input': 'high',
        'user_friendly_input': 'high',
        'offi': 'high',
        'comparable': 'low',
        'source': 'IGM_10',
        'finer':
            {
                'scale': 50000,
                'res': None,
                'unit': None,
            },
        },

    'bui_Ec_pistas_IGM_10': {
        'path': ['Oficial/IGM/pista_aterrizaje_l.shp'],
        'scoring': 'road_scores_l1',
        'year': 2010,
        'units': 'meters',
        'accu_input': 'high',
        'sustained_input': 'med',
        'well_docmted_input': 'high',
        'user_friendly_input': 'high',
        'offi': 'high',
        'comparable': 'low',
        'source': 'IGM_10',
        'finer':
            {
                'scale': 50000,
                'res': None,
                'unit': None,
            },
        },


        # Official Peru
    'bui_Pe_a_urbana_MINAM_11': {
        'path': ['Oficial/MINAM/Geoservidor/Cobertura_Vegetal/mapa_cobertura_vegetal_2015/Area_urbana.shp'],
        'scoring': 'urban_scores',
        'year': 2011,
        'units': 'meters',
        'accu_input': 'null',
        'sustained_input': 'high',
        'well_docmted_input': 'null',
        'user_friendly_input': 'high',
        'offi': 'high',
        'comparable': 'low',
        'source': 'MINAM_11',
        'finer':
            {
                'scale': 100000,
                'res': None,
                'unit': None,
            },
        },
    'bui_Pe_poblados_MINAM_11': {
        'path': [
        "Oficial/MINAM/Geoservidor/Vulnerabilidad_Fisica/vulnerabilidad_fisica/vulne_fisica/e_expuesto/ccpp.shp"],
        'scoring': 'settlement_scores',
        'year': 2011,
        'units': 'meters',
        'accu_input': 'null',
        'sustained_input': 'high',
        'well_docmted_input': 'null',
        'user_friendly_input': 'high',
        'offi': 'high',
        'comparable': 'low',
        'source': 'MINAM_11',
        'finer':
            {
                'scale': 100000,
                'res': None,
                'unit': None,
            },
        },

    'bui_Pe_pob_indig_MinCul_20': {
        'path': ['Oficial/DGOTA/CentroPobladoIndigena.gpkg'],
        'scoring': 'settlement_scores',
        'year': 2020,
        'units': 'meters',
        'accu_input': 'null',
        'sustained_input': 'low',
        'well_docmted_input': 'high',
        'user_friendly_input': 'med',
        'offi': 'high',
        'comparable': 'low',
        'source': 'MinCul_20',
        'finer':
            {
                'scale': None,
                'res': None,
                'unit': None,
            },
        },

    # 'Pe_botaderos_OEFAnooficial_18': {
    #     'path': ['Oficial/OEFA/Rellenos sanitarios y botaderos.gpkg'],
    #     'scoring': 'Part_imp_poll_05',
    #     'year': 2018,
    #     'units': 'meters',
    #     'accu_input': 'null',
    #     'sustained_input': 'low',
    #     'well_docmted_input': 'null',
    #     'user_friendly_input': 'low',
    #     'offi': 'high',
    #     # 'offi': 'med',
    #     'comparable': 'low',
    #     'source': 'OEFA_18',
    #     'finer':
    #         {
    #             'scale': None,
    #             'res': None,
    #             'unit': None,
    #         },
    #     },

#     #  ## Population

    # Official Ecuador
    'Ec_pob_INEC_10': {
        # 'path': ['Oficial/INEC/INEC2010_Density_250.tif'],
        'path': ['Oficial/INEC/INEC2010_Density_90.tif'],
        # 'path': ['Oficial/INEC/INEC2010_Density_30.tif'],
        'scoring': 'pop_scores_INEC_INEI',
        'year': 2010,
        'units': 'hab/km2',
        'accu_input': 'null',
        'sustained_input': 'high',
        'well_docmted_input': 'med',
        'user_friendly_input': 'med',
        'offi': 'high',
        'comparable': 'low',
        'source': 'INEC_10',
        'finer':
            {
                'scale': None,  # The scale of 1:50000 assigned to the GBD is not appplicable for purpose scoring
                'res': None,
                'unit': None,
            },
    },

    #  # Official Peru
    # Official Ecuador
    'Pe_pob_INEI_17': {
        'path': ['Oficial/INEI/Peru_PopD_scores_2017.tif'],
        'scoring': 'pop_scores_INEC_INEI',
        'year': 2017,
        'units': 'hab/km2',
        'accu_input': 'null',
        'sustained_input': 'low',
        'well_docmted_input': 'null',
        'user_friendly_input': 'low',
        'offi': 'high',
        'comparable': 'low',
        'source': 'INEI_17',
        'finer':
            {
                'scale': None,
                'res': None,
                'unit': None,
            },
    },


    # Best

    'Ec_Meta_Pob_20':{
        'path': ["No_Oficial/Population/Facebook/ecu_general_2020.tif"],
        'scoring': 'built_Meta_scores',
        # 'threshold_divide': {
        #     'l1':(10000,1000000), #  dummy upper value
        #     'l2':(5000,10000),
        #     'l3':(0.01,5000),
            # },
        'year': 2020,
        # 'check_intersection': True,
        'units': 'hab/pixel',
        'accu_input': 'high',
        'sustained_input': 'high',
        'well_docmted_input': 'high',
        'user_friendly_input': 'high',
        'offi': 'low',
        'comparable': 'high',
        'source': 'Meta_20',
        'finer':
            {
                'scale': None,
                'res': 30,
                'unit': 'm',
            },
        },


    'Pe_Meta_Pob_20':{
        'path': ["No_Oficial/Population/Facebook/per_general_2020.tif"],
        'scoring': 'built_Meta_scores',
        'year': 2020,
        'units': 'hab/pixel',
        'accu_input': 'high',
        'sustained_input': 'high',
        'well_docmted_input': 'high',
        'user_friendly_input': 'high',
        'offi': 'low',
        'comparable': 'high',
        'source': 'Meta_20',
        'finer':
            {
                'scale': None,
                'res': 30,
                'unit': 'm',
            },
        },


    'Ec_World_pop_10':{
        'path': ["No_Oficial/Population/Worldpop/ecu_ppp_2010.tif"],
        'scoring': 'worldpop_scores',
        'year': 2010,
        'units': 'hab/pixel',
        'accu_input': 'high',
        'sustained_input': 'high',
        'well_docmted_input': 'high',
        'user_friendly_input': 'high',
        'offi': 'low',
        'comparable': 'high',
        'source': 'Worldpop',
        'finer':
            {
                'scale': None,
                'res': 100,
                'unit': 'm',
            },
        },


    'Pe_World_pop_17':{
        'path': ["No_Oficial/Population/Worldpop/per_ppp_2017.tif"],
        'scoring': 'worldpop_scores',
        'year': 2017,
        'units': 'hab/pixel',
        'accu_input': 'high',
        'sustained_input': 'high',
        'well_docmted_input': 'high',
        'user_friendly_input': 'high',
        'offi': 'low',
        'comparable': 'high',
        'source': 'Worldpop',
        'finer':
            {
                'scale': None,
                'res': 100,
                'unit': 'm',
            },
        },

    'Pe_World_pop_07':{
        'path': ["No_Oficial/Population/Worldpop/per_ppp_2007.tif"],
        'scoring': 'worldpop_scores',
        'year': 2007,
        'units': 'hab/pixel',
        'accu_input': 'high',
        'sustained_input': 'high',
        'well_docmted_input': 'high',
        'user_friendly_input': 'high',
        'offi': 'low',
        'comparable': 'high',
        'source': 'Worldpop',
        'finer':
            {
                'scale': None,
                'res': 100,
                'unit': 'm',
            },
        },

    ## Land use

    # Multitemporal / Official Ecuador
    'Ec_cut_MAAE_90': {
        'path': ['Oficial/MAAE/v_ff010_cobertura_vegetal_1990_aPolygon.shp'],
        'scoring': 'luc_MAAE_scores',
        'cat_field': 'cobertura_',
        'year': 1990,
          'units': 'categorical',
          # 'offi': 'high',
          # 'comparable': 'low',
          },
    'Ec_cut_MAAE_00': {
        'path': ['Oficial/MAAE/v_ff010_cobertura_vegetal_2000_aPolygon.shp'],
        'scoring': 'luc_MAAE_scores',
        'cat_field': 'cobertura1',
        'year': 2000,
          'units': 'categorical',
          # 'offi': 'high',
          # 'comparable': 'low',
          },
    'Ec_cut_MAAE_08': {
        'path': ['Oficial/MAAE/v_ff010_cobertura_vegetal_2008_aPolygon.shp'],
        'scoring': 'luc_MAAE_scores',
        'cat_field': 'cobertura_',
        'year': 2008,
          'units': 'categorical',
          # 'offi': 'high',
          # 'comparable': 'low',
              },
    'Ec_cut_MAAE_14': {
        'path': ['Oficial/MAAE/v_ff010_cobertura_vegetal_2014_aPolygon.shp'],
        'scoring': 'luc_MAAE_scores',
        'cat_field': 'cobertura_',
        'year': 2014,
        'units': 'categorical',
        # 'offi': 'high',
        # 'comparable': 'low',
        },
    'Ec_cut_MAAE_16': {
        'path': ['Oficial/MAAE/v_ff010_cobertura_vegetal_2016_aPolygon.shp'],
        'scoring': 'luc_MAAE_scores',
        'cat_field': 'cobertura_',
        'year': 2016,
        'units': 'categorical',
        # 'offi': 'high',
        # 'comparable': 'low',
        },
    'Ec_cut_MAAE_18': {
        'path': ['Oficial/MAAE/v_ff010_cobertura_vegetal_2018_aPolygon.shp'],
        'scoring': 'luc_MAAE_scores',
        'cat_field': 'cobertura0',  # This one is different
        'year': 2018,
        'units': 'categorical',
        # 'offi': 'high',
        # 'comparable': 'low',
        },
    'Ec_cut_MAAE_20': {
        'path': ['Oficial/MAAE/v_ff010_cobertura_vegetal_2020_aPolygon.shp'],
        'scoring': 'luc_MAAE_scores',
        'cat_field': 'ctn2',  # This one is different
        'year': 2020,
        'units': 'categorical',
        # 'offi': 'high',
        # 'comparable': 'low',
        },
    'Ec_cut_MAAE_22': {
        'path': ['Oficial/MAAE/v_ff010_cobertura_vegetal_2022_aPolygon.shp'],
        'scoring': 'luc_MAAE_scores',
        'cat_field': 'ctn2',  # This one is different
        'year': 2022,
        'units': 'categorical',
        # 'offi': 'high',
        # 'comparable': 'low',
        },

    # Multitemporal / Official Ecuador
    'Ec_bui_MAAE_90': {
        'path': ['Oficial/MAAE/v_ff010_cobertura_vegetal_1990_aPolygon.shp'],
        'scoring': 'bui_MAAE_scores',
        'cat_field': 'cobertura_',
        'year': 1990,
        'units': 'categorical',
                        },
    'Ec_bui_MAAE_00': {
        'path': ['Oficial/MAAE/v_ff010_cobertura_vegetal_2000_aPolygon.shp'],
        'scoring': 'bui_MAAE_scores',
        'cat_field': 'cobertura1',
        'year': 2000,
        'units': 'categorical',
              },
    'Ec_bui_MAAE_08': {
        'path': ['Oficial/MAAE/v_ff010_cobertura_vegetal_2008_aPolygon.shp'],
        'scoring': 'bui_MAAE_scores',
        'cat_field': 'cobertura_',
        'year': 2008,
        'units': 'categorical',
          },
    'Ec_bui_MAAE_14': {
        'path': ['Oficial/MAAE/v_ff010_cobertura_vegetal_2014_aPolygon.shp'],
        'scoring': 'bui_MAAE_scores',
        'cat_field': 'cobertura_',
        'year': 2014,
        'units': 'categorical',
        # 'offi': 'high',
        # 'comparable': 'low',
        },
    'Ec_bui_MAAE_16': {
        'path': ['Oficial/MAAE/v_ff010_cobertura_vegetal_2016_aPolygon.shp'],
        'scoring': 'bui_MAAE_scores',
        'cat_field': 'cobertura_',
        'year': 2016,
        'units': 'categorical',
        # 'offi': 'high',
        # 'comparable': 'low',
        },
    'Ec_bui_MAAE_18': {
        'path': ['Oficial/MAAE/v_ff010_cobertura_vegetal_2018_aPolygon.shp'],
        'scoring': 'bui_MAAE_scores',
        'cat_field': 'cobertura0',  # This one is different
        'year': 2018,
        'units': 'categorical',
        # 'offi': 'high',
        # 'comparable': 'low',
        },
    'Ec_bui_MAAE_20': {
        'path': ['Oficial/MAAE/v_ff010_cobertura_vegetal_2020_aPolygon.shp'],
        'scoring': 'bui_MAAE_scores',
        'cat_field': 'ctn2',  # This one is different
        'year': 2020,
        'units': 'categorical',
        # 'offi': 'high',
        # 'comparable': 'low',
                        },
    'Ec_bui_MAAE_22': {
        'path': ['Oficial/MAAE/v_ff010_cobertura_vegetal_2022_aPolygon.shp'],
        'scoring': 'bui_MAAE_scores',
        'cat_field': 'ctn2',  # This one is different
        'year': 2022,
        'units': 'categorical',
        # 'offi': 'high',
        # 'comparable': 'low',
        },

    'Pe_Censo_Agr_MIDAGRI_18': {
        'path': ['Oficial/MIDAGRI/Cobertura_Agricola/Peru_cober_Aagri_Dist_geowgs84.gpkg'],
        'scoring': 'agr_MINAGRI_scores',
        # 'cat_field': 'CobVeg2013',
        'year': 2018,
        'units': 'categorical',
        'accu_input': 'null',
        'sustained_input': 'high',
        'well_docmted_input': 'high',
        'user_friendly_input': 'high',
        'offi': 'high',
        'comparable': 'low',
        'source': 'MIDAGRI_18',
        'finer':
            {
                'scale': 10000,
                'res': None,
                'unit': None,
            },
        },


    #Bui Mapbiomas
    "Pe_bui_Mapbiopmas_12": {
        'path': ["No_Oficial/Land_use/Mapbiomas/peru_coverage_2012.tif"],
        'scoring': 'bui_Mapbiopmas_scores',
        'year': 2012,
        'units': 'categorical',
        # 'offi': 'med',
        # 'comparable': 'high',
        },

    "Pe_bui_Mapbiopmas_13": {
        'path': ["No_Oficial/Land_use/Mapbiomas/peru_coverage_2013.tif"],
        'scoring': 'bui_Mapbiopmas_scores',
        'year': 2013,
        'units': 'categorical',
        # 'offi': 'med',
        # 'comparable': 'high',
        },

    "Pe_bui_Mapbiopmas_14": {
        'path': ["No_Oficial/Land_use/Mapbiomas/peru_coverage_2014.tif"],
        'scoring': 'bui_Mapbiopmas_scores',
        'year': 2014,
        'units': 'categorical',
        # 'offi': 'med',
        # 'comparable': 'high',
        },

    "Pe_bui_Mapbiopmas_15": {
        'path': ["No_Oficial/Land_use/Mapbiomas/peru_coverage_2015.tif"],
        'scoring': 'bui_Mapbiopmas_scores',
        'year': 2015,
        'units': 'categorical',
        # 'offi': 'med',
        # 'comparable': 'high',
        },

    "Pe_bui_Mapbiopmas_16": {
        'path': ["No_Oficial/Land_use/Mapbiomas/peru_coverage_2016.tif"],
        'scoring': 'bui_Mapbiopmas_scores',
        'year': 2016,
        'units': 'categorical',
        # 'offi': 'med',
        # 'comparable': 'high',
        },

    "Pe_bui_Mapbiopmas_17": {
        'path': ["No_Oficial/Land_use/Mapbiomas/peru_coverage_2017.tif"],
        'scoring': 'bui_Mapbiopmas_scores',
        'year': 2017,
        'units': 'categorical',
        # 'offi': 'med',
        # 'comparable': 'high',
        },

    "Pe_bui_Mapbiopmas_18": {
        'path': ["No_Oficial/Land_use/Mapbiomas/peru_coverage_2018.tif"],
        'scoring': 'bui_Mapbiopmas_scores',
        'year': 2018,
        'units': 'categorical',
        # 'offi': 'med',
        # 'comparable': 'high',
        },

    "Pe_bui_Mapbiopmas_19": {
        'path': ["No_Oficial/Land_use/Mapbiomas/peru_coverage_2019.tif"],
        'scoring': 'bui_Mapbiopmas_scores',
        'year': 2019,
        'units': 'categorical',
        # 'offi': 'med',
        # 'comparable': 'high',
        },

    "Pe_bui_Mapbiopmas_20": {
        'path': ["No_Oficial/Land_use/Mapbiomas/peru_coverage_2020.tif"],
        'scoring': 'bui_Mapbiopmas_scores',
        'year': 2020,
        'units': 'categorical',
        # 'offi': 'med',
        # 'comparable': 'high',
        },

    "Pe_bui_Mapbiopmas_21": {
        'path': ["No_Oficial/Land_use/Mapbiomas/peru_coverage_2021.tif"],
        'scoring': 'bui_Mapbiopmas_scores',
        'year': 2021,
        'units': 'categorical',
        # 'offi': 'med',
        # 'comparable': 'high',
        },
    
    "Pe_bui_Mapbiopmas_22": {
        'path': ["No_Oficial/Land_use/Mapbiomas/peru_coverage_2022.tif"],
        'scoring': 'bui_Mapbiopmas_scores',
        'year': 2022,
        'units': 'categorical',
        # 'offi': 'med',
        # 'comparable': 'high',
        },


    #LUC Mapbiomas
    "Pe_luc_Mapbiopmas_12": {
        'path': ["No_Oficial/Land_use/Mapbiomas/peru_coverage_2012.tif"],
        'scoring': 'luc_Mapbiopmas_scores',
        'year': 2012,
        'units': 'categorical',
        # 'offi': 'med',
        # 'comparable': 'high',
        },

    "Pe_luc_Mapbiopmas_13": {
        'path': ["No_Oficial/Land_use/Mapbiomas/peru_coverage_2013.tif"],
        'scoring': 'luc_Mapbiopmas_scores',
        'year': 2013,
        'units': 'categorical',
        # 'offi': 'med',
        # 'comparable': 'high',
        },

    "Pe_luc_Mapbiopmas_14": {
        'path': ["No_Oficial/Land_use/Mapbiomas/peru_coverage_2014.tif"],
        'scoring': 'luc_Mapbiopmas_scores',
        'year': 2014,
        'units': 'categorical',
        # 'offi': 'med',
        # 'comparable': 'high',
        },

    "Pe_luc_Mapbiopmas_15": {
        'path': ["No_Oficial/Land_use/Mapbiomas/peru_coverage_2015.tif"],
        'scoring': 'luc_Mapbiopmas_scores',
        'year': 2015,
        'units': 'categorical',
        # 'offi': 'med',
        # 'comparable': 'high',
        },

    "Pe_luc_Mapbiopmas_16": {
        'path': ["No_Oficial/Land_use/Mapbiomas/peru_coverage_2016.tif"],
        'scoring': 'luc_Mapbiopmas_scores',
        'year': 2016,
        'units': 'categorical',
        # 'offi': 'med',
        # 'comparable': 'high',
        },

    "Pe_luc_Mapbiopmas_17": {
        'path': ["No_Oficial/Land_use/Mapbiomas/peru_coverage_2017.tif"],
        'scoring': 'luc_Mapbiopmas_scores',
        'year': 2017,
        'units': 'categorical',
        # 'offi': 'med',
        # 'comparable': 'high',
        },

    "Pe_luc_Mapbiopmas_18": {
        'path': ["No_Oficial/Land_use/Mapbiomas/peru_coverage_2018.tif"],
        'scoring': 'luc_Mapbiopmas_scores',
        'year': 2018,
        'units': 'categorical',
        # 'offi': 'med',
        # 'comparable': 'high',
        },

    "Pe_luc_Mapbiopmas_19": {
        'path': ["No_Oficial/Land_use/Mapbiomas/peru_coverage_2019.tif"],
        'scoring': 'luc_Mapbiopmas_scores',
        'year': 2019,
        'units': 'categorical',
        # 'offi': 'med',
        # 'comparable': 'high',
        },

    "Pe_luc_Mapbiopmas_20": {
        'path': ["No_Oficial/Land_use/Mapbiomas/peru_coverage_2020.tif"],
        'scoring': 'luc_Mapbiopmas_scores',
        'year': 2020,
        'units': 'categorical',
        # 'offi': 'med',
        # 'comparable': 'high',
        },

    "Pe_luc_Mapbiopmas_21": {
        'path': ["No_Oficial/Land_use/Mapbiomas/peru_coverage_2021.tif"],
        'scoring': 'luc_Mapbiopmas_scores',
        'year': 2021,
        'units': 'categorical',
        # 'offi': 'med',
        # 'comparable': 'high',
        },

    "Pe_luc_Mapbiopmas_22": {
        'path': ["No_Oficial/Land_use/Mapbiomas/peru_coverage_2022.tif"],
        'scoring': 'luc_Mapbiopmas_scores',
        'year': 2022,
        'units': 'categorical',
        # 'offi': 'med',
        # 'comparable': 'high',
        },


    # Mining Mapbiomas
    "Pe_mining_Mapbiopmas_12": {'path': ["No_Oficial/Land_use/Mapbiomas/peru_coverage_2012.tif"],
                  'scoring': 'mining_Mapbiopmas_scores',
                  'year': 2012,
                  'units': 'categorical',
                  # 'offi': 'med',
                  # 'comparable': 'high',
                  },

    "Pe_mining_Mapbiopmas_13": {'path': ["No_Oficial/Land_use/Mapbiomas/peru_coverage_2013.tif"],
                  'scoring': 'mining_Mapbiopmas_scores',
                  'year': 2013,
                  'units': 'categorical',
                  # 'offi': 'med',
                  # 'comparable': 'high',
                  },

    "Pe_mining_Mapbiopmas_14": {'path': ["No_Oficial/Land_use/Mapbiomas/peru_coverage_2014.tif"],
                  'scoring': 'mining_Mapbiopmas_scores',
                  'year': 2014,
                  'units': 'categorical',
                  # 'offi': 'med',
                  # 'comparable': 'high',
                  },

    "Pe_mining_Mapbiopmas_15": {'path': ["No_Oficial/Land_use/Mapbiomas/peru_coverage_2015.tif"],
                  'scoring': 'mining_Mapbiopmas_scores',
                  'year': 2015,
                  'units': 'categorical',
                  # 'offi': 'med',
                  # 'comparable': 'high',
                  },

    "Pe_mining_Mapbiopmas_16": {'path': ["No_Oficial/Land_use/Mapbiomas/peru_coverage_2016.tif"],
                  'scoring': 'mining_Mapbiopmas_scores',
                  'year': 2016,
                  'units': 'categorical',
                  # 'offi': 'med',
                  # 'comparable': 'high',
                  },

    "Pe_mining_Mapbiopmas_17": {'path': ["No_Oficial/Land_use/Mapbiomas/peru_coverage_2017.tif"],
                  'scoring': 'mining_Mapbiopmas_scores',
                  'year': 2017,
                  'units': 'categorical',
                  # 'offi': 'med',
                  # 'comparable': 'high',
                  },

    "Pe_mining_Mapbiopmas_18": {'path': ["No_Oficial/Land_use/Mapbiomas/peru_coverage_2018.tif"],
                  'scoring': 'mining_Mapbiopmas_scores',
                  'year': 2018,
                  'units': 'categorical',
                  # 'offi': 'med',
                  # 'comparable': 'high',
                  },

    "Pe_mining_Mapbiopmas_19": {'path': ["No_Oficial/Land_use/Mapbiomas/peru_coverage_2019.tif"],
                  'scoring': 'mining_Mapbiopmas_scores',
                  'year': 2019,
                  'units': 'categorical',
                  # 'offi': 'med',
                  # 'comparable': 'high',
                  },

    "Pe_mining_Mapbiopmas_20": {'path': ["No_Oficial/Land_use/Mapbiomas/peru_coverage_2020.tif"],
                  'scoring': 'mining_Mapbiopmas_scores',
                  'year': 2020,
                  'units': 'categorical',
                  # 'offi': 'med',
                  # 'comparable': 'high',
                  },

    "Pe_mining_Mapbiopmas_21": {'path': ["No_Oficial/Land_use/Mapbiomas/peru_coverage_2021.tif"],
                  'scoring': 'mining_Mapbiopmas_scores',
                  'year': 2021,
                  'units': 'categorical',
                  # 'offi': 'med',
                  # 'comparable': 'high',
                  },

    "Pe_mining_Mapbiopmas_22": {'path': ["No_Oficial/Land_use/Mapbiomas/peru_coverage_2022.tif"],
                  'scoring': 'mining_Mapbiopmas_scores',
                  'year': 2022,
                  'units': 'categorical',
                  # 'offi': 'med',
                  # 'comparable': 'high',
                  },

    # Multitemporal

    # Official Ecuador
    'Ec_vias_primarias_IGM_10': {
        'path': ["Oficial/IGM/via_l_primaria.shp"],
        'scoring': 'road_scores_l1',
        'year': 2010,
        'units': 'meters',
        'accu_input': 'high',
        'sustained_input': 'med',
        'well_docmted_input': 'high',
        'user_friendly_input': 'high',
        'offi': 'high',
        'comparable': 'low',
        'source': 'IGM_10',
        'finer':
            {
                'scale': 50000,
                'res': None,
                'unit': None,
            },
        },
        
    'Ec_vias_secundarias_IGM_10': {
        'path': ["Oficial/IGM/via_l_secundaria.shp"],
        'scoring': 'road_scores_l2',
        'year': 2010,
        'units': 'meters',
        'accu_input': 'high',
        'sustained_input': 'med',
        'well_docmted_input': 'high',
        'user_friendly_input': 'high',
        'offi': 'high',
        'comparable': 'low',
        'source': 'IGM_10',
        'finer':
            {
                'scale': 50000,
                'res': None,
                'unit': None,
            },
        },
        
    'Ec_vias_vecinales_IGM_10': {
        'path': ["Oficial/IGM/via_l_rural.shp"],
        'scoring': 'road_scores_l3',
        'year': 2010,
        'units': 'meters',
        'accu_input': 'high',
        'sustained_input': 'med',
        'well_docmted_input': 'high',
        'user_friendly_input': 'high',
        'offi': 'high',
        'comparable': 'low',
        'source': 'IGM_10',
        'finer':
            {
                'scale': 50000,
                'res': None,
                'unit': None,
            },
        },

    'Ec_lin_ferreas_IGM_10': {
        'path': ["Oficial/IGM/linea_tren_l.shp"],
        'scoring': 'road_scores_l1',
        'year': 2010,
        'units': 'meters',
        'accu_input': 'high',
        'sustained_input': 'med',
        'well_docmted_input': 'high',
        'user_friendly_input': 'high',
        'offi': 'high',
        'comparable': 'low',
        'source': 'IGM_10',
        'finer':
            {
                'scale': 50000,
                'res': None,
                'unit': None,
            },
        },

    'Ec_indirect': {
        'path': ["No_Oficial/Ec_water.gpkg"],
        'scoring': 'indirect_scores',
        'year': 0, #  Dummy value
        'units': 'meters',
        'accu_input': 'high',
        'sustained_input': 'low',
        'well_docmted_input': 'high',
        'user_friendly_input': 'high',
        'offi': 'low',
        'comparable': 'high',
        'source': 'derived',
        'finer':
            {
                'scale': None,
                'res': None,
                'unit': None,
            },
        },

      # Official Peru
    'Pe_vias_nacional_MTC_19': {
        'path': ['Oficial/MTC/red_vial_nacional_dic19/red_vial_nacional_dic19.shp'],
        'scoring': 'road_scores_l1',
        'year': 2019,
        'units': 'meters',
        'accu_input': 'null',
        'sustained_input': 'high',
        'well_docmted_input': 'med',
        'user_friendly_input': 'high',
        'offi': 'high',
        'comparable': 'low',
        'source': 'MTC',
        'finer':
            {
                'scale': 100000,
                'res': None,
                'unit': None,
            },
        },
        
    'Pe_vias_deprtmtal_MTC_19': {
        'path': ['Oficial/MTC/red_vial_departamental_dic19/red_vial_departamental_dic19.shp'],
        'scoring': 'road_scores_l2',
        'year': 2019,
        'units': 'meters',
        'accu_input': 'null',
        'sustained_input': 'high',
        'well_docmted_input': 'med',
        'user_friendly_input': 'high',
        'offi': 'high',
        'comparable': 'low',
        'source': 'MTC',
        'finer':
            {
                'scale': 100000,
                'res': None,
                'unit': None,
            },
        },
        
    'Pe_vias_vecinal_MTC_19': {
        'path': ['Oficial/MTC/red_vial_vecinal_dic19/red_vial_vecinal_dic19.shp'],
        'scoring': 'road_scores_l3',
        'year': 2019,
        'units': 'meters',
        'accu_input': 'null',
        'sustained_input': 'high',
        'well_docmted_input': 'med',
        'user_friendly_input': 'high',
        'offi': 'high',
        'comparable': 'low',
        'source': 'MTC',
        'finer':
            {
                'scale': 100000,
                'res': None,
                'unit': None,
            },
        },
        
    'Pe_lin_ferreas_MTC_18': {
        'path': ['Oficial/MTC/linea_ferrea_dic18/linea_ferrea_dic18.gpkg'],
        'scoring': 'road_scores_l1',
        'year': 2018,
        'units': 'meters',
        'accu_input': 'null',
        'sustained_input': 'high',
        'well_docmted_input': 'med',
        'user_friendly_input': 'high',
        'offi': 'high',
        'comparable': 'low',
        'source': 'MTC',
        'finer':
            {
                'scale': 100000,
                'res': None,
                'unit': None,
            },
        },
        
    'Pe_puertos_MINAM_11': {
        'path': [
        'Oficial/MINAM/Geoservidor/Vulnerabilidad_Fisica/vulnerabilidad_fisica/vulne_fisica/e_expuesto/Puertos.shp'],
        'scoring': 'settlement_scores',
        'year': 2011,
        'units': 'meters',
        'accu_input': 'null',
        'sustained_input': 'high',
        'well_docmted_input': 'null',
        'user_friendly_input': 'high',
        'offi': 'high',
        'comparable': 'low',
        'source': 'MINAM_11',
        'finer':
            {
                'scale': 100000,
                'res': None,
                'unit': None,
            },
        },
    # 'Pe_rios_MINAM_15': {
    'Pe_indirect': {
        'path': ['Oficial/MINAM/Geoservidor/Cobertura_Vegetal/mapa_cobertura_vegetal_2015/Rios_CobVeg_180615.shp'],
        'scoring': 'indirect_scores',
        'year': 0, #  Dummy value
        'units': 'meters',
        'accu_input': 'null',
        'sustained_input': 'high',
        'well_docmted_input': 'high',
        'user_friendly_input': 'high',
        'offi': 'low',
        'comparable': 'high',
        'source': 'derived',
        'finer':
            {
                'scale': None,
                'res': None,
                'unit': None,
            },
    },

    #  # Best Ecuador
      'Ec_vias_primarias_OSM_21': {
          # 'path': ["No_Oficial/OSM/ecuador_vias/primaria.shp"],
          'path': ["No_Oficial/OSM/ecuador_vias/primaria.gpkg"],
          'scoring': 'road_scores_l1',
          'year': 2021,
          'units': 'meters',
          'accu_input': 'null',
          'sustained_input': 'high',
          'well_docmted_input': 'high',
          'user_friendly_input': 'med',
          'offi': 'low',
          'comparable': 'high',
          'source': 'OSM',
          'finer':
              {
                  'scale': 50000,
                  'res': None,
                  'unit': None,
                },
              },

      'Ec_vias_secundarias_OSM_21': {
          'path': ["No_Oficial/OSM/ecuador_vias/secundaria.gpkg"],
          'scoring': 'road_scores_l2',
          'year': 2021,
          'units': 'meters',
          'accu_input': 'null',
          'sustained_input': 'high',
          'well_docmted_input': 'high',
          'user_friendly_input': 'med',
          'offi': 'low',
          'comparable': 'high',
          'source': 'OSM',
          'finer':
              {
                  'scale': 50000,
                  'res': None,
                  'unit': None,
                  },
              },

      'Ec_vias_vecinales_OSM_21': {
          'path': ["No_Oficial/OSM/ecuador_vias/vecinal.gpkg"],
          'scoring': 'road_scores_l3',
          'year': 2021,
          'units': 'meters',
          'accu_input': 'null',
          'sustained_input': 'high',
          'well_docmted_input': 'high',
          'user_friendly_input': 'med',
          'offi': 'low',
          'comparable': 'high',
          'source': 'OSM',
          'finer':
              {
                  'scale': 50000,
                  'res': None,
                  'unit': None,
                  },
              },

      'Ec_vias_peatonales_OSM_21': {
          'path': ["No_Oficial/OSM/ecuador_vias/peatonal.gpkg"],
          'scoring': 'road_scores_l4',
          'year': 2021,
          'units': 'meters',
          'accu_input': 'null',
          'sustained_input': 'high',
          'well_docmted_input': 'high',
          'user_friendly_input': 'med',
          'offi': 'low',
          'comparable': 'high',
          'source': 'OSM',
          'finer':
              {
                  'scale': 50000,
                  'res': None,
                  'unit': None,
                  },
              },

      'Ec_lin_ferreas_OSM_21': {
          'path': ["No_Oficial/OSM/ecuador-latest-free.shp//gis_osm_railways_free_1.gpkg"],
          'scoring': 'road_scores_l1',
          'year': 2021,
          'units': 'meters',
          'accu_input': 'null',
          'sustained_input': 'high',
          'well_docmted_input': 'high',
          'user_friendly_input': 'med',
          'offi': 'low',
          'comparable': 'high',
          'source': 'OSM',
          'finer':
              {
                  'scale': 50000,
                  'res': None,
                  'unit': None,
                  },
              },
          
    # Best Peru
    'Pe_vias_primarias_OSM_21': {
        'path': ["No_Oficial/OSM/peru_vias/primaria.gpkg"],
        'scoring': 'road_scores_l1',
        'year': 2021,
        'units': 'meters',
        'accu_input': 'null',
        'sustained_input': 'high',
        'well_docmted_input': 'high',
        'user_friendly_input': 'med',
        'offi': 'low',
        'comparable': 'high',
        'source': 'OSM',
        'finer':
            {
                'scale': 50000,
                'res': None,
                'unit': None,
            },
        },
        
    'Pe_vias_secundarias_OSM_21': {
        'path': ["No_Oficial/OSM/peru_vias/secundaria.gpkg"],
        'scoring': 'road_scores_l2',
        'year': 2021,
        'units': 'meters',
        'accu_input': 'null',
        'sustained_input': 'high',
        'well_docmted_input': 'high',
        'user_friendly_input': 'med',
        'offi': 'low',
        'comparable': 'high',
        'source': 'OSM',
        'finer':
            {
                'scale': 50000,
                'res': None,
                'unit': None,
            },
        },
        
    'Pe_vias_vecinales_OSM_21': {
        'path': ["No_Oficial/OSM/peru_vias/vecinal.gpkg"],
        'scoring': 'road_scores_l3',
        'year': 2021,
        'units': 'meters',
        'accu_input': 'null',
        'sustained_input': 'high',
        'well_docmted_input': 'high',
        'user_friendly_input': 'med',
        'offi': 'low',
        'comparable': 'high',
        'source': 'OSM',
        'finer':
            {
                'scale': 50000,
                'res': None,
                'unit': None,
            },
        },
        
    'Pe_vias_peatonales_OSM_21': {
        'path': ["No_Oficial/OSM/peru_vias/peatonal.gpkg"],
        'scoring': 'road_scores_l4',
        'year': 2021,
        'units': 'meters',
        'accu_input': 'null',
        'sustained_input': 'high',
        'well_docmted_input': 'high',
        'user_friendly_input': 'med',
        'offi': 'low',
        'comparable': 'high',
        'source': 'OSM',
        'finer':
            {
                'scale': 50000,
                'res': None,
                'unit': None,
            },
        },
        
    'Pe_lin_ferreas_OSM_21': {
        'path': ["No_Oficial/OSM/peru-latest-free.shp/gis_osm_railways_free_1.gpkg"],
        'scoring': 'road_scores_l1',
        'year': 2021,
        'units': 'meters',
        'accu_input': 'null',
        'sustained_input': 'high',
        'well_docmted_input': 'high',
        'user_friendly_input': 'med',
        'offi': 'low',
        'comparable': 'high',
        'source': 'OSM',
        'finer':
            {
                'scale': 50000,
                'res': None,
                'unit': None,
            },
        },

    #  ## Infrastructure

    #  # Multitemporal

    # Official Ecuador
    # Varios shapefiles se transformaron para quitar la dimensión Z,

    'Ec_lin_transmis_ARCERNNR_19': {
        'path': ["Oficial/ARCERNNR/lineas_transmision_subtransmision_2019/lineas_transmision_subtransmision_2019.gpkg"],
        'scoring': 'line_inf_scores',
        'year': 2019,
        'units': 'meters',
        'accu_input': 'null',
        'sustained_input': 'low',
        'well_docmted_input': 'null',
        'user_friendly_input': 'low',
        'offi': 'high',
        'comparable': 'low',
        'source': 'ARCERNNR_19',
        'finer':
            {
                'scale': None,
                'res': None,
                'unit': None,
            },
        },

    'Ec_centrales_ARCERNNR_19': {
        'path': ["Oficial/ARCERNNR/centrales_2019/centrales_2019.shp"],
        'scoring': 'Inf_part_imp_15',
        'year': 2020,
        'units': 'meters',
        'accu_input': 'null',
        'sustained_input': 'low',
        'well_docmted_input': 'null',
        'user_friendly_input': 'low',
        'offi': 'high',
        'comparable': 'low',
        'source': 'ARCERNNR_19',
        'finer':
            {
                'scale': None,
                'res': None,
                'unit': None,
            },
        },

    'Ec_subestaciones_ARCERNNR_19': {
        'path': ["Oficial/ARCERNNR/subestaciones_todas_2019/subestaciones_todas_2019.shp"],
        'scoring': 'Infr_imp_scores',
        'year': 2020,
        'units': 'meters',
        'accu_input': 'null',
        'sustained_input': 'low',
        'well_docmted_input': 'null',
        'user_friendly_input': 'low',
        'offi': 'high',
        'comparable': 'low',
        'source': 'ARCERNNR_19',
        'finer':
            {
                'scale': None,
                'res': None,
                'unit': None,
            },
        },

    'Ec_power_plant_OSM_23': {
        'path': ["No_Oficial/OSM/231228_OSM_Ec_electrical/Ec_power_plant.gpkg"],
        'scoring': 'Infr_imp_scores',
        'year': 2023,
        'units': 'meters',
        'accu_input': 'null',
        'sustained_input': 'high',
        'well_docmted_input': 'high',
        'user_friendly_input': 'med',
        'offi': 'low',
        'comparable': 'high',
        'source': 'OSM',
        'finer':
            {
                'scale': 50000,
                'res': None,
                'unit': None,
            },
        },

    'Ec_dam_OSM_23': {
        'path': ["No_Oficial/OSM/231228_OSM_Ec_electrical/Ec_waterway_dam.gpkg"],
        'scoring': 'Infr_imp_scores',
        'year': 2023,
        'units': 'meters',
        'accu_input': 'null',
        'sustained_input': 'high',
        'well_docmted_input': 'high',
        'user_friendly_input': 'med',
        'offi': 'low',
        'comparable': 'high',
        'source': 'OSM',
        'finer':
            {
                'scale': 50000,
                'res': None,
                'unit': None,
            },
        },

    'Ec_substations_OSM_23': {
        'path': ["No_Oficial/OSM/231228_OSM_Ec_electrical/Ec_power_substation.gpkg"],
        'scoring': 'Infr_imp_scores',
        'year': 2023,
        'units': 'meters',
        'accu_input': 'null',
        'sustained_input': 'high',
        'well_docmted_input': 'high',
        'user_friendly_input': 'med',
        'offi': 'low',
        'comparable': 'high',
        'source': 'OSM',
        'finer':
            {
                'scale': 50000,
                'res': None,
                'unit': None,
            },
        },

    'Ec_power_line_OSM_23': {
        'path': ["No_Oficial/OSM/231228_OSM_Ec_electrical/Ec_power_line.gpkg"],
        'scoring': 'line_inf_scores',
        'year': 2023,
        'units': 'meters',
        'accu_input': 'null',
        'sustained_input': 'high',
        'well_docmted_input': 'high',
        'user_friendly_input': 'med',
        'offi': 'low',
        'comparable': 'high',
        'source': 'OSM',
        'finer':
            {
                'scale': 50000,
                'res': None,
                'unit': None,
            },
        },

    'Ec_power_tower_OSM_23': {
        'path': ["No_Oficial/OSM/231228_OSM_Ec_electrical/Ec_power_tower.gpkg"],
        'scoring': 'Infr_imp_scores',
        'year': 2023,
        'units': 'meters',
        'accu_input': 'null',
        'sustained_input': 'high',
        'well_docmted_input': 'high',
        'user_friendly_input': 'med',
        'offi': 'low',
        'comparable': 'high',
        'source': 'OSM',
        'finer':
            {
                'scale': 50000,
                'res': None,
                'unit': None,
            },
        },

    'Ec_wind_turbine_OSM_23': {
        'path': ["No_Oficial/OSM/231228_OSM_Ec_electrical/Ec_generator_source_wind.gpkg"],
        'scoring': 'Infr_imp_scores',
        'year': 2023,
        'units': 'meters',
        'accu_input': 'null',
        'sustained_input': 'high',
        'well_docmted_input': 'high',
        'user_friendly_input': 'med',
        'offi': 'low',
        'comparable': 'high',
        'source': 'OSM',
        'finer':
            {
                'scale': 50000,
                'res': None,
                'unit': None,
            },
        },

    'Ec_solar_plant_OSM_23': {
        'path': ["No_Oficial/OSM/231228_OSM_Ec_electrical/Ec_plant_source_solar.gpkg"],
        'scoring': 'Inf_part_imp_05',
        'year': 2023,
        'units': 'meters',
        'accu_input': 'null',
        'sustained_input': 'high',
        'well_docmted_input': 'high',
        'user_friendly_input': 'med',
        'offi': 'low',
        'comparable': 'high',
        'source': 'OSM',
        'finer':
            {
                'scale': 50000,
                'res': None,
                'unit': None,
            },
        },

    'Ec_depositos_MERNNR_20': {
        'path': ["Oficial/MERNNR/Infraestructura_Sector_Hidrocarburos/Deposito_GLP2.shp"],
        'scoring': 'Infr_imp_poll_scores_5',
        'year': 2020,
        'units': 'meters',
        'accu_input': 'null',
        'sustained_input': 'low',
        'well_docmted_input': 'null',
        'user_friendly_input': 'low',
        'offi': 'high',
        'comparable': 'low',
        'source': 'MERNNR_20',
        'finer':
            {
                'scale': None,
                'res': None,
                'unit': None,
            },
        },

    'Ec_refinerias_MERNNR_20': {
        'path': ["Oficial/MERNNR/Infraestructura_Sector_Hidrocarburos/Refinerias2.shp"],
        'scoring': 'Infr_imp_poll_scores_5',
        'year': 2020,
        'units': 'meters',
        'accu_input': 'null',
        'sustained_input': 'low',
        'well_docmted_input': 'null',
        'user_friendly_input': 'low',
        'offi': 'high',
        'comparable': 'low',
        'source': 'MERNNR_20',
        'finer':
            {
                'scale': None,
                'res': None,
                'unit': None,
            },
        },

    'Ec_term_depositos_MERNNR_20': {
        'path': ["Oficial/MERNNR/Infraestructura_Sector_Hidrocarburos/Terminales_Depositos2.shp"],
        'scoring': 'Infr_imp_poll_scores_15',
        'year': 2020,
        'units': 'meters',
        'accu_input': 'null',
        'sustained_input': 'low',
        'well_docmted_input': 'null',
        'user_friendly_input': 'low',
        'offi': 'high',
        'comparable': 'low',
        'source': 'MERNNR_20',
        'finer':
            {
                'scale': None,
                'res': None,
                'unit': None,
            },
        },

    'Ec_envasadoras_MERNNR_20': {
        'path': ["Oficial/MERNNR/Infraestructura_Sector_Hidrocarburos/Envasadoras_Gas2.shp"],
        'scoring': 'Infr_imp_poll_scores_15',
        'year': 2020,
        'units': 'meters',
        'accu_input': 'null',
        'sustained_input': 'low',
        'well_docmted_input': 'null',
        'user_friendly_input': 'low',
        'offi': 'high',
        'comparable': 'low',
        'source': 'MERNNR_20',
        'finer':
            {
                'scale': None,
                'res': None,
                'unit': None,
            },
        },

    'Ec_estaciones_MERNNR_20': {
        'path': ["Oficial/MERNNR/Infraestructura_Sector_Hidrocarburos/Estaciones.shp"],
        'scoring': 'Infr_imp_poll_scores_15',
        'year': 2020,
        'units': 'meters',
        'accu_input': 'null',
        'sustained_input': 'low',
        'well_docmted_input': 'null',
        'user_friendly_input': 'low',
        'offi': 'high',
        'comparable': 'low',
        'source': 'MERNNR_20',
        'finer':
            {
                'scale': None,
                'res': None,
                'unit': None,
            },
        },

    'Ec_estaciones_GO_MERNNR_20': {
        'path': ["Oficial/MERNNR/Infraestructura_Sector_Hidrocarburos/EstacionesCaptacion_GasOriente.shp"],
        'scoring': 'Infr_imp_poll_scores_15',
        'year': 2020,
        'units': 'meters',
        'accu_input': 'null',
        'sustained_input': 'low',
        'well_docmted_input': 'null',
        'user_friendly_input': 'low',
        'offi': 'high',
        'comparable': 'low',
        'source': 'MERNNR_20',
        'finer':
            {
                'scale': None,
                'res': None,
                'unit': None,
            },
        },

    'Ec_pozos_MERNNR_20': {
        'path': ["Oficial/MERNNR/Infraestructura_Sector_Hidrocarburos/Pozos.shp"],
        'scoring': 'Infr_imp_poll_scores_05',
        'year': 2020,
        'units': 'meters',
        'accu_input': 'null',
        'sustained_input': 'low',
        'well_docmted_input': 'null',
        'user_friendly_input': 'low',
        'offi': 'high',
        'comparable': 'low',
        'source': 'MERNNR_20',
        'finer':
            {
                'scale': None,
                'res': None,
                'unit': None,
            },
        },

    # 'Ec_plataformas_MERNNR_20': {
    #     'path': ["Oficial/MERNNR/Infraestructura_Sector_Hidrocarburos/plataformas.gpkg"],
    #     'scoring': 'Infr_imp_poll_scores_05',
    #     'year': 2020,
    #     'units': 'meters',
    #     'accu_input': 'null',
    #     'sustained_input': 'low',
    #     'well_docmted_input': 'null',
    #     'user_friendly_input': 'low',
    #     'offi': 'high',
    #     'comparable': 'low',
    #     'source': 'MERNNR_20',
    #     'finer':
    #         {
    #             'scale': None,
    #             'res': None,
    #             'unit': None,
    #         },
    #     },

    'Ec_ductos_MERNNR_20': {
        'path': ["Oficial/MERNNR/Infraestructura_Sector_Hidrocarburos/Ductos3.shp"],
        'scoring': 'line_inf_poll_scores',
        'year': 2020,
        'units': 'meters',
        'accu_input': 'null',
        'sustained_input': 'low',
        'well_docmted_input': 'null',
        'user_friendly_input': 'low',
        'offi': 'high',
        'comparable': 'low',
        'source': 'MERNNR_20',
        'finer':
            {
                'scale': None,
                'res': None,
                'unit': None,
            },
        },

    'Ec_Gasoductos_Petroecuador_MERNNR_20': {
        'path': ["Oficial/MERNNR/Infraestructura_Sector_Hidrocarburos/Gasoductos_Petroecuador.shp"],
        'scoring': 'line_inf_poll_scores',
        'year': 2020,
        'units': 'meters',
        'accu_input': 'null',
        'sustained_input': 'low',
        'well_docmted_input': 'null',
        'user_friendly_input': 'low',
        'offi': 'high',
        'comparable': 'low',
        'source': 'MERNNR_20',
        'finer':
            {
                'scale': None,
                'res': None,
                'unit': None,
            },
        },

    'Ec_OCP_MERNNR_20': {
        'path': ["Oficial/MERNNR/Infraestructura_Sector_Hidrocarburos/OCP2.shp"],
        'scoring': 'line_inf_poll_scores',
        'year': 2020,
        'units': 'meters',
        'accu_input': 'null',
        'sustained_input': 'low',
        'well_docmted_input': 'null',
        'user_friendly_input': 'low',
        'offi': 'high',
        'comparable': 'low',
        'source': 'MERNNR_20',
        'finer':
            {
                'scale': None,
                'res': None,
                'unit': None,
            },
        },

    'Ec_Poliducto_Shushufindi_Quito_MERNNR_20': {
        'path': ["Oficial/MERNNR/Infraestructura_Sector_Hidrocarburos/Poliducto_Shushufindi_Quito.shp"],
        'scoring': 'line_inf_poll_scores',
        'year': 2020,
        'units': 'meters',
        'accu_input': 'null',
        'sustained_input': 'low',
        'well_docmted_input': 'null',
        'user_friendly_input': 'low',
        'offi': 'high',
        'comparable': 'low',
        'source': 'MERNNR_20',
        'finer':
            {
                'scale': None,
                'res': None,
                'unit': None,
            },
        },

    'Ec_Poliductos_Petroecuador_MERNNR_20': {
        'path': ["Oficial/MERNNR/Infraestructura_Sector_Hidrocarburos/Poliductos_Petroecuador.shp"],
        'scoring': 'line_inf_poll_scores',
        'year': 2020,
        'units': 'meters',
        'accu_input': 'null',
        'sustained_input': 'low',
        'well_docmted_input': 'null',
        'user_friendly_input': 'low',
        'offi': 'high',
        'comparable': 'low',
        'source': 'MERNNR_20',
        'finer':
            {
                'scale': None,
                'res': None,
                'unit': None,
            },
        },

    'Ec_SOTE_MERNNR_20': {
        'path': ["Oficial/MERNNR/Infraestructura_Sector_Hidrocarburos/SOTE2.shp"],
        'scoring': 'line_inf_poll_scores',
        'year': 2020,
        'units': 'meters',
        'accu_input': 'null',
        'sustained_input': 'low',
        'well_docmted_input': 'null',
        'user_friendly_input': 'low',
        'offi': 'high',
        'comparable': 'low',
        'source': 'MERNNR_20',
        'finer':
            {
                'scale': None,
                'res': None,
                'unit': None,
            },
        },

    'Ec_mineria_a_IGM_10': {
        'path': ["Oficial/IGM//mina_a.shp"],
        'scoring': 'Part_imp_poll',
        'year': 2010,
        'units': 'meters',
        'accu_input': 'high',
        'sustained_input': 'med',
        'well_docmted_input': 'high',
        'user_friendly_input': 'high',
        'offi': 'high',
        'comparable': 'low',
        'source': 'IGM_10',
        'finer':
            {
                'scale': 50000,
                'res': None,
                'unit': None,
            },
        },

    'Ec_mineria_p_IGM_10': {
        'path': ["Oficial/IGM//mina_p.shp"],
        'scoring': 'Part_imp_poll_05',
        'year': 2010,
        'units': 'meters',
        'accu_input': 'high',
        'sustained_input': 'med',
        'well_docmted_input': 'high',
        'user_friendly_input': 'high',
        'offi': 'high',
        'comparable': 'low',
        'source': 'IGM_10',
        'finer':
            {
                'scale': 50000,
                'res': None,
                'unit': None,
            },
        },

    'Ec_quarry_pt_OSM_22': {
        'path': ["No_Oficial/OSM/221011_QuickOSM_quarry/land_use_quarry_ecuador_point.shp"],
        'scoring': 'Part_imp_poll_05',
        'year': 2022,
        'units': 'meters',
        'accu_input': 'null',
        'sustained_input': 'high',
        'well_docmted_input': 'high',
        'user_friendly_input': 'med',
        'offi': 'low',
        'comparable': 'high',
        'source': 'OSM',
        'finer':
              {
                  'scale': 50000,
                  'res': None,
                  'unit': None,
              },
          },

    'Ec_quarry_pl_OSM_22': {
        'path': ["No_Oficial/OSM/221011_QuickOSM_quarry/land_use_quarry_ecuador_pol.shp"],
        'scoring': 'Part_imp_poll',
        'year': 2022,
        'units': 'meters',
        'accu_input': 'null',
        'sustained_input': 'high',
        'well_docmted_input': 'high',
        'user_friendly_input': 'med',
        'offi': 'low',
        'comparable': 'high',
        'source': 'OSM',
        'finer':
              {
                  'scale': 50000,
                  'res': None,
                  'unit': None,
              },
          },

    'Ec_plantations_MAG_17': {
        'path': ["Oficial/MAG/FC_TIERRA_FORESTAL/FC001_PLANTACION_FORESTAL_A.shp"],
        'scoring': 'plantations_scores',
        'year': 2017,
        'units': 'meters',
        'accu_input': 'null',
        'sustained_input': 'high',
        'well_docmted_input': 'high',
        'user_friendly_input': 'med',
        'offi': 'high',
        'comparable': 'low',
        'source': 'MAG_17',
        'finer':
            {
                'scale': None,
                'res': None,
                'unit': None,
            },
        },

      # Official Peru
    'Pe_lin_transmis_MINAM_11': {
        'path': [
        'Oficial/MINAM/Geoservidor/Vulnerabilidad_Fisica/vulnerabilidad_fisica/vulne_fisica/e_expuesto/electrico.shp'],
        'scoring': 'line_inf_scores',
        'year': 2011,
        'units': 'meters',
        'accu_input': 'null',
        'sustained_input': 'high',
        'well_docmted_input': 'null',
        'user_friendly_input': 'high',
        'offi': 'high',
        'comparable': 'low',
        'source': 'MINAM_11',
        'finer':
            {
                'scale': None,
                'res': None,
                'unit': None,
            },
        },

    'Pe_oleoducto_MINAM_11': {
        'path': ['Oficial/MINAM_Envio/oleoducto/oleducto.shp'],
        'scoring': 'line_inf_poll_scores',
        'year': 2011,
        'units': 'meters',
        'accu_input': 'null',
        'sustained_input': 'high',
        'well_docmted_input': 'null',
        'user_friendly_input': 'high',
        'offi': 'high',
        'comparable': 'low',
        'source': 'MINAM_11',
        'finer':
            {
                'scale': None,
                'res': None,
                'unit': None,
            },
        },

    'Pe_camisea_MINAM_11': {
        'path': [
        'Oficial/MINAM/Geoservidor/Vulnerabilidad_Fisica/vulnerabilidad_fisica/vulne_fisica/e_expuesto/camisea.shp'],
        'scoring': 'line_inf_poll_scores',
        'year': 2011,
        'units': 'meters',
        'accu_input': 'null',
        'sustained_input': 'high',
        'well_docmted_input': 'null',
        'user_friendly_input': 'high',
        'offi': 'high',
        'comparable': 'low',
        'source': 'MINAM_11',
        'finer':
            {
                'scale': None,
                'res': None,
                'unit': None,
            },
        },

    'Pe_gasoducto_OSINERGMIN_18': {
        'path': ['Oficial/OSINERGMIN/gasoducto.shp'],
        'scoring': 'line_inf_poll_scores',
        'year': 2018,
        'units': 'meters',
        'accu_input': 'null',
        'sustained_input': 'low',
        'well_docmted_input': 'high', # had medatada
        'user_friendly_input': 'low',
        'offi': 'high',
        'comparable': 'low',
        'source': 'OSINERGMIN_18',
        'finer':
            {
                'scale': None,
                'res': None,
                'unit': None,
            },
        },

    'Pe_oleoducto_OSINERGMIN_18': {
        'path': ['Oficial/OSINERGMIN/oleoducto.shp'],
        'scoring': 'line_inf_poll_scores',
        'year': 2018,
        'units': 'meters',
        'accu_input': 'null',
        'sustained_input': 'low',
        'well_docmted_input': 'null',
        'user_friendly_input': 'low',
        'offi': 'high',
        'comparable': 'low',
        'source': 'OSINERGMIN_18',
        'finer':
            {
                'scale': None,
                'res': None,
                'unit': None,
            },
        },

    'Pe_hidroel_OSINERGMIN_18': {
        'path': ['Oficial/OSINERGMIN/c_hidrolectrica.shp'],
        'scoring': 'Inf_part_imp_05',
        'year': 2018,
        'units': 'meters',
        'accu_input': 'null',
        'sustained_input': 'low',
        'well_docmted_input': 'null',
        'user_friendly_input': 'low',
        'offi': 'high',
        'comparable': 'low',
        'source': 'OSINERGMIN_18',
        'finer':
            {
                'scale': None,
                'res': None,
                'unit': None,
            },
        },

    'Pe_pozos_PERUPETRO_19': {
        'path': ["Oficial/PERUPETRO/Pozos/Pozos_petroleros_noZM.shp"],
        'scoring': 'Infr_imp_poll_scores_05',
        'year': 2019,
        'units': 'meters',
        'accu_input': 'null',
        'sustained_input': 'low',
        'well_docmted_input': 'null',
        'user_friendly_input': 'low',
        'offi': 'high',
        'comparable': 'low',
        'source': 'PERUPETRO_19',
        'finer':
            {
                'scale': None,
                'res': None,
                'unit': None,
            },
        },

    'Pe_mineria_MINAM_11': {
        'path': ['Oficial/MINAM/Geoservidor/Cobertura_Vegetal/mapa_cobertura_vegetal_2015/CobVeg_180615_UTF_8.shp'],
        'scoring': 'mining_MINAM_scores',
        'cat_field': 'CobVeg2013',
        'year': 2011,
        'units': 'categorical',
        'accu_input': 'null',
        'sustained_input': 'high',
        'well_docmted_input': 'null',
        'user_friendly_input': 'high',
        'offi': 'high',
        'comparable': 'low',
        'source': 'MINAM_11',
        'finer':
            {
                'scale': 100000,
                'res': None,
                'unit': None,
            },
        },

    'Pe_power_plant_OSM_23': {
        'path': ["No_Oficial/OSM/231228_OSM_Pe_electrical/Pe_power_plant.gpkg"],
        'scoring': 'Inf_part_imp_05',
        'year': 2023,
        'units': 'meters',
        'accu_input': 'null',
        'sustained_input': 'high',
        'well_docmted_input': 'high',
        'user_friendly_input': 'med',
        'offi': 'low',
        'comparable': 'high',
        'source': 'OSM',
        'finer':
            {
                'scale': 50000,
                'res': None,
                'unit': None,
            },
        },

    'Pe_dam_OSM_23': {
        'path': ["No_Oficial/OSM/231228_OSM_Pe_electrical/Pe_waterway_dam.gpkg"],
        'scoring': 'Infr_imp_scores',
        'year': 2023,
        'units': 'meters',
        'accu_input': 'null',
        'sustained_input': 'high',
        'well_docmted_input': 'high',
        'user_friendly_input': 'med',
        'offi': 'low',
        'comparable': 'high',
        'source': 'OSM',
        'finer':
            {
                'scale': 50000,
                'res': None,
                'unit': None,
            },
        },

    'Pe_substations_OSM_23': {
        'path': ["No_Oficial/OSM/231228_OSM_Pe_electrical/Pe_power_substation.gpkg"],
        'scoring': 'Infr_imp_scores',
        'year': 2023,
        'units': 'meters',
        'accu_input': 'null',
        'sustained_input': 'high',
        'well_docmted_input': 'high',
        'user_friendly_input': 'med',
        'offi': 'low',
        'comparable': 'high',
        'source': 'OSM',
        'finer':
            {
                'scale': 50000,
                'res': None,
                'unit': None,
            },
        },

    'Pe_power_line_OSM_23': {
        'path': ["No_Oficial/OSM/231228_OSM_Pe_electrical/Pe_power_line.gpkg"],
        'scoring': 'line_inf_scores',
        'year': 2023,
        'units': 'meters',
        'accu_input': 'null',
        'sustained_input': 'high',
        'well_docmted_input': 'high',
        'user_friendly_input': 'med',
        'offi': 'low',
        'comparable': 'high',
        'source': 'OSM',
        'finer':
            {
                'scale': 50000,
                'res': None,
                'unit': None,
            },
        },

    'Pe_power_tower_OSM_23': {
        'path': ["No_Oficial/OSM/231228_OSM_Pe_electrical/Pe_power_tower.gpkg"],
        'scoring': 'Infr_imp_scores',
        'year': 2023,
        'units': 'meters',
        'accu_input': 'null',
        'sustained_input': 'high',
        'well_docmted_input': 'high',
        'user_friendly_input': 'med',
        'offi': 'low',
        'comparable': 'high',
        'source': 'OSM',
        'finer':
            {
                'scale': 50000,
                'res': None,
                'unit': None,
            },
        },

    'Pe_wind_turbine_OSM_23': {
        'path': ["No_Oficial/OSM/231228_OSM_Pe_electrical/Pe_generator_source_wind.gpkg"],
        'scoring': 'Infr_imp_scores',
        'year': 2023,
        'units': 'meters',
        'accu_input': 'null',
        'sustained_input': 'high',
        'well_docmted_input': 'high',
        'user_friendly_input': 'med',
        'offi': 'low',
        'comparable': 'high',
        'source': 'OSM',
        'finer':
            {
                'scale': 50000,
                'res': None,
                'unit': None,
            },
        },

    'Pe_solar_plant_OSM_23': {
        'path': ["No_Oficial/OSM/231228_OSM_Pe_electrical/Pe_plant_source_solar.gpkg"],
        'scoring': 'Inf_part_imp_05',
        'year': 2023,
        'units': 'meters',
        'accu_input': 'null',
        'sustained_input': 'high',
        'well_docmted_input': 'high',
        'user_friendly_input': 'med',
        'offi': 'low',
        'comparable': 'high',
        'source': 'OSM',
        'finer':
            {
                'scale': 50000,
                'res': None,
                'unit': None,
            },
        },

    'Pe_quarry_pt_OSM_22': {
        'path': ["No_Oficial/OSM/221011_QuickOSM_quarry/land_use_quarry_peru_point.shp"],
        'scoring': 'Part_imp_poll_05',
        'year': 2022,
        'units': 'meters',
        'accu_input': 'null',
        'sustained_input': 'high',
        'well_docmted_input': 'high',
        'user_friendly_input': 'med',
        'offi': 'low',
        'comparable': 'high',
        'source': 'OSM',
        'finer':
              {
                  'scale': 50000,
                  'res': None,
                  'unit': None,
              },
          },

    'Pe_quarry_pl_OSM_22': {
        'path': ["No_Oficial/OSM/221011_QuickOSM_quarry/land_use_quarry_peru_pol.shp"],
        'scoring': 'Part_imp_poll',
        'year': 2022,
        'units': 'meters',
        'accu_input': 'null',
        'sustained_input': 'high',
        'well_docmted_input': 'high',
        'user_friendly_input': 'med',
        'offi': 'low',
        'comparable': 'high',
        'source': 'OSM',
        'finer':
              {
                  'scale': 50000,
                  'res': None,
                  'unit': None,
              },
          },

    'in_global_mining': {
        'path':
        ["No_Oficial/Mining/global_mining_polygons_v1_PEC.shp", ],
         'scoring': 'Part_imp_poll',
         'year': 2020,
         'units': '',
         'accu_input': 'high',
         'sustained_input': 'high',
         'well_docmted_input': 'high',
         'user_friendly_input': 'high',
         'offi': 'low',
         'comparable': 'high',
         'source': 'Global-scale mining',
         'finer':
             {
                 'scale': None,
                 'res': 10,
                 'unit': 'm',
             },
         },
}
