-- MySQL dump 10.13  Distrib 5.5.12, for solaris10 (i386)
--
-- Host: sql    Database: u_earwig_copyvios
-- ------------------------------------------------------
-- Server version       5.1.59


CREATE DATABASE `u_earwig_copyvios`
  DEFAULT CHARACTER SET utf8
  DEFAULT COLLATE utf8_unicode_ci;

--
-- Table structure for table `background`
--

DROP TABLE IF EXISTS `background`;
CREATE TABLE `background` (
  `background_id` int(9) unsigned NOT NULL,
  `background_filename` varchar(512) COLLATE utf8_unicode_ci DEFAULT NULL,
  `background_url` varchar(512) COLLATE utf8_unicode_ci DEFAULT NULL,
  `background_descurl` varchar(512) COLLATE utf8_unicode_ci DEFAULT NULL,
  `background_width` int(9) unsigned DEFAULT NULL,
  `background_height` int(9) unsigned DEFAULT NULL,
  PRIMARY KEY (`background_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Table structure for table `language`
--

DROP TABLE IF EXISTS `language`;
CREATE TABLE `language` (
  `lang_code` varchar(64) COLLATE utf8_unicode_ci NOT NULL DEFAULT '',
  `lang_name` varchar(512) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`lang_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Table structure for table `project`
--

DROP TABLE IF EXISTS `project`;
CREATE TABLE `project` (
  `project_code` varchar(64) COLLATE utf8_unicode_ci NOT NULL DEFAULT '',
  `project_name` varchar(512) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`project_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Table structure for table `updates`
--

DROP TABLE IF EXISTS `updates`;
CREATE TABLE `updates` (
  `update_service` varchar(128) COLLATE utf8_unicode_ci NOT NULL DEFAULT '',
  `update_time` int(10) unsigned DEFAULT NULL,
  PRIMARY KEY (`update_service`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- Dump completed on 2012-07-20 20:16:08
