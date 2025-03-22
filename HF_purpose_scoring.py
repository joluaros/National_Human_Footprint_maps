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

# https://medium.com/python-in-plain-english/radar-chart-basics-with-pythons-matplotlib-ba9e002ddbcd
# https://www.pythoncharts.com/matplotlib/radar-charts/


# import sys
# scripts_path = 'E:\\OneDrive - UNBC\\Scripts'
# if scripts_path not in sys.path:
#     sys.path.append(scripts_path)

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import os
import re
from HF_settings import GENERAL_SETTINGS
from HF_layers import layers_settings, multitemporal_layers
from matplotlib.patches import Rectangle
import matplotlib.lines as mlines
from matplotlib.gridspec import GridSpec
from matplotlib.colors import LinearSegmentedColormap


# def bar_plot(df, title, keep_fields=None):
        
#     if keep_fields:
#         df = df.loc[:, keep_fields]
    
#     # Plotting
#     # fig, ax = plt.subplots()
#     fig, ax = plt.subplots(figsize=(12, 6))
    
#     # Width of each bar group
#     bar_width = 0.1
    
#     # Positions for the bars
#     x = np.arange(len(df.index))
    
#     # Iterate through each attribute
#     for i, attribute in enumerate(df.columns):
#         # Plotting the bars for each attribute
#         ax.bar(x + i * bar_width, df[attribute], bar_width, label=attribute)
    
#     # Adding labels and legend
#     ax.set_xlabel('Datasets')
#     ax.set_ylabel('Purpose scoring')
#     ax.set_title(title)
#     ax.set_xticks(x + bar_width * (len(df.columns) - 1) / 2)
#     ax.set_xticklabels(df.index)
#     ax.legend()
    
#     # Rotate x-axis labels for better readability
#     plt.xticks(rotation=45, ha='right')
    
#     # Show plot
#     plt.show()


# def plot_by_dataset(purpose_scores, map_setting):
    
    
#     # cols = ['Fine-resolution', 'Nationally-validated', 'Internationally-comparable', 'Multitemporal', 'Current']
    
#     cols = ['Nationally-validated']
    
#     for col in cols:
#         # print(purpose_scores['Built_Environments'][col])
        
#         dfs = [purpose_scores[pressure][[col]].dropna() for pressure in purpose_scores.keys()]
#         df = pd.concat(dfs)
        
#         title = f'{map_setting} HF scores of {col}'
#         bar_plot(df, title)


# def plot_input_analysis(df_pivot_pressures, pressures, maps_list):

#     # Set up graph 
#     desired_figsize_mm = (88, 70)  # Set your desired figure size in mm (width, height)
#     # Convert mm to inches (1 inch = 25.4 mm)
#     desired_figsize = (desired_figsize_mm[0] / 25.4, desired_figsize_mm[1] / 25.4)
#     # desired_figsize=(3.46*2, 4)
#     desired_font = {'family': 'sans-serif', 'weight': 'normal', 'size': 5}
#     plt.rcParams['figure.dpi'] = 300
#     plt.rcParams['savefig.dpi'] = 300
#     plt.rcParams.update({'font.size': 5})
#     plt.rc('font', **desired_font)

#     # create_hist = True
#     # create_hist = False

#     # Create a figure and GridSpec layout
#     fig = plt.figure(figsize=desired_figsize)
#     name = 'Input_analysis_scoring'
#     if fig_letter:
#         name2 = fig_letter + " " + name
#         # plt.text(-0.16, 1.12, fig_letter, fontsize=7, transform=plt.gca().transAxes,)# weight='bold'
#     fig.suptitle(f"{name2.replace('_', ' ')} {country}", fontsize=7)
    

#     # Create subplots
#     gs = GridSpec(1, 1)
#     ax_heatmap1 = fig.add_subplot(gs[0, 0])
#     # ax_heatmap2 = fig.add_subplot(gs[0, 9:])

#     # # Create subplots
#     # gs = GridSpec(1, 14)
#     # ax_heatmap1 = fig.add_subplot(gs[0, :9])
#     # ax_heatmap2 = fig.add_subplot(gs[0, 9:])

#     # # Create subplots
#     # gs = GridSpec(1, 4) if create_hist else GridSpec(1, 3)
#     # ax_heatmap1 = fig.add_subplot(gs[0, 0:2])
#     # ax_heatmap2 = fig.add_subplot(gs[0, 2])

#     # if create_hist: 
        
#     #     # Create histogram as barplot
#     #     ax_hist_row = fig.add_subplot(gs[0, 3])
        
#     #     # Bin the data    
#     #     min_value = 0
#     #     max_value = 3
#     #     bin_edges = pd.interval_range(start=min_value, end=max_value, freq=0.5)
#         # df['bin'] = pd.cut(df['average'], bins=bin_edges)
#     #     bin_counts = df['bin'].value_counts().sort_index()
        
#     #     # Create a DataFrame for plotting
#     #     plot_df = pd.DataFrame({'bin': bin_counts.index.astype(str), 'frequency': bin_counts.values})
#     #     bin_order = [f"({i:.1f}, {i + 0.5:.1f}]" for i in np.arange(max_value-.5, min_value-.5, -0.5)]
#     #     plot_df['bin'] = pd.Categorical(plot_df['bin'], categories=bin_order, ordered=True)
#     #     plot_df = plot_df.sort_values('bin')
        
#     #     # Plot histogram
#     #     sns.barplot(x='frequency', y='bin', data=plot_df, orient='h', ax=ax_hist_row, color='lightgrey')
#     #     ax_hist_row.set_title('Input scoring histogram', fontsize=5)
#     #     ax_hist_row.set(ylabel=None)
#     #     ax_hist_row.set_yticks(np.arange(-0.5, 6, 1))
#     #     ax_hist_row.set_yticklabels([])
    
#     #     # Change width of lines
#     #     sns.despine(ax=ax_hist_row, top=True, right=True)
#     #     for spine in ax_hist_row.spines.values():
#     #         spine.set_linewidth(0.6) 

#     # # Pivot tables for heatmaps\
#     # # Remove accurate and complete as they are analyzed differently
#     # chars_list = [char for char in purposes_scoring+input_analysis_scoring if char not in ['Accurate', 'Complete']]
#     # df_pivot_pressures = pivot_table(df, pressures, chars_list)
#     # name = f'Input_analysis_heatmap_values_pressures_{country}'
#     # print_save(df_pivot_pressures, scoring_folder, name, print_=False)
#     # # df_pivot_HF_maps = pivot_table(df, maps_list, chars_list)    

#     # Plot heatmaps on the second row
#     annot = True
#     xticks_rotation = 90
#     # xticks_rotation = 0
#     colors = ['#d73027', '#fdae61', '#ffffbf', '#a1d99b', '#1a9850']
#     cmap = LinearSegmentedColormap.from_list('RdYlGr', colors)
#     # cmap = 'RdYlBu'
    
#     # Heatmap pressures 
#     sns.heatmap(df_pivot_pressures, ax=ax_heatmap1, cmap=cmap, annot=annot, cbar=True, vmin=0, vmax=3)
#     ax_heatmap1.set(ylabel=None)
#     ax_heatmap1.set(xlabel=None)
#     # # ax_heatmap1.xticks(rotation=xticks_rotation)
#     ax_heatmap1.set_xticklabels([format_labet(label.get_text()) for label in ax_heatmap1.get_xticklabels()], rotation=xticks_rotation)
#     ax_heatmap1.set_yticklabels([format_labet(label.get_text()) for label in ax_heatmap1.get_yticklabels()])
#     # # ax_heatmap1.set_xticklabels([label.get_text().replace('-', '\n').replace('_', '\n') for label in ax_heatmap1.get_xticklabels()])
#     # # ax_heatmap1.set_yticklabels([label.get_text().replace('-', '\n').replace('_', '\n') for label in ax_heatmap1.get_yticklabels()])
#     # # ax_heatmap1.set_yticklabels([label.get_text().split('_', 1)[0] .replace('_', '-')+ '\n' + label.get_text().replace('_', '-').split('-', 1)[1] if '-' in label.get_text() else label.get_text() for label in ax_heatmap1.get_yticklabels()])

#     # Bold last column and row
#     n_rows, n_cols = df_pivot_pressures.shape
#     for text in ax_heatmap1.texts:
#         row, col = divmod(ax_heatmap1.texts.index(text), n_cols)
#         if row == n_rows - 1 or col == n_cols - 1:
#             text.set_fontweight('bold')

#     # Bold the tick labels for the last row and last column
#     # X-axis (columns)
#     for tick in ax_heatmap1.get_xticklabels():
#         if tick.get_text() == 'Pressures\nAverage':  # Bold last column tick label
#             tick.set_fontweight('bold')
    
#     # Y-axis (rows)
#     for tick in ax_heatmap1.get_yticklabels():
#         if tick.get_text() == 'Characteristics\nAverage':  # Bold last row tick label
#             tick.set_fontweight('bold')


#     # ax_heatmap1.set_title('Scoring heatmap by pressure', fontsize=5)
    
#     # # Heatmap HF maps
#     # sns.heatmap(df_pivot_HF_maps, ax=ax_heatmap2, cmap=cmap, annot=annot, cbar=True, vmin=0, vmax=3)
#     # # ax_heatmap2.collections[0].colorbar.set_ticks([])
#     # cbar = ax_heatmap2.collections[0].colorbar
#     # cbar.ax.tick_params(length=0)
#     # ax_heatmap2.set(yticks=[], ylabel=None)
#     # ax_heatmap2.set(xlabel=None)
#     # ax_heatmap2.set_xticklabels([format_labet(label.get_text() )for label in ax_heatmap2.get_xticklabels()], rotation=xticks_rotation)
#     # # ax_heatmap2.set_xticklabels([label.get_text().replace('-', '\n').replace('_', '\n') for label in ax_heatmap2.get_xticklabels()])
#     # ax_heatmap2.set_title('Scoring heatmap by HF map', fontsize=5)
    
#     # Adjust layout and show
#     plt.tight_layout()
#     # plt.show()

#     # Save
#     fig_path = f'{scoring_folder}/{name}_{country}.png'
#     plt.savefig(fig_path, bbox_inches='tight')
#     fig_path = f'{scoring_folder}/{name}_{country}.svg'
#     plt.savefig(fig_path, bbox_inches='tight', transparent=True)
#     fig_path = f'{scoring_folder}/{name}_{country}.eps'
#     plt.savefig(fig_path, bbox_inches='tight')
#     plt.show()


def get_validation_df(map_settings, main_folder):

    # Get csv files paths
    keys = [i for i in map_settings]
    vals = \
        [f'{main_folder}HF_maps/b06_HF_maps/{map_settings[i][0]}/Validation_dataframe.csv' \
         for i in map_settings]
    paths = dict(zip(keys, vals))

    # Create dataframe
    dfs = [pd.read_csv(paths[i]) for i in paths]

    return pd.concat(dfs).set_index('Purpose')


def weighted_average(df, pressure):
    
    # print()
    # print(df.info())

    if pressure in ('Built_Environments', 'Land_Cover',
                    'Electrical_Infrastructure'):

        # Define weights (more weight to the first row)
        weights = [1] + [0.25] * (df.shape[0] - 1)

    else:
        weights = [1] * (df.shape[0])

    index_list = df.index.tolist()
    col_list = df.columns.tolist()
    # col_list.remove('Source')
    av_row = []

    for col in col_list: # if col!='Source'
        av_sum = count = 0
        # print(f'{col=}')

        for index, index_name in enumerate(index_list):

            cel_val = df.loc[index_name, col]
            if cel_val==None: cel_val=np.nan
            weight = weights[index]
            # print(f'{cel_val=}')
            if not np.isnan(cel_val):
                av_sum += cel_val * weight
                count += weight

        if av_sum:
            av_row.append(av_sum/count)

        else:
            # print(0)
            av_row.append(np.nan)

    # Add the result as a new row at the end of the DataFrame
    df.loc['average'] = av_row

    return df


def calculate_scores(pressure, map_setting, ps, settings, purposes_scoring, input_analysis_scoring):
    """
    Help test.

    Parameters
    ----------
    pressure : TYPE
        DESCRIPTION.

    Returns
    -------
    list
        DESCRIPTION.
    """
    df_col_list = purposes_scoring + input_analysis_scoring + ['Source']
    df = pd.DataFrame(columns=df_col_list)

    for dataset in settings.purpose_layers[map_setting]['pressures'][pressure]['datasets']:
        
        # print(f'{map_setting=} {dataset=}')

        s_Nat_val = s_Real = s_Uptod = s_Mult = s_plete = s_Local = \
            s_parable = None
        i_accu_input = i_sustained_input = i_well_docmted_input = \
            i_user_friendly_input = None
        i_source = None

        # Get purpose scores from layers
        if dataset in multitemporal_layers:
            dataset_ = multitemporal_layers[dataset]['purp_scores']
            years = multitemporal_layers[dataset]['years_datasets']
            year = years[-1]
        else:
            dataset_ = layers_settings[dataset]
            years = []
            year = layers_settings[dataset]['year']

        # Nationally validated score
        s_Nat_val = ps[dataset_['offi']]

        # Accuracy purpose calculated later
        s_Real = np.nan  # Dummy value

        # Current or Up-to-date score
        dif_y = 2024 - year
        if 0 <= dif_y <= 3:
            s_Uptod = 3
        elif 3 < dif_y <= 6:
            s_Uptod = 2
        elif 6 < dif_y <= 10:
            s_Uptod = 1
        elif 10 < dif_y <= 100: # dummy max value to catch errors
            s_Uptod = 0
        else:
            s_Uptod = -900

        # Multitemporal score
        l_lim = 2012  # lower limit for time range
        # u_lim = 2020
        if not years:
            # print(f'{dataset=}')
            s_Mult = ps['low']
            # s_Mult = 1
        else:
            years = np.array(years)
            years = years[years>=l_lim]
            s_Mult = len(years)
            if s_Mult > ps['high']: s_Mult = ps['high']

        # Completion purpose calculated later
        s_plete = np.nan  # Dummy value

        # Local score
        finer_ = dataset_['finer']
        scale, res, unit = finer_['scale'], finer_['res'], finer_['unit']
        # Convert all info to resolution in m
        if not (scale or res or unit):
            res_m = None
        elif scale:
            res_m = scale / 2000
        elif res and unit == 'm':
            res_m = res
        else:
            res_m = None

        # Convert to score from upper values
        limit_vals = (
            ((0, 25), 3),
            ((25, 50), 2.5),
            ((50, 125), 2),
            ((125, 250), 1.5),
            ((250, 500), 1),
            ((500, 1000), 0.5),
            ((1000, np.inf), 0.5),
            )
        # s_Local = None
        if res_m:
            for i in limit_vals:
                if i[0][0] < res_m <= i[0][1]:
                    s_Local = i[1]

        # International comparability score
        s_parable = ps[dataset_['comparable']]

        # Input analysis scores
        i_accu_input = ps[dataset_['accu_input']]
        i_sustained_input = ps[dataset_['sustained_input']]
        i_well_docmted_input = ps[dataset_['well_docmted_input']]
        i_user_friendly_input = ps[dataset_['user_friendly_input']]
        i_source = dataset_['source']

        scores_dict = {
            'Accurate': s_Real,
            'Complete': s_plete,
            'Nationally-validated': s_Nat_val,
            'Internationally-comparable': s_parable,
            'Multitemporality': s_Mult,
            'Current': s_Uptod,
            'Fine-resolution': s_Local,
            'Accuracy_as_input': i_accu_input,
            'Sustained_input': i_sustained_input,
            'Well_docmted_input': i_well_docmted_input,
            'User_friendly_input': i_user_friendly_input,
            'Source': i_source,
            }

        scores_list = []
        for purpose in df_col_list:
            if purpose in scores_dict:
                scores_list.append(scores_dict[purpose])

        # Append to pressure df
        # print(scores_list)
        df.loc[dataset] = scores_list

    dataset_scores = df.copy()
    df = df.drop('Source', axis=1)
    df = weighted_average(df, pressure)
    av = df.loc['average']

    averages_dict = {
        'Accurate': av['Accurate'],
        'Complete': av['Complete'],
        'Nationally-validated': av['Nationally-validated'],
        'Internationally-comparable': av['Internationally-comparable'],
        'Multitemporality': av['Multitemporality'],
        'Current': av['Current'],
        'Fine-resolution': av['Fine-resolution']
        }

    scores_dict = {}
    for purpose in purposes_scoring:
        if purpose in averages_dict:
            scores_dict[purpose] = averages_dict[purpose]


    return scores_dict, dataset_scores


def reorder_columns(df, cols_list, order=None):
    
    remaining_cols = [col for col in df.columns if col not in cols_list]
    if order == 'last':
        return df[remaining_cols + cols_list]
    elif order == 'first':
        return df[cols_list + remaining_cols]
    else:
        return None


def pivot_table(df, X_axis, chars_list, source=False):
    
    # Code for unweighted average
    if not source:
        df_melted = pd.melt(df, id_vars=X_axis,
                            value_vars=chars_list,
                            var_name='Characteristic', value_name='Score')
        df_filtered = pd.melt(df_melted, id_vars=['Characteristic', 'Score'],
                              value_vars=X_axis,
                              var_name='X_axis', value_name='Present')
        df_filtered = df_filtered[df_filtered['Present'] == 'Yes']
        df_grouped = df_filtered.groupby(['Characteristic', 'X_axis'], as_index=False).agg({'Score': 'mean'})
        df_pivot = df_grouped.pivot(index='Characteristic', columns='X_axis', values='Score')

        # Add missing columns with zeros
        for col in X_axis: 
            if col not in df_pivot.columns: df_pivot[col] = 0
          
        # Calculate averages
        df_pivot['Pressures\nAverage'] = df_pivot[X_axis].mean(axis=1)  
    
    elif source:
        df_melted = pd.melt(df, id_vars=X_axis,
                            value_vars=chars_list,
                            var_name='Characteristic', value_name='Score')
        df_grouped = df_melted.groupby(['Characteristic', 'Source'], as_index=False).agg({'Score': 'mean'})
        df_pivot = df_grouped.pivot(index='Characteristic', columns='Source', values='Score')
        
        # Calculate averages
        df_pivot['Sources\nAverage'] = df_pivot.mean(axis=1)  
    
    # Calculate characteristic averages
    mean_row = pd.DataFrame(df_pivot.mean()).T
    mean_row.index = ['Characteristics\nAverage']
    df_pivot = pd.concat([df_pivot, mean_row], ignore_index=False)

    return round(df_pivot,2)
    
    # # Change Yes to Yes_weighted when datasets came from extensive layers
    # dataset_names = [
    #     'Ec_bui_MAAE',
    #     'Ec_cut_MAAE',
    #     'Ec_World_pop_10',
    #     'ntl_VIIRS',
    #     'Ec_pob_INEC_10',
    #     'Pe_bui_Mapbiopmas',
    #     'Pe_luc_Mapbiopmas',
    #     'Pe_World_pop_07',
    #     'bui_Pe_a_urbana_MINAM_11',
    #     'Pe_Censo_Agr_MIDAGRI_18',
    #     'Pe_pob_INEI_17',
    #     ]

    # for pressure in X_axis:
    #     df.loc[(df.index.isin(dataset_names)) & (df[pressure] == 'Yes'), pressure] = 'Yes_weighted'
    # df_melted = pd.melt(df, id_vars=X_axis,
    #                     value_vars=chars_list,
    #                     var_name='Characteristic', value_name='Score')
    # df_filtered = pd.melt(df_melted, id_vars=['Characteristic', 'Score'],
    #                       value_vars=X_axis,
    #                       var_name='X_axis', value_name='Present')
    # df_filtered = df_filtered[df_filtered['Present'].isin(['Yes', 'Yes_weighted'])]
    # df_filtered['Weight'] = 1
    # # Change here if weighted average
    # # df_filtered.loc[(df_filtered['Present'] == 'Yes_weighted'), 'Weight'] = 4
    # df_filtered.loc[(df_filtered['Present'] == 'Yes_weighted'), 'Weight'] = 1
    # def weighted_mean(df, value_col, weight_col):
    #     return np.average(df[value_col], weights=df[weight_col])
    # df_grouped = df_filtered.groupby(['Characteristic', 'X_axis'], as_index=False)[['Score', 'Weight']].apply(
    #     lambda x: pd.Series({
    #         'Score': weighted_mean(x, 'Score', 'Weight')
    #     })
    # )
    # df_grouped.reset_index(drop=True, inplace=True)
    # df_pivot = df_grouped.pivot(index='Characteristic', columns='X_axis', values='Score')
    



def format_labet(label):
    
    label = label.replace('Mining_Infrastructure', 'Mining')
    label = label.replace('Well_docmted', 'Well_documented')
    label = label.replace('_as', '')
    label = label.replace('_input', '')
    label = label.replace('-', '_')
    label = label.replace('_', '\n')
    label = re.sub(r'\n\d+', '', label)
    label = label.replace('Oil\nGas', 'Oil and Gas')
    label = label.replace('Accuracy', 'Accuracy\nreported')
    label = label.replace('Multitemporality', 'Multitemporal')
    label = label.replace('CUT\nMAATE', 'CUT MAATE')
    
    return label


def create_heatmap_ax(df, ax='ax_heatmap1', cmap='cmap', annot='annot',
                      cbar=True, vmin=0, vmax=3, ticks='No', title='title',
                      xticks_rotation=0):

    # Heatmap settings 
    sns.heatmap(df, ax=ax, cmap=cmap, annot=annot, cbar=cbar, cbar_kws={"pad": .02}, vmin=0, vmax=3)
    ax.set(ylabel=None)
    ax.set(xlabel=None)
    ax.set_xticklabels([format_labet(label.get_text()) for label in ax.get_xticklabels()], rotation=xticks_rotation)
    ax.set_yticklabels([format_labet(label.get_text()) for label in ax.get_yticklabels()])
    ax.set_title(title, fontsize=5)

    # Bold last column and row
    n_rows, n_cols = df.shape
    for text in ax.texts:
        row, col = divmod(ax.texts.index(text), n_cols)
        if row == n_rows - 1 or col == n_cols - 1:
            text.set_fontweight('bold')

    # Bold the tick labels for the last row and last column
    # X-axis (columns)
    for tick in ax.get_xticklabels():
        if tick.get_text() in ['Sources\nAverage', 'Pressures\nAverage']:  # Bold last column tick label
            tick.set_fontweight('bold')
    
    # Y-axis (rows)
    for tick in ax.get_yticklabels():
        if tick.get_text() == 'Characteristics\nAverage':  # Bold last row tick label
            tick.set_fontweight('bold')
            
    if ticks == 'No': ax.set(yticks=[])


def reorder_cols(df):
    
    # Sort by list of rows
    # ORder from Pe and Ec averages 
    sorted_rows = [  
        'Multitemporality',        
        'Accuracy_as_input', 
        'Fine-resolution',        
        'Current',
        'Internationally-comparable', 
        'Well_docmted_input',
        'Nationally-validated',
        'User_friendly_input',
        'Sustained_input', 
        'Characteristics\nAverage',
        ]
    df = df.reindex(sorted_rows)

    # Sort by national validation value
    av_col = df.columns[-1]
    cols_to_sort = df.columns[df.columns != av_col]  # Exclude 'Sources average'
    # national_row_values = df.loc['Nationally-validated', cols_to_sort]
    national_row_values = df.loc['Characteristics\nAverage', cols_to_sort]
    sorted_columns = national_row_values.sort_values(ascending=True).index.tolist()
    sorted_columns.append(av_col)
    
    # sources_avg = df[av_col]
    # df_transposed = df[df.columns[:-1]].T
    # correlations = df_transposed.corrwith(sources_avg, axis=1)
    # correlations = df.corrwith(sources_avg, axis=1)
    # sorted_rows = correlations.abs().sort_values(ascending=False).index
    # df = df.loc[sorted_rows]

    return df[sorted_columns]


def combined_heatmap(scoring_folder_Ec, scoring_folder_Pe, subtxt):
    
    # Read pivot dfs    
    path_df_Ec = f'{scoring_folder_Ec}/Input_analysis_heatmap_values_{subtxt}_Ecuador.csv'
    path_df_Pe = f'{scoring_folder_Pe}/Input_analysis_heatmap_values_{subtxt}_Peru.csv'
    df_pivot_Ec = pd.read_csv(path_df_Ec, index_col=0)
    df_pivot_Pe = pd.read_csv(path_df_Pe, index_col=0)

    # Reorder cols according to national validation
    df_pivot_Ec = reorder_cols(df_pivot_Ec)
    df_pivot_Pe = reorder_cols(df_pivot_Pe)

    # Set up graph 
    desired_figsize_mm = (88*2, 70)  # Set your desired figure size in mm (width, height)
    desired_figsize = (desired_figsize_mm[0] / 25.4, desired_figsize_mm[1] / 25.4)  # Convert mm to inches (1 inch = 25.4 mm)
    # desired_figsize=(3.46*2, 4)
    desired_font = {'family': 'sans-serif', 'weight': 'normal', 'size': 5}
    plt.rcParams['figure.dpi'] = 300
    plt.rcParams['savefig.dpi'] = 300
    plt.rcParams.update({'font.size': 5})
    plt.rc('font', **desired_font)
    fig = plt.figure(figsize=desired_figsize)
    if subtxt=='pressures':
        subtitle = ' - Pressures'
        pretitle = 'Inputs'
    elif subtxt=='sources':
        subtitle = 'Sources'
        pretitle = ''
    fig.suptitle(f'{pretitle}{subtitle} analysis', fontsize=7)
    
    # Create subplots
    gs = GridSpec(1, 30)
    ax_heatmap1 = fig.add_subplot(gs[0, :15])
    ax_heatmap2 = fig.add_subplot(gs[0, 15:])

    # Set up heatmaps
    annot = True
    # annot = False
    xticks_rotation = 90
    # xticks_rotation = 0
    colors = ['#d73027', '#fdae61', '#ffffbf', '#a1d99b', '#1a9850']
    cmap = LinearSegmentedColormap.from_list('RdYlGr', colors)
    # cmap = 'RdYlBu'
    
    # Create heatmaps
    title_Ec = fig_letter_Ec + ' Ecuador'
    title_Pe = fig_letter_Pe + ' Peru'
    create_heatmap_ax(df_pivot_Ec, ax=ax_heatmap2, cmap=cmap, annot=annot,
                      cbar=True, vmin=0, vmax=3, ticks='No', title=title_Ec, 
                      xticks_rotation=xticks_rotation)
    create_heatmap_ax(df_pivot_Pe, ax=ax_heatmap1, cmap=cmap, annot=annot, 
                      cbar=False, vmin=0, vmax=3, ticks='Yes', title=title_Pe, 
                      xticks_rotation=xticks_rotation)

    # Adjust layout and show
    plt.tight_layout()
    # plt.show()

    # Save
    name = f'Input_analysis_dataset_scores_Pe_Ec_{subtxt}'
    for scoring_folder in [scoring_folder_Ec, scoring_folder_Pe]:
        fig_path = f'{scoring_folder}/{name}.png'
        plt.savefig(fig_path, bbox_inches='tight')
        # fig_path = f'{scoring_folder}/{name}.svg'
        # plt.savefig(fig_path, bbox_inches='tight', transparent=True)
        fig_path = f'{scoring_folder}/{name}.eps'
        plt.savefig(fig_path, bbox_inches='tight')
        # plt.show()


def radar_plot(purposes_scoring, df_ps, country, scoring_folder, map_settings,
               fig_letter=None):

    # Size in millimeters
    desired_figsize_mm = (88, 70)  # Set your desired figure size in mm (width, height)
    # Convert mm to inches (1 inch = 25.4 mm)
    desired_figsize = (desired_figsize_mm[0] / 25.4, desired_figsize_mm[1] / 25.4)
    # print(f'{desired_figsize=}') # desired_figsize=(3.4645669291338583, 2.7559055118110236)
    desired_font = {'family': 'sans-serif', 'weight': 'normal', 'size': 5}  # Set your desired font
    plt.rcParams['figure.dpi'] = 300
    plt.rcParams['savefig.dpi'] = 300
    plt.rcParams.update({'font.size': 5})  # Set default font size for the plot
    markersize = 3

    # Number of variables we're plotting.
    num_vars = len(purposes_scoring)

    # Split the circle into even parts and save the angles
    # so we know where to put each axis.
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()

    # The plot is a circle, so we need to "complete the loop"
    # and append the start value to the end.
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=desired_figsize, subplot_kw=dict(polar=True))

    # Set font and text size
    plt.rc('font', **desired_font)

    # Add each web to the chart.
    for map_setting in map_settings:
        colour = map_settings[map_setting][1]
        marker = map_settings[map_setting][2]
        values = df_ps.drop(['average'],axis=1).loc[map_setting].tolist()
        values += values[:1]
        ax.plot(angles, values, color=colour,  marker=marker, markersize=markersize,
                linewidth=1, label=map_setting)

    # Fix axis to go in the right order and start at 12 o'clock.
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    # Draw axis lines for each angle and label.
    ax.set_thetagrids(np.degrees(angles[:-1]), [i.replace('-','\n') for i in purposes_scoring])
    # Go through purposes_scoring and adjust alignment based on where
    # it is in the circle.
    for label, angle in zip(ax.get_xticklabels(), angles):
      if angle in (0, np.pi):
        label.set_horizontalalignment('center')
      elif 0 < angle < np.pi:
        label.set_horizontalalignment('left')
      else:
        label.set_horizontalalignment('right')
    # Set position of y-purposes_scoring to be in the middle
    # of the first two axes.
    ax.set_rlabel_position(180 / num_vars)
    ax.tick_params(colors='#222222')
    ax.tick_params(axis='y', labelsize=5)
    ax.tick_params(axis='x', pad=-5) 
    ax.grid(color='#AAAAAA')
    ax.spines['polar'].set_color('#222222')
    ax.set_facecolor('#FAFAFA')

    # Add title.
    ax.set_title(f'Actionable characteristics scoring in {country}', y=1.08)

    # Add the text "a)" in the upper left corner
    if fig_letter:
        plt.text(-0.16, 1.12, fig_letter, fontsize=7, transform=plt.gca().transAxes,)# weight='bold'

    # # Add a legend
    # Sort Dataframe by average
    df_ps = df_ps.sort_values(by='average', ascending=False)
    # https://stackoverflow.com/questions/25830780/tabular-legend-layout-for-matplotlib/25995730
    # create blank rectangle
    extra = Rectangle((0, 0), 1, 1, fc="w", fill=False, edgecolor='none', linewidth=0)
    #Create organized list containing all handles for table. Extra represents empty space
    legend_handle = [extra] +\
        [mlines.Line2D([], [], color=map_settings[row[0]][1], \
                       marker=map_settings[row[0]][2], markersize=markersize)\
         for row in df_ps.iterrows()] +\
        [extra for map_setting in map_settings] * 2 + [extra] * 2

    add_txt = {
        'SDG15': '',
        'Multitemporal': '',
        'Official': '',
        }
    #organize labels for table construction
    legend_labels = [''] + ['' for row in df_ps.iterrows()] + [r'$\mathbf{HF}$'+' '+r'$\mathbf{version}$'] +\
        [row[0]+add_txt[row[0]] for row in df_ps.iterrows()] + [r'$\mathbf{av.}$'] +\
            [np.round(row[-1]['average'], 2) for row in df_ps.iterrows()]
    #Create legend
    ax.legend(legend_handle, legend_labels,
            bbox_to_anchor=(1.2, -.05),#loc = 1,
          ncol = 3, shadow = False, handletextpad = -1.5)

    # Save the figure
    fig_path = f'{scoring_folder}/Purposes_scoring_{country}.png'
    plt.savefig(fig_path, bbox_inches='tight')
    # fig_path = f'{scoring_folder}/Purposes_scoring_{country}.svg'
    # plt.savefig(fig_path, bbox_inches='tight', transparent=True)
    fig_path = f'{scoring_folder}/Purposes_scoring_{country}.eps'
    plt.savefig(fig_path, bbox_inches='tight')
    # print(f'{scoring_folder=}')

    # Show the plot (optional)
    plt.show()


def print_save(df_ps, scoring_folder, name, print_=True):

    if print_:
        print(round(df_ps,1))
    # Save the CSV file
    csv_file_path = f'{scoring_folder}/{name}.csv'
    df_ps.to_csv(csv_file_path, index=True)


def save_settings(country, map_settings, scoring_folder):

    df = pd.DataFrame(map_settings)
    csv_file_path = f'{scoring_folder}/Settings.csv'
    df.to_csv(csv_file_path, index=False)


def get_purpose_scores(purposes_scoring, input_analysis_scoring, map_settings, ps, df_val_metrics):

    df_ps = pd.DataFrame(columns=purposes_scoring)
    df_input_analysis = pd.DataFrame()
    maps_list = list(map_settings.keys())
    maps_list = [map_+'_HF' for map_ in maps_list]
    
    for map_setting in  map_settings:

        df = pd.DataFrame(columns=purposes_scoring)
        # purpose_scores = {}
        if map_setting+'_HF' not in df_input_analysis.columns: df_input_analysis[map_setting+'_HF'] = pd.NA

        # Scores offi, curr, finer, mult
        pressures = list(settings.purpose_layers[map_setting]['pressures'].keys())

        for pressure in pressures:

            # Get scores by pressure
            if pressure not in df_input_analysis.columns: df_input_analysis[pressure] = pd.NA
            purp_dict, dataset_scores = calculate_scores(pressure, map_setting, ps, settings,
                                         purposes_scoring, input_analysis_scoring)
            df.loc[pressure] =[purp_dict[purp] for purp in purposes_scoring]
            
            # Input analysis
            # Drop complete and accurate, add only if not there yet, fill with 'Yes'
            dataset_scores2 = dataset_scores.drop(['Accurate', 'Complete'], axis=1)
            char_list = dataset_scores2.columns.tolist()
            df2_unique_rows = dataset_scores2.loc[dataset_scores2.index.difference(df_input_analysis.index)]
            df_input_analysis = pd.concat([df_input_analysis, df2_unique_rows])
            df_input_analysis.loc[dataset_scores2.index, map_setting+'_HF'] = 'Yes'
            df_input_analysis.loc[dataset_scores2.index, pressure] = 'Yes'
                    
        # # Possible plots
        # plot_by_dataset(purpose_scores, map_setting)

        # Calculate Indirect pressure scores as the average of the components:
        # Built_Environments, Land_Cover, Roads_Railways, Rivers
        indirect_pressures_list = ['Built_Environments', 'Land_Cover', 'Roads_Railways']#, 'Indirect_pressure'
        cols_to_change = ['Fine-resolution', 'Nationally-validated',
               'Internationally-comparable', 'Multitemporality', 'Current',]
        selected_df = df.loc[indirect_pressures_list]
        selected_df[cols_to_change] = selected_df[cols_to_change].fillna(0)
        indirect_average_row = selected_df.mean()
        df.loc['Indirect_pressure'] = indirect_average_row
        
        # Use groupby to group by each column and calculate the average
        averages_dict = {column: df[column].mean(skipna=True) for column in df.columns}

        values = []
        for purpose in purposes_scoring:
            if purpose in averages_dict:
                values.append(averages_dict[purpose])

        df_ps.loc[map_setting] = values
        
    # Restructure and save data for input analysis
    df_input_analysis = df_input_analysis[df_input_analysis['Source']!='derived']
    df_input_analysis.fillna(0, inplace=True)
    # df_input_analysis['average'] = df_input_analysis[char_list].mean(axis=1)
    df_input_analysis = reorder_columns(df_input_analysis, maps_list, order='last')
    df_input_analysis = reorder_columns(df_input_analysis, char_list, order='first')
    name = f'Input_analysis_dataset_scores_{country}'
    print_save(df_input_analysis, scoring_folder, name, print_=False)
    
    # Remove indirect from input analysis as it was not a collected dataset
    pressures_input = [pr for pr in pressures if pr!='Indirect_pressure']
    # Pivot tables for heatmaps\
    # Remove accurate and complete as they are part of input analysis
    chars_list = [char for char in purposes_scoring+input_analysis_scoring if char not in ['Accurate', 'Complete']]
    # df_input_analysis_NonOff = df_input_analysis[df_input_analysis['Nationally-validated']!=3]
    # df_input_analysis_Off = df_input_analysis[df_input_analysis['Nationally-validated']==3]
    df_pivot_pressures = pivot_table(df_input_analysis, pressures_input, chars_list, source=False)
    df_pivot_sources = pivot_table(df_input_analysis, ['Source'], chars_list, source=True)
    # df_pivot_pressures_NonOff = pivot_table(df_input_analysis_NonOff, pressures_input, chars_list)
    # df_pivot_pressures_Off = pivot_table(df_input_analysis_Off, pressures_input, chars_list)
    name_pres = f'Input_analysis_heatmap_values_pressures_{country}'
    print_save(df_pivot_pressures, scoring_folder, name_pres, print_=False)
    name_sour = f'Input_analysis_heatmap_values_sources_{country}'
    print_save(df_pivot_sources, scoring_folder, name_sour, print_=False)
    # name_NonOff = f'Input_analysis_heatmap_values_pressures_{country}_NonOff'
    # print_save(df_pivot_pressures_NonOff, scoring_folder, name_NonOff, print_=False)
    # name_Off = f'Input_analysis_heatmap_values_pressures_{country}_Off'
    # print_save(df_pivot_pressures_Off, scoring_folder, name_Off, print_=False)
    # plot_input_analysis(df_pivot_pressures, pressures_input, maps_list)

    # Accuracy score
    sub_df = df_val_metrics[df_val_metrics['Country'] == settings.country].copy()
    sub_df['RMSE_norm'] = 1 - ((sub_df['RMSE'] - sub_df['RMSE'].min()) /
                               (sub_df['RMSE'].max() - sub_df['RMSE'].min()))
    sub_df['Kappa_norm'] = (sub_df['Kappa'] - sub_df['Kappa'].min()) /\
        (sub_df['Kappa'].max() - sub_df['Kappa'].min())
    sub_df['R2_norm'] = (sub_df['R2'] - sub_df['R2'].min()) /\
        (sub_df['R2'].max() - sub_df['R2'].min())

    for map_setting in map_settings:
        df_2 = sub_df.loc[[map_setting]]
        df_ps.loc[map_setting]['Accurate'] = df_2['RMSE_norm'] + \
            df_2['Kappa_norm'] + df_2['R2_norm']

    # Completion score
    comp_df = pd.DataFrame(index=(list(map_settings.keys())), columns=['Pressures', 'Categories'])
    for map_setting in  map_settings:
        pressures, numb_categories = 0, 0
        for pressure in settings.purpose_layers[map_setting]['pressures']:
            if settings.purpose_layers[map_setting]['pressures'][pressure]['datasets']:
                pressures += 1
                numb_categories += settings.purpose_layers[map_setting]['pressures'][pressure]['numb_categories']
        comp_df.loc[map_setting]['Pressures'] = pressures
        comp_df.loc[map_setting]['Categories'] = numb_categories

    comp_df['Pressures_norm'] = comp_df['Pressures'] / comp_df['Pressures'].max()
    comp_df['Categories_norm'] = comp_df['Categories'] / comp_df['Categories'].max()
    
    # title = 'Completion'
    # keep_fields = ['Pressures_norm', 'Categories_norm']
    # bar_plot(comp_df, title, keep_fields=keep_fields)

    for map_setting in map_settings:
        df_ps.loc[map_setting]['Complete'] = \
            (1.5 * comp_df.loc[map_setting]['Pressures_norm']) +\
                (1.5 * comp_df.loc[map_setting]['Categories_norm'])
                
    df_ps['average'] = df_ps.mean(numeric_only=True, axis=1)
    name = f'Purposes_scores_dataframe_{country}'
    print_save(df_ps, scoring_folder, name)

    return df_ps


#######################################################################
if __name__ == "__main__":
#######################################################################
# Settings

    # Characteristics to score
    # Results analysis
    purposes_scoring = [
        'Accurate',
        'Fine-resolution',
        'Nationally-validated',
        'Internationally-comparable',
        'Multitemporality',
        'Current',
        'Complete',
        ]
    # Input analysis
    input_analysis_scoring = [
        'Accuracy_as_input',
        'Sustained_input',
        'Well_docmted_input',
        'User_friendly_input',
        ]
        
    # Settings
    ps = {
        'null': 0,
        'low': 1,
        # 'low': .5,
        'med': 2,
        'high': 3,
        }

    countries_to_process = ['Peru', 'Ecuador']
    # countries_to_process = ['Ecuador']
    
    for c2p in countries_to_process:
        
        if c2p=='Peru':

            # Main folder on the same level as the scripts. Keep format '/folder//'
            country_processing = 'Peru_HH'
            # Purposes maps
            map_settings = {
                'SDG15': ['Pe_20241012_162237_SDG15_Peru_IGN_30m', '#1ABD1A', 's'],
                'Multitemporal': ['Pe_20241012_204320_Multitemporal_Peru_IGN_30m', '#1395D4', '^'],
                'Official': ['Pe_20241013_004303_Official_Peru_IGN_30m', '#D4AF13', 'o'],
                }
            fig_letter = 'a)'
            # fig_letter = None
    
        if c2p=='Ecuador':
    
            # Main folder on the same level as the scripts. Keep format '/folder//'
            country_processing = 'Ecuador_HH'
            map_settings = {
                'SDG15': ['Ec_20241010_184840_SDG15_Limite_CONALI_2019_30m', '#1ABD1A', 's'],
                'Multitemporal': ['Ec_20241010_183814_Multitemporal_Limite_CONALI_2019_30m', '#1395D4', '^'],
                'Official': ['Ec_20241011_011155_Official_Limite_CONALI_2019_30m', '#D4AF13', 'o'],
                }
            fig_letter = 'b)'
            # fig_letter = None
    
        # General settings
        main_folder = os.getcwd() + f'/{country_processing}//'
        settings = GENERAL_SETTINGS(country_processing, main_folder)
        country = settings.country
        scoring_folder = main_folder + 'HF_maps/b06_HF_maps/0_Purposes_scoring//'
        if c2p=='Peru':
            scoring_folder_Pe = scoring_folder
            fig_letter_Pe = fig_letter
        if c2p=='Ecuador':
            scoring_folder_Ec = scoring_folder
            fig_letter_Ec = fig_letter
        if not os.path.exists(scoring_folder):
            os.makedirs(scoring_folder)
        save_settings(country, map_settings, scoring_folder)

    
# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
# Process

        # Start validation
        # Validation metrics
        df_val_metrics = get_validation_df(map_settings, main_folder)
    
        # # Dataframe for purposes scores
        df_ps = get_purpose_scores(purposes_scoring, input_analysis_scoring,
                                   map_settings, ps, df_val_metrics)
    
        # Create radar plot
        radar_plot(purposes_scoring, df_ps, country, scoring_folder, map_settings,
                   fig_letter=fig_letter)
        
    # print('''
           
    #       ''') 
        
    # Create heatmap graph for both countries
    # Saves same result in both folders
    heatm_versions = ['pressures', 'sources']
    for hv in heatm_versions:
        combined_heatmap(scoring_folder_Ec, scoring_folder_Pe, hv)
    # combined_heatmap(scoring_folder_Ec, scoring_folder_Pe)

CHECK THAT CHANGE IN YEARS IN SETTINGS DOES NOT IMPACT HERE
        
    