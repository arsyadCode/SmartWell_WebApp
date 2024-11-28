import pandas as pd
import numpy as np
import os, time, shutil
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt

def run_ml(filtered_df, start_date, end_date):
    folder_marker = 'export'
    if os.path.exists(folder_marker):
        for item in os.listdir(folder_marker):
            item_path = os.path.join(folder_marker, item)
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.unlink(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)

    matched_universal_values = filtered_df['Universal'].unique()
    dataset = filtered_df[filtered_df['Universal'].isin(matched_universal_values)]

    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    filtered_df['DATE'] = pd.to_datetime(filtered_df['DATE'])
    dataset['DATE'] = pd.to_datetime(dataset['DATE'])

    def label_mark(row):
        if pd.to_datetime(row['DATE']) <= end_date:
            return 'TRAIN'
        else:
            return 'TEST'

    dataset['mark'] = dataset.apply(label_mark, axis=1)

    ### ML SECTION ###
    train_well = dataset[dataset['mark'] == 'TRAIN']['Universal'].unique()
    test_well = dataset[dataset['mark'] == 'TEST']['Universal'].unique()
    blind_well = list(set(test_well) - set(train_well))
    dataset.loc[dataset['Universal'].isin(blind_well), 'mark'] = 'BLIND'

    blind_slice = dataset[dataset['Universal'].isin(blind_well)]
    first_slice = dataset[dataset['Universal'].isin(train_well)] 

    training_set = first_slice[first_slice['mark'] == 'TRAIN']
    testing_set = first_slice[first_slice['mark'] == 'TEST']

    predictors_features = ['WHP', 'WHT', 'CHOKE', 'EVENT', 'LAST_EVENT', 'EVENT_PLATFORM', 'LAST_EVENT_PLATFORM', 'NORM_PROD_DAYS']
    existing_features = [feature for feature in predictors_features if feature in filtered_df.columns]
    
    predictors = existing_features
    targets = ['OIL', 'WATER', 'GAS'] 

    train_y = training_set[targets]
    train_x = training_set[predictors]
    test_y = testing_set[targets]
    test_x = testing_set[predictors]
    blind_y = blind_slice[targets]
    blind_x = blind_slice[predictors]

    scaler = MinMaxScaler()
    train_X_scaled = scaler.fit_transform(train_x)
    test_X_scaled = scaler.transform(test_x)

    rf_model = RandomForestRegressor(n_estimators=500)
    rf_model.fit(train_X_scaled, train_y)

    train_score = rf_model.score(train_X_scaled, train_y)
    test_score = rf_model.score(test_X_scaled, test_y)

    test_y_predicted = rf_model.predict(test_X_scaled)
    test_y_predicted = pd.DataFrame(test_y_predicted, columns=targets)
    test_y_predicted.index = test_y.index

    train_y_predicted = rf_model.predict(train_X_scaled)
    train_y_predicted = pd.DataFrame(train_y_predicted, columns=targets)
    train_y_predicted.index = train_y.index

    blind_X_scaled = scaler.transform(blind_x)
    blind_y_predicted = rf_model.predict(blind_X_scaled)
    blind_y_predicted = pd.DataFrame(blind_y_predicted, columns=targets)
    blind_y_predicted.index = blind_x.index

    train_y_predicted['mark'] = 'TRAIN'
    test_y_predicted['mark'] = 'TEST'
    predicted = pd.concat([train_y_predicted, test_y_predicted], axis=0).sort_index()

    result_non_blind = pd.concat([first_slice[['Universal', 'DATE']], predicted], axis=1)
    result_blind = pd.concat([blind_slice[['Universal', 'DATE']], blind_y_predicted], axis=1)
    result_blind['mark'] = 'BLIND'
    result = pd.concat([result_non_blind, result_blind], axis=0).sort_index()

    actual = dataset[['Universal', 'DATE'] + targets].copy()
    actual['mark'] = result['mark']

    merged_df = pd.merge(result, dataset[['DATE', 'Universal', 'CHOKE']], on=['DATE', 'Universal'], how='left')
    condition = (merged_df['CHOKE'] == 0) & (merged_df['mark'].isin(['TEST', 'BLIND']))
    merged_df.loc[condition, targets] = 0
    merged_df.drop(columns=['CHOKE'], inplace=True)
    result.update(merged_df[targets])

    filtered = actual[['DATE'] + targets].copy()
    actual_platform = filtered.groupby('DATE').sum().reset_index()
    filtered = result[['DATE'] + targets].copy()
    result_platform = filtered.groupby('DATE').sum().reset_index()
    actual_platform['mark'] = actual_platform.apply(label_mark, axis=1)
    result_platform['mark'] = result_platform.apply(label_mark, axis=1)

    def rolling_within_group(data):
        return data[targets].rolling(window=7, min_periods=1).mean()

    grouped = result.groupby('Universal').apply(rolling_within_group, include_groups=False).reset_index(level=0, drop=True)
    result_rolling = pd.concat([result[['DATE', 'Universal', 'mark']], grouped], axis=1)

    ### ERROR SECTION ###
    save_dir = f'./{folder_marker}/1-Metrics'

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    absolute_error = pd.DataFrame(columns=result.columns)
    absolute_error[['Universal', 'DATE', 'mark']] = result[['Universal', 'DATE', 'mark']]

    for target in targets:
        absolute_error[target] = abs(result[target] - actual[target])

    absolute_error.to_csv(os.path.join(save_dir, 'absolute_error.csv'), index=False)
    relative_error = pd.DataFrame(columns=result.columns)
    relative_error[['Universal', 'DATE', 'mark']] = absolute_error[['Universal', 'DATE', 'mark']]

    for target in targets:
        relative_error[target] = absolute_error[target] / actual[target] * 100
    file_path = os.path.join(save_dir, 'MAE_combined.xlsx')

    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        for marker in result.mark.unique():
            filtered_df = absolute_error[absolute_error['mark'] == marker]
            pivot_table_mae = pd.pivot_table(filtered_df, values=targets, index='Universal', aggfunc='mean', margins=True, margins_name='Total')
            pivot_table_mae = pivot_table_mae.round(2)
            pivot_table_mae.to_excel(writer, sheet_name=marker, index=True)
    pivot_table_mae = pd.pivot_table(absolute_error, values=targets, index=['Universal', 'mark'], aggfunc='mean', margins=True, margins_name='Total')
    absolute_error_rolling = pd.DataFrame(columns=result_rolling.columns)
    absolute_error_rolling[['Universal', 'DATE', 'mark']] = result_rolling[['Universal', 'DATE', 'mark']]

    for target in targets:
        absolute_error_rolling[target] = abs(result_rolling[target] - actual[target])

    absolute_error_rolling.to_csv(os.path.join(save_dir, 'absolute_error_rolling.csv'), index=False)
    file_path = os.path.join(save_dir, 'MAE_combined_rolling.xlsx')

    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        for marker in result.mark.unique():
            filtered_df = absolute_error_rolling[absolute_error_rolling['mark'] == marker]
            pivot_table_mae_rolling = pd.pivot_table(filtered_df, values=targets, index='Universal', aggfunc='mean', margins=True, margins_name='Total')
            pivot_table_mae_rolling = pivot_table_mae_rolling.round(2)
            pivot_table_mae_rolling.to_excel(writer, sheet_name=marker, index=True)
    pivot_table_mae_rolling = pd.pivot_table(absolute_error_rolling, values=targets, index=['Universal', 'mark'], aggfunc='mean', margins=True, margins_name='Total')
    absolute_error_platform = pd.DataFrame(columns=result_platform.columns)
    absolute_error_platform[['DATE', 'mark']] = result_platform[['DATE', 'mark']]

    for target in targets:
        absolute_error_platform[target] = abs(result_platform[target] - actual_platform[target])

    absolute_error_platform.to_csv(os.path.join(save_dir, 'absolute_error_platform.csv'), index=False)


    ### PLOTTING SECTION ###
    test_df = pd.read_csv('./Data/test_df.csv')

    def plot_well_data(locpath, dataset, pivot_mae):
        save_dir = f'./{folder_marker}/{locpath}'
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        for well_name in dataset.Universal.unique():
            filtered_result = result[result['Universal'] == well_name]
            filtered_actual = actual[actual['Universal'] == well_name]
            filtered_test = test_df[test_df['Universal'] == well_name]

            fig, axs = plt.subplots(len(targets), 1, figsize=(len(targets) * 3, 10))

            for i, col_name in enumerate(targets):
                axs[i].plot(filtered_actual['DATE'], filtered_actual[col_name], label=f'{col_name} (Actual)')
                axs[i].scatter(filtered_test['DATE'], filtered_test[col_name], label=f'{col_name} (Well Test)', color='red', s=5, alpha=0.5)

                for mark in filtered_result['mark'].unique():
                    subset = filtered_result[filtered_result['mark'] == mark]
                    axs[i].plot(subset['DATE'], subset[col_name], label=f'{col_name} ({mark})')
                    mae = pivot_mae.loc[(well_name, mark), col_name]
                    if mark != 'TRAIN':
                        axs[i].fill_between(subset['DATE'], subset[col_name] - mae, subset[col_name] + mae, color='orange', alpha=0.1, label=f'Error band ±{mae:.2f}')

                axs[i].set_xlabel('DATE')
                axs[i].set_ylabel(col_name)
                axs[i].set_ylim(bottom=0)
                axs[i].legend()

            plt.suptitle(f'{well_name}')
            plt.tight_layout()
            plt.savefig(os.path.join(save_dir, f'{well_name}.png'))
            plt.close()

    plot_well_data('0-Result Overlay', dataset, pivot_table_mae)
    plot_well_data('0-Rolling Result Overlay', dataset, pivot_table_mae_rolling)

    ## PLOTTING VS SECTION ##
    def plot_vs_data(locpath, dataset, error_type, supptitle):
        save_dir = f'./{folder_marker}/1-Error {locpath}'
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        for well_name in dataset.Universal.unique():
            filtered_result = error_type[error_type['Universal'] == well_name]
            fig, axs = plt.subplots(len(targets), 1, figsize=(len(targets)*3, 10))

            for i, col_name in enumerate(targets):
                for mark in filtered_result['mark'].unique():
                    subset = filtered_result[filtered_result['mark'] == mark]
                    axs[i].plot(subset['DATE'], subset[col_name], label=f'{col_name} ({mark})')
                axs[i].set_xlabel('DATE')
                axs[i].set_ylabel(col_name)
                axs[i].set_ylim(bottom=0)
                if(locpath == 'MAPE vs Time'):
                    axs[i].axhline(y=10, color='r', linestyle='--', linewidth=2)
                    axs[i].set_yscale('log')
                    axs[i].set_ylim(bottom=0.1)
                axs[i].legend()

            plt.suptitle(f'{supptitle}: {well_name}')
            plt.tight_layout()
            plt.savefig(os.path.join(save_dir, f'{well_name}.png'))
            plt.close()

    plot_vs_data('MAPE vs Time', dataset, relative_error, 'MAPE(%)')
    plot_vs_data('vs Time', dataset, absolute_error, 'Absolute Error')
    plot_vs_data('vs Time (Rolling)', dataset, absolute_error_rolling, 'Absolute Error (Rolling)')

    ## PLOTTING VS SECTION II ##
    def plot_vs_data_2(locpath, dataset, supptitle):
        save_dir = f'./{folder_marker}/2-Actual vs {locpath}'
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        for well_name in dataset.Universal.unique():
            filtered_result = result[result['Universal'] == well_name]
            filtered_actual = actual[actual['Universal'] == well_name]
            fig, axs = plt.subplots(1, len(targets), figsize=(len(targets)*5, 5))

            for i, col_name in enumerate(targets):
                max_actual = np.max(filtered_actual[col_name])
                max_result = np.max(filtered_result[col_name])
                max_axis = np.max([max_result, max_actual])
                x = np.linspace(0, max_axis, 10)

                for mark in filtered_result['mark'].unique():
                    subset_result = filtered_result[filtered_result['mark'] == mark]
                    subset_actual = filtered_actual[filtered_actual['mark'] == mark]
                    axs[i].scatter(subset_actual[col_name], subset_result[col_name], label=f'{col_name} ({mark})')
                axs[i].plot(x, x, linestyle='--', color='r', linewidth=1)
                axs[i].set_xlabel('Actual')
                axs[i].set_ylabel('Prediction')
                axs[i].set_ylim(bottom=0, top=max_axis)
                axs[i].set_xlim(left=0, right=max_axis)
                axs[i].set_title(col_name)
                axs[i].legend()

            plt.suptitle(f'{supptitle}: {well_name}')
            plt.tight_layout()
            plt.savefig(os.path.join(save_dir, f'{well_name}.png'))
            plt.close()

    plot_vs_data_2('Prediction', dataset, 'Actual vs Prediction')

    return folder_marker