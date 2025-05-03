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


import pandas as pd
import numpy as np
import os
import geopandas as gpd
import matplotlib.pyplot as plt
import rasterstats as rs

# Import scores
from HF_scores import Urban_area_score
from HF_scores import Densily_populated_areas_score
from HF_scores import Infrastructure_impervious_pollution_score
from HF_scores import Main_road_score
from HF_scores import Secondary_road_score
from HF_scores import Settlement_score
from HF_scores import Country_road_score
from HF_scores import Pasture_score
from HF_scores import Agriculture_score
from HF_scores import Tree_plantation_score
from HF_scores import Trail_score


# osr.UseExceptions()

def get_RMSE(x):
    return np.sqrt(np.average(x))


def clean_df(vdf, fields_vis_scores, other_fields,\
                           remove_field, remove_value, keep_dict,
                           nrows=None):

    # Remove points from Colombia
    vdf = vdf[vdf[remove_field] != remove_value]

    # Remove more if needed
    for keep_field, keep_value in keep_dict.items():
        vdf = vdf[vdf[keep_field] == keep_value]

    # Change any nan values to 0
    vdf[fields_vis_scores]=vdf[fields_vis_scores].fillna(0)

    return vdf


def calculate_visual_score(vdf, fields_vis_scores, other_fields,
                           pressures_dict, nrows=None):

    # Score all visual fields
    vis_txt = '_vis'
    for pressure, scored_fields in pressures_dict.items():
        if not pressure[:3]=='HF_':
            for scored_field, score in scored_fields.items():
                # *score standardizes to pressure to 0-10
                vdf[scored_field+vis_txt] = vdf[scored_field] * score/3
                vdf[scored_field+vis_txt] = vdf[scored_field+vis_txt].fillna(0)

    # Create all 0s visual pressure fields
    for pressure, scored_fields in pressures_dict.items():
        vdf[pressure+vis_txt] = 0

    # Add to pressures
    for pressure, scored_fields in pressures_dict.items():
        if not pressure[:3]=='HF_':

            for scored_field, score in scored_fields.items():
                vdf[pressure+vis_txt] = np.maximum(vdf[pressure+vis_txt], vdf[scored_field+vis_txt])

    # Deal with not co-occurring layers
    # Change indirect to 0 if built environments
    if ('Indirect_pressure_vis' in vdf.columns) and ('Built_Environments_vis' in vdf.columns):
        vdf['Indirect_pressure_vis'] = np.where(vdf['Built_Environments_vis']>0, 0, vdf['Indirect_pressure_vis'])
        
    # Add to HF index
    HF_field = None
    for pressure, scored_fields in pressures_dict.items():
        if pressure[:3]=='HF_':
            HF_field = pressure

    if HF_field:
        for pressure, scored_fields in pressures_dict.items():
            if not pressure[:3]=='HF_':
                vdf[HF_field+vis_txt] = vdf[HF_field+vis_txt] + vdf[pressure+vis_txt]

    return vdf


def extract_values(vis_path, raster_path):
    raster = rs.zonal_stats(vis_path, raster_path, stats="mean")
    return [feature['mean'] for feature in raster]


def values_from_rasters(vis_path, vdf, country_field, results_folder,
                            xfield, yfield, purpose, settings,
                            pressures_dict, other_rasters, res, lim_txt):

    '''

    '''
    
    raster_values_df_path = results_folder + 'Validation_raster_values_df.csv'
    exists = os.path.isfile(raster_values_df_path)
    
    if not exists:
        
        # Create list of rasters to extract values from
        map_txt = '_map'
        
        # Create empty df
        raster_values_df = pd.DataFrame(index=vdf.index)
        
        # pressure_paths = {}
        for pressure, scored_fields in pressures_dict.items():

            initial_txt='' if pressure[:3]=='HF_' else 'p_'
            raster_path = f'{initial_txt}{pressure}_{lim_txt}_{purpose}_2018_GHF_{res}m.tif'
    
            exists = os.path.isfile(results_folder+raster_path)
            if exists:
                raster_values_df[pressure+map_txt] = extract_values(vis_path, results_folder+raster_path)
                raster_values_df[pressure+map_txt] = raster_values_df[pressure+map_txt].fillna(0)
            else:
                raster_values_df[pressure+map_txt] = 0
    
        for raster_name, raster_path in other_rasters.items():
            raster_values_df[raster_name] = extract_values(vis_path, raster_path)
            
        # Save df
        raster_values_df.to_csv(raster_values_df_path)
        
    else:
        
        raster_values_df = pd.read_csv(raster_values_df_path)

    return pd.concat([vdf, raster_values_df], axis=1)


def scatter_plot(vdf, field1, field2, pressure, txt, results_folder, purpose):
    
    # Convert the GeoDataFrame to a regular DataFrame
    vdf.plot(x=field1, y=field2, kind="scatter")

    # # Add a unity diagonal line
    # plt.plot([df[field1].min(), df[field1].max()], [df[field2].min(), df[field2].max()], color='red')

    # Set axis labels and title
    plt.xlabel(f'Map score {txt}')
    plt.ylabel(f'Visual score {txt}')
    plt.title(f'{pressure} {purpose} validation scatterplot')
    plt.savefig(results_folder + f'/Validation_scatterplot{txt}.png')

    # Show the plot
    plt.show()

def calculate_metrics(vdf, field1, field2, pressure, results_folder, purpose):  # map, vis

    # Normalize fields
    vdf[field1+'_norm'] = vdf[field1] / (vdf[field1].max() - vdf[field1].min()) # map
    vdf[field2+'_norm'] = vdf[field2] / (vdf[field2].max() - vdf[field2].min()) # vis

    if pressure[:3]=='HF_':
        scatter_plot(vdf, field1, field2, pressure, '', results_folder, purpose)

    # Get RMSE by pressure
    vdf[f'{pressure}_RMSE_step1'] = (vdf[field1+'_norm'] -\
                            vdf[field2+'_norm'])**2
    # Remove features with no RMSE
    vdf = vdf.dropna().copy()
    # Calculate RMSEs
    RMSE = get_RMSE(vdf[f'{pressure}_RMSE_step1'])

    agr = .2  # Agreement
    vdf[f'{pressure}_Dif'] = np.round(vdf[field1+'_norm']-vdf[field2+'_norm'],2) #  Map - Vis

    # Get Kappa
    median = np.median(vdf[f'{pressure}_Dif'])
    vdf[f'{pressure}_NotAgree_map_high'] = np.where(vdf[f'{pressure}_Dif']>agr, 1, 0)
    vdf[f'{pressure}_NotAgree_map_low'] = np.where(-(vdf[f'{pressure}_Dif'])>agr, 1, 0)
    vdf[f'{pressure}_Agree_map_high'] = np.where(vdf[f'{pressure}_NotAgree_map_high']==0,\
                                np.where(vdf[f'{pressure}_NotAgree_map_low']==0,\
                                np.where(vdf[f'{pressure}_Dif']>median,1,0),0),0)
    vdf[f'{pressure}_Agree_map_low'] = np.where(vdf[f'{pressure}_NotAgree_map_high']==0,\
                                np.where(vdf[f'{pressure}_NotAgree_map_low']==0,\
                                np.where(vdf[f'{pressure}_Dif']<=median,1,0),0),0)


    vdf[f'{pressure}_Agreement'] = np.where(vdf[f'{pressure}_Dif']>agr, 'NotAgree_map_high',
                                      np.where(-(vdf[f'{pressure}_Dif'])>agr, 'NotAgree_map_low',
                                               np.where(vdf[f'{pressure}_Dif']>median,'Agree_map_high','Agree_map_low')))


    Ll = np.count_nonzero(vdf[f'{pressure}_Agree_map_low'] == 1)
    Lh = np.count_nonzero(vdf[f'{pressure}_NotAgree_map_high'] == 1)
    Hl = np.count_nonzero(vdf[f'{pressure}_NotAgree_map_low'] == 1)
    Hh = np.count_nonzero(vdf[f'{pressure}_Agree_map_high'] == 1)

    dict_kappa_agreement = {
        'Agree_map_low': Ll,
        'NotAgree_map_high': Lh,
        'NotAgree_map_low': Hl,
        'Agree_map_high': Hh,
        }

    print(f'{dict_kappa_agreement=}')

    data = [{'low': Ll, 'high': Lh},
            {'low': Hl, 'high': Hh}]
    df_kappa = pd.DataFrame(data, index =['Low', 'High'])

    # Add a row of column sums AND a column of row sums
    df_kappa.loc['Total_h'] = df_kappa.sum()
    df_kappa['Total_v'] = df_kappa.sum(axis=1)
    agreement_kappa = df_kappa.loc['Low','low'] + df_kappa.loc['High','high']
    by_ch1 = df_kappa.loc['Total_h','low'] * df_kappa.loc['Low','Total_v'] / df_kappa.loc['Total_h','Total_v']
    by_ch2 = df_kappa.loc['Total_h','high'] * df_kappa.loc['High','Total_v'] / df_kappa.loc['Total_h','Total_v']
    by_chance = by_ch1 + by_ch2
    skkappa = (agreement_kappa - by_chance) / (df_kappa.loc['Total_h','Total_v'] - by_chance)

    # Calculate correlation
    corr = vdf[field1+'_norm'].corr(vdf[field2+'_norm'])
    corr2 = corr*corr

    # return vdf, RMSE, df_kappa, agreement_kappa, by_chance, kappa, corr2
    return vdf, RMSE, skkappa, corr2, dict_kappa_agreement


def get_validation_metrics(vdf, results_folder, pressures_dict, country, purpose):

    validation_text = []
    validation_text.append(country)

    for pressure, scored_field in pressures_dict.items():

        if pressure[:3] == 'HF_':
        # if True:

            rounding = 2
            vis_field, map_field = pressure+'_vis', pressure+'_map'
            vdf, RMSE, kappa, corr2, dict_kappa_agreement = calculate_metrics(vdf, map_field,
                                                        vis_field, pressure,
                                                        results_folder, purpose)

            # Save a file of validation stats (overwrites)
            validation_text.append(f'\n\nValidation metrics {pressure} \n')
            validation_text.append(f'RMSE = {np.round(RMSE, rounding)}')
            validation_text.append(f'Kappa statistic = {np.round(kappa, rounding)}')
            validation_text.append(f'Determination coefficient (r^2) = {np.round(corr2, rounding)}')

            print()
            print(f'Validation stats {country}/{pressure}')
            print(f'   RMSE {pressure} = {np.round(RMSE, rounding)}')
            print(f'   Kappa statistic = {np.round(kappa, rounding)}')
            print(f'   Determination coefficient (r^2) = {np.round(corr2, rounding)}')

    # Add difference fields for pressures
    for pressure, scored_field in pressures_dict.items():
        if pressure[:3] != 'HF_':
            vis_field, map_field = pressure+'_vis', pressure+'_map'
            vdf[pressure+'_Dif'] = np.round(vdf[pressure+'_map'] - vdf[pressure+'_vis'], 2)

    # Create a DataFrame
    df = pd.DataFrame({
        'Country': [country],
        'Purpose': [purpose],
        'RMSE': [np.round(RMSE, rounding)],
        'Kappa': [np.round(kappa, rounding)],
        'R2': [np.round(corr2, rounding)],
        'NotAgree_map_low': [dict_kappa_agreement['NotAgree_map_low']],
        'Agree_map_low': [dict_kappa_agreement['Agree_map_low']],
        'Agree_map_high': [dict_kappa_agreement['Agree_map_high']],
        'NotAgree_map_high': [dict_kappa_agreement['NotAgree_map_high']],
        })

    df.set_index('Country', inplace=True)
    df.to_csv(results_folder + 'Validation_dataframe.csv')
    return vdf


def validate_HF_map(main_folder, settings, purpose, results_folder, res, country):

    print()
    print(f"Calculating validation metrics {purpose} {country}")

    fields_vis_scores = [
        'Crops', #'Vis_Built-environments',
        'Pasture',
        'Disturbed vegetation',
        'Forestry',
        'roads-paved',
        'roads-unpaved',
        'roads-private',
        'Railways',
        'Track',
        'road indirect',
        'Urban',
        'Human dwellings',
        'Infractructure',
        'Settlements indirect',
        'Navigable waterways',
        'Navigable waterways indirect',
        'Other',
    ]

    other_fields = [
        'id',
        'Certain',
        'Country',
        'position',
        'POINT_X',
        'POINT_Y',
        'geometry',
        ]

    max_ind_score = 2*3 #Multiplying by 3 corrects the division in function calculate_visual_score
    
    pressures_dicts = {

        'SDG15': {
            
        'Built_Environments': {
            'Urban': Urban_area_score,
            'Human dwellings': Settlement_score,
            },

        'Land_Cover': {
            'Crops': Agriculture_score,
            'Pasture': Pasture_score,
            'Disturbed vegetation': Agriculture_score,
            'Forestry': Tree_plantation_score,
            },

        'Roads_Railways': {
            'roads-paved': Main_road_score,
            'roads-unpaved': Country_road_score,
            'roads-private': Secondary_road_score,
            'Railways': Main_road_score,
            'Track': Trail_score,
            },

        'Indirect_pressure': {
            'Settlements indirect': max_ind_score,
            'Navigable waterways indirect': max_ind_score,
            'road indirect': max_ind_score,
            },

        'Population_Density': {
            'Urban': Densily_populated_areas_score,
            'Settlements indirect': max_ind_score,
            },

        'Electrical_Infrastructure': {
            'Urban': Densily_populated_areas_score,
            'Settlements indirect': max_ind_score,
            },

        'Oil_Gas_Infrastructure': {
            'Infractructure': Infrastructure_impervious_pollution_score, #Linear_infrastructure_pollution_score
            },

        'Mining_Infrastructure': {
            },

        f'HF_{country}':{
            },},


          'Multitemporal': {

              'Built_Environments': {
                  'Urban': Urban_area_score,
                   # 'Human dwellings': Settlement_score,
                  },

              'Land_Cover': {
                  'Crops': Agriculture_score,
                  'Pasture': Pasture_score,
                  'Disturbed vegetation': Agriculture_score,
                  'Forestry': Tree_plantation_score,
                  },

              # 'Roads_Railways': {
              #     'roads-paved': Main_road_score,
              #     'roads-unpaved': Country_road_score,
              #     'roads-private': Secondary_road_score,
              #     'Railways': Main_road_score,
              #     'Track': Trail_score,
              #     },

              'Indirect_pressure': {
                  'Settlements indirect': max_ind_score,
                  'Navigable waterways indirect': max_ind_score,
                  # 'road indirect': max_ind_score,
                  },

              # 'Population_Density': {
              #     'Urban': Densily_populated_areas_score,
              #     'Settlements indirect': max_ind_score,
              #     },

              'Electrical_Infrastructure': {
                  'Urban': Densily_populated_areas_score,
                  'Settlements indirect': max_ind_score,
                  },

              # 'Oil_Gas_Infrastructure': {
              #     'Infractructure': Infrastructure_impervious_pollution_score, #Linear_infrastructure_pollution_score
              #     },

              # 'Mining_Infrastructure': {
              #     },

              f'HF_{country}':{
                  },},



        'Official': {
            
            'Built_Environments': {
                'Urban': Urban_area_score,
                'Human dwellings': Settlement_score,
                },

            'Land_Cover': {
                'Crops': Agriculture_score,
                'Pasture': Pasture_score,
                'Disturbed vegetation': Agriculture_score,
                'Forestry': Tree_plantation_score,
                },

            'Roads_Railways': {
                'roads-paved': Main_road_score,
                'roads-unpaved': Country_road_score,
                'roads-private': Secondary_road_score,
                'Railways': Main_road_score,
                # 'Track': Trail_score,
                },

            'Indirect_pressure': {
                'Settlements indirect': max_ind_score,
                'Navigable waterways indirect': max_ind_score,
                'road indirect': max_ind_score,
                },

            'Population_Density': {
                'Urban': Densily_populated_areas_score,
                'Settlements indirect': max_ind_score,
                },

            'Electrical_Infrastructure': {
                'Urban': Densily_populated_areas_score,
                'Settlements indirect': max_ind_score,
                },

            'Oil_Gas_Infrastructure': {
                'Infractructure': Infrastructure_impervious_pollution_score, #Linear_infrastructure_pollution_score
                },

            'Mining_Infrastructure': {
                },

            f'HF_{country}':{
                },},
        
        }


    # River raster to remove water pixels
    country_txt= settings.country[:2]
    extent = settings.extent_Polygon
    extent_str = extent.split('/')[-1].split('.')[-2]
    other_rasters = {
        'rivers': f'{main_folder}HF_maps/b03_Prepared_pressures/{extent_str}_{country_txt}_indirect_rivers_{res}m_rasterized.tif'
        }

    if country == 'Peru':
        vis_path = main_folder + r'Validation_inputs/210417_1_Validation_Pe.gpkg'

    elif country == 'Ecuador':
        vis_path = main_folder + r'Validation_inputs/210417_1_Validation_Ec.gpkg'

    # Field to look for country
    country_field = 'Country'
    # Fields for x and y
    xfield = "POINT_X"
    yfield = "POINT_Y"
    # Remove Colombia points if existing
    remove_field = 'Country'
    remove_value = 'Colombia'
    # Keep only points for position 0 if other are available
    keep_dict = {
        'position': 'p0',
        'rivers': 0,
        'Certain': 'y',
        }

    pressures_dict = pressures_dicts[purpose]

    # Open and Leave only important fields
    vdf = gpd.read_file(vis_path)
    vdf = vdf[vdf.columns.intersection(fields_vis_scores+other_fields)]

    # Get values from pressures and HF rasters
    results_folder += '//'
    vdf = values_from_rasters(vis_path, vdf,  country_field, results_folder,
                                xfield, yfield, purpose, settings,
                                pressures_dict, other_rasters, res, extent_str)

    # Calculate visual score
    vdf = calculate_visual_score(vdf, fields_vis_scores, other_fields,
                                            pressures_dict,)

    # Do some cleaning
    vdf = clean_df(vdf, fields_vis_scores, other_fields,
                                remove_field, remove_value, keep_dict,
                                nrows=None)

    # # Calculate validation metrics and save new geopackage
    vdf = get_validation_metrics(vdf, results_folder, pressures_dict, country, purpose)
    vdf_path = results_folder + '/Validation_points.gpkg'
    vdf.to_file(vdf_path, driver='GPKG')

class GENERAL_SETTINGS:
    """

    """

    def __init__(self, country, main_folder):
        self.country = country
        if country=='Peru':
            self.extent_Polygon = main_folder + r'HF_maps/01_Limits/Peru_IGN.gpkg'
        elif country=='Ecuador':
            self.extent_Polygon = main_folder + r'HF_maps/01_Limits/Limite_CONALI_2019.gpkg'
        self.clip_by_Polygon = False
        self.pixel_res = 30


############################################

if __name__ == "__main__":  
    
    country = 'Ecuador'
    # country = 'Peru'

    init_settings = {
        'Ecuador': {
            'main_folder': r'G:\Conservation Solution Lab\People\Jose\OneDrive - UNBC\LoL_Data\Ecuador_HH//',
            
            'purposes': {
                
                'SDG15': {
                    'HF_name': 'HF_Ecuador_Limite_CONALI_2019_SDG15_2018_GHF_30m.tif',
                    'more_folders': r'HF_maps\b06_HF_maps\Ec_20250226_085705_SDG15_Limite_CONALI_2019_30m//',
                    },
                
                'Multitemporal': {
                    'HF_name': 'HF_Ecuador_Limite_CONALI_2019_Multitemporal_2018_GHF_30m.tif',
                    'more_folders': r'HF_maps\b06_HF_maps\Ec_20250226_095320_Multitemporal_Limite_CONALI_2019_30m//',
                    },
                
                'Official': {
                    'HF_name': 'HF_Ecuador_Limite_CONALI_2019_Official_2018_GHF_30m.tif',
                    'more_folders': r'HF_maps\b06_HF_maps\Ec_20250226_100107_Official_Limite_CONALI_2019_30m//',
                    },
                
                }
            },
        
        'Peru': {
            'main_folder': r'G:\Conservation Solution Lab\People\Jose\OneDrive - UNBC\LoL_Data\Peru_HH//',
            
            'purposes': {
                
                'SDG15': {
                    'HF_name': 'HF_Peru_Peru_IGN_SDG15_2018_GHF_30m.tif',
                    'more_folders': r'HF_maps\b06_HF_maps\Pe_20241012_162237_SDG15_Peru_IGN_30m//',
                    },
                
                'Multitemporal': {
                    'HF_name': 'HF_Peru_Peru_IGN_Multitemporal_2018_GHF_30m.tif',
                    'more_folders': r'HF_maps\b06_HF_maps\Pe_20241012_204320_Multitemporal_Peru_IGN_30m//',
                    },
                
                'Official': {
                    'HF_name': 'HF_Peru_Peru_IGN_Official_2018_GHF_30m.tif',
                    'more_folders': r'HF_maps\b06_HF_maps\Pe_20241013_004303_Official_Peru_IGN_30m//',
                    },
                }
            },
        }

    # Process by country
    country_settings = init_settings[country]
    main_folder = country_settings['main_folder']
    settings = GENERAL_SETTINGS(country, main_folder)
    res = settings.pixel_res
    
    # Loop over HF versions
    for purpose, purpose_settings in country_settings['purposes'].items():
        
        results_folder = main_folder + purpose_settings['more_folders']
        HF_path = results_folder + purpose_settings['HF_name']
        validate_HF_map(main_folder, settings, purpose, results_folder, res, country)

    print('\007')
    # print("------ FIN ------")


