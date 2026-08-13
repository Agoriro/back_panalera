BEGIN;

CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL, 
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Running upgrade  -> e18e2c160be2

CREATE TABLE categories (
    id_category UUID DEFAULT gen_random_uuid() NOT NULL, 
    name_category VARCHAR NOT NULL, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
    updated_at TIMESTAMP WITH TIME ZONE, 
    PRIMARY KEY (id_category), 
    UNIQUE (name_category)
);

CREATE TABLE colors (
    id_color UUID DEFAULT gen_random_uuid() NOT NULL, 
    name_color VARCHAR NOT NULL, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
    updated_at TIMESTAMP WITH TIME ZONE, 
    PRIMARY KEY (id_color), 
    UNIQUE (name_color)
);

CREATE TABLE genders (
    id_gender UUID DEFAULT gen_random_uuid() NOT NULL, 
    name_gender VARCHAR NOT NULL, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
    updated_at TIMESTAMP WITH TIME ZONE, 
    PRIMARY KEY (id_gender), 
    UNIQUE (name_gender)
);

CREATE TABLE roles (
    id_role UUID DEFAULT gen_random_uuid() NOT NULL, 
    name VARCHAR NOT NULL, 
    PRIMARY KEY (id_role), 
    UNIQUE (name)
);

CREATE TABLE sizes (
    id_size UUID DEFAULT gen_random_uuid() NOT NULL, 
    name_size VARCHAR NOT NULL, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
    updated_at TIMESTAMP WITH TIME ZONE, 
    PRIMARY KEY (id_size), 
    UNIQUE (name_size)
);

CREATE TABLE suppliers (
    id_supplier UUID DEFAULT gen_random_uuid() NOT NULL, 
    name_supplier VARCHAR NOT NULL, 
    address VARCHAR, 
    is_active BOOLEAN DEFAULT true, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
    updated_at TIMESTAMP WITH TIME ZONE, 
    PRIMARY KEY (id_supplier)
);

CREATE TABLE inventory (
    id_inventory UUID DEFAULT gen_random_uuid() NOT NULL, 
    description_inventory VARCHAR NOT NULL, 
    code_inventory VARCHAR,
    barcode_inventory VARCHAR,
    utility NUMERIC(18, 6) NOT NULL, 
    id_supplier UUID NOT NULL, 
    id_color UUID NOT NULL, 
    id_size UUID NOT NULL, 
    id_category UUID NOT NULL, 
    id_gender UUID NOT NULL, 
    is_active BOOLEAN DEFAULT true, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
    updated_at TIMESTAMP WITH TIME ZONE, 
    PRIMARY KEY (id_inventory), 
    FOREIGN KEY(id_category) REFERENCES categories (id_category), 
    FOREIGN KEY(id_color) REFERENCES colors (id_color), 
    FOREIGN KEY(id_gender) REFERENCES genders (id_gender), 
    FOREIGN KEY(id_size) REFERENCES sizes (id_size), 
    FOREIGN KEY(id_supplier) REFERENCES suppliers (id_supplier)
);

CREATE TABLE users (
    id_user UUID DEFAULT gen_random_uuid() NOT NULL, 
    "user" VARCHAR NOT NULL, 
    password VARCHAR NOT NULL, 
    id_role UUID NOT NULL, 
    is_active BOOLEAN DEFAULT true, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
    updated_at TIMESTAMP WITH TIME ZONE, 
    PRIMARY KEY (id_user), 
    FOREIGN KEY(id_role) REFERENCES roles (id_role), 
    UNIQUE ("user")
);

CREATE TABLE inventory_photos (
    id_reg UUID DEFAULT gen_random_uuid() NOT NULL, 
    id_inventory UUID NOT NULL, 
    url_photo VARCHAR NOT NULL, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
    updated_at TIMESTAMP WITH TIME ZONE, 
    PRIMARY KEY (id_reg), 
    FOREIGN KEY(id_inventory) REFERENCES inventory (id_inventory) ON DELETE CASCADE
);

CREATE TYPE movementtype AS ENUM ('BUY', 'SELL');

CREATE TABLE movements (
    id_movement UUID DEFAULT gen_random_uuid() NOT NULL, 
    type_movement movementtype NOT NULL, 
    date TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    id_supplier UUID, 
    id_inventory UUID NOT NULL, 
    quantity INTEGER NOT NULL, 
    value NUMERIC(18, 6) NOT NULL, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
    updated_at TIMESTAMP WITH TIME ZONE, 
    PRIMARY KEY (id_movement), 
    FOREIGN KEY(id_inventory) REFERENCES inventory (id_inventory), 
    FOREIGN KEY(id_supplier) REFERENCES suppliers (id_supplier)
);

INSERT INTO alembic_version (version_num) VALUES ('e18e2c160be2') RETURNING alembic_version.version_num;

COMMIT;

