CREATE TABLE IF NOT EXISTS `warns` (
  `id` INT(11) NOT NULL,
  `user_id` VARCHAR(20) NOT NULL,
  `server_id` VARCHAR(20) NOT NULL,
  `moderator_id` VARCHAR(20) NOT NULL,
  `reason` VARCHAR(255) NOT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

DROP TABLE IF EXISTS [categories];
CREATE TABLE IF NOT EXISTS [categories] (
  [id] INT PRIMARY KEY,
  [guild_id] VARCHAR(20) NOT NULL,
  [category_name] VARCHAR(255) NOT NULL,
  [category_description] VARCHAR(4000) NOT NULL,
  [created_at] TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

DROP TABLE IF EXISTS [items_to_rate];
CREATE TABLE IF NOT EXISTS [items_to_rate] (
  [id] INT PRIMARY KEY,
  [guild_id] VARCHAR(20) NOT NULL,
  [category_id] INT NOT NULL,
  [name] VARCHAR(255) NOT NULL,
  [description] VARCHAR(4000) NOT NULL,
  [available_to_rate_date] TIMESTAMP NOT NULL,
  [created_at] TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

DROP TABLE IF EXISTS [ratings];
CREATE TABLE IF NOT EXISTS [ratings] (
  [id] INT PRIMARY KEY,
  [guild_id] VARCHAR(20) NOT NULL,
  [item_id] INT NOT NULL,
  [user_id] VARCHAR(20) NOT NULL,
  [rating] INT NOT NULL,
  [created_at] TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);