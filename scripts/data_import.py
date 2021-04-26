#!/usr/bin/env python
# coding: utf-8
import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
import psycopg2
from sqlalchemy import create_engine
import yaml
import sys, getopt
import logging
import logging.config
import zipfile

# Copyright 2021 National Technology & Engineering Solutions of Sandia, LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S. Government retains certain rights in this software.

# Function to convert a list to a string
def listToString(s):
    # initialize an empty string
    str1 = ""

    # traverse in the string
    for ele in s:
        str1 += ele

        # return string
    return str1


# unpack the dataframe and calculate quantities used in statistics
def calc_cycle_quantities(df):

    logging.info('calculate quantities used in statistics')

    tmp_arr = df[["test_time", "i", "v", "ah_c", 'e_c', 'ah_d', 'e_d', 'cycle_time']].to_numpy()

    start = 0
    last_time = 0
    last_i = 0
    last_v = 0
    last_ah_c = 0
    last_e_c = 0
    last_ah_d = 0
    last_e_d = 0
    initial_time = 0

    for x in tmp_arr:

        if start == 0:
            start += 1
            initial_time = x[0]
        else:
            if x[1] >= 0:
                x[3] = (x[0]-last_time)*(x[1]+last_i)*0.5+last_ah_c
                x[4] = (x[0]-last_time)*(x[1]+last_i)*0.5*(x[2]+last_v)*0.5+last_e_c
            elif x[1] <= 0:
                x[5] = (x[0] - last_time) * (x[1] + last_i) * 0.5 + last_ah_d
                x[6] = (x[0] - last_time) * (x[1] + last_i) * 0.5 * (x[2] + last_v) * 0.5 + last_e_d

        x[7] = x[0] - initial_time

        last_time = x[0]
        last_i = x[1]
        last_v = x[2]
        last_ah_c = x[3]
        last_e_c = x[4]
        last_ah_d = x[5]
        last_e_d = x[6]

    df_tmp = pd.DataFrame(data=tmp_arr[:, [3]], columns=["ah_c"])
    df_tmp.index += df.index[0]
    df['ah_c'] = df_tmp['ah_c']/3600.0

    df_tmp = pd.DataFrame(data=tmp_arr[:, [4]], columns=["e_c"])
    df_tmp.index += df.index[0]
    df['e_c'] = df_tmp['e_c']/3600.0

    df_tmp = pd.DataFrame(data=tmp_arr[:, [5]], columns=["ah_d"])
    df_tmp.index += df.index[0]
    df['ah_d'] = -df_tmp['ah_d']/3600.0

    df_tmp = pd.DataFrame(data=tmp_arr[:, [6]], columns=["e_d"])
    df_tmp.index += df.index[0]
    df['e_d'] = -df_tmp['e_d']/3600.0

    df_tmp = pd.DataFrame(data=tmp_arr[:, [7]], columns=["cycle_time"])
    df_tmp.index += df.index[0]
    df['cycle_time'] = df_tmp['cycle_time']

    return df


# calculate statistics and cycle time
def calc_stats(df_t):

    logging.info('calculate cycle time and cycle statistics')
    df_t['cycle_time'] = 0

    no_cycles = int(df_t['cycle_index'].max())

    # Initialize the cycle_data time frame
    a = [0 for x in range(no_cycles)]  # using loops

    df_c = pd.DataFrame(data=a, columns=["cycle_index"])

    df_c['cell_id'] = df_t['cell_id']
    df_c['cycle_index'] = 0
    df_c['v_max'] = 0
    df_c['i_max'] = 0
    df_c['v_min'] = 0
    df_c['i_min'] = 0
    df_c['ah_c'] = 0
    df_c['ah_d'] = 0
    df_c['e_c'] = 0
    df_c['e_d'] = 0
    df_c['v_c_mean'] = 0
    df_c['v_d_mean'] = 0
    df_c['test_time'] = 0
    df_c['ah_eff'] = 0
    df_c['e_eff'] = 0

    for c_ind in df_c.index:
        x = c_ind + 1

        df_f = df_t[df_t['cycle_index'] == x]

        df_f['ah_c'] = 0
        df_f['e_c'] = 0
        df_f['ah_d'] = 0
        df_f['e_d'] = 0

        if not df_f.empty:

            try:

                df_c.iloc[c_ind, df_c.columns.get_loc('cycle_index')] = x

                df_c.iloc[c_ind, df_c.columns.get_loc('v_max')] = df_f.loc[df_f['v'].idxmax()].v
                df_c.iloc[c_ind, df_c.columns.get_loc('v_min')] = df_f.loc[df_f['v'].idxmin()].v

                df_c.iloc[c_ind, df_c.columns.get_loc('i_max')] = df_f.loc[df_f['i'].idxmax()].i
                df_c.iloc[c_ind, df_c.columns.get_loc('i_min')] = df_f.loc[df_f['i'].idxmin()].i

                df_c.iloc[c_ind, df_c.columns.get_loc('test_time')] = df_f.loc[df_f['test_time'].idxmax()].test_time

                df_f['dt'] = df_f['test_time'].diff() / 3600.0
                df_f_c = df_f[df_f['i'] > 0]
                df_f_d = df_f[df_f['i'] < 0]

                df_f = calc_cycle_quantities(df_f)

                df_t.loc[df_t.cycle_index == x, 'cycle_time'] = df_f['cycle_time']
                df_t.loc[df_t.cycle_index == x, 'ah_c'] = df_f['ah_c']
                df_t.loc[df_t.cycle_index == x, 'e_c'] = df_f['e_c']
                df_t.loc[df_t.cycle_index == x, 'ah_d'] = df_f['ah_d']
                df_t.loc[df_t.cycle_index == x, 'e_d'] = df_f['e_d']

                df_c.iloc[c_ind, df_c.columns.get_loc('ah_c')] = df_f['ah_c'].max()
                df_c.iloc[c_ind, df_c.columns.get_loc('ah_d')] = df_f['ah_d'].max()
                df_c.iloc[c_ind, df_c.columns.get_loc('e_c')] = df_f['e_c'].max()
                df_c.iloc[c_ind, df_c.columns.get_loc('e_d')] = df_f['e_d'].max()

                df_c.iloc[c_ind, df_c.columns.get_loc('v_c_mean')] = df_f_c['v'].mean()
                df_c.iloc[c_ind, df_c.columns.get_loc('v_d_mean')] = df_f_d['v'].mean()

                if df_c.iloc[c_ind, df_c.columns.get_loc('ah_c')] == 0:
                    df_c.iloc[c_ind, df_c.columns.get_loc('ah_eff')] = 0
                else:
                    df_c.iloc[c_ind, df_c.columns.get_loc('ah_eff')] = df_c.iloc[c_ind, df_c.columns.get_loc('ah_d')] / \
                                                                       df_c.iloc[c_ind, df_c.columns.get_loc('ah_c')]

                if df_c.iloc[c_ind, df_c.columns.get_loc('e_c')] == 0:
                    df_c.iloc[c_ind, df_c.columns.get_loc('e_eff')] = 0
                else:
                    df_c.iloc[c_ind, df_c.columns.get_loc('e_eff')] = df_c.iloc[c_ind, df_c.columns.get_loc('e_d')] / \
                                                                      df_c.iloc[c_ind, df_c.columns.get_loc('e_c')]

            except Exception as e:
                logging.info("Exception @ x: " + str(x))
                logging.info(e)

    logging.info("cycle: " + str(x))

    df_cc = df_c[df_c['cycle_index'] > 0]
    df_tt = df_t[df_t['cycle_index'] > 0]

    return df_cc, df_tt


# import data from Arbin-generated Excel files
def read_timeseries_arbin(cell_id, file_path):

    # the importer can read Excel worksheets with the Channel number from Arbin files.
    # it assumes column names generated by the Arbin:
    # Cycle_Index -> cycle_index
    # Test_Time(s) -> test_time
    # Current(A) -> i
    # Voltage(V) -> v
    # Date_Time -> date_time

    logging.info('adding files')

    listOfFiles = glob.glob(file_path + '*.xls*')

    for i in range(len(listOfFiles)):
        listOfFiles[i] = listOfFiles[i].replace(file_path[:-1], '')

    logging.info('list of files to add: ' + str(listOfFiles))

    df_file = pd.DataFrame(listOfFiles, columns=['filename'])

    df_file.sort_values(by=['filename'], inplace=True)

    if df_file.empty:
        return

    df_file['cell_id'] = cell_id

    df_tmerge = pd.DataFrame()

    # Loop through all the Excel test files
    for ind in df_file.index:

        filename = df_file['filename'][ind]
        cellpath = file_path + filename
        timeseries = ""

        logging.info('processing file: ' + filename)

        if os.path.exists(cellpath):
            df_cell = pd.read_excel(cellpath, None)
            # Find the time series sheet in the excel file
            for k in df_cell.keys():
                if "hannel" in k:
                    logging.info("file: " + filename + " sheet:" + str(k))
                    timeseries = k

                    df_time_series_file = df_cell[timeseries]

                    df_time_series = pd.DataFrame()

                    df_time_series['cycle_index_file'] = df_time_series_file['Cycle_Index']
                    df_time_series['test_time'] = df_time_series_file['Test_Time(s)']
                    df_time_series['i'] = df_time_series_file['Current(A)']
                    df_time_series['v'] = df_time_series_file['Voltage(V)']
                    df_time_series['date_time'] = df_time_series_file['Date_Time']
                    df_time_series['filename'] = filename

                    df_time_series['ah_c'] = 0
                    df_time_series['e_c'] = 0
                    df_time_series['ah_d'] = 0
                    df_time_series['e_d'] = 0
                    df_time_series['cell_id'] = cell_id
                    df_time_series['cycle_index'] = 0
                    df_time_series['cycle_time'] = 0

                    if df_tmerge.empty:
                        df_tmerge = df_time_series
                    else:
                        df_tmerge = df_tmerge.append(df_time_series, ignore_index=True)

    return df_tmerge


# sort data imported to insure cycle index and test times are correctly calculated
def sort_timeseries(df_tmerge):
    # Arrange the data by date time first, then by test time
    # Rebuild Cycle Index and test time to increment from file to file
    # This method does not depend on data from a specific testers

    logging.info('sorting timeseries dataframe')

    if not df_tmerge.empty:

        df_t = df_tmerge.sort_values(by=['date_time'])
        df_t = df_t.reset_index(drop=True)

        cycles = df_t[["cycle_index_file", "cycle_index", "filename", "test_time"]].to_numpy()

        max_cycle = 1
        past_index = 1
        max_time = 0
        last_file = ""
        delta_t = 0
        start = 0

        for x in cycles:

            if start == 0:
                last_file = x[2]
                start += 1

            if x[2] != last_file:
                delta_t = max_time
                x[3] += delta_t
                last_file = x[2]
            else:
                x[3] += delta_t
                max_time = x[3]
                last_file = x[2]

            if x[0] < max_cycle:

                if past_index == x[0]:
                    past_index = x[0]
                    x[1] = max_cycle
                else:
                    past_index = x[0]
                    x[1] = max_cycle + 1
                    max_cycle = x[1]

            else:
                past_index = x[0]
                max_cycle = x[0]
                x[1] = x[0]

        df_tmp = pd.DataFrame(data=cycles[:, [1]], columns=["cycle_index"])
        df_t['cycle_index'] = df_tmp['cycle_index']

        df_tmp = pd.DataFrame(data=cycles[:, [3]], columns=["test_time"])
        df_t['test_time'] = pd.to_numeric(df_tmp['test_time'])

        df_ts = df_t.sort_values(by=['test_time'])

        # Remove quantities only needed to tag files
        df_ts.drop('filename', axis=1, inplace=True)
        df_ts.drop('cycle_index_file', axis=1, inplace=True)

        return df_ts


# Build cell metadata
def populate_metadata(df_c_md):

    # Build cell metadata
    df_cell_md = pd.DataFrame()
    df_cell_md['cell_id'] = [df_c_md['cell_id']]
    df_cell_md['anode'] = [df_c_md['anode']]
    df_cell_md['cathode'] = [df_c_md['cathode']]
    df_cell_md['source'] = [df_c_md['source']]
    df_cell_md['ah'] = [df_c_md['ah']]
    df_cell_md['form_factor'] = [df_c_md['form_factor']]

    # Build test metadata
    df_test_md = pd.DataFrame()
    df_test_md['cell_id'] = [df_c_md['cell_id']]
    df_test_md['crate_c'] = [df_c_md['crate_c']]
    df_test_md['crate_d'] = [df_c_md['crate_d']]
    df_test_md['soc_max'] = [df_c_md['soc_max']]
    df_test_md['soc_min'] = [df_c_md['soc_min']]

    return df_cell_md, df_test_md


# delete records (call with caution)
def delete_records(cell_id, conn):
    # this method will delete data for a cell_id. Use with caution as there is no undo
    db_conn = psycopg2.connect(conn)
    curs = db_conn.cursor()

    curs.execute("delete from timeseries_data where cell_id='" + cell_id + "'")
    curs.execute("delete from cycle_data where cell_id='" + cell_id + "'")
    curs.execute("delete from cell_metadata where cell_id='" + cell_id + "'")
    curs.execute("delete from test_metadata where cell_id='" + cell_id + "'")

    db_conn.commit()
    curs.close()
    db_conn.close()

    return


# add cells to the database
def add_cells(cell_list, conn, save, plot, path, slash):
    # The importer expects an Excel file with cell and test information
    # The file contains one row per cell

    logging.info('add cells')
    df_excel = pd.read_excel(cell_list)

    # Process one cell at the time
    for ind in df_excel.index:

        cell_id = df_excel['cell_id'][ind]
        file_id = df_excel['file_id'][ind]

        logging.info("add file: " + file_id + " cell: " + cell_id)

        df_tmp = df_excel.iloc[ind]
        df_cell_md, df_test_md = populate_metadata(df_tmp)

        # Unzip the data in a folder with the same name of the file_id
        with zipfile.ZipFile(path + file_id + '.zip', 'r') as zip_ref:
            zip_ref.extractall(path + file_id)

        # Read time series data: Excel files from Arbin tester
        # Modify this method to add more testers
        file_path = path + file_id + slash

        # importer specific to the Arbin file (TODO)
        df_merge = read_timeseries_arbin(cell_id, file_path)

        # Sort the timeseries data and rebuild cycle index and test time
        df_ts = sort_timeseries(df_merge)

        # Calculate statistics and prepare the dataframes for saving
        df_cycle_data, df_timeseries_data = calc_stats(df_ts)

        # Useful flag during testing
        if plot:
            df_cycle_data.plot(x='cycle_index', y='ah_c')
            df_cycle_data.plot(x='cycle_index', y='ah_d')
            df_cycle_data.plot(x='cycle_index', y='e_c')
            df_cycle_data.plot(x='cycle_index', y='e_d')
            plt.show()

        # Controls when data is saved to the database
        if save:
            engine = create_engine(conn)
            logging.info('save cell metadata')
            df_cell_md.to_sql('cell_metadata', con=engine, if_exists='append', chunksize=1000, index=False)
            logging.info('save test metadata')
            df_test_md.to_sql('test_metadata', con=engine, if_exists='append', chunksize=1000, index=False)
            logging.info('save cycle data')
            df_cycle_data.to_sql('cycle_data', con=engine, if_exists='append', chunksize=1000, index=False)
            logging.info('save timeseries data')
            df_timeseries_data.to_sql('timeseries_data', con=engine, if_exists='append', chunksize=1000, index=False)


# generate csv files with cycle data
def generate_cycle_data(cell_id, conn, path):

    # generate cycle data in csv format

    logging.info('export cell cycle data to csv files')

    sql_str = """select 
        cycle_index as "Cycle_Index", 
        round(test_time,3) as "Test_Time (s)",
        round(i_min,3) as "Min_Current (A)", 
        round(i_max,3) as "Max_Current (A)", 
        round(v_min,3) as "Min_Voltage (V)", 
        round(v_max,3) as "Max_Voltage (V)", 
        round(ah_c,3) as "Charge_Capacity (Ah)", 
        round(ah_d,3) as "Discharge_Capacity (Ah)", 
        round(e_c,3) as "Charge_Energy (Wh)", 
        round(e_d,3)  as "Discharge_Energy (Wh)" 
      from cycle_data where cell_id='""" + cell_id + """' order by cycle_index"""

    df = pd.read_sql(sql_str[0], conn)

    cell_id_to_file = cell_id[0].replace(r'/', '-')
    csv = path + cell_id_to_file + '_cycle_data.csv'
    df.to_csv(csv, encoding='utf-8', index=False)


# generate csv files with time series data
def generate_timeseries_data(cell_id, conn, path):

    # generate timeseries data

    logging.info('export cell timeseries data to csv files')

    sql_str = """select 
          date_time as "Date_Time",
          round(test_time,3) as "Test_Time (s)", 
          cycle_index as "Cycle_Index", 
          round(i,3) as "Current (A)",
          round(v,3) as "Voltage (V)",
          round(ah_c,3) as "Charge_Capacity (Ah)", 
          round(ah_d,3) as "Discharge_Capacity (Ah)", 
          round(e_c,3) as "Charge_Energy (Wh)", 
          round(e_d,3) as "Discharge_Energy (Wh)",
          round(temp_1,3) as "Environment_Temperature (C)",
          round(temp_2,3) as "Cell_Temperature (C)"
      from timeseries_data where cell_id='""" + cell_id + """' order by test_time"""

    df = pd.read_sql(sql_str[0], conn)

    cell_id_to_file = cell_id[0].replace(r'/', '-')
    csv = path + cell_id_to_file + '_timeseries_data.csv'
    df.to_csv(csv, encoding='utf-8', index=False)


# generate csv files with time series and cycle data
def export_cells(cell_list, conn, path):

    # export data from the cell list

    logging.info('export cell data to csv files')
    df_excel = pd.read_excel(cell_list)

    # Process one cell at the time
    for ind in df_excel.index:
        cell_id_try = df_excel['cell_id'][ind]
        sql = "select * from cell_metadata where cell_id='" + cell_id_try + "'"
        df_tmp = pd.read_sql(sql, conn)

        # if the cell exist, then update, otherwise skip
        if not df_tmp.empty:

            cell_id = df_tmp['cell_id']
            generate_cycle_data(cell_id, conn, path)
            generate_timeseries_data(cell_id, conn, path)

    return;


# add new calculated quantities to cells previously imported, or update existing calculated statistics
def update_cells(cell_list, conn, save, plot):

    logging.info('update cell data')

    # The importer expects an Excel file with the cell id and test information
    # The file contains one row per cell
    df_excel = pd.read_excel(cell_list)

    # Process one cell at the time
    for ind in df_excel.index:

        cell_id_try = df_excel['cell_id'][ind]
        sql = "select * from cell_metadata where cell_id='" + cell_id_try + "'"
        df_try = pd.read_sql(sql, conn)

        # if the cell exist, then update, otherwise skip
        if not df_try.empty:

            df_tmp = df_excel.iloc[ind]
            df_cell_md, df_test_md = populate_metadata(df_tmp)

            cell_id = df_tmp['cell_id']
            logging.info("update:" + cell_id)

            sql = "select * from timeseries_data where cell_id='" + cell_id + "' order by test_time"
            df_ts = pd.read_sql(sql, conn)

            df_cycle_data, df_timeseries_data = calc_stats(df_ts)

            delete_records(cell_id, conn)

            # Useful flag during testing
            if plot:
                df_cycle_data.plot(x='cycle_index', y='ah_c')
                df_cycle_data.plot(x='cycle_index', y='ah_d')
                plt.show()

            # Controls when data is saved to the database
            if save:
                engine = create_engine(conn)
                logging.info('save cell metadata')
                df_cell_md.to_sql('cell_metadata', con=engine, if_exists='append', chunksize=1000, index=False)
                logging.info('save test metadata')
                df_test_md.to_sql('test_metadata', con=engine, if_exists='append', chunksize=1000, index=False)
                logging.info('save cycle data')
                df_cycle_data.to_sql('cycle_data', con=engine, if_exists='append', chunksize=1000, index=False)
                logging.info('save timeseries data')
                df_timeseries_data.to_sql('timeseries_data', con=engine, if_exists='append', chunksize=1000,
                                          index=False)

        else:
            logging.info("cell:" + cell_id_try + " not found")

    return


def main(argv):

    # command line variables that can be used to run from an IDE without passing arguments
    mode = 'env'
    path = r'C:\\Users\\vdeange\\Documents\\BA\\calce\\'

    # initializing the logger
    logging.basicConfig(format='%(asctime)s %(message)s', filename='blc-python.log', level=logging.DEBUG)
    logging.info('starting')

    try:
        opts, args = getopt.getopt(argv, "hm:p:", ["mode=", "path="])
    except getopt.GetoptError:
        print('run as: data_import.py -m <mode> -p <path>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('data_import.py -m <mode> -p <path>')
            sys.exit()
        elif opt in ("-m", "--mode"):
            mode = arg
        elif opt in ("-p", "--path"):
            path = arg

    # read database connection
    conn = ''
    try:
        env = yaml.safe_load(open('../env'))
        x = env.split(" ")
        for i in x:
            j = i.split("=")
            if j[0] == 'DATABASE_CONNECTION':
                conn =  j[1]
    except:
        print("Error opening env file:", sys.exc_info()[0])

    # read configuration values
    data = yaml.safe_load(open('battery-blc-library.yaml'))

    plot = data['environment']['PLOT']
    save = data['environment']['SAVE']
    style = data['environment']['STYLE']

    # use default if env file not there
    if conn == '':
        conn = data['environment']['DATABASE_CONNECTION']

    logging.info('command line: ' + str(opts))
    logging.info('configuration: ' + str(data))

    # needed to maintain compatibility with windows machines
    if style == 'unix':
        slash = "/"
    elif style == 'windows':
        slash = r'\\'

    # Mode of operation
    if mode == 'add':
        add_cells(path + "cell_list.xlsx", conn, save, plot, path, slash)
        logging.info('Done adding files')
    elif mode == 'update':
        update_cells(path + "cell_list.xlsx", conn, save, plot)
        logging.info('Done updating files')
    elif mode == 'export':
        export_cells(path + "cell_list.xlsx", conn, path)
        logging.info('Done exporting files')
    elif mode == 'env':
        logging.info('printing environment variables only')
        print("style: " + style)
        print("  -slash: " + slash)
        print("  -path: " + path)
        print("conn: " + conn)
        print("plot: " + str(plot))
        print("save: " + str(save))
    else:
        print('data_import.py -m <mode> -p <path>')


if __name__ == "__main__":
   main(sys.argv[1:])



