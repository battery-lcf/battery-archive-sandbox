/*
Name: Data Download
Data source: 1
Created By: admin
Last Update At: 2021-07-02T17:18:04.892Z
*/

select cell_id, REPLACE(cell_id, '/', '-' ), '_cycle_data.csv', '_timeseries.csv' from cell_metadata where cell_id IN ({{cell_id}})   