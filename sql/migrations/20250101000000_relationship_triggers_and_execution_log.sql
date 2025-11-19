-- Migration: Database triggers for automatic relationship linking and script execution log
-- This migration replaces the need to run relationship scripts manually
-- Created: 2025-01-01

-- ============================================================================
-- Script Execution Log Table
-- ============================================================================
-- Tracks which scripts have been executed to make them idempotent

create table if not exists script_execution_log (
    id uuid primary key default gen_random_uuid(),
    script_name text not null unique,
    executed_at timestamp not null default now(),
    execution_count int not null default 1,
    last_execution_at timestamp not null default now(),
    notes text,
    created_at timestamp not null default now(),
    updated_at timestamp not null default now()
);

create index if not exists idx_script_execution_log_script_name 
    on script_execution_log(script_name);

comment on table script_execution_log is 'Tracks script executions to enable idempotent script behavior';

-- ============================================================================
-- Helper Functions for Normalization
-- ============================================================================

-- Normalize branch name (matches Python logic)
create or replace function normalize_branch_name(name text)
returns text
language sql
immutable
as $$
    select lower(trim(regexp_replace(name, '\s+', ' ', 'g')))
$$;

comment on function normalize_branch_name is 'Normalizes branch names for matching (matches Python script logic)';

-- ============================================================================
-- Trigger Functions for Automatic Relationship Linking
-- ============================================================================

-- Auto-link LeadStatus to BookedOpportunities via quote_number
create or replace function auto_link_lead_status_to_booked_opportunity()
returns trigger
language plpgsql
security invoker
set search_path = ''
as $$
begin
    -- Only link if booked_opportunity_id is NULL and quote_number exists
    if new.booked_opportunity_id is null and new.quote_number is not null then
        select id into new.booked_opportunity_id
        from public.booked_opportunities
        where quote_number = new.quote_number
        limit 1;
    end if;
    
    return new;
end;
$$;

comment on function auto_link_lead_status_to_booked_opportunity is 'Automatically links LeadStatus to BookedOpportunities via quote_number on insert/update';

-- Auto-link LostLead to BookedOpportunities via quote_number
create or replace function auto_link_lost_lead_to_booked_opportunity()
returns trigger
language plpgsql
security invoker
set search_path = ''
as $$
begin
    -- Only link if booked_opportunity_id is NULL and quote_number exists
    if new.booked_opportunity_id is null and new.quote_number is not null then
        select id into new.booked_opportunity_id
        from public.booked_opportunities
        where quote_number = new.quote_number
        limit 1;
    end if;
    
    return new;
end;
$$;

comment on function auto_link_lost_lead_to_booked_opportunity is 'Automatically links LostLead to BookedOpportunities via quote_number on insert/update';

-- Auto-link BadLead to LeadStatus (via customer matching)
-- This is more complex, so we'll create a function that can be called
-- Note: This trigger runs AFTER insert/update to allow customer linking to happen first
create or replace function auto_link_badlead_to_leadstatus()
returns trigger
language plpgsql
security invoker
set search_path = ''
as $$
declare
    matched_lead_status_id uuid;
begin
    -- Only link if lead_status_id is NULL
    if new.lead_status_id is not null then
        return new;
    end if;
    
    -- Try to match via customer_id -> booked_opportunity -> lead_status
    if new.customer_id is not null then
        select ls.id into matched_lead_status_id
        from public.lead_status ls
        join public.booked_opportunities bo on ls.booked_opportunity_id = bo.id
        where bo.customer_id = new.customer_id
        order by ls.created_at asc
        limit 1;
        
        if matched_lead_status_id is not null then
            new.lead_status_id := matched_lead_status_id;
            return new;
        end if;
    end if;
    
    -- Try to match via email -> customer -> booked_opportunity -> lead_status
    if new.customer_email is not null then
        select ls.id into matched_lead_status_id
        from public.lead_status ls
        join public.booked_opportunities bo on ls.booked_opportunity_id = bo.id
        join public.customers c on bo.customer_id = c.id
        where c.email = new.customer_email
          and c.email is not null
        order by ls.created_at asc
        limit 1;
        
        if matched_lead_status_id is not null then
            new.lead_status_id := matched_lead_status_id;
            return new;
        end if;
    end if;
    
    -- Try to match via phone -> customer -> booked_opportunity -> lead_status
    if new.customer_phone is not null then
        select ls.id into matched_lead_status_id
        from public.lead_status ls
        join public.booked_opportunities bo on ls.booked_opportunity_id = bo.id
        join public.customers c on bo.customer_id = c.id
        where c.phone = new.customer_phone
          and c.phone is not null
        order by ls.created_at asc
        limit 1;
        
        if matched_lead_status_id is not null then
            new.lead_status_id := matched_lead_status_id;
            return new;
        end if;
    end if;
    
    return new;
end;
$$;

comment on function auto_link_badlead_to_leadstatus is 'Automatically links BadLead to LeadStatus via customer matching (email, phone, or customer_id)';

-- ============================================================================
-- Create Triggers
-- ============================================================================

-- Trigger for LeadStatus -> BookedOpportunity linking
drop trigger if exists trigger_auto_link_lead_status_to_booked_opportunity on public.lead_status;
create trigger trigger_auto_link_lead_status_to_booked_opportunity
    before insert or update on public.lead_status
    for each row
    execute function auto_link_lead_status_to_booked_opportunity();

-- Trigger for LostLead -> BookedOpportunity linking
drop trigger if exists trigger_auto_link_lost_lead_to_booked_opportunity on public.lost_leads;
create trigger trigger_auto_link_lost_lead_to_booked_opportunity
    before insert or update on public.lost_leads
    for each row
    execute function auto_link_lost_lead_to_booked_opportunity();

-- Trigger for BadLead -> LeadStatus linking
drop trigger if exists trigger_auto_link_badlead_to_leadstatus on public.bad_leads;
create trigger trigger_auto_link_badlead_to_leadstatus
    before insert or update on public.bad_leads
    for each row
    execute function auto_link_badlead_to_leadstatus();

-- ============================================================================
-- Helper Function for Script Execution Logging
-- ============================================================================

-- Function to log script execution (for use in Python scripts)
create or replace function log_script_execution(script_name_param text, notes_param text default null)
returns void
language plpgsql
security invoker
set search_path = ''
as $$
begin
    insert into public.script_execution_log (script_name, notes)
    values (script_name_param, notes_param)
    on conflict (script_name) do update
    set 
        execution_count = script_execution_log.execution_count + 1,
        last_execution_at = now(),
        updated_at = now(),
        notes = coalesce(notes_param, script_execution_log.notes);
end;
$$;

comment on function log_script_execution is 'Logs script execution for idempotency tracking';

-- Function to check if script has been executed
create or replace function script_already_executed(script_name_param text)
returns boolean
language sql
stable
as $$
    select exists (
        select 1 
        from public.script_execution_log 
        where script_name = script_name_param
    );
$$;

comment on function script_already_executed is 'Checks if a script has been executed before';

