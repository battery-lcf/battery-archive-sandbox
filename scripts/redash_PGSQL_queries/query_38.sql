/*
Name: Filters: Anode
Data source: 1
Created By: admin
Last Update At: 2021-07-02T17:20:01.513Z
*/

select distinct anode as a, count(*) from cell_metadata group by a order by a