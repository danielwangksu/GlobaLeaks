PRAGMA foreign_keys = ON;

CREATE TABLE user (
    id VARCHAR NOT NULL,
    creation_date VARCHAR NOT NULL,
    username VARCHAR NOT NULL,
    password VARCHAR NOT NULL,
    salt VARCHAR NOT NULL,
    role VARCHAR NOT NULL CHECK (role IN ('admin', 'receiver')),
    state VARCHAR NOT NULL CHECK (state IN ('disabled', 'enabled')),
    last_login VARCHAR NOT NULL,
    last_update VARCHAR,
    language VARCHAR NOT NULL,
    timezone INTEGER DEFAULT 0,
    password_change_needed INTEGER NOT NULL,
    password_change_date VARCHAR NOT NULL,
    PRIMARY KEY (id),
    UNIQUE (username)
);

CREATE TABLE message (
    id VARCHAR NOT NULL,
    visualized INTEGER NOT NULL,
    creation_date VARCHAR NOT NULL,
    author VARCHAR NOT NULL,
    receivertip_id VARCHAR NOT NULL,
    type VARCHAR NOT NULL CHECK (type IN ('receiver', 'whistleblower' )),
    mark VARCHAR NOT NULL CHECK (mark IN ('not notified', 'notified', 'unable to notify', 'disabled', 'skipped')),
    content VARCHAR NOT NULL,
    FOREIGN KEY(receivertip_id) REFERENCES receivertip(id) ON DELETE CASCADE,
    PRIMARY KEY (id)
);

CREATE TABLE comment (
    id VARCHAR NOT NULL,
    creation_date VARCHAR NOT NULL,
    author VARCHAR NOT NULL,
    internaltip_id VARCHAR NOT NULL,
    type VARCHAR NOT NULL CHECK (type IN ('receiver', 'whistleblower', 'system')),
    mark VARCHAR NOT NULL CHECK (mark IN ('not notified', 'notified', 'unable to notify', 'disabled', 'skipped')),
    content VARCHAR NOT NULL,
    system_content BLOB,
    FOREIGN KEY(internaltip_id) REFERENCES internaltip(id) ON DELETE CASCADE,
    PRIMARY KEY (id)
);

CREATE TABLE context (
    id VARCHAR NOT NULL,
    creation_date VARCHAR NOT NULL,
    description BLOB NOT NULL,
    file_max_download INTEGER NOT NULL,
    last_update VARCHAR,
    name BLOB NOT NULL,
    tip_max_access INTEGER NOT NULL,
    tip_timetolive INTEGER NOT NULL,
    submission_timetolive INTEGER NOT NULL,
    receiver_introduction BLOB NOT NULL,
    select_all_receivers INTEGER NOT NULL,
    postpone_superpower INTEGER NOT NULL,
    can_delete_submission INTEGER NOT NULL,
    maximum_selectable_receivers INTEGER,
    show_small_cards INTEGER NOT NULL,
    show_receivers INTEGER NOT NULL,
    enable_private_messages INTEGER NOT NULL,
    presentation_order INTEGER,
    PRIMARY KEY (id)
);

CREATE TABLE internalfile (
    id VARCHAR NOT NULL,
    creation_date VARCHAR NOT NULL,
    content_type VARCHAR NOT NULL,
    file_path VARCHAR,
    mark VARCHAR NOT NULL CHECK (mark IN ('not processed', 'locked', 'ready', 'delivered')),
    name VARCHAR NOT NULL,
    description VARCHAR,
    size INTEGER NOT NULL,
    internaltip_id VARCHAR NOT NULL,
    FOREIGN KEY(internaltip_id) REFERENCES internaltip(id) ON DELETE CASCADE,
    PRIMARY KEY (id)
);

CREATE TABLE receiverfile (
    id VARCHAR NOT NULL,
    creation_date VARCHAR NOT NULL,
    file_path VARCHAR,
    size INTEGER NOT NULL,
    downloads INTEGER NOT NULL,
    last_access VARCHAR,
    internalfile_id VARCHAR NOT NULL,
    receiver_id VARCHAR NOT NULL,
    internaltip_id VARCHAR NOT NULL,
    receiver_tip_id VARCHAR NOT NULL,
    mark VARCHAR NOT NULL CHECK (mark IN ('not notified', 'notified', 'unable to notify', 'disabled', 'skipped')),
    status VARCHAR NOT NULL CHECK (status IN ('reference', 'encrypted', 'unavailable', 'nokey')),
    FOREIGN KEY(internalfile_id) REFERENCES internalfile(id) ON DELETE CASCADE,
    FOREIGN KEY(receiver_id) REFERENCES receiver(id) ON DELETE CASCADE,
    FOREIGN KEY(internaltip_id) REFERENCES internaltip(id) ON DELETE CASCADE,
    PRIMARY KEY (id)
);

CREATE TABLE internaltip (
    id VARCHAR NOT NULL,
    creation_date VARCHAR NOT NULL,
    access_limit INTEGER NOT NULL,
    download_limit INTEGER NOT NULL,
    expiration_date VARCHAR NOT NULL,
    wb_steps BLOB,
    last_activity VARCHAR,
    mark VARCHAR NOT NULL CHECK (mark IN ('submission', 'finalize', 'first')),
    context_id VARCHAR NOT NULL,
    FOREIGN KEY(context_id) REFERENCES context(id) ON DELETE CASCADE,
    PRIMARY KEY (id)
);

CREATE TABLE node (
    id VARCHAR NOT NULL,
    creation_date VARCHAR NOT NULL,
    description BLOB NOT NULL,
    presentation BLOB NOT NULL,
    footer BLOB NOT NULL,
    security_awareness_title BLOB NOT NULL,
    security_awareness_text BLOB NOT NULL,
    whistleblowing_question BLOB NOT NULL,
    whistleblowing_button BLOB NOT NULL,
    email VARCHAR NOT NULL,
    hidden_service VARCHAR NOT NULL,
    receipt_regexp VARCHAR NOT NULL,
    languages_enabled BLOB NOT NULL,
    default_language VARCHAR NOT NULL,
    default_timezone INTEGER DEFAULT 0,
    name VARCHAR NOT NULL,
    receipt_salt VARCHAR NOT NULL,
    public_site VARCHAR NOT NULL,
    stats_update_time INTEGER NOT NULL,
    last_update VARCHAR,
    maximum_namesize INTEGER NOT NULL,
    maximum_textsize INTEGER NOT NULL,
    maximum_filesize INTEGER NOT NULL,
    tor2web_admin INTEGER NOT NULL,
    tor2web_submission INTEGER NOT NULL,
    tor2web_receiver INTEGER NOT NULL,
    tor2web_unauth INTEGER NOT NULL,
    postpone_superpower INTEGER NOT NULL,
    can_delete_submission INTEGER NOT NULL,
    ahmia INTEGER NOT NULL,
    wizard_done INTEGER NOT NULL,
    exception_email VARCHAR NOT NULL,
    allow_unencrypted INTEGER NOT NULL,
    allow_iframes_inclusion INTEGER NOT NULL,
    disable_privacy_badge INTEGER NOT NULL,
    disable_security_awareness_badge INTEGER NOT NULL,
    disable_security_awareness_questions INTEGER NOT NULL,
    enable_custom_privacy_badge INTEGER NOT NULL DEFAULT 0,
    custom_privacy_badge_tor BLOB NOT NULL,
    custom_privacy_badge_none BLOB NOT NULL,
    header_title_homepage BLOB NOT NULL,
    header_title_submissionpage BLOB NOT NULL,
    landing_page VARCHAR NOT NULL CHECK (landing_page IN ('homepage', 'submissionpage')),
    PRIMARY KEY (id)
);

CREATE TABLE notification (
    id VARCHAR NOT NULL,
    creation_date VARCHAR NOT NULL,
    server VARCHAR,
    port INTEGER,
    password VARCHAR,
    username VARCHAR,
    source_name VARCHAR NOT NULL,
    source_email VARCHAR NOT NULL,
    security VARCHAR NOT NULL CHECK (security IN ('TLS', 'SSL')),
    encrypted_tip_template BLOB,
    encrypted_tip_mail_title BLOB,
    plaintext_tip_template BLOB,
    plaintext_tip_mail_title BLOB,
    encrypted_file_template BLOB,
    encrypted_file_mail_title BLOB,
    plaintext_file_template BLOB,
    plaintext_file_mail_title BLOB,
    encrypted_message_template BLOB,
    encrypted_message_mail_title BLOB,
    plaintext_message_template BLOB,
    plaintext_message_mail_title BLOB,
    encrypted_comment_template BLOB,
    encrypted_comment_mail_title BLOB,
    plaintext_comment_template BLOB,
    plaintext_comment_mail_title BLOB,
    admin_anomaly_template BLOB,
    admin_pgp_alert_mail_template BLOB,
    admin_pgp_alert_mail_title BLOB,
    pgp_alert_mail_template BLOB,
    pgp_alert_mail_title BLOB,
    zip_description BLOB,
    ping_mail_template BLOB,
    ping_mail_title BLOB,
    disable_admin_notification_emails INTEGER NOT NULL,
    disable_receivers_notification_emails INTEGER NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE receiver (
    id VARCHAR NOT NULL,
    user_id VARCHAR NOT NULL,
    configuration VARCHAR NOT NULL CHECK (configuration IN ('default', 'forcefully_selected', 'unselectable')),
    creation_date VARCHAR NOT NULL,
    can_delete_submission INTEGER NOT NULL,
    postpone_superpower INTEGER NOT NULL,
    description BLOB NOT NULL,
    last_update VARCHAR,
    name VARCHAR NOT NULL,
    comment_notification INTEGER NOT NULL,
    file_notification INTEGER NOT NULL,
    tip_notification INTEGER NOT NULL,
    message_notification INTEGER NOT NULL,
    ping_notification INTEGER NOT NULL,
    mail_address VARCHAR NOT NULL,
    ping_mail_address VARCHAR NOT NULL,
    gpg_key_status VARCHAR NOT NULL CHECK (gpg_key_status IN ('disabled', 'enabled')),
    gpg_key_info VARCHAR,
    gpg_key_fingerprint VARCHAR,
    gpg_key_armor VARCHAR,
    gpg_key_expiration INTEGER,
    presentation_order INTEGER,
    PRIMARY KEY (id),
    UNIQUE (name),
    FOREIGN KEY(user_id) REFERENCES user(id) ON DELETE CASCADE
);

CREATE TABLE eventlogs (
    id VARCHAR NOT NULL,
    creation_date VARCHAR NOT NULL,
    event_reference VARCHAR NOT NULL,
    description VARCHAR NOT NULL,
    title VARCHAR NOT NULL,
    receiver_id VARCHAR NOT NULL,
    receivertip_id VARCHAR,
    mail_sent INTEGER,
    PRIMARY KEY (id),
    FOREIGN KEY(receiver_id) REFERENCES receiver(id) ON DELETE CASCADE,
    FOREIGN KEY(receivertip_id) REFERENCES receivertip(id) ON DELETE CASCADE
);

CREATE TABLE receiver_context (
    context_id VARCHAR NOT NULL,
    receiver_id VARCHAR NOT NULL,
    PRIMARY KEY (context_id, receiver_id),
    FOREIGN KEY (context_id) REFERENCES context(id) ON DELETE CASCADE,
    FOREIGN KEY (receiver_id) REFERENCES receiver(id) ON DELETE CASCADE
);

CREATE TABLE receiver_internaltip (
    receiver_id VARCHAR NOT NULL,
    internaltip_id VARCHAR NOT NULL,
    PRIMARY KEY (receiver_id, internaltip_id),
    FOREIGN KEY (receiver_id) REFERENCES receiver(id) ON DELETE CASCADE,
    FOREIGN KEY (internaltip_id) REFERENCES internaltip(id) ON DELETE CASCADE
);

CREATE TABLE field_field (
    parent_id VARCHAR NOT NULL,
    child_id VARCHAR NOT NULL,
    PRIMARY KEY (parent_id, child_id),
    FOREIGN KEY (parent_id) REFERENCES field(id) ON DELETE CASCADE,
    FOREIGN KEY (child_id) REFERENCES field(id) ON DELETE CASCADE
);

CREATE TABLE step_field (
    step_id VARCHAR NOT NULL,
    field_id VARCHAR NOT NULL,
    PRIMARY KEY (step_id, field_id),
    UNIQUE (field_id)
    FOREIGN KEY (step_id) REFERENCES step(id) ON DELETE CASCADE,
    FOREIGN KEY (field_id) REFERENCES field(id) ON DELETE CASCADE
);

CREATE TABLE receivertip (
    id VARCHAR NOT NULL,
    creation_date VARCHAR NOT NULL,
    access_counter INTEGER NOT NULL,
    internaltip_id VARCHAR NOT NULL,
    last_access VARCHAR,
    notification_date VARCHAR,
    mark VARCHAR NOT NULL CHECK (mark IN ('not notified', 'notified', 'unable to notify', 'disabled', 'skipped')),
    receiver_id VARCHAR NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY(internaltip_id) REFERENCES internaltip(id) ON DELETE CASCADE,
    FOREIGN KEY(receiver_id) REFERENCES receiver(id) ON DELETE CASCADE
);

CREATE TABLE whistleblowertip (
    id VARCHAR NOT NULL,
    creation_date VARCHAR NOT NULL,
    access_counter INTEGER NOT NULL,
    internaltip_id VARCHAR NOT NULL,
    last_access VARCHAR,
    receipt_hash VARCHAR NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY(internaltip_id) REFERENCES internaltip(id) ON DELETE CASCADE
);

CREATE TABLE applicationdata (
    id VARCHAR NOT NULL,
    creation_date VARCHAR NOT NULL,
    version INTEGER NOT NULL,
    fields BLOB,
    PRIMARY KEY (id)
);

CREATE TABLE anomalies (
    id VARCHAR NOT NULL,
    creation_date VARCHAR NOT NULL,
    content BLOB,
    stored_when VARCHAR NOT NULL,
    alarm INTEGER NOT NULL,
    events BLOB,
    PRIMARY KEY (id)
);

CREATE TABLE stats (
    id VARCHAR NOT NULL,
    creation_date VARCHAR NOT NULL,
    start VARCHAR NOT NULL,
    free_disk_space INTEGER,
    summary BLOB,
    PRIMARY KEY (id)
);

CREATE TABLE field (
    id VARCHAR NOT NULL,
    creation_date VARCHAR NOT NULL,
    label TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    hint TEXT NOT NULL DEFAULT '',
    multi_entry INTEGER NOT NULL DEFAULT 0,
    required INTEGER,
    preview INTEGER,
    stats_enabled INTEGER NOT NULL DEFAULT 0,
    is_template INTEGER NOT NULL DEFAULT 0,
    x INTEGER NOT NULL DEFAULT 0,
    y INTEGER NOT NULL DEFAULT 0,
    type VARCHAR NOT NULL CHECK (TYPE IN ('inputbox',
                                          'textarea',
                                          'selectbox',
                                          'checkbox',
                                          'modal',
                                          'dialog',
                                          'tos',
                                          'fileupload',
                                          'fieldgroup'
                                          )),
    PRIMARY KEY (id)
);

CREATE TABLE fieldoption (
    id VARCHAR NOT NULL,
    creation_date VARCHAR NOT NULL,
    field_id VARCHAR NOT NULL,
    attrs TEXT NOT NULL DEFAULT '{}',
    number INTEGER NOT NULL CHECK(number > 0),
    PRIMARY KEY (id),
    FOREIGN KEY(field_id) REFERENCES field(id) ON DELETE CASCADE
);

CREATE TABLE step (
    id VARCHAR NOT NULL,
    creation_date VARCHAR NOT NULL,
    label TEXT NOT NULL,
    description TEXT NOT NULL,
    hint TEXT NOT NULL,
    context_id VARCHAR NOT NULL,
    number INTEGER NOT NULL CHECK(number > 0),
    PRIMARY KEY (id)
    UNIQUE (context_id, number),
    FOREIGN KEY(context_id) REFERENCES context(id) ON DELETE CASCADE
);
