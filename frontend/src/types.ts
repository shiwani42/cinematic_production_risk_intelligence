export type CrewMember = {
  role: string;
  department: string;
  call_time_24h: number;
  wrap_time_24h: number;
  consecutive_shoot_days: number;
  travel_to_set_km: number;
  location_elevation_m?: number;
  physically_demanding_role?: boolean;
  days_since_last_rest_day?: number;
};

export type Callsheet = {
  production?: string;
  shoot_date?: string;
  location?: string;
  crew: CrewMember[];
};

export type HazardRow = {
  id: string;
  category: string;
  subsection?: string;
  hazard: string;
  likelihood: string;
  consequence?: string;
  controls: string[];
  scene_refs?: number[];
  interaction_notes?: string[];
};

export type SceneRisk = {
  scene_number: number;
  slug_line?: string;
  adjusted_risk_score: number;
  risk_level: string;
  hazard_flags: string[];
  interaction_notes?: string[];
};

export type Fatigue = {
  crew_role: string;
  department: string;
  fatigue_score: number;
  risk_level: string;
  hours_on_set: number;
  top_contributing_factors: string[];
};

export type Brief = {
  meta: { production_title: string; location: string; shoot_date: string };
  executive_summary: {
    overall_risk: string;
    overall_label: string;
    one_liner: string;
    total_scenes_analysed: number;
    critical_scenes: number;
    crew_at_risk: number;
    average_scene_risk_score: number;
    highest_scene_risk_score: number;
  };
  scenes: SceneRisk[];
  risk_register: HazardRow[];
  risk_register_sections: { category: string; rows: HazardRow[] }[];
  crew_fatigue_summary: { all: Fatigue[]; critical: Fatigue[]; high_risk: Fatigue[] };
  location_intelligence: {
    location_name: string;
    location_type: string;
    elevation_m: number;
    weather?: { seasonal_summary?: string };
    emergency_services?: {
      nearest_trauma_center?: string;
      estimated_response_time_minutes?: number;
      cell_coverage?: string;
    };
    terrain_hazards?: string[];
  };
  emergency_reference: { nearest_trauma: string; response_time: string; on_set_protocol: string[] };
  action_items: { priority: string; action: string }[];
  disclaimer: string;
  agent_trace?: { agent: string; tool: string; detail: string }[];
  thesis?: {
    headline: string;
    do_not_roll: string;
    if_we_miss_this: string;
    location_brings: string[];
    production_brings: string[];
    collisions: { scene?: number; note: string; score?: number }[];
  };
};

export type Stack = {
  adk: boolean;
  adk_version: string;
  root_agent: string;
  model: string;
  sub_agents: string[];
  gemini_configured: boolean;
  apps: string[];
};

export type Step = "home" | "questions" | "hazards" | "report" | "intel";
export type Question = "who" | "what" | "where" | "when";

export type Who = { crew_size: string; key_roles: string; specialists: string; experience: string };
export type What = { production_type: string; activities: string; equipment: string; script_text: string };
export type Where = { environment: string };
export type When = { notes: string };
