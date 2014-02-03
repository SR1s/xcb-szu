# database schema
CREATE TABLE IF NOT EXISTS `columns` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(255) NOT NULL,
  `order` int(11) NOT NULL DEFAULT '255',
  `parent_id` int(11) NOT NULL DEFAULT '0',
  `is_delete` int(1) NOT NULL DEFAULT '0',
  `comments` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=7 ;
