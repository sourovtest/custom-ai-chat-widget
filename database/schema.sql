/* Bootstrap schema. Apply future changes through reviewed, versioned migrations
   after backing up the database; do not use this file to reset existing data. */
CREATE TABLE IF NOT EXISTS chat_sessions (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    session_token VARCHAR(128) NOT NULL,
    ip_address VARCHAR(45) NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_chat_sessions_session_token (session_token),
    KEY idx_chat_sessions_created_at (created_at)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS chat_messages (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    session_id BIGINT UNSIGNED NOT NULL,
    sender_type VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_chat_messages_session_timestamp (session_id, timestamp, id),
    CONSTRAINT fk_chat_messages_session
        FOREIGN KEY (session_id) REFERENCES chat_sessions (id)
        ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS chatbot_rules (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    rule_name VARCHAR(255) NOT NULL,
    trigger_event VARCHAR(255) NOT NULL,
    action_type VARCHAR(100) NOT NULL,
    static_message TEXT NULL,
    assigned_role VARCHAR(255) NULL,
    trigger_config JSON NULL,
    priority SMALLINT UNSIGNED NOT NULL DEFAULT 100,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    execution_frequency VARCHAR(32) NOT NULL DEFAULT 'once_per_session',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_chatbot_rules_active_trigger_priority
        (is_active, trigger_event, priority)
) ENGINE=InnoDB;
