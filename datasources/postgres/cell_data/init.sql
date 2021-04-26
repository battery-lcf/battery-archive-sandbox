-- Copyright 2021 National Technology & Engineering Solutions of Sandia, LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S. Government retains certain rights in this software.
CREATE USER battery_datasource;
CREATE DATABASE public;
GRANT ALL PRIVILEGES ON DATABASE public TO battery_datasource;
-- Table: public.cell_metadata

-- DROP TABLE public.cell_metadata;

CREATE TABLE public.cell_metadata
(
    cathode character varying(50) COLLATE pg_catalog."default",
    anode character varying(50) COLLATE pg_catalog."default",
    source character varying(50) COLLATE pg_catalog."default",
    ah numeric,
    form_factor character varying(50) COLLATE pg_catalog."default",
    cell_id character varying(100) COLLATE pg_catalog."default"
)

TABLESPACE pg_default;

ALTER TABLE public.cell_metadata
    OWNER to postgres;
-- Index: idx_cell_metadata_cell_id

-- DROP INDEX public.idx_cell_metadata_cell_id;

CREATE INDEX idx_cell_metadata_cell_id
    ON public.cell_metadata USING btree
    (cell_id COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;


-- Table: public.test_metadata

-- DROP TABLE public.test_metadata;

CREATE TABLE public.test_metadata
(
    temp numeric,
    soc_max numeric,
    soc_min numeric,
    v_max numeric,
    v_min numeric,
    crate_c numeric,
    crate_d numeric,
    cell_id character varying(100) COLLATE pg_catalog."default"
)

TABLESPACE pg_default;

ALTER TABLE public.test_metadata
    OWNER to postgres;
-- Index: idx_test_metadata_cell_id

-- DROP INDEX public.idx_test_metadata_cell_id;

CREATE INDEX idx_test_metadata_cell_id
    ON public.test_metadata USING btree
    (cell_id COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;


-- Table: public.cycle_data

-- DROP TABLE public.cycle_data;

CREATE TABLE public.cycle_data
(
    v_max numeric,
    v_min numeric,
    ah_c numeric,
    ah_d numeric,
    e_c numeric,
    e_d numeric,
    i_max numeric,
    i_min numeric,
    v_c_mean numeric,
    v_d_mean numeric,
    e_eff numeric,
    ah_eff numeric,
    cycle_index numeric,
    test_time numeric,
    cell_id character varying(100) COLLATE pg_catalog."default"
)

TABLESPACE pg_default;

ALTER TABLE public.cycle_data
    OWNER to postgres;
-- Index: idx_cycle_data_cell_id

-- DROP INDEX public.idx_cycle_data_cell_id;

CREATE INDEX idx_cycle_data_cell_id
    ON public.cycle_data USING btree
    (cell_id COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;


-- Table: public.timeseries_data

-- DROP TABLE public.timeseries_data;

CREATE TABLE public.timeseries_data
(
    i numeric,
    v numeric,
    ah_c numeric,
    ah_d numeric,
    e_c numeric,
    e_d numeric,
    temp_1 numeric,
    temp_2 numeric,
    cycle_time numeric,
    date_time timestamp without time zone,
    cycle_index numeric,
    test_time numeric,
    cell_id character varying(100) COLLATE pg_catalog."default"
)

TABLESPACE pg_default;

ALTER TABLE public.timeseries_data
    OWNER to postgres;
-- Index: idx_timeseries_data_cell_id

-- DROP INDEX public.idx_timeseries_data_cell_id;

CREATE INDEX idx_timeseries_data_cell_id
    ON public.timeseries_data USING btree
    (cell_id COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;
