CREATE DATABASE network;

USE network;

CREATE TABLE IF NOT EXISTS `vpc_subnets` (
    `id` int(11) NOT NULL auto_increment,       
    `network` varchar(250)  NOT NULL default '',
    `region` varchar(250)  NOT NULL default '',
    `ip_cidr_ranges` varchar(250)  NOT NULL default '',
    PRIMARY KEY  (`id`)
);