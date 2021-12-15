/*
Name: Filters: Source
Data source: 1
Created By: admin
Last Update At: 2021-07-02T17:18:58.068Z
*/

select distinct source as a, count(*) from cell_metadata group by a order by a 