/*
Name: Cell Stats V1
Data source: 1
Created By: admin
Last Update At: 2021-07-02T04:26:55.735Z
*/

SELECT
	cell_id,
	trunc(cycle_index,0) as cycle_index,  
	trunc(ah_c,3) as ah_c,  
	trunc(ah_d,3) as ah_d,  
	trunc(e_c,3) as e_c,  
	trunc(e_d,3) as e_d  
FROM cycle_data
where 
    cell_id IN ({{cell_id}}) and 
    MOD(cycle_index,{{step}})=0 
order by cycle_index, cell_id 
