-- MySQL dump 10.13  Distrib 5.5.12, for solaris10 (i386)
--
-- Host: sql    Database: u_earwig_toolserver
-- ------------------------------------------------------
-- Server version       5.1.59

--
-- Table structure for table `language`
--

DROP TABLE IF EXISTS `language`;
CREATE TABLE `language` (
  `lang_code` varchar(16) NOT NULL DEFAULT '',
  `lang_name` varchar(16) DEFAULT NULL,
  PRIMARY KEY (`lang_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Table structure for table `project`
--

DROP TABLE IF EXISTS `project`;
CREATE TABLE `project` (
  `project_code` varchar(16) NOT NULL DEFAULT '',
  `project_name` varchar(16) DEFAULT NULL,
  PRIMARY KEY (`project_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Table structure for table `updates`
--

DROP TABLE IF EXISTS `updates`;
CREATE TABLE `updates` (
  `update_service` varchar(128) NOT NULL DEFAULT '',
  `update_time` int(10) unsigned DEFAULT NULL,
  PRIMARY KEY (`update_service`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Dump completed on 2012-07-20 18:28:12
