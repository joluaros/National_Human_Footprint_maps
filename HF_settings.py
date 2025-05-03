# -*- coding: utf-8 -*-
"""
Module for creating the Human Footprint maps of Peru and Ecuador.

Version 250503 (SciData)

This script will read spatial datasets of pressures, prepared them by
converting them all to a raster format with identical dimensions, then
score them to reflect their expected human influence.
The scored pressures will then be added to calculate a Human Footprint map.

The structure of the module requires the following:
    - HF_main.py (this script) to control the higher level of the process.
    - HF_settings to control the general settings.
    - HF_tasks to call all functions according to the HF workflow.
    - HF_spatial to provide all spatial functions and classes.
    - HF_scores to provide scores of humnan influence.
    - HF_layers for the settings related to layers (e.g. paths).
    - HF_validation for calculating validation metrics.
    - HF_purpose_scoring (Optional) is not required to create HF maps. It 
    compares different HF versions according to the TARA framework.

This is part of the project Life on Land, with UNDP, the Ministries of the
Environment of each country, and funded by NASA.

Created on Thu Jun 18 18:26:00 2020

@author: Jose Aragon-Osejo aragon@unbc.ca / jose.luis.aragon.ec@gmail.com

"""

from HF_spatial import VECTOR


# Settings
general_settings = {
    'Ecuador_HH': {
        'country': 'Ecuador',
        # Extent...() ,True) for clipping, False for not clipping. Clipping all
        # country extent takes too long and is unnecessary
        'extent_Polygon': ('HF_maps/01_Limits/Limite_CONALI_2019.gpkg', False),  # Final maps
        # 'extent_Polygon': ('HF_maps/01_Limits/Quito_tests.shp', True),
        # 'extent_Polygon': ('HF_maps/01_Limits/mini_sierra.shp', True),
        'elev_path': 'Oficial/IGM/Elevacion/ecu_dtm1_rev.gpkg',
        'slope_path': 'Oficial/IGM/Elevacion/slope_grass.tif',
        'coast_path': 'Oficial/Límite_CONALI/Costa_CONALI_2019.shp',
        'flooded_path': 'Oficial/MAAE/Ecosistema_inundados_fill.tif',
        'split_folder': 'HF_maps/01_Limits/split_folder//',
        'scoring_template': 'GHF',
        'purpose_layers': {


            'SDG15': {

                'years': [2014, 2016, 2018, 2020, 2022],
                # 'years': [2018], #  for tests
                'years_available': [2014, 2016, 2018, 2020, 2022],
                'pixel_res': 30,

                'pressures': {

                    'Built_Environments': {
                        'datasets': [
                            'Ec_bui_MAAE',
                            'Ec_Meta_Pob_20',
                            'bui_Ec_pistas_IGM_10',
                        ],
                        'numb_categories': 3,
                        },

                    'Land_Cover': {
                        'datasets': [
                            'Ec_cut_MAAE',
                            'Ec_plantations_MAG_17',
                        ],
                        'numb_categories': 4,
                        # Crops, pastures, forestry, Human_water
                        },

                    'Roads_Railways': {
                        'datasets': [
                            'Ec_vias_primarias_OSM_21',
                            'Ec_vias_secundarias_OSM_21',
                            'Ec_vias_vecinales_OSM_21',
                            'Ec_vias_peatonales_OSM_21',
                            'Ec_lin_ferreas_IGM_10',
                        ],
                        'numb_categories': 5,
                        },

                    'Indirect_pressure': {
                        'datasets': [
                            'Ec_indirect',
                        ],
                        'numb_categories': 1,
                        },

                    'Population_Density': {
                        'datasets': [
                            'Ec_World_pop_10',
                        ],
                        'numb_categories': 1,
                        },

                    'Electrical_Infrastructure': {
                        'datasets': [
                            'ntl_VIIRS',
                            'Ec_power_plant_OSM_23',
                            'Ec_dam_OSM_23',
                            'Ec_substations_OSM_23',
                            'Ec_power_line_OSM_23',
                            'Ec_power_tower_OSM_23',
                            'Ec_wind_turbine_OSM_23',
                            'Ec_solar_plant_OSM_23',
                        ],
                        'numb_categories': 7,
                        # NTL, plants, dams, substations, powerlines,
                        # power towers, wind turbines
                        },

                    'Oil_Gas_Infrastructure': {
                        'datasets': [
                            'Ec_depositos_MERNNR_20',
                            'Ec_refinerias_MERNNR_20',
                            'Ec_term_depositos_MERNNR_20',
                            'Ec_envasadoras_MERNNR_20',
                            'Ec_estaciones_MERNNR_20',
                            'Ec_estaciones_GO_MERNNR_20',
                            'Ec_pozos_MERNNR_20',
                            'Ec_ductos_MERNNR_20',
                            'Ec_Gasoductos_Petroecuador_MERNNR_20',
                            'Ec_OCP_MERNNR_20',
                            'Ec_Poliducto_Shushufindi_Quito_MERNNR_20',
                            'Ec_Poliductos_Petroecuador_MERNNR_20',
                            'Ec_SOTE_MERNNR_20',
                        ],
                        'numb_categories': 5,#6,
                        # deposits, refineries, stations, wells, #platforms,
                        # pipelines
                        },

                    'Mining_Infrastructure': {
                        'datasets': [
                            'Ec_mineria_a_IGM_10',
                            'Ec_mineria_p_IGM_10',
                            'in_global_mining',
                            'Ec_quarry_pt_OSM_22',
                            'Ec_quarry_pl_OSM_22',
                        ],
                        'numb_categories': 1,
                        },

                    },
                },


            'Multitemporal': {

                'years_available': [2014, 2016, 2018, 2020, 2022],
                'years': [2018],
                'pixel_res': 30,

                'pressures': {

                    'Built_Environments': {
                        'datasets': [
                            'Ec_bui_MAAE',
                        ],
                        'numb_categories': 1,
                        },

                    'Land_Cover': {
                        'datasets': [
                            'Ec_cut_MAAE',
                        ],
                        'numb_categories': 4,
                        # Crops, pastures, forestry, Human_water
                        },

                    'Roads_Railways': {
                        'datasets': [
                        ],
                        'numb_categories': 0,
                        },

                    'Indirect_pressure': {
                        'datasets': [
                            'Ec_indirect',
                        ],
                        'numb_categories': 1,
                        },

                    'Population_Density': {
                        'datasets': [
                        ],
                        'numb_categories': 0,
                        },

                    'Electrical_Infrastructure': {
                        'datasets': [
                            'ntl_VIIRS',
                        ],
                        'numb_categories': 1,
                        },

                    'Oil_Gas_Infrastructure': {
                        'datasets': [
                        ],
                        'numb_categories': 0,
                        },

                    'Mining_Infrastructure': {
                        'datasets': [
                        ],
                        'numb_categories': 0,
                        },

                    },
                },


            'Official': {

                'years': [2018],
                'years_available': [2018],
                'pixel_res': 30,

                'pressures': {

                    'Built_Environments': {
                        'datasets': [
                            'Ec_bui_MAAE',
                            'bui_Ec_poblados_IGM_10',
                            'bui_Ec_pistas_IGM_10',
                        ],
                        'numb_categories': 3,
                        },

                    'Land_Cover': {
                        'datasets': [
                            'Ec_cut_MAAE',
                            'Ec_plantations_MAG_17',
                        ],
                        'numb_categories': 4,
                        # Crops, pastures, forestry, Human_water
                        },

                    'Roads_Railways': {
                        'datasets': [
                            'Ec_vias_primarias_IGM_10',
                            'Ec_vias_secundarias_IGM_10',
                            'Ec_vias_vecinales_IGM_10',
                            'Ec_lin_ferreas_IGM_10',
                        ],
                        'numb_categories': 4,
                        },

                    'Indirect_pressure': {
                        'datasets': [
                            'Ec_indirect',
                        ],
                        'numb_categories': 1,
                        },

                    'Population_Density': {
                        'datasets': [
                            'Ec_pob_INEC_10',
                        ],
                        'numb_categories': 1,
                        },

                    'Electrical_Infrastructure': {
                        'datasets': [
                            'Ec_lin_transmis_ARCERNNR_19',
                            'Ec_centrales_ARCERNNR_19',
                            'Ec_subestaciones_ARCERNNR_19',
                        ],
                        'numb_categories': 3,
                        # centrals, substations, powerlines,
                        },

                    'Oil_Gas_Infrastructure': {
                        'datasets': [
                            'Ec_depositos_MERNNR_20',
                            'Ec_refinerias_MERNNR_20',
                            'Ec_term_depositos_MERNNR_20',
                            'Ec_envasadoras_MERNNR_20',
                            'Ec_estaciones_MERNNR_20',
                            'Ec_estaciones_GO_MERNNR_20',
                            'Ec_pozos_MERNNR_20',
                            'Ec_ductos_MERNNR_20',
                            'Ec_Gasoductos_Petroecuador_MERNNR_20',
                            'Ec_OCP_MERNNR_20',
                            'Ec_Poliducto_Shushufindi_Quito_MERNNR_20',
                            'Ec_Poliductos_Petroecuador_MERNNR_20',
                            'Ec_SOTE_MERNNR_20',
                        ],
                        'numb_categories': 5,#6,
                        # deposits, refineries, stations, wells, #platforms,
                        # pipelines
                        },

                    'Mining_Infrastructure': {
                        'datasets': [
                            'Ec_mineria_a_IGM_10',
                            'Ec_mineria_p_IGM_10',
                        ],
                        'numb_categories': 1,
                        },
                    },
                },
        }
    },

    'Peru_HH': {
        'country': 'Peru',
        # Extent...() ,True) for clipping, False for not clipping. Clipping all
        # country extent takes too long and is unnecessary
        'extent_Polygon': ('HF_maps/01_Limits/Peru_IGN.gpkg', False),  # Final maps
        # "extent_Polygon": ('HF_maps/01_Limits/Peru_04-2.shp', True),
        'scoring_template': 'GHF',
        'elev_path': 'No_Oficial/MERIT_Hydro/Merge_MERIT_elev_Peru.tif',
        'slope_path': 'No_Oficial/MERIT_Hydro/Slope_GRASS_MERIT_Peru.tif',
        'coast_path': 'Oficial/IGN/Costa_IGN.shp',
        'flooded_path': 'Oficial/MINAM/Geoservidor/Cobertura_Vegetal/mapa_cobertura_vegetal_2015/Ecosistemas_inundados.tif',
        'split_folder': 'HF_maps/01_Limits/polygons_split//',
        'purpose_layers': {


            'SDG15': {

                'years': list(range(2012,2022)), # 2022 is not part of the series
                'years_available': list(range(2012,2022)), # 2022 is not part of the series
                
                'pixel_res': 30,

                'pressures': {

                    'Built_Environments': {
                        'datasets': [
                            'Pe_bui_Mapbiopmas',
                            'Pe_Meta_Pob_20',
                            'Pe_puertos_MINAM_11',
                        ],
                        'numb_categories': 4,
                        },

                    'Land_Cover': {
                        'datasets': [
                            'Pe_luc_Mapbiopmas',
                        ],
                        'numb_categories': 3,
                        # Crops, pastures, forestry
                        },

                    'Roads_Railways': {
                        'datasets': [
                            'Pe_vias_primarias_OSM_21',
                            'Pe_vias_secundarias_OSM_21',
                            'Pe_vias_vecinales_OSM_21',
                            'Pe_vias_peatonales_OSM_21',
                            'Pe_lin_ferreas_OSM_21',
                        ],
                        'numb_categories': 5,
                        },

                    'Indirect_pressure': {
                        'datasets': [
                            'Pe_indirect',
                        ],
                        'numb_categories': 1,
                        },

                    'Population_Density': {
                        'datasets': [
                            'Pe_World_pop_07',
                        ],
                        'numb_categories': 1,
                        },

                    'Electrical_Infrastructure': {
                        'datasets': [
                            'ntl_VIIRS',
                            'Pe_power_plant_OSM_23',
                            'Pe_dam_OSM_23',
                            'Pe_substations_OSM_23',
                            'Pe_power_line_OSM_23',
                            'Pe_power_tower_OSM_23',
                            'Pe_wind_turbine_OSM_23',
                            'Pe_solar_plant_OSM_23',
                        ],
                        'numb_categories': 7,
                        # NTL, plants, dams, substations, powerlines,
                        # power towers, wind turbines
                        },

                    'Oil_Gas_Infrastructure': {
                        'datasets': [
                            'Pe_oleoducto_MINAM_11',
                            'Pe_camisea_MINAM_11',
                            'Pe_gasoducto_OSINERGMIN_18',
                            'Pe_oleoducto_OSINERGMIN_18',
                            'Pe_pozos_PERUPETRO_19',
                        ],
                        'numb_categories': 2,
                        # wells, pipelines
                        },

                    'Mining_Infrastructure': {
                        'datasets': [
                            'in_global_mining',
                            'Pe_mineria_MINAM_11',
                            'Pe_quarry_pt_OSM_22',
                            'Pe_quarry_pl_OSM_22',
                            'Pe_mining_Mapbiopmas',
                        ],
                        'numb_categories': 1,
                        },
                },
            },



            'Multitemporal': {
                
                'years_available': list(range(2012,2022)), # 2022 is not part of the series
                'years': [2018],
                'pixel_res': 30,

                'pressures': {

                    'Built_Environments': {
                        'datasets': [
                            'Pe_bui_Mapbiopmas',
                        ],
                        'numb_categories': 1,
                        },

                    'Land_Cover': {
                        'datasets': [
                            'Pe_luc_Mapbiopmas',
                        ],
                        'numb_categories': 3,
                        # Crops, pastures, forestry
                        },
                    'Roads_Railways': {
                        'datasets': [
                        ],
                        'numb_categories': 0,
                        },

                    'Indirect_pressure': {
                        'datasets': [
                            'Pe_indirect',
                        ],
                        'numb_categories': 1,
                        },

                    'Population_Density': {
                        'datasets': [
                        ],
                        'numb_categories': 0,
                        },

                    'Electrical_Infrastructure': {
                        'datasets': [
                            'ntl_VIIRS',
                        ],
                        'numb_categories': 1,
                        },

                    'Oil_Gas_Infrastructure': {
                        'datasets': [
                        ],
                        'numb_categories': 0,
                        },

                    'Mining_Infrastructure': {
                        'datasets': [
                            'Pe_mining_Mapbiopmas',
                        ],
                        'numb_categories': 1,
                        },

                },
            },


            'Official': {

                'years': [2018],
                'years_available': [2018],
                'pixel_res': 30,

                'pressures': {

                    'Built_Environments': {
                        'datasets': [
                            'bui_Pe_a_urbana_MINAM_11',  # Official
                            'bui_Pe_poblados_MINAM_11',  # Official
                            'bui_Pe_pob_indig_MinCul_20',  # Official
                            'Pe_puertos_MINAM_11',  # Official
                        ],
                        'numb_categories': 4,
                        },

                    'Land_Cover': {
                        'datasets': [
                            'Pe_Censo_Agr_MIDAGRI_18',
                        ],
                        'numb_categories': 1,
                        },

                    'Roads_Railways': {
                        'datasets': [
                            'Pe_vias_nacional_MTC_19',  # Official
                            'Pe_vias_deprtmtal_MTC_19',  # Official
                            'Pe_vias_vecinal_MTC_19',  # Official
                            'Pe_lin_ferreas_MTC_18',  # Official
                        ],
                        'numb_categories': 4,
                        },

                    'Indirect_pressure': {
                        'datasets': [
                            'Pe_indirect',
                        ],
                        'numb_categories': 1,
                        },

                    'Population_Density': {
                        'datasets': [
                            'Pe_pob_INEI_17',
                        ],
                        'numb_categories': 1,
                        },

                    'Electrical_Infrastructure': {
                        'datasets': [
                            'Pe_lin_transmis_MINAM_11',
                            'Pe_hidroel_OSINERGMIN_18',
                        ],
                        'numb_categories': 2,
                        },

                    'Oil_Gas_Infrastructure': {
                        'datasets': [
                            'Pe_oleoducto_MINAM_11',
                            'Pe_camisea_MINAM_11',
                            'Pe_gasoducto_OSINERGMIN_18',
                            'Pe_oleoducto_OSINERGMIN_18',
                            'Pe_pozos_PERUPETRO_19',
                        ],
                        'numb_categories': 2,
                        # wells, pipelines
                        },

                    'Mining_Infrastructure': {
                        'datasets': [
                            'Pe_mineria_MINAM_11',
                        ],
                        'numb_categories': 1,
                        },
                },
            },
        },
    },
}


class GENERAL_SETTINGS:
    """
    Class for general technical settings:
        country
        extent polygon for study area
        coordinates system (from extent polygon)
        scoring template
        pixel resolution
        Layers according to the version/purpose of the HF maps
            years to process
            pressures
                datasets per pressure
    """

    def get_crs(self, path):
        """ Gets the coordinate system of a vector """
        vector_crs = VECTOR(path)
        crs = vector_crs.crs
        crs_authority = vector_crs.crs_authority
        vector_crs.close()
        return crs, crs_authority

    def __init__(self, country_processing, main_folder):
        """


        Parameters
        ----------
        main_folder : Name of folder in root for all analysis.

        Returns
        -------
        None.

        """
        settings_c = general_settings[country_processing]

        # Settings
        self.country = settings_c['country']
        # Extent...() ,True) for clipping, False for not clipping. Clipping all
        # country extent takes too long and is unnecessary
        self.extent_Polygon = main_folder + settings_c['extent_Polygon'][0]
        self.clip_by_Polygon = settings_c['extent_Polygon'][1]
        self.crs, self.crs_authority = self.get_crs(self.extent_Polygon) #  Don't change this
        self.scoring_template = settings_c['scoring_template']
        self.pixel_res = settings_c['purpose_layers']
        self.purpose_layers = settings_c['purpose_layers']
        self.elev_path = settings_c['elev_path']
        self.slope_path = settings_c['slope_path']
        self.coast_path = settings_c['coast_path']
        self.flooded_path = settings_c['flooded_path']
        self.split_folder = settings_c['split_folder']


############################################
# Code to calculate number of datasets
if __name__ == "__main__":

    summary_dict = {}
    
    for HF, HF_dict in general_settings.items():
        
        summary_dict[HF] = {}
        print(HF)
        
        for HF_version, HF_version_dict in HF_dict['purpose_layers'].items():
            
            print('   '+HF_version)
            summary_dict[HF][HF_version] = {}
            
            num_pressures = 0
            num_datasets = 0
            
            for pressure, pressure_dict in HF_version_dict['pressures'].items():
                
                if len(pressure_dict['datasets'])>0:
                    # print(pressure)
                    num_pressures += 1
                if pressure != 'Indirect_pressure' and len(pressure_dict['datasets'])>0:
                    print(pressure)
                    num_datasets += len(pressure_dict['datasets'])
            summary_dict[HF][HF_version]['num_pressures'] = num_pressures
            summary_dict[HF][HF_version]['num_datasets'] = num_datasets
            summary_dict[HF][HF_version]['num_updates'] = len(HF_version_dict['years_available'])

    print('Analysis of datasets for paper')
    print(summary_dict)
    print('''For dataset numbers, need to subtract 1 in Ecuador and 2 in Peru, as built environments 
and land use layers (and mining in Peru) come from the same layer
''')