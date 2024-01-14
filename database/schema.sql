IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = [categories]) then
    CREATE TABLE [categories] (
        [id] INT IDENTITY(1,1) PRIMARY KEY,
        [guild_id] INT NOT NULL,
        [category_name] VARCHAR(255) NOT NULL,
        [category_description] VARCHAR(4000) NULL,
        [created_at] DATETIME2 NOT NULL DEFAULT GETUTCDATE()
    );

IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = [items_to_rate]) then
    CREATE TABLE [items_to_rate] (
        [id] INT IDENTITY(1,1) PRIMARY KEY,
        [guild_id] INT NOT NULL,
        [category_id] INT NOT NULL,
        [name] VARCHAR(255) NOT NULL,
        [description] VARCHAR(4000) NULL,
        [available_to_rate_date] DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
        [created_at] DATETIME2 NOT NULL DEFAULT GETUTCDATE()
    );

IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = [ratings]) then
    CREATE TABLE [ratings] (
        [id] INT IDENTITY(1,1) PRIMARY KEY,
        [guild_id] VARCHAR(20) NOT NULL,
        [item_id] INT NOT NULL,
        [user_id] VARCHAR(20) NOT NULL,
        [rating] INT NOT NULL,
        [created_at] DATETIME2 NOT NULL DEFAULT GETUTCDATE()
    );