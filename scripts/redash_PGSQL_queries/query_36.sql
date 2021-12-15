/*
Name: Voltage and Current
Data source: 1
Created By: admin
Last Update At: 2021-07-02T17:20:14.719Z
*/

SELECT KEY || ': ' || r.cell_id AS series_1,
KEY || ' ' || cycle_index || ': ' || r.cell_id AS series_2,
              r.cycle_index,
              r.test_time,
              r.cycle_time,
              value
FROM
  (SELECT timeseries_data.cell_id,
          cycle_index,
          test_time,
          cycle_time,
          json_build_object('V', v, 'C', i) AS line
   FROM timeseries_data TABLESAMPLE BERNOULLI ({{sample}})
   WHERE cell_id IN ({{cell_id}})
     AND cycle_index IN ({{cycles}})) AS r
JOIN LATERAL json_each_text(r.line) ON (KEY ~ '[V,C]')
ORDER BY r.cell_id,
         r.test_time,
         r.cycle_time,
         KEY
