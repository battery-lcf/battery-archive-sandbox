/*
Name: Filters: Nominal Capacity (Ah)
Data source: 1
Created By: admin
Last Update At: 2021-07-02T17:19:14.665Z
*/

select distinct ah as a, count(*) from cell_metadata group by a order by a