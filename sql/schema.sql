CREATE TABLE IF NOT EXISTS agent_outputs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_name TEXT NOT NULL,
    module_name TEXT NOT NULL,
    output_type TEXT NOT NULL,
    scope_type TEXT,
    scope_value TEXT,
    date_from TEXT NOT NULL,
    date_to TEXT NOT NULL,
    data_json TEXT NOT NULL,
    version TEXT,
    model_used TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS agent_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_name TEXT NOT NULL,
    run_type TEXT NOT NULL,
    model_used TEXT,
    tokens_used_input INTEGER DEFAULT 0,
    tokens_used_output INTEGER DEFAULT 0,
    estimated_cost REAL DEFAULT 0,
    duration_ms INTEGER DEFAULT 0,
    status TEXT NOT NULL,
    error_message TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS metrics_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_name TEXT NOT NULL,
    metric_group TEXT NOT NULL,
    channel TEXT,
    category TEXT,
    value REAL NOT NULL,
    date TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS system_health (
    component_name TEXT PRIMARY KEY,
    status TEXT NOT NULL,
    last_success_at TEXT,
    last_error_at TEXT,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS delivery_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_name TEXT NOT NULL,
    destination_type TEXT NOT NULL,
    destination_name TEXT NOT NULL,
    status TEXT NOT NULL,
    sent_at TEXT NOT NULL,
    error_message TEXT
);

CREATE TABLE IF NOT EXISTS bot_interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    channel_type TEXT,
    channel_name TEXT,
    question TEXT NOT NULL,
    response_summary TEXT,
    agent_used TEXT,
    model_used TEXT,
    created_at TEXT NOT NULL
);
