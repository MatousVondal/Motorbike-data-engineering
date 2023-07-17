CREATE OR REPLACE TABLE `my-data-project-392011.bike_analysis.dashboard_table` AS(
SELECT
  company_name,
  continent_name,
  country_name,
  body_type_name,
  transmission_type_name,
  manual_automat,
  year,
  model_name,
  CAST(price_usd AS INT) as price_usd,
  number_of_cylinders,
  horse_power_hp,
  torque_nm,
  cc,
  rpm,
  engine_type,
  looks,
  number_of_seating
FROM
  `my-data-project-392011.bike_analysis.fact_table` as f
JOIN
  `my-data-project-392011.bike_analysis.company_dim` as c 
  ON f.company_id = c.company_id
JOIN
  `my-data-project-392011.bike_analysis.body_type_dim` as b 
  ON f.body_type_id = b.body_type_id
JOIN
  `my-data-project-392011.bike_analysis.transmission_type_dim` as t 
  ON f.transmission_type_id = t.transmission_type_id
JOIN
  `my-data-project-392011.bike_analysis.engine_type_dim` as e 
  ON f.engine_type_id = e.engine_type_id
JOIN
  `my-data-project-392011.bike_analysis.drive_train_dim` as d
  ON f.drive_train_id = d.drive_train_id
)
