/*
Name: Cycle Quantities by step
Data source: 1
Created By: admin
Last Update At: 2021-07-02T17:18:42.396Z
*/

select * from 
(SELECT
	trunc(cycle_time,1) as cycle_time,
	trunc(v,3) as voltage,  
	trunc(cycle_index,0) as cycle_index,  
	case 
	    when i>0 then
	        trunc(ah_c,3)  
	    when i<0 then
	        trunc(ah_d,3)
	    end ah,
	case 
	    when i>0 then
	        cell_id || ' c: ' || cycle_index  
	    when i<0 then
	        cell_id || ' d: ' || cycle_index
	    end series
FROM timeseries_data
where 
    cell_id IN ({{cell_id}}) and 
    MOD(cycle_index,{{step}})=0 
order by cycle_index, series) as foo where series is not null     
