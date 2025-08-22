-- setup.sql
-- Run as ACCOUNTADMIN role (trial account is fine).
-- Example region: AWS us-east-2 (Ohio).
-- Adjust database/warehouse names if needed.

------------------------------------------------------------
-- 1) Resource Monitors
-- Resource monitors help prevent cost overruns.
-- One monitor is monthly for the whole account,
-- another is daily for the warehouse.
------------------------------------------------------------

-- Monthly account-level resource monitor
CREATE OR REPLACE RESOURCE MONITOR RM_BUDGET_MONTHLY
  WITH CREDIT_QUOTA = 350
  FREQUENCY = MONTHLY
  START_TIMESTAMP = IMMEDIATELY
  TRIGGERS ON 75 PERCENT DO NOTIFY
           ON 85 PERCENT DO SUSPEND
           ON 95 PERCENT DO SUSPEND_IMMEDIATE;

-- Assign the monthly monitor to the account
ALTER ACCOUNT SET RESOURCE_MONITOR = RM_BUDGET_MONTHLY;

-- Daily warehouse-level resource monitor
CREATE OR REPLACE RESOURCE MONITOR RM_COVID_DAILY
  WITH CREDIT_QUOTA = 30
  FREQUENCY = DAILY
  START_TIMESTAMP = IMMEDIATELY
  TRIGGERS ON 75 PERCENT DO NOTIFY
           ON 85 PERCENT DO SUSPEND
           ON 95 PERCENT DO SUSPEND_IMMEDIATE;

------------------------------------------------------------
-- 2) Warehouse
-- Create a small warehouse for queries.
-- Auto-suspend after 60 seconds of inactivity,
-- auto-resume on next query.
------------------------------------------------------------
CREATE OR REPLACE WAREHOUSE WH_COVID
  WAREHOUSE_SIZE = 'XSMALL'
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE
  INITIALLY_SUSPENDED = TRUE
  RESOURCE_MONITOR = RM_COVID_DAILY;

------------------------------------------------------------
-- 3) Database and Schema
-- Create database for COVID analysis.
-- Schema "ANALYTICS" will hold processed data.
------------------------------------------------------------
CREATE OR REPLACE DATABASE DB_COVID;

USE DATABASE DB_COVID;

CREATE OR REPLACE SCHEMA ANALYTICS;

USE SCHEMA ANALYTICS;
