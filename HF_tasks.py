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

import os
import shutil
from HF_settings import GENERAL_SETTINGS
from datetime import datetime
from shutil import copyfile
import numpy as np
from HF_layers import multitemporal_layers, layers_settings
from HF_spatial import *  # TODO change
from HF_validation import validate_HF_map


class begin_HF():
    """

    """

    def __init__(self, purpose, tasks, country_processing):
        """

        Parameters
        ----------
        purpose : Purpose of the Human footprint maps. Will match purpose_layers
        in Class GENERAL_SETTINGS
        tasks : Tasks to perform: preparing, scoring, combining and calculating
        the maps, validating.
        main_folder : Name of folder in root for all analysis.

        Returns
        -------
        None.

        """


        # General settings
        self.main_folder = os.getcwd() + f'/{country_processing}//'
        settings = GENERAL_SETTINGS(country_processing, self.main_folder)
        scoring_template = settings.scoring_template
        purpose_layers = settings.purpose_layers[purpose]
        years = purpose_layers['years']
        res = purpose_layers['pixel_res']

        print('------------------------------------------------------------------------------------------------------------------------------')
        print(f'Processing HF map(s) {settings.country} {purpose} {years} {res}m')
        print('------------------------------------------------------------------------------------------------------------------------------')

        # Prepare working folders
        self.prepare_working_folders()

        # Prepare base raster layer
        base_path = self.prepare_base_raster(settings, res)

        # Prepare results folder
        extent = settings.extent_Polygon.split('/')[-1].split('.')[-2]
        results_folder = self.create_processing_folder(settings, purpose, extent, res)

        if tasks and purpose_layers['pressures']:

            # Prepare and score pressures and loop by topics first topic
            for pressure in purpose_layers['pressures']:

                if purpose_layers['pressures'][pressure]['datasets'] and years:
                    print()
                    print(f'Processing {pressure}')

                list_datasets = {}
                for year in years:

                    for dataset in purpose_layers['pressures'][pressure]['datasets']:

                        if year not in list_datasets:
                            list_datasets[year] = []

                        # Determine year to use and scoring method
                        if dataset in multitemporal_layers:

                            # Determine which version in time is closer to year,
                            # if it's a multitemporal layer
                            closer_year = 1000000
                            for layer_aux in multitemporal_layers[dataset]['datasets']:
                                version_year = layers_settings[layer_aux]['year']
                                if abs(version_year - year) <= abs(closer_year - year):
                                    closer_year = version_year
                                    layer = layer_aux

                            # Determine scoring methods
                            # If it's a multitemporal layer, use first one for scoring
                            layer_aux = multitemporal_layers[dataset]['datasets'][0]
                            scoring_method = layers_settings[layer_aux]['scoring']
                            multitemp = True

                        else:
                            layer = dataset
                            scoring_method = layers_settings[layer]['scoring']
                            multitemp = False


                        # If it's Navigable_Waterways, it's multitemporal anyway
                        # if pressure == 'Navigable_Waterways': multitemp = True
                        if scoring_method in ('indirect_scores'): multitemp = True

                        list_datasets[year].append([layer,multitemp])


                        if "Preparing" in tasks:
                            PREPARING(layer, year, settings, base_path, purpose,
                                      scoring_template, scoring_method,
                                      results_folder, self.main_folder, res,
                                      multitemp)

                        if "Scoring" in tasks:
                            SCORING(layer, year, settings, base_path, purpose,
                                    scoring_template, scoring_method,
                                    self.main_folder, multitemp, res)

                for year in years:
                    if "Combining" in tasks and list_datasets:
                        combineRasters(pressure, year, list_datasets[year],
                                        settings, base_path, purpose, res,
                                        scoring_template, results_folder,
                                        self.main_folder)

            # Calculate maps
            if "Calculating_maps" in tasks:
                for year in years:
                    last_y = True if year == years[-1] else False
                    CALCULATING_MAPS(year, settings, results_folder, purpose,
                                      scoring_template, res, last_y,
                                      self.main_folder,)

            # Mask water
            if "Preparing_folder" in tasks:
                # tif_folder = r"G:\Conservation Solution Lab\People\Jose\OneDrive - UNBC\LoL_Data\Peru_HH\HF_maps\b05_HF_maps\Pe_20230605_183825_SDG15_Peru_IGN"
                # river_raster_path = r"Z:\Peru_HH\HF_maps\b03_Prepared_pressures/Peru_IGN_Pe_luc_Mapbiopmas_15_2015_GHF_30m_prepared.tif"
                # water_val = 33
                preparing_folder(results_folder, settings, self.main_folder,
                                  res)

            # Mask water
            if "Validating" in tasks:
                # tif_folder = r"G:\Conservation Solution Lab\People\Jose\OneDrive - UNBC\LoL_Data\Peru_HH\HF_maps\b05_HF_maps\Pe_20230605_183825_SDG15_Peru_IGN"
                # river_raster_path = r"Z:\Peru_HH\HF_maps\b03_Prepared_pressures/Peru_IGN_Pe_luc_Mapbiopmas_15_2015_GHF_30m_prepared.tif"
                # water_val = 33
                if 2018 in years and not settings.clip_by_Polygon:
                    validate_HF_map(self.main_folder, settings, purpose, 
                                    results_folder, res, settings.country)
                else:
                    print('''
********************************************************
Validation can only be performed when the HF is created
at the national level AND for the year 2018.
********************************************************
                          ''')


    def create_processing_folder(self, settings, purpose, extent, res):
        """
        Creates a new folder for all results.

        Parameters
        ----------
        settings : general settings from GENERAL_SETTINGS class.
        purpose : Purpose of the Human footprint maps. Will match purpose_layers
        in Class GENERAL_SETTINGS.

        Returns
        -------
        folder_path : returns path
            'main_folder\HF_maps\b05_HF_maps/country_datetime_purpose'

        """

        # Settings and working directory
        country = settings.country
        now = datetime.now()
        dt_string = now.strftime("_%Y%m%d_%H%M%S")
        folder_path = f'{self.main_folder}/HF_maps/b06_HF_maps/{country[:2]}{dt_string}_{purpose}_{extent}_{res}m'
        os.mkdir(folder_path)

        scripts = ('layers', 'main', 'scores', 'settings', 'spatial', 'tasks',
                   'purpose_scoring', 'validation')

        for script in scripts:
            src = f'{os.getcwd()}/HF_{script}.py'
            dst = f'{folder_path}/Backup_HF_{script}.py'
            copyfile(src, dst)

        print()
        print(f'Folder {folder_path} created with a backup of the scripts')

        return folder_path

    def prepare_working_folders(self):
        """
        Creates/restores working folders if necessary.
        Working folders are:
            b02_Base_rasters
            b03_Prepared_pressures
            b04_Scored_pressures
            b05_HF_maps
        Folders starring with 'b' can be deleted and the script will
        reconstruct them with their contents.

        Returns
        -------
        None.

        """

        # Get main folder and strings to working folders
        folders = (
            f'{self.main_folder}HF_maps/b02_Base_rasters',
            f'{self.main_folder}HF_maps/b03_Prepared_pressures',
            f'{self.main_folder}HF_maps/b04_Scored_pressures',
            f'{self.main_folder}HF_maps/b05_Added_pressures',
            f'{self.main_folder}HF_maps/b06_HF_maps',
        )

        # Check if folders exist and if not, create it
        for f in folders:
            if not os.path.exists(f):
                os.makedirs(f)

    def prepare_base_raster(self, settings, res):
        """
        Converts extent polygon to a raster if necessary.
        The base raster will be the model for ALL rasters to be created.

        Parameters
        ----------
        settings : general settings from GENERAL_SETTINGS class.

        Returns
        -------
        base_path : path to base raster.

        """

        # Prepare name for base raster
        extent = settings.extent_Polygon
        # res = settings.pixel_res
        chunk = extent.split('/')[-1].replace('.', '_')
        base_path = f'{self.main_folder}HF_maps/b02_Base_rasters/base_{chunk}_{res}m.tif'

        # Search for base raster is exists
        base = os.path.isfile(base_path)

        # If base raster does not exist, create it
        if not base:
            print()
            print('Creating base raster')
            create_base_raster(base_path, settings, res)

            # Compress result and delete previous version
            compress(base_path)

        else:
            print()
            print('Base raster already existed')

        return base_path


class PREPARING():
    """
    Converts spatial inputs of pressures to a raster that will be later on
    scored.
    Performs all transformations regarding to format, resolution, units.

    """

    def __init__(self, layer, year, settings, base_path, purpose, scoring_template,
                  scoring_method, results_folder, main_folder, res, multitemp):
        """


        Parameters
        ----------
        layer : Layer name of the pressure/dataset to prepare
        year : year of HF map. If it's a multitemporal layer, the closest will
        be selected.
        settings : general settings from GENERAL_SETTINGS class.
        base_path : path to base raster.
        purpose : Purpose of the Human footprint maps. Will match purpose_layers
        in Class GENERAL_SETTINGS.
        scoring_template : Name of the scoring template from HF_scores.
        E.g. 'GHF'.
        scoring_method : scoring method is a setting of each layer and will
        determine the type of preparing and scoring. Comes from HF_layers.
        results_folder : Folder in root for all results.
        main_folder : Name of folder in root for all analysis.
        multitemp : XXX.

        Returns
        -------
        None.

        """

        # print()
        print(f'      Preparing {layer} {year}')

        # Check if prepared layer exists
        extent = settings.extent_Polygon
        extent = extent.split('/')[-1].split('.')[-2]
        year_txt = f'{year}_' if multitemp else ''
        purp = f'{purpose}_' if scoring_method in ('indirect_scores') else ''
        pressure_path = f'{main_folder}/HF_maps/b03_Prepared_pressures/{extent}_{layer}_{purp}{year_txt}{scoring_template}_{res}m_prepared.tif'

        # If pressure does not exist, create it
        pressure_exists = os.path.isfile(pressure_path)

        if not pressure_exists:

            # Call spatial functions according to scoring method
            if scoring_method in (
                                  'pop_scores_INEC_INEI',
                                  'ntl_VIIRS_scores',
                                  'worldpop_scores',
                                  'bui_Mapbiopmas_scores', 'luc_Mapbiopmas_scores',
                                  'mining_Mapbiopmas_scores',
                                  'built_Meta_scores',
                                    ):

                # Warp raster
                warp_raster(layer, settings, base_path, pressure_path,
                            scoring_template, scoring_method, main_folder)

            elif scoring_method in ('road_scores_l1', 'road_scores_l2',
                                    'road_scores_l3', 'road_scores_l4',
                                    'urban_scores', 'built_Meta_scores',
                                    'Infr_imp_scores', 'Infr_imp_poll_scores_05',
                                    'Infr_imp_poll_scores_15', 'Infr_imp_poll_scores_5',
                                    'Part_imp_poll_05', 'Inf_part_imp_05',
                                    'Inf_part_imp_15', 
                                    'line_inf_poll_scores', 'line_inf_scores',
                                    'plantations_scores',
                                    'settlement_scores',
                                    ):

                # Get proximity raster from shapefile
                print('         Creating proximity raster for ' + layer)
                create_proximity_raster(layer, settings, base_path,
                                        pressure_path,
                                        scoring_template, main_folder, res)

            elif scoring_method in ('luc_MAAE_scores', 'bui_MAAE_scores',
                                    'mining_MINAM_scores',
                                    'agr_MINAGRI_scores',):

                # Create categorical raster from vector layer
                create_categorical_raster(layer, settings, base_path, pressure_path,
                                          main_folder, scoring_template)

            elif scoring_method in ('indirect_scores'):

                # Create categorical raster from vector layer
                create_proximity_raster_from_pixels(layer, year, settings,
                                                    base_path, pressure_path,
                                                    scoring_template, purpose,
                                                    results_folder, main_folder,
                                                    res, scoring_method, multitemp)

            else:
                print(f'{scoring_method} not found in preparing options')

            # Compress result and delete previous version
            compress(pressure_path)

        else:
            print(f'         {layer} was already prepared')


class SCORING():
    """
    Scores prepared rasters of pressures.
    Human influence scores according to scoring template in HF_scores.


    """

    def __init__(self, layer, year, settings, base_path, purpose,
                  scoring_template, scoring_method, main_folder, multitemp, res):
        """


        Parameters
        ----------
        layer : Layer name of the pressure/dataset to prepare
        year : year of HF map. If it's a multitemporal layer, the closest will
        be selected.
        settings : general settings from GENERAL_SETTINGS class.
        base_path : path to base raster.
        purpose : Purpose of the Human footprint maps. Will match purpose_layers
        in Class GENERAL_SETTINGS.
        scoring_template : Name of the scoring template from HF_scores.
        E.g. 'GHF'.
        scoring_method : scoring method is a setting of each layer and will
        determine the type of preparing and scoring. Comes from HF_layers.
        results_folder : Folder in root for all results.
        main_folder : Name of folder in root for all analysis.
        multitemp : XXX

        Returns
        -------
        None.

        """

        # print()
        print(f'      Scoring {layer} {year}')

        # Check if scored layer exists
        extent = settings.extent_Polygon
        extent_str = extent.split('/')[-1].split('.')[-2]
        year_txt = f'{year}_' if multitemp else ''
        purp = f'{purpose}_' if scoring_method in ('indirect_scores') else ''
        in_path = f'{main_folder}/HF_maps/b03_Prepared_pressures/{extent_str}_{layer}_{purp}{year_txt}{scoring_template}_{res}m_prepared.tif'
        scored_path = f'{main_folder}/HF_maps/b04_Scored_pressures/{extent_str}_{layer}_{purp}{year_txt}{scoring_template}_{res}m_scored.tif'
        score_exists = os.path.isfile(scored_path)
        scoring_method = layers_settings[layer]['scoring']

        # If pressure does not exist, create it
        if not score_exists:

            vecfunc = 'dummy'

            # Define function to assign scores according to scoring method
            # Vectors with cetegories as text and scores are assigned during preparation
            if scoring_method in (
                    'bui_MAAE_scores', 
                    'luc_MAAE_scores',
                    'mining_MINAM_scores',
                    ):
                vecfunc = 'remain'

            in_paths = {'':{'in_path': in_path,
                            'scoring_m': scoring_method,
                            'scored_path': scored_path,
                            }}

            # Loop through inpaths
            for in_path in in_paths:

                if vecfunc != 'remain':

                    scoring_method2 = in_paths[in_path]['scoring_m']

                    # Open prepared pressure raster
                    not_scored_raster = RASTER(in_paths[in_path]['in_path'])
                    not_scored_array = not_scored_raster.get_array()
                    not_scored_array = not_scored_array.astype(np.float32)

                    # Assign parameters for scoring functions
                    # Float True for creating a floating type raster
                    Float = True
                    self.nodata = not_scored_raster.nodata
                    template = getattr(HF_scores, settings.scoring_template)
                    scoring_method_template = template[scoring_method2]
                    if scoring_method_template['func'] == 'bins':
                        self.scores = scoring_method_template['scores_by_bins']
                        # Float = True
                    elif scoring_method_template['func'] == 'exp':
                        self.direct_score = scoring_method_template['direct_score']
                        self.max_score_exp = scoring_method_template['max_score_exp']
                        self.min_score_exp = scoring_method_template['min_score_exp']
                        self.max_dist = scoring_method_template['max_dist']
                        # Float = True
                    elif scoring_method_template['func'] == 'log':
                        self.max_score = scoring_method_template['max_score']
                        self.mult_factor = scoring_method_template['mult_factor']
                        self.min_threshold = scoring_method_template['min_threshold']
                        self.max_threshold = scoring_method_template['max_threshold']
                        self.scaling_factor = scoring_method_template['scaling_factor']
                        # Float = True
                    elif scoring_method_template['func'] == 'categories':
                        self.scores = scoring_method_template['scores_by_categories']
                    elif scoring_method_template['func'] == 'linear':
                        self.max_score = scoring_method_template['max_score']
                        self.max_threshold = scoring_method_template['max_threshold']  #  Median for samples in urban areas
                        self.min_threshold = scoring_method_template['min_threshold']
                        self.resampling_method = 'bilinear'
                        # Float = True

                    # Get units of original layer
                    self.units = layers_settings[layer]['units']

                    # If it's rivers/accessiblility, calculations are made in time
                    if scoring_method in ('indirect_scores'):
                        self.units = '10seconds'

                    if self.units in ('meters'):#, 'hab/pixel'
                        denom = 1000
                    elif self.units in ('10seconds'):
                        denom = 36000
                    elif self.units in ('kilometers', 'hours'):
                        denom = 1

                    # Assign scores and save new raster
                    if scoring_method in (
                            'settlement_scores',
                            ):
                        scored_array = \
                        np.where(not_scored_array > self.max_dist, 0,
                                 np.where(not_scored_array == 0, self.direct_score,
                                 self.max_score_exp * np.exp(-(not_scored_array / denom)) + self.min_score_exp
                                  ))

                    elif scoring_method in (
                            'indirect_scores',
                                            ):

                        # Score built as 0 to control for package for calculating distances
                        # that misses some built areas
                        max_ind_score = self.max_score_exp
                        built_path = f'{main_folder}HF_maps/b03_Prepared_pressures/{extent_str}_{layer}_built_{year_txt}{purp}{res}m.tif'
                        built_raster = RASTER(built_path)
                        built_array = built_raster.get_array()
                        scored_array = \
                        np.where(not_scored_array > self.max_dist, 0,
                                 np.where(np.logical_or(not_scored_array==0,built_array==1), self.direct_score,
                                 np.where(self.max_score_exp * np.exp(-(not_scored_array / denom)) + self.min_score_exp < max_ind_score,
                                 self.max_score_exp * np.exp(-(not_scored_array / denom)) + self.min_score_exp, max_ind_score
                                  )))
                        built_raster.close()

                    elif scoring_method in (
                            'road_scores_l1', 'road_scores_l2',
                            'road_scores_l3', 'road_scores_l4',
                            'urban_scores', 'built_Meta_scores',
                            'Infr_imp_scores', 'Infr_imp_poll_scores_05',
                            'Infr_imp_poll_scores_15', 'Infr_imp_poll_scores_5',
                            'Part_imp_poll_05', 'Inf_part_imp_05',
                            'Inf_part_imp_15', 
                            'line_inf_poll_scores', 'line_inf_scores',
                            'plantations_scores',
                            ):

                    #     Returns score according to bins in HF_scores.py/GHF/scoring_method.
                        scored_array = copy.deepcopy(not_scored_array)
                        for i in self.scores:
                            goods = np.where((i[0][0] <= not_scored_array) & (not_scored_array <= i[0][1]) & (not_scored_array != 65535))
                            scored_array[goods] = i[1]
                        del goods

                    #     if value == 65535: return 0  # Value when proximity is empty
                        scored_array[np.where(not_scored_array == 65535)] = 0

                        # If there is a minimum threshold, make everything below it 0s
                        try:
                            scored_array[np.where(not_scored_array < self.min_threshold)] = 0
                        except:
                            pass

                    elif scoring_method in (
                            'pop_scores_INEC_INEI',
                            'worldpop_scores',
                    ):

                        scored_array = copy.deepcopy(not_scored_array)
                        scored_array[np.where(not_scored_array < self.min_threshold)] = 0
                        scored_array[np.where(not_scored_array > self.max_threshold)] = self.max_score
                        goods = np.where((self.min_threshold <= not_scored_array) & (not_scored_array <= self.max_threshold))
                        scored_array[goods] = self.mult_factor * np.log10(((not_scored_array[goods]-self.min_threshold) / self.scaling_factor) + 1)
                        goods = np.where(scored_array > self.max_score)
                        scored_array[goods] = self.max_score
                        goods = np.where(scored_array <0)
                        scored_array[goods] = 0
                        del goods



                    elif scoring_method in (
                            'ntl_VIIRS_scores',
                    ):

                        # Make copy to score
                        scored_array = copy.deepcopy(not_scored_array)

                        # Change everythins outside valid range
                        scored_array[np.where(not_scored_array < self.min_threshold)] = 0
                        scored_array[np.where(not_scored_array > self.max_threshold)] = self.max_score

                        # Score linearly inner values
                        goods = np.logical_and(self.min_threshold <= not_scored_array, not_scored_array <= self.max_threshold)
                        scored_array[goods] = np.interp(not_scored_array[goods], (self.min_threshold, self.max_threshold), (0, self.max_score))


                    elif scoring_method in (
                            'agr_MINAGRI_scores',
                            'bui_Mapbiopmas_scores', 'luc_Mapbiopmas_scores', 'mining_Mapbiopmas_scores',
                            ):

                        scored_array = copy.deepcopy(not_scored_array)#.astype(np.intc)
                        for cat in self.scores:
                            for val in self.scores[cat][1]:
                                goods = np.where((not_scored_array==val) & (not_scored_array!=self.nodata))
                                scored_array[goods] = self.scores[cat][0]
                        del goods

                        scored_array[np.where(not_scored_array == self.nodata)] = 0

                    else:

                        print('scoring_method not found')

                    del not_scored_array

                    # Create scores raster dataset and save
                    base_raster = RASTER(base_path)
                    copy_raster(in_paths[in_path]['scored_path'], base_raster, Float)
                    base_raster.close()
                    scores_raster = RASTER(in_paths[in_path]['scored_path'])
                    save_array(scores_raster.bd, scored_array)
                    del scored_array

                    # Close rasters
                    scores_raster.close()
                    not_scored_raster.close()

                else:
                    # If the scores are already in the raster, just copy the file
                    shutil.copy2(in_paths[in_path]['in_path'], in_paths[in_path]['scored_path'])

                # Clip score raster to study area
                clip_raster_by_extent(in_paths[in_path]['scored_path'],
                                      in_paths[in_path]['scored_path'],
                                      settings, base_path)

                # Compress result and delete previous version
                compress(in_paths[in_path]['scored_path'])

        else:
            print(f'         {layer} was already scored')

    # def get_bins(self, array, min_th, nd):
    #     """


    #     Parameters
    #     ----------
    #     array : array from nightime lights raster.
    #     min_th : minimum threshold used to filter out possible noise in the
    #     form of very small values.
    #     nd : Nodata value from nightime lights raster.

    #     Returns
    #     -------
    #     scores : bins of scores in the form of (DN=Digital Number):
    #             ((0, DN=500), 1), #  Bin 1
    #             ((500, 1000), 2), #  Bin 2
    #             ...
    #             ((1500, np.inf), 10) #  Bin 10

    #     """

    #     ar_f = array.flatten()
    #     ar_f = np.delete(ar_f, np.where(ar_f < min_th))
    #     ar_f = np.delete(ar_f, np.where(ar_f == 0))
    #     ar_f = np.delete(ar_f, np.where(ar_f == nd))

    #     r = range(0,11)
    #     limits = [np.quantile(ar_f, i/10, interpolation='midpoint') for i in r]
    #     scores = [[[limits[i], limits[i+1]],i+1] for i in r if i < 10]

    #     scores[-1][0][1] = np.inf
    #     return scores


class CALCULATING_MAPS():
    """
    Call all functions for calculating maps.

    """

    def __init__(self, year, settings, results_folder, purpose,
                  scoring_template, res, last_y, main_folder):
        """

        Parameters
        ----------
        year : year of HF map. If it's a multitemporal layer, the closest will
        be selected.
        settings : general settings from GENERAL_SETTINGS class.
        purpose : Purpose of the Human footprint maps. Will match purpose_layers
        in Class GENERAL_SETTINGS.
        scoring_template : Name of the scoring template from HF_scores.
        E.g. 'GHF'.
        results_folder : Folder in root for all results.

        Returns
        -------
        None.

        """

        print()
        print(f'Calculating {year} Human Footprint map')

        # Create sum of pressures maps
        if settings.purpose_layers[purpose]:

            # Add topic rasters, create statistics
            HF_path = addRasters(year, settings, results_folder, purpose,
                        scoring_template, res, main_folder)

            # Validating the map
            # print('***Activate validation again***')
            # if last_y:
            #     validate_HF_map(HF_path, main_folder, settings, purpose,
            #                     results_folder)

            # Purpose scoring

