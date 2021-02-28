
CREATE TABLE `craigslist_jobs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `site` varchar(100) NOT NULL,
  `title` text NOT NULL,
  `location` varchar(100) NOT NULL,
  `body` longtext NOT NULL,
  `time` datetime NOT NULL,
  `post_id` varchar(150) NOT NULL,
  `times_encountered` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  UNIQUE KEY `post_id_UNIQUE` (`post_id`)
)

CREATE TABLE `craigslist_reposts` (
  `id` int NOT NULL AUTO_INCREMENT,
  `post_id` varchar(45) NOT NULL,
  `original_post_id` varchar(45) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `COMBO KEY UNIQUE` (`post_id`,`original_post_id`),
  KEY `original_ids` (`original_post_id`),
  CONSTRAINT `post_id_in_original` FOREIGN KEY (`original_post_id`) REFERENCES `jobs_craigslist` (`post_id`) ON DELETE CASCADE ON UPDATE CASCADE
)
